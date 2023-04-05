from classes.enums import OffsetStatus, UserRole
from classes.exception import CustomException
from classes.response import ResponseBodyJSON
from config.flask_config import app
from flask import abort, jsonify, request
from models.models import Offset, User, db
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
def handle_integrity_error(e: IntegrityError):
    """Handles exception when integrity constraint in database are violated. E.g. not nullable fields are null (due to missing fields in request body)"""
    app.logger.exception(e)
    data = CustomException(
        f"Integrity constraint in database are violated. Did you check if all fields are present in request body? Error message: {str(e)}"
    ).json()
    res = ResponseBodyJSON(False, data).json()

    return jsonify(res), 400


@app.errorhandler(Exception)
def handle_unhandled_exception(e: Exception):
    app.logger.exception(e)
    data = CustomException(str(e)).json()
    res = ResponseBodyJSON(False, data).json()
    return jsonify(res), 500


@app.route("/users")
def find_all_users():
    args = request.args

    milestone_id = args.get("milestone_id")
    if milestone_id is not None:
        offsets = (
            db.session.execute(
                db.select(Offset).where(Offset.milestone_id == milestone_id)
            )
            .scalars()
            .all()
        )
        data = [offset.buyer.json() for offset in offsets]
        res = ResponseBodyJSON(True, data).json()
        return jsonify(res), 200

    elif args.get("role") == UserRole.VERIFIER.value:
        users = (
            db.session.execute(
                db.select(User).where(User.role == UserRole.VERIFIER.value)
            )
            .scalars()
            .all()
        )
        data = [user.json() for user in users]
        res = ResponseBodyJSON(True, data).json()
        return jsonify(res), 200

    else:
        users = db.session.execute(db.select(User)).scalars().all()
        data = [user.json() for user in users]
        res = ResponseBodyJSON(True, data).json()
        return jsonify(res), 200


@app.route("/users/<uuid:id>")
def find_user_by_id(id):
    user = db.session.execute(db.select(User).where(User.id == id)).scalars().first()

    if user is None:
        abort(404, description=f"User {str(id)} not found.")

    data = user.json()
    res = ResponseBodyJSON(True, data).json()
    return jsonify(res), 200


@app.route("/users", methods=["POST"])
def create_user():
    body = request.get_json()
    app.logger.info(f"body: {body}")

    user = User(**body)
    db.session.add(user)
    db.session.commit()

    data = user.json()
    res = ResponseBodyJSON(True, data).json()
    return jsonify(res), 201


@app.route("/users/<uuid:id>/offset", methods=["POST"])
def create_user_offset(id):
    body = request.get_json()
    app.logger.info(f"body: {body}")

    user = db.session.execute(db.select(User).where(User.id == id)).scalars().first()
    if user is None:
        abort(404, description=f"User {str(id)} not found.")

    offset = Offset(**body, buyer=user)
    db.session.add(offset)
    db.session.commit()

    data = offset.json()
    res = ResponseBodyJSON(True, data).json()
    return jsonify(res), 201


@app.route("/users/<uuid:id>/offset/<string:payment_id>", methods=["PATCH"])
def update_buyer_offset(id, payment_id):
    """
    If status is confirmed,
    1. update the offset status to 'confirmed'
    2. the buyer's footprint is increased.
    else if status is 'refund', only the offset status is updated as 'refund'.
    """

    buyer: User or None = (
        db.session.execute(db.select(User).where(User.id == id)).scalars().first()
    )
    if buyer is None:
        abort(404, description=f"User {str(id)} not found.")

    body = request.get_json()
    app.logger.info(f"body: {body}")

    status = body["status"]
    if status not in OffsetStatus.values():
        abort(
            400,
            description=f"Invalid status '{status}'. Status can only be the following: {OffsetStatus.values()}",
        )

    offset = (
        db.session.execute(db.select(Offset).where(Offset.payment_id == payment_id))
        .scalars()
        .first()
    )
    if offset is None:
        abort(404, description=f"Offset {str(payment_id)} not found.")

    offset.status = status
    db.session.commit()

    if status == OffsetStatus.CONFIRMED:
        buyer.footprint_in_tCO2e += offset.amount
        db.session.commit()

    data = buyer.json()
    res = ResponseBodyJSON(True, data).json()
    return jsonify(res), 200


@app.route("/offset")
def find_all_offset():
    offsets = db.session.execute(db.select(Offset)).scalars().all()
    data = [o.json() for o in offsets]
    res = ResponseBodyJSON(True, data).json()
    return jsonify(res), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
