from datetime import datetime
from models.base import BaseModel
from extensions import db

class Proposal(BaseModel):
    __tablename__ = 'proposals'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    requirement_id = db.Column(db.Integer, db.ForeignKey('requirements.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    admin = db.relationship('User', back_populates='proposals')
    requirement = db.relationship('Requirement', back_populates='proposals')
    messages = db.relationship('RequirementMessage', back_populates='proposal', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'status': self.status,
            'admin_id': self.admin_id,
            'requirement_id': self.requirement_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Proposal {self.title}>' 