from config.flask_config import app
from models.models import Project, Milestone, ReservedOffset, db
from flask import abort, request, jsonify
from datetime import datetime
from classes.response import ResponseBodyJSON
from classes.exception import CustomException
from classes.amqp_payload import Payload
from classes.enums import MilestoneStatus, ProjectStatus, AmqpPayloadType
from sqlalchemy.exc import IntegrityError
from config.amqp_setup import (
    RABBITMQ_HOSTNAME, RABBITMQ_PORT, exchangename, exchangetype, connection, channel, ROUTING_KEY, QUEUES, 
    PROJECTS_CREATED_QUEUE, PROJECTS_MILESTONES_ADD_QUEUE, PROJECTS_VERIFIED_QUEUE, PROJECTS_MILESTONES_OFFSETS_RESERVE_QUEUE,
    PROJECTS_MILESTONES_OFFSETS_COMMIT_QUEUE, PROJECTS_MILESTONES_OFFSETS_ROLLBACK_QUEUE, PROJECTS_MILESTONES_REWARD_QUEUE, 
    PROJECTS_MILESTONES_PENALISE_QUEUE,
    publish_message)
import json

request_time_format = '%Y-%m-%dT%H:%M:%S.%fZ'

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
    app.logger.exception(e)
    data = CustomException(f"Integrity constraint in database are violated. Did you check if all fields are present in request body? Error message: {str(e)}").json()
    res = ResponseBodyJSON(False, data).json()
    
    return jsonify(res), 400

@app.errorhandler(Exception)
def handle_unhandled_exception(e: Exception):
    app.logger.exception(e)
    data = CustomException(str(e)).json()
    res = ResponseBodyJSON(False, data).json()
    return jsonify(res), 500


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
    """ Creates a project and all its milestones in db and publishes created project to project_created queue.
    """
    body = request.get_json()

    milestones = body.pop('milestones')

    # add project first then add all milestones to populate project id in `project`
    project = Project(**body)
    db.session.add(project)
    db.session.flush() # for sqlalchemy to populate null fields in project
    
    for milestone in milestones:
        milestone['due_date'] = datetime.strptime(milestone['due_date'], request_time_format) # parse iso format string in request body to datetime
        m = Milestone(**milestone, project=project, offsets_total=milestone['offsets_available'])
        db.session.add(m)

    db.session.commit()
    
    # publish to project_created queue
    amqp_data = { "project": project.json() } # project will have all the milestones populated due to the `relationship()` in models.py
    payload =  Payload(resource_id=str(project.id), type=AmqpPayloadType.PROJECT_CREATE.value, data=amqp_data)
    payload_serialised = json.dumps(payload.json())
    publish_message(connection=connection, channel=channel, hostname=RABBITMQ_HOSTNAME, exchangename=exchangename, port=RABBITMQ_PORT, exchangetype=exchangetype, routing_key=QUEUES[PROJECTS_CREATED_QUEUE][ROUTING_KEY], message=payload_serialised)

    rest_data = project.json()
    res = ResponseBodyJSON(True, rest_data).json()
    return jsonify(res), 201


@app.route("/projects/<uuid:id>/status", methods=['PATCH'])
def update_project_status(id):
    """PATCH endpoint to update project status e.g. "verified" and publishes to project_verified queue.
    """
    
    project = db.session.execute(db.select(Project).where(Project.id == id)).scalars().first()
    if project is None:
        abort(404, description=f"Project {str(id)} not found.")
        
    body = request.get_json()
    
    # If request body status is "verified" publish to project_verified queue
    if body['status'] not in ProjectStatus.values():
        abort(400, description=f"Invalid status '{body['status']}'. Status can only be the following: {ProjectStatus.values()}")

    project.status = body['status']
    db.session.commit()

    amqp_data = { "project": project.json() }
    payload =  Payload(resource_id=str(project.id), type=AmqpPayloadType.PROJECT_VERIFY.value, data=amqp_data)
    payload_serialised = json.dumps(payload.json()) 
    publish_message(connection=connection, channel=channel, hostname=RABBITMQ_HOSTNAME, exchangename=exchangename, port=RABBITMQ_PORT, exchangetype=exchangetype, routing_key=QUEUES[PROJECTS_VERIFIED_QUEUE][ROUTING_KEY], message=payload_serialised)

    rest_data = project.json()
    res = ResponseBodyJSON(True, rest_data).json()
    return jsonify(res), 200

@app.route("/projects/<uuid:id>/milestones", methods=['POST'])
def create_project_milestone(id):
    """ Creates milestones for a project in db and publishes to milestone_add queue.
    """
    body = request.get_json()

    # Get project by id
    project = db.session.execute(db.select(Project).where(Project.id == id)).scalars().first()
    if project is None:
        abort(404, description=f"Project {str(id)} not found.")
    
    body['due_date'] = datetime.strptime(body['due_date'], request_time_format) # parse iso format string in request body to datetime
    milestone = Milestone(**body, project=project, offsets_total=body['offsets_available'])
    db.session.add(milestone)

    db.session.commit()
    rest_data = milestone.json()
    
    amqp_data = { 'project': project.json() }

    payload =  Payload(resource_id=str(milestone.id), type=AmqpPayloadType.MILESTONE_ADD.value, data=amqp_data)
    payload_serialised = json.dumps(payload.json())
    publish_message(connection=connection, channel=channel, hostname=RABBITMQ_HOSTNAME, exchangename=exchangename, port=RABBITMQ_PORT, exchangetype=exchangetype, routing_key=QUEUES[PROJECTS_MILESTONES_ADD_QUEUE][ROUTING_KEY], message=payload_serialised)

    res = ResponseBodyJSON(True, rest_data).json()
    return jsonify(res), 201

    
@app.route("/projects/<uuid:id>/milestones/<uuid:mid>/status", methods=['PATCH'])
def update_project_milestone_status(id, mid):
    """ PATCH endpoint to 
    1. update project milestone status e.g. "Met" | "Rejected" 
    2. if status is "Met"
        2a. increase project rating
        2b. publish to `ratings_reward` queue
    3. if status is "Rejected"
        3a. decrease project rating
        3b. publish to `ratings_penalise` queue
    """
    project = db.session.execute(db.select(Project).where(Project.id == id)).scalars().first()
    if project is None:
        abort(404, description=f"Project {str(id)} not found.")

    body = request.get_json()
    target_milestone = list(filter(lambda m: m.id == mid, project.milestones))
    if len(target_milestone) == 0:
        abort(404, description=f"Milestone {str(mid)} not found.")
    
    milestone = target_milestone[0]
    if body['status'] not in MilestoneStatus.values():
        abort(400, description=f"Invalid status '{body['status']}'. Status can only be the following: {MilestoneStatus.values()}")

    milestone.status = body['status']
    db.session.commit()
    
    # increase project rating + publish to project_verified queue
    if body['status'] == MilestoneStatus.MET.value:
        project.rating += 10
        amqp_data = { "project": project.json() } 
        payload =  Payload(resource_id=str(milestone.id), type=AmqpPayloadType.MILESTONE_REWARD.value, data=amqp_data)
        payload_serialised = json.dumps(payload.json()) 
        publish_message(connection=connection, channel=channel, hostname=RABBITMQ_HOSTNAME, exchangename=exchangename, port=RABBITMQ_PORT, exchangetype=exchangetype, routing_key=QUEUES[PROJECTS_MILESTONES_REWARD_QUEUE][ROUTING_KEY], message=payload_serialised)
        
    # decrease project rating + publish to project_penalised queue
    elif body['status'] == MilestoneStatus.REJECTED.value:
        project.rating -= 10
        amqp_data = { "project": project.json() } 
        payload =  Payload(resource_id=str(milestone.id), type=AmqpPayloadType.MILESTONE_PENALISE.value, data=amqp_data)
        payload_serialised = json.dumps(payload.json()) 
        publish_message(connection=connection, channel=channel, hostname=RABBITMQ_HOSTNAME, exchangename=exchangename, port=RABBITMQ_PORT, exchangetype=exchangetype, routing_key=QUEUES[PROJECTS_MILESTONES_PENALISE_QUEUE][ROUTING_KEY], message=payload_serialised)

    rest_data = milestone.json()
    res = ResponseBodyJSON(True, rest_data).json()
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
    try:
        amount = float(amount)
    except ValueError:
        abort(400, description=f"Invalid amount {amount}. Amount must be a number.")

    if amount > milestone.offsets_available:
        abort(400, description=f"Unable to reserve {amount} offsets. Amount to reserve {amount} exceeds offsets available {milestone.offsets_available}.")
    
    # Insert new row in reserved offset table to reserve the amount, user_id, milestone_id, for a payment_id.
    reserved_offset = ReservedOffset(**body, milestone_id=str(mid))
    db.session.add(reserved_offset)

    # Deduct `amount` from request body from project milestone to reserve the amount for the buyer
    milestone.offsets_available -= amount
    
    db.session.commit()

    # publish to queue
    amqp_data = { "reserved_offset": reserved_offset.json() }
    amqp_data['project'] = project.json() # add project to the payload for search
    payload =  Payload(resource_id=reserved_offset.payment_id, type=AmqpPayloadType.OFFSETS_RESERVE.value, data=amqp_data)
    payload_serialised = json.dumps(payload.json())
    publish_message(connection=connection, channel=channel, hostname=RABBITMQ_HOSTNAME, exchangename=exchangename, port=RABBITMQ_PORT, exchangetype=exchangetype, routing_key=QUEUES[PROJECTS_MILESTONES_OFFSETS_RESERVE_QUEUE][ROUTING_KEY], message=payload_serialised)

    rest_data = reserved_offset.json() 
    res = ResponseBodyJSON(True, rest_data).json()
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
    reservation: ReservedOffset or None = db.session.execute(db.select(ReservedOffset).where(ReservedOffset.payment_id == payment_id)).scalars().first()
    if reservation is None:
        abort(404, description=f"Reservation does not exist")
    
    db.session.delete(reservation)
    db.session.commit()

    # publish to project_milestone_offsets_commit queue
    amqp_data = { "reserved_offset": reservation.json() }
    payload =  Payload(resource_id=reservation.payment_id, type=AmqpPayloadType.OFFSETS_COMMIT.value, data=amqp_data)
    payload_serialised = json.dumps(payload.json())
    publish_message(connection=connection, channel=channel, hostname=RABBITMQ_HOSTNAME, exchangename=exchangename, port=RABBITMQ_PORT, exchangetype=exchangetype, routing_key=QUEUES[PROJECTS_MILESTONES_OFFSETS_COMMIT_QUEUE][ROUTING_KEY], message=payload_serialised)

    rest_data = reservation.json()
    res = ResponseBodyJSON(True, rest_data).json()
    return jsonify(res), 200
    
    
@app.route("/projects/milestones/offset", methods=['DELETE'])
def rollback_reserved_offset():
    """ DELETE endpoint to
    1. rollback (delete reservation in db) a reserved offset for a project milestone, buyer, and amount after payment failure
    2. add the reserved amount back to the project milestone `offsets_available`
    """
    body = request.get_json()
    payment_id = body['payment_id']
    reservation: ReservedOffset or None = db.session.execute(db.select(ReservedOffset).where(ReservedOffset.payment_id == payment_id)).scalars().first()
    if reservation is None:
        abort(404, description=f"Reservation does not exist.")
    
    # Given the payment_id, search for the corresponding reserved amount in reservedOffset table, and add it back to the milestone offset_available field.
    rollback_amount = reservation.amount
    milestone_id = reservation.milestone_id
    milestone = db.session.execute(db.select(Milestone).where(Milestone.id == milestone_id)).scalars().first()
    milestone.offsets_available += rollback_amount

    db.session.delete(reservation)
    db.session.commit()

    # Get project and publish to project_milestone_offsets_rollback queue
    amqp_data = { "reserved_offset": reservation.json() }
    project = db.session.execute(db.select(Project).where(Project.id == milestone.project_id)).scalars().first()
    amqp_data['project'] = project.json() # add project to the payload for search
    payload =  Payload(resource_id=reservation.payment_id, type=AmqpPayloadType.OFFSETS_ROLLBACK.value, data=amqp_data)
    payload_serialised = json.dumps(payload.json())
    publish_message(connection=connection, channel=channel, hostname=RABBITMQ_HOSTNAME, exchangename=exchangename, port=RABBITMQ_PORT, exchangetype=exchangetype, routing_key=QUEUES[PROJECTS_MILESTONES_OFFSETS_ROLLBACK_QUEUE][ROUTING_KEY], message=payload_serialised)

    rest_data = reservation.json()
    res = ResponseBodyJSON(True, rest_data).json()
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