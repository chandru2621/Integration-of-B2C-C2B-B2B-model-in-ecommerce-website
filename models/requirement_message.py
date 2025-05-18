from datetime import datetime
from models.base import BaseModel
from extensions import db

class RequirementMessage(BaseModel):
    __tablename__ = 'requirement_messages'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    requirement_id = db.Column(db.Integer, db.ForeignKey('requirements.id'), nullable=False)
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposals.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sender = db.relationship('User', back_populates='messages')
    requirement = db.relationship('Requirement', back_populates='messages')
    proposal = db.relationship('Proposal', back_populates='messages')

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'sender_id': self.sender_id,
            'requirement_id': self.requirement_id,
            'proposal_id': self.proposal_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<RequirementMessage {self.id}>' 