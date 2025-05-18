from datetime import datetime
from models.base import BaseModel
from extensions import db

class Product(BaseModel):
    __tablename__ = 'products'
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.String(50), nullable=False)
    subcategory = db.Column(db.String(50))
    brand = db.Column(db.String(50))
    sustainability_score = db.Column(db.Integer, nullable=False, default=0)
    image_url = db.Column(db.String(200))
    materials = db.Column(db.String(200))
    certifications = db.Column(db.String(200))
    minimum_quantity = db.Column(db.Integer, default=1)
    bulk_price = db.Column(db.Float)
    bulk_discount = db.Column(db.String(100))
    condition = db.Column(db.String(20), default='new')  # 'new' or 'used'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    admin = db.relationship('User', back_populates='products')
    cart_items = db.relationship('CartItem', back_populates='product', cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', back_populates='product', cascade='all, delete-orphan')
    returns = db.relationship('Return', back_populates='product', cascade='all, delete-orphan')
    quotes = db.relationship('Quote', back_populates='product', cascade='all, delete-orphan')
    reviews = db.relationship('Review', back_populates='product', cascade='all, delete-orphan')
    
    # Valid categories
    CATEGORIES = [
        'Reusable Fashion',
        'Eco-friendly Home Items',
        'Recycled Electronics',
        'Refillable Personal Care',
        'Reusable Kitchenware',
        'Office Supplies',
        'Cleaning Supplies',
        'Food Service',
        'Promotional Items',
        'Energy Solutions',
        'Office Furniture'
    ]
    
    def __init__(self, **kwargs):
        if 'category' in kwargs and kwargs['category'] not in self.CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(self.CATEGORIES)}")
            
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f'<Product {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'stock': self.stock,
            'image_url': self.image_url,
            'sustainability_score': self.sustainability_score,
            'materials': self.materials,
            'certifications': self.certifications,
            'bulk_discount': self.bulk_discount,
            'condition': self.condition,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 