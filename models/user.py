from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from datetime import datetime
from sqlalchemy import func
from models.base import BaseModel

class User(UserMixin, BaseModel):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default='customer')  # customer, admin, seller
    stripe_customer_id = db.Column(db.String(50), unique=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', back_populates='admin', lazy='dynamic')
    carts = db.relationship('Cart', back_populates='user', cascade='all, delete-orphan')
    orders = db.relationship('Order', back_populates='user', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', back_populates='user', cascade='all, delete-orphan')
    requirements = db.relationship('Requirement', back_populates='requester', cascade='all, delete-orphan')
    messages = db.relationship('RequirementMessage', back_populates='sender', cascade='all, delete-orphan')
    proposals = db.relationship('Proposal', back_populates='admin', cascade='all, delete-orphan')
    returns = db.relationship('Return', back_populates='user', cascade='all, delete-orphan')
    quotes = db.relationship('Quote', back_populates='user', cascade='all, delete-orphan')
    reviews = db.relationship('Review', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if the user is an admin."""
        return self.role == 'admin'
    
    def is_customer(self):
        return self.role == 'customer'
    
    def has_role(self, role):
        return self.role == role
    
    @staticmethod
    def create_admin(username, email, password):
        admin = User(
            username=username,
            email=email,
            role='admin',
            is_active=True
        )
        admin.set_password(password)
        try:
            db.session.add(admin)
            db.session.commit()
            return admin
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin user: {e}")
            return None
    
    @property
    def total_spent(self):
        return sum(order.total_amount for order in self.orders if order.status == 'delivered')
    
    def get_cart(self):
        cart = Cart.query.filter_by(user_id=self.id).first()
        if not cart:
            cart = Cart(user_id=self.id)
            db.session.add(cart)
            db.session.commit()
        return cart
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>' 