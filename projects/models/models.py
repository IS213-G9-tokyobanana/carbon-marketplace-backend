from config.config import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY, VARCHAR, TEXT, TIMESTAMP, FLOAT, UUID

db = SQLAlchemy(app)

class Project(db.Model):
    __tablename__ = 'project'

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    name = Column(TEXT, nullable=False)
    owner_id = Column(TEXT, nullable=False)
    description = Column(TEXT, nullable=False)
    types = Column(ARRAY(TEXT))
    status = Column(VARCHAR(20), nullable=False, default="Pending")
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    rating = Column(FLOAT, nullable=False, default=100.00)

    milestones = relationship('Milestone', back_populates='project')

    def json(self) -> dict:
        return {
            "id": self.id, 
            "name": self.name,
            "owner_id": self.owner_id,
            "description": self.description,
            "types": self.types,
            "status": self.status,
            "created_at": self.created_at.replace(microsecond=0).isoformat(),
            "updated_at": self.updated_at.replace(microsecond=0).isoformat(),
            "rating": self.rating,
            "milestones": None if self.milestones is None else [m.json() for m in self.milestones]
            }
    
    def __repr__(self) -> str:
        return f'{self.json()}'

class Milestone(db.Model):
    __tablename__ = "milestone"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    name = Column(TEXT, nullable=False)
    description = Column(TEXT, nullable=False)
    type = Column(VARCHAR(20), nullable=False) # -- 'Temporal' | 'Qualitative' | 'Quantitative'
    offsets_available = Column(FLOAT, nullable=False)
    offsets_total = Column(FLOAT, nullable=False)
    status = Column(VARCHAR(20), nullable=False, default="Pending") # -- "Pending" | "Verified" | "Met" | "Rejected"
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow) 
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = Column(TIMESTAMP, nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey('project.id'))
    project = relationship('Project', back_populates='milestones')

    def json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "offsets_available": self.offsets_available,
            "offsets_total": self.offsets_total,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "due_date": self.due_date.isoformat(),
            "project_id": self.project_id
        }

    def __repr__(self) -> str:
        return f'{self.json()}'

class ReservedOffset(db.Model):
    __tablename__ = "reserved_offset"

    payment_id = Column(TEXT, primary_key=True)
    milestone_id = Column(UUID(as_uuid=True), ForeignKey('milestone.id'))
    buyer_id = Column(TEXT, nullable=False)
    amount = Column(FLOAT, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    def json(self) -> dict:
        return {
            "payment_id": self.payment_id,
            "milestone_id": self.milestone_id,
            "buyer_id": self.buyer_id,
            "amount": self.amount,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self) -> str:
        return f'{self.json()}'
