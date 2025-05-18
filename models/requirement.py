from datetime import datetime
from models.base import BaseModel
from extensions import db

class Requirement(BaseModel):
    __tablename__ = 'requirements'

    id = db.Column(db.Integer, primary_key=True)
    # Foreign keys
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Fields
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    budget = db.Column(db.Float)
    status = db.Column(db.String(20), default='open')  # open, in_progress, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    requester = db.relationship('User', back_populates='requirements')
    proposals = db.relationship('Proposal', back_populates='requirement', cascade='all, delete-orphan')
    messages = db.relationship('RequirementMessage', back_populates='requirement', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'budget': self.budget,
            'status': self.status,
            'requester_id': self.requester_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Requirement {self.title}>' 