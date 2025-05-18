from datetime import datetime
from models.base import BaseModel
from extensions import db

class Return(BaseModel):
    __tablename__ = 'returns'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, completed
    return_date = db.Column(db.DateTime, default=datetime.utcnow)
    processed_date = db.Column(db.DateTime)
    refund_amount = db.Column(db.Float)
    notes = db.Column(db.Text)
    
    # Relationships
    order = db.relationship('Order', back_populates='returns')
    user = db.relationship('User', back_populates='returns')
    product = db.relationship('Product', back_populates='returns')
    
    def __repr__(self):
        return f'<Return {self.id} - Order {self.order_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'reason': self.reason,
            'status': self.status,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'processed_date': self.processed_date.isoformat() if self.processed_date else None,
            'refund_amount': self.refund_amount,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 