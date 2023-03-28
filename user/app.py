from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, TEXT, TIMESTAMP, FLOAT, UUID, BOOLEAN, VARCHAR
from sqlalchemy.orm import relationship
from datetime import datetime
import classes.customexception as CustomException
import classes.responsebody as ResponseBodyJSON
import psycopg2
from sqlalchemy import create_engine

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://user:password@localhost:3306/users"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)
engine = create_engine('postgresql+psycopg2://user:password@localhost/mydatabase?sslmode=require')


time_format = "%Y-%m-%dT%H:%M:%SZ"

@app.errorhandler(404)
def handle_resource_not_found(e):
    """Handles exception thrown when flask app is aborted using `abort` with HTTP status code 404."""
    app.logger.exception(e)
    data = CustomException(str(e)).json()
    print(data)
    return jsonify(error=str(e)), 404


class User(db.Model):
    __tablename__ = 'user'

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    name = Column(TEXT, nullable=False)
    email = Column(TEXT, nullable=False)
    type = Column(TEXT, nullable=False)
    footprint_in_tCO2e = Column(FLOAT, nullable=False, default=0.00)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    offsets = relationship('Offset', back_populates='buyer')

    def json(self) -> dict:
        return {
            "id": str(self.id), 
            "name": self.name,
            "email": self.email,
            "type": self.type,
            "footprint_in_tCO2e": self.footprint_in_tCO2e,
            "created_at": self.created_at.strftime(time_format),
            "updated_at": self.updated_at.strftime(time_format),
            "offsets": [] if self.offsets is None else [o.json() for o in self.offsets]
            }
    
    def __repr__(self) -> str:
        return f'{self.json()}'

class Offset(db.Model):
    __tablename__ = "offset"

    payment_id = Column(TEXT, primary_key=True)
    milestone_id = Column(TEXT, nullable=False)
    amount = Column(FLOAT, nullable=False)
    status = Column(VARCHAR(20), nullable=False) # "pending" | "confirmed"
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))

    buyer = relationship('User', back_populates='offsets')

    def json(self) -> dict:
        return {
            "payment_id": self.payment_id,
            "milestone_id": self.milestone_id,
            "amount": self.amount,
            "status": self.status,
            "created_at": self.created_at.strftime(time_format), 
            "updated_at": self.updated_at.strftime(time_format), 
            "buyer_id": str(self.buyer_id)
        }

    def __repr__(self) -> str:
        return f'{self.json()}'


@app.route("/user/<uuid:id>")
def get_user_by_id(id):
    user = User.query.filter_by(id=id).first()
    if User:
        return jsonify(
            {
                "code": 200,
                "data": user.json()
            }
        )
    abort(404, "User not found")

@app.route("/createuser", methods=['POST'])
def create_user():
    body = request.get_json()

    user = User(**body)
    db.session.add(user)
    db.session.commit()
    
    data = user.json()
    res = ResponseBodyJSON(True, data).json()
    return jsonify(res), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5433, debug=True)
