from datetime import datetime
from models.base import BaseModel
from extensions import db

class Payment(BaseModel):
    __tablename__ = 'payments'
    
    # Foreign keys
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    
    # Fields
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    payment_method = db.Column(db.String(50), nullable=False)
    transaction_id = db.Column(db.String(100))
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    order = db.relationship('Order', back_populates='payment')
    
    def __repr__(self):
        return f'<Payment {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'amount': self.amount,
            'status': self.status,
            'payment_method': self.payment_method,
            'payment_date': self.payment_date.isoformat()
        } 