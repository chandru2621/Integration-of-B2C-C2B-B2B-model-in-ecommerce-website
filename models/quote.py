from extensions import db
from datetime import datetime
from models.base import BaseModel

class Quote(BaseModel):
    __tablename__ = 'quotes'

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_unit = db.Column(db.Float)
    total_price = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = db.relationship('Product', back_populates='quotes')
    user = db.relationship('User', back_populates='quotes')

    def __repr__(self):
        return f'<Quote {self.id}>' 