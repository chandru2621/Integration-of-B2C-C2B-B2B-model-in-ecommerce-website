from datetime import datetime
from models.base import BaseModel
from extensions import db

class Notification(BaseModel):
    __tablename__ = 'notifications'
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    
    # Fields
    title = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='notifications')
    order = db.relationship('Order', back_populates='notifications')
    
    def __repr__(self):
        return f'<Notification {self.id}>' 