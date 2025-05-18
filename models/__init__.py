# This file is intentionally left empty to avoid circular imports
# Models will be imported in app.py after db initialization

from extensions import db

# Import base model first
from models.base import BaseModel

# Import all models
from models.user import User
from models.product import Product
from models.cart import Cart, CartItem
from models.order import Order, OrderItem
from models.payment import Payment
from models.requirement import Requirement
from models.proposal import Proposal
from models.requirement_message import RequirementMessage
from models.notification import Notification
from models.return_request import Return

# Import model relationships after all models are defined
import models.relationships

# Export all models
__all__ = [
    'BaseModel',
    'User',
    'Product',
    'Cart',
    'CartItem',
    'Order',
    'OrderItem',
    'Payment',
    'Requirement',
    'Proposal',
    'RequirementMessage',
    'Notification',
    'Return'
] 