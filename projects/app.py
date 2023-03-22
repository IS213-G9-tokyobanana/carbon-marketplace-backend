from config.config import app
from models.models import Project, Milestone, ReservedOffset, db
from flask import abort, request, jsonify
from datetime import datetime
from classes.response import ResponseBodyJSON, CustomException
from sqlalchemy.exc import IntegrityError

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
def integrity_error(e: IntegrityError):
    """Handles exception when integrity constraint in database are violated. E.g. not nullable fields are null (due to missing fields in request body)"""
    # print(f'IntegrityError: {e._message}')
    app.logger.exception(e._message)
    data = CustomException(f"Integrity constraint in database are violated. Did you check if all fields are present in request body? Error message: {e._message}").json()
    res = ResponseBodyJSON(False, data).json()
    
    return jsonify(res), 400

@app.errorhandler(Exception)
def unhandled_exception(e: Exception):
    app.logger.exception(e)
    data = CustomException(e).json()
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
    body = request.get_json()
    # print(f'body: {body}')

    milestones = body.pop('milestones')

    # add project first then add all milestones to populate project id in `project`
    project = Project(**body)
    db.session.add(project)
    db.session.flush()
    
    for milestone in milestones:
        milestone['due_date'] = datetime.strptime(milestone['due_date'], '%Y-%m-%dT%H:%M:%S.%fZ') # parse iso format string to datetime
        m = Milestone(**milestone, project=project, offsets_total=milestone['offsets_available'])
        db.session.add(m)
    
    db.session.commit()

    data = project.json()
    res = ResponseBodyJSON(True, data).json()
    return jsonify(res), 201
    

@app.route("/projects/<uuid:id>/status", methods=['PATCH'])
def verify_project(id):
    project = db.session.execute(db.select(Project).where(Project.id == id)).scalars().first()
    if project is None:
        abort(404, description=f"Project {str(id)} not found.")
        
    body = request.get_json()
    project.status = body['status']
    db.session.commit()
    
    data = project.json()
    res = ResponseBodyJSON(True, data).json()
    return jsonify(res), 200

    
@app.route("/projects/<uuid:id>/milestone/<uuid:mid>/status", methods=['PATCH'])
def verify_project_milestone(id, mid):
    project = db.session.execute(db.select(Project).where(Project.id == id)).scalars().first()
    if project is None:
        abort(404, description=f"Project {str(id)} not found.")

    body = request.get_json()
    for milestone in project.milestones:
        if milestone.id == mid:
            milestone.status = body["status"]
            db.session.commit()
            data = project.json()
            res = ResponseBodyJSON(True, data).json()
            return jsonify(res), 200
    
    abort(404, description=f"milestone of id {mid} not found.")
    

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
    body = request.get_json()
    payment_id = body['payment_id']
    if db.session.execute(db.select(ReservedOffset).where(ReservedOffset.payment_id == payment_id)).scalars().first() is not None:
        abort(400, description=f"Reservation already exists.")

    # Get project by id
    project = db.session.execute(db.select(Project).where(Project.id == id)).scalars().first()
    if project is None:
        abort(404, description=f"Project {str(id)} not found.")
        
    # Get milestone by id
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
    db.session.commit()
    data = reserved_offset.json()
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
    body = request.get_json()
    payment_id = body['payment_id']
    reservation = db.session.execute(db.select(ReservedOffset).where(ReservedOffset.payment_id == payment_id)).scalars().first()
    if reservation is None:
        abort(404, description=f"Reservation does not exist")
    
    db.session.delete(reservation)
    db.session.commit()

    return jsonify(), 204
    
    
@app.route("/projects/milestones/offset", methods=['DELETE'])
def rollback_reserved_offset():
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
    db.session.commit()
    data = milestone.json()
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
