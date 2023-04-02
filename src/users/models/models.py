from config.flask_config import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import VARCHAR, TEXT, TIMESTAMP, FLOAT, UUID, BOOLEAN
from classes.enums import OffsetStatus, UserRole

db = SQLAlchemy(app)

time_format = "%Y-%m-%dT%H:%M:%SZ"

class User(db.Model):
    __tablename__ = 'user'

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    name = Column(TEXT, nullable=False)
    email = Column(TEXT, nullable=False)
    role = Column(VARCHAR(20), nullable=False, default=UserRole.BUYER.value)
    footprint_in_tCO2e = Column(FLOAT, nullable=False, default=0.00)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    offsets = relationship('Offset', back_populates='buyer')

    def json(self) -> dict:
        return {
            "id": str(self.id), 
            "name": self.name,
            "email": self.email,
            "role": self.role,
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
    status = Column(VARCHAR(20), nullable=False, default=OffsetStatus.PENDING.value) # "pending" | "confirmed"
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

