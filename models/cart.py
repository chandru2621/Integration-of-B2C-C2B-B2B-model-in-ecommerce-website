from datetime import datetime
from models.base import BaseModel
from extensions import db

class Cart(BaseModel):
    __tablename__ = 'carts'
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', back_populates='carts')
    items = db.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, user_id):
        self.user_id = user_id
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items)
    
    @property
    def total_amount(self):
        return sum(item.quantity * item.product.price for item in self.items)
    
    def add_item(self, product_id, quantity=1):
        # Check if product already exists in cart
        existing_item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product_id
        ).first()
        
        if existing_item:
            existing_item.quantity += quantity
        else:
            new_item = CartItem(cart_id=self.id, product_id=product_id, quantity=quantity)
            db.session.add(new_item)
        
        db.session.commit()
    
    def remove_item(self, product_id):
        item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product_id
        ).first()
        
        if item:
            db.session.delete(item)
            db.session.commit()
    
    def update_quantity(self, product_id, quantity):
        item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product_id
        ).first()
        
        if item:
            if quantity > 0:
                item.quantity = quantity
            else:
                db.session.delete(item)
            db.session.commit()
    
    def clear(self):
        CartItem.query.filter_by(cart_id=self.id).delete()
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Cart {self.id} for User {self.user_id}>'

class CartItem(BaseModel):
    __tablename__ = 'cart_items'
    
    # Foreign keys
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Fields
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cart = db.relationship('Cart', back_populates='items')
    product = db.relationship('Product', back_populates='cart_items')
    
    @property
    def total(self):
        return self.product.price * self.quantity
    
    def __repr__(self):
        return f'<CartItem {self.id} in Cart {self.cart_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'cart_id': self.cart_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'product': self.product.to_dict() if self.product else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 