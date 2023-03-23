from config.flask_config import app
from models.models import Project, Milestone, ReservedOffset, db
from flask import abort, request, jsonify
from datetime import datetime
from classes.response import ResponseBodyJSON
from classes.exception import CustomException
from classes.amqp_payload import Payload
from sqlalchemy.exc import IntegrityError
from config.amqp_setup import *
import json

@app.errorhandler(404)
def handle_resource_not_found(e):
    """Handles exception thrown when flask app is aborted using `abort` with HTTP status code 404."""
    app.logger.exception(e)
    data = CustomException(str(e)).json()
    res = ResponseBodyJSON(False, data).json()
    return jsonify(res), 404

@app.errorhandler(400)
def handle_bad_request(e):
    """Handles exception thrown when flask app is aborted using `abort` with HTTP status code 400."""
    app.logger.exception(e)
    data = CustomException(str(e)).json()
    res = ResponseBodyJSON(False, data).json()
    return jsonify(res), 400

@app.errorhandler(KeyError)
def handle_key_error(e: KeyError):
    """Handles exception thrown when KeyError is thrown most probably when a field is missing in request body."""
    app.logger.exception(e)
    data = CustomException(f"Fields missing from request body {e.args}").json()
    res = ResponseBodyJSON(False, data).json()
    return jsonify(res), 400

@app.errorhandler(IntegrityError)
def handle_integrity_error(e: IntegrityError):
    """Handles exception when integrity constraint in database are violated. E.g. not nullable fields are null (due to missing fields in request body)"""
    # print(f'IntegrityError: {e._message}')
    app.logger.exception(e._message)
    data = CustomException(f"Integrity constraint in database are violated. Did you check if all fields are present in request body? Error message: {e._message}").json()
    res = ResponseBodyJSON(False, data).json()
    
    return jsonify(res), 400

@app.errorhandler(Exception)
def handle_unhandled_exception(e: Exception):
    app.logger.exception(e)
    data = CustomException(e).json()
    res = ResponseBodyJSON(False, data).json()
    return jsonify(res), 500


@app.route('/test')
def test():
    return 'test'

@app.route('/projects')
def find_all_projects():
    projects = db.session.execute(db.select(Project)).scalars().all()
    data = [project.json() for project in projects]
    res =  ResponseBodyJSON(True, data).json()
    return jsonify(res), 200
    
@app.route("/projects/<uuid:id>")
def find_project_by_id(id):
    project = db.session.execute(db.select(Project).where(Project.id == id)).scalars().first()

    if project is None:
        abort(404, description=f"Project {str(id)} not found.")
    
    data = project.json()
    res = ResponseBodyJSON(True, data).json()
    return jsonify(res), 200

@app.route("/projects", methods=['POST'])
def create_project():
    """ Creates a project and all its milestones in db and publishes created project to project_verified queue.
    """
    body = request.get_json()

    milestones = body.pop('milestones')

    # add project first then add all milestones to populate project id in `project`
    project = Project(**body)
    db.session.add(project)
    db.session.flush() # for sqlalchemy to populate null fields in project
    
    for milestone in milestones:
        milestone['due_date'] = datetime.strptime(milestone['due_date'], '%Y-%m-%dT%H:%M:%S.%fZ') # parse iso format string in request body to datetime
        m = Milestone(**milestone, project=project, offsets_total=milestone['offsets_available'])
        db.session.add(m)

    data = project.json() # project will have all the milestones populated due to the `relationship()` in models.py

    # publish to project_verified queue
    check_setup(connection, channel, hostname, port, exchangename, exchangetype)
    payload =  Payload(resource_id=str(project.id), type='project.create', data=data)
    payload_serialised = json.dumps(payload.json())
    publish_message(channel=channel, exchangename=exchangename, routing_key=QUEUES[PROJECTS_CREATED_QUEUE][ROUTING_KEY], message=payload_serialised)

    db.session.commit()
    res = ResponseBodyJSON(True, data).json()
    return jsonify(res), 201


@app.route("/projects/<uuid:id>/status", methods=['PATCH'])
def update_project_status(id):
    """PATCH endpoint to update project status e.g. "Verified" and publishes to project_verified queue.
    """
    
    project = db.session.execute(db.select(Project).where(Project.id == id)).scalars().first()
    if project is None:
        abort(404, description=f"Project {str(id)} not found.")
        
    body = request.get_json()
    
    # If request body status is "Verified" publish to project_verified queue
    data = project.json()
    if body['status'] == 'Verified':
        project.status = body['status']
        check_setup(connection, channel, hostname, port, exchangename, exchangetype)
        payload =  Payload(resource_id=str(project.id), type='project.verify', data=data)
        payload_serialised = json.dumps(payload.json()) 
        publish_message(channel=channel, exchangename=exchangename, routing_key=QUEUES[PROJECTS_VERIFIED_QUEUE][ROUTING_KEY], message=payload_serialised)

    else:
        abort(400, description=f"Invalid status {body['status']}. Status can only be 'Verified'.") # update more status later e.g. "Rejected"

    db.session.commit()
    res = ResponseBodyJSON(True, data).json()
    return jsonify(res), 200

    
@app.route("/projects/<uuid:id>/milestone/<uuid:mid>/status", methods=['PATCH'])
def update_project_milestone_status(id, mid):
    """ PATCH endpoint to 
    1. update project milestone status e.g. "Met" | "Rejected" 
    2. if status is "Met"
        2a. increase project rating
        2b. publish to `project_verified` queue
    3. if status is "Rejected"
        3a. decrease project rating
        3b. publish to `project_rejected` queue
    """
    project: Project or None = db.session.execute(db.select(Project).where(Project.id == id)).scalars().first()
    if project is None:
        abort(404, description=f"Project {str(id)} not found.")

    body = request.get_json()
    target_milestone = list(filter(lambda m: m.id == mid, project.milestones))
    if len(target_milestone) == 0:
        abort(404, description=f"Milestone {str(mid)} not found.")
    
    milestone = target_milestone[0]
    milestone.status = body['status']
    
    check_setup(connection, channel, hostname, port, exchangename, exchangetype)
    data = project.json()
    print(f'project data: {data}', end='\n\n')
    # publish to project_verified queue if status is "Met" + increase project rating
    if body['status'] == 'Met':
        payload =  Payload(resource_id=str(milestone.id), type='milestone.reward', data=data)
        payload_serialised = json.dumps(payload.json()) 
        publish_message(channel=channel, exchangename=exchangename, routing_key=QUEUES[PROJECTS_MILESTONES_REWARD_QUEUE][ROUTING_KEY], message=payload_serialised)
        print(f'published to {PROJECTS_MILESTONES_REWARD_QUEUE}: {payload_serialised}')
        project.rating += 10
    
    # publish to project_penalised queue if status is "Rejected" + decrease project rating
    elif body['status'] == 'Rejected':
        payload =  Payload(resource_id=str(milestone.id), type='milestone.penalise', data=data)
        payload_serialised = json.dumps(payload.json()) 
        publish_message(channel=channel, exchangename=exchangename, routing_key=QUEUES[PROJECTS_MILESTONES_PENALISE_QUEUE][ROUTING_KEY], message=payload_serialised)
        project.rating -= 10
    else:
        abort(400, description=f"Invalid status {body['status']}. Expected 'Met' or 'Rejected'.")

    data = milestone.json()
    db.session.commit()
    res = ResponseBodyJSON(True, data).json()
    return jsonify(res), 200
    

@app.route("/projects/milestones/<uuid:mid>")
def find_milestone_by_id(mid):
    milestone = db.session.execute(db.select(Milestone).where(Milestone.id == mid)).scalars().first()

    if milestone is None:
        data = CustomException(f"Milestone {str(mid)} not found.", str(mid)).json()
        res = ResponseBodyJSON(False, data).json()
        return jsonify(res), 404
    
    data = milestone.json()
    res = ResponseBodyJSON(True, data).json()
    return jsonify(res), 200


@app.route("/projects/<uuid:id>/milestones/<uuid:mid>/offset", methods=['POST'])
def create_reserved_offset(id, mid):
    """ POST endpoint to 
    1. create a reserved offset for a project milestone, buyer, and amount
    2. deduct offsets from project milestone `offsets_available`
    3. publish to `offset_reserved` queue
    """
    body = request.get_json()
    payment_id = body['payment_id']
    if db.session.execute(db.select(ReservedOffset).where(ReservedOffset.payment_id == payment_id)).scalars().first() is not None:
        abort(400, description=f"Reservation already exists.")

    project = db.session.execute(db.select(Project).where(Project.id == id)).scalars().first()
    if project is None:
        abort(404, description=f"Project {str(id)} not found.")
        
    milestone = db.session.execute(db.select(Milestone).where(Milestone.id == mid)).scalars().first()
    if milestone is None:
        abort(404, description=f"Milestone {str(mid)} not found.")
    
    amount = body['amount']
    if amount > milestone.offsets_available:
        abort(400, description=f"Amount to reserve {amount} exceeds offsets available {milestone.offsets_available}.")
    
    # Insert new row in reserved offset table to reserve the amount, user_id, milestone_id, for a payment_id.
    reserved_offset = ReservedOffset(**body, milestone_id=str(mid))
    db.session.add(reserved_offset)

    # Deduct `amount` from request body from project milestone to reserve the amount for the buyer
    milestone.offsets_available -= amount
    
    db.session.flush() # to populate the created_at field for reserved_offset
    data = reserved_offset.json()

    # publish to project_milestone_offsets_reserve queue
    check_setup(connection, channel, hostname, port, exchangename, exchangetype)
    payload =  Payload(resource_id=reserved_offset.payment_id, type='offset.reserved', data=data)
    payload_serialised = json.dumps(payload.json())
    publish_message(channel=channel, exchangename=exchangename, routing_key=QUEUES[PROJECTS_MILESTONES_OFFSETS_RESERVE_QUEUE][ROUTING_KEY], message=payload_serialised)

    db.session.commit()
    res = ResponseBodyJSON(True, data).json()
    return jsonify(res), 201

    
@app.route("/projects/milestones/offset/<string:pid>")
def find_reserved_offset(pid):
    reservation = db.session.execute(db.select(ReservedOffset).where(ReservedOffset.payment_id == pid)).scalars().first()
    if reservation is None:
        abort(404, description=f"Reservation does not exist.")
    
    data = reservation.json()
    res = ResponseBodyJSON(True, data).json()
    return jsonify(res), 200


@app.route("/projects/milestones/offset", methods=['PATCH'])
def commit_reserved_offset():
    """ PATCH endpoint to 
    1. commit (delete reservation in db) a reserved offset for a project milestone, buyer, and amount after payment success
    2. publish to `offset_commit` queue
    """
    body = request.get_json()
    payment_id = body['payment_id']
    reservation = db.session.execute(db.select(ReservedOffset).where(ReservedOffset.payment_id == payment_id)).scalars().first()
    if reservation is None:
        abort(404, description=f"Reservation does not exist")
    
    data = reservation.json()
    db.session.delete(reservation)

    # publish to project_milestone_offsets_commit queue
    check_setup(connection, channel, hostname, port, exchangename, exchangetype)
    payload =  Payload(resource_id=data['payment_id'], type='offset.commit', data=data)
    payload_serialised = json.dumps(payload.json())
    publish_message(channel=channel, exchangename=exchangename, routing_key=QUEUES[PROJECTS_MILESTONES_OFFSETS_COMMIT_QUEUE][ROUTING_KEY], message=payload_serialised)

    db.session.commit()
    return jsonify(), 204
    
    
@app.route("/projects/milestones/offset", methods=['DELETE'])
def rollback_reserved_offset():
    """ DELETE endpoint to
    1. rollback (delete reservation in db) a reserved offset for a project milestone, buyer, and amount after payment failure
    2. add the reserved amount back to the project milestone `offsets_available`
    """
    body = request.get_json()
    payment_id = body['payment_id']
    reservation = db.session.execute(db.select(ReservedOffset).where(ReservedOffset.payment_id == payment_id)).scalars().first()
    if reservation is None:
        abort(404, description=f"Reservation does not exist.")
    
    # Given the payment_id, search for the corresponding reserved amount in reservedOffset table, and add it back to the milestone offset_available field.
    rollback_amount = reservation.amount
    milestone_id = reservation.milestone_id
    milestone = db.session.execute(db.select(Milestone).where(Milestone.id == milestone_id)).scalars().first()
    milestone.offsets_available += rollback_amount

    db.session.delete(reservation)

    data = milestone.json()
    # Get project and publish to project_milestone_offsets_rollback queue
    project = db.session.execute(db.select(Project).where(Project.id == milestone.project_id)).scalars().first()
    check_setup(connection, channel, hostname, port, exchangename, exchangetype)
    payload =  Payload(resource_id=str(milestone.id), type='offset.rollback', data=project.json())
    payload_serialised = json.dumps(payload.json())
    publish_message(channel=channel, exchangename=exchangename, routing_key=QUEUES[PROJECTS_MILESTONES_OFFSETS_ROLLBACK_QUEUE][ROUTING_KEY], message=payload_serialised)

    db.session.commit()
    res = ResponseBodyJSON(True, data).json()
    return jsonify(res), 200

    
@app.route("/projects/milestones/offset")
def find_all_reserved_offset():
    reserved_offsets = db.session.execute(db.select(ReservedOffset)).scalars().all()
    data = [r.json() for r in reserved_offsets]
    res = ResponseBodyJSON(True, data).json()
    return jsonify(res), 200
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
