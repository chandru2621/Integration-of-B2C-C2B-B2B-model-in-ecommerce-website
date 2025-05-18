from datetime import datetime
from models.base import BaseModel
from extensions import db

class Order(BaseModel):
    __tablename__ = 'orders'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    shipping_name = db.Column(db.String(100), nullable=False)
    shipping_address = db.Column(db.String(200), nullable=False)
    shipping_city = db.Column(db.String(100), nullable=False)
    shipping_state = db.Column(db.String(100), nullable=False)
    shipping_zip = db.Column(db.String(20), nullable=False)
    shipping_country = db.Column(db.String(100), nullable=False, default='United States')
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(50), nullable=False, default='pending')
    status = db.Column(db.String(50), nullable=False, default='pending')
    tracking_number = db.Column(db.String(100))
    delivered_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='orders')
    items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    payment = db.relationship('Payment', back_populates='order', uselist=False)
    notifications = db.relationship('Notification', back_populates='order', cascade='all, delete-orphan')
    returns = db.relationship('Return', back_populates='order', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.id}>'

    def update_payment_status(self, status, method=None):
        """Update payment status and method"""
        if method:
            self.payment_method = method
        self.payment_status = status
        if status == 'completed':
            self.status = 'processing'
        db.session.commit()

    def is_eligible_for_return(self):
        """Check if the order is eligible for returns."""
        # Only check if the order is delivered
        return self.status == 'delivered'

    def mark_as_delivered(self):
        """Allow customer to mark order as delivered."""
        if self.status == 'shipped':
            self.status = 'delivered'
            self.delivered_at = datetime.utcnow()
            return True
        return False

class OrderItem(BaseModel):
    __tablename__ = 'order_items'

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Price at time of order
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    order = db.relationship('Order', back_populates='items')
    product = db.relationship('Product', back_populates='order_items')

    @property
    def total(self):
        return self.price * self.quantity

    def __repr__(self):
        return f'<OrderItem {self.id}>' 