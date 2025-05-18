from flask import Flask
from config import Config
from extensions import db, login_manager, mail, migrate
from dotenv import load_dotenv
import os
from flask_login import LoginManager
from models.user import User
from models.product import Product
from models.cart import Cart, CartItem
from models.order import Order, OrderItem
from models.notification import Notification
from models.requirement import Requirement
from models.proposal import Proposal
from models.requirement_message import RequirementMessage
from models.quote import Quote
from models.review import Review
from models.bulk_request import BulkRequest
import sys
from routes.bulk_order import bulk_order_bp

# Load environment variables
load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config.Config')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    with app.app_context():
        try:
            # Import base model first
            from models.base import BaseModel
            
            # Import models in dependency order
            from models.user import User
            from models.product import Product
            from models.cart import Cart, CartItem
            from models.order import Order, OrderItem
            from models.payment import Payment
            from models.requirement import Requirement
            from models.requirement_message import RequirementMessage
            from models.quote import Quote
            from models.notification import Notification
            from models.review import Review
            from models.bulk_request import BulkRequest
            
            # Verify database connection
            db.engine.connect()
            print("✅ Database connection successful")
            
            # Check existing data
            user_count = User.query.count()
            product_count = Product.query.count()
            order_count = Order.query.count()
            
            print(f"\nCurrent Database Status:")
            print(f"Users: {user_count}")
            print(f"Products: {product_count}")
            print(f"Orders: {order_count}")
            
        except Exception as e:
            print(f"❌ Database connection error: {str(e)}")
            raise e
        
        # Import blueprints here to avoid circular imports
        from routes.main import main_bp
        from routes.auth import auth_bp
        from routes.products import products_bp
        from routes.cart import cart_bp
        from routes.order import order_bp
        from routes.payment import payment_bp
        from routes.admin import admin_bp
        from routes.requirement import requirement_bp
        
        # Register blueprints
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(products_bp)
        app.register_blueprint(cart_bp)
        app.register_blueprint(order_bp)
        app.register_blueprint(payment_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(requirement_bp)
        app.register_blueprint(bulk_order_bp)  # Add this line
        
        # Set up user loader
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        # Create database tables if they don't exist
        db.create_all()
        print("✅ Database tables verified")
        
        # Create admin user if none exists
        if not User.query.filter_by(role='admin').first():
            admin = User.create_admin(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            if admin:
                print("✅ Admin user created")
        
        # Create sample products only if no products exist
        if Product.query.count() == 0:
            admin = User.query.filter_by(role='admin').first()
            if admin:
                sample_products = [
                    {
                        'name': 'Eco-friendly Laptop',
                        'description': 'High-performance laptop with recycled materials and energy-efficient components',
                        'price': 999.99,
                        'category': 'Recycled Electronics',
                        'stock': 10,
                        'admin_id': admin.id,
                        'sustainability_score': 4,
                        'materials': 'Recycled aluminum, recycled plastic',
                        'certifications': 'EPEAT Gold',
                        'bulk_discount': '15% off for orders over 5 units',
                        'condition': 'new'
                    },
                    {
                        'name': 'Bamboo Cutlery Set',
                        'description': 'Reusable bamboo cutlery for eco-conscious dining, includes fork, knife, spoon, and chopsticks',
                        'price': 19.99,
                        'category': 'Reusable Kitchenware',
                        'stock': 50,
                        'admin_id': admin.id,
                        'sustainability_score': 5,
                        'materials': 'Bamboo, stainless steel',
                        'certifications': 'FSC certified',
                        'bulk_discount': '20% off for orders over 20 sets',
                        'condition': 'new'
                    },
                    {
                        'name': 'Organic Cotton T-Shirt',
                        'description': '100% organic cotton t-shirt, fair trade certified, made with natural dyes',
                        'price': 29.99,
                        'category': 'Reusable Fashion',
                        'stock': 100,
                        'admin_id': admin.id,
                        'sustainability_score': 5,
                        'materials': 'Organic cotton',
                        'certifications': 'Fair Trade Certified, GOTS certified',
                        'bulk_discount': '25% off for orders over 50 pieces',
                        'condition': 'new'
                    },
                    {
                        'name': 'Solar-Powered LED Lamp',
                        'description': 'Portable solar-powered lamp with 12-hour battery life, perfect for outdoor activities',
                        'price': 39.99,
                        'category': 'Recycled Electronics',
                        'stock': 25,
                        'admin_id': admin.id,
                        'sustainability_score': 4,
                        'materials': 'Recycled plastic, solar panels',
                        'certifications': 'RoHS compliant',
                        'bulk_discount': '15% off for orders over 10 units',
                        'condition': 'new'
                    },
                    {
                        'name': 'Bamboo Toothbrush Set',
                        'description': 'Pack of 4 biodegradable bamboo toothbrushes with BPA-free bristles',
                        'price': 12.99,
                        'category': 'Refillable Personal Care',
                        'stock': 75,
                        'admin_id': admin.id,
                        'sustainability_score': 5,
                        'materials': 'Bamboo, BPA-free bristles',
                        'certifications': 'FSC certified',
                        'bulk_discount': '30% off for orders over 100 sets',
                        'condition': 'new'
                    },
                    {
                        'name': 'Recycled Glass Water Bottle',
                        'description': 'Elegant water bottle made from recycled glass with protective silicone sleeve',
                        'price': 24.99,
                        'category': 'Reusable Kitchenware',
                        'stock': 40,
                        'admin_id': admin.id,
                        'sustainability_score': 5,
                        'materials': 'Recycled glass, silicone sleeve',
                        'certifications': 'FDA approved',
                        'bulk_discount': '20% off for orders over 25 units',
                        'condition': 'new'
                    },
                    {
                        'name': 'Hemp Shopping Bag',
                        'description': 'Durable shopping bag made from sustainable hemp with organic cotton lining',
                        'price': 15.99,
                        'category': 'Reusable Fashion',
                        'stock': 60,
                        'admin_id': admin.id,
                        'sustainability_score': 5,
                        'materials': 'Hemp, organic cotton lining',
                        'certifications': 'GOTS certified',
                        'bulk_discount': '25% off for orders over 30 bags',
                        'condition': 'new'
                    },
                    {
                        'name': 'Beeswax Food Wraps',
                        'description': 'Set of 3 reusable beeswax food wraps, perfect alternative to plastic wrap',
                        'price': 18.99,
                        'category': 'Reusable Kitchenware',
                        'stock': 45,
                        'admin_id': admin.id,
                        'sustainability_score': 5,
                        'materials': 'Organic cotton, beeswax, tree resin',
                        'certifications': 'Organic certified',
                        'bulk_discount': '20% off for orders over 20 sets',
                        'condition': 'new'
                    },
                    {
                        'name': 'Solar Phone Charger',
                        'description': 'Portable solar charger for smartphones and tablets, with built-in power bank',
                        'price': 49.99,
                        'category': 'Recycled Electronics',
                        'stock': 30,
                        'admin_id': admin.id,
                        'sustainability_score': 4,
                        'materials': 'Recycled plastic, solar panels',
                        'certifications': 'RoHS compliant',
                        'bulk_discount': '15% off for orders over 10 units',
                        'condition': 'new'
                    },
                    {
                        'name': 'Organic Cotton Face Masks',
                        'description': 'Pack of 5 reusable face masks made from organic cotton with filter pocket',
                        'price': 14.99,
                        'category': 'Reusable Fashion',
                        'stock': 200,
                        'admin_id': admin.id,
                        'sustainability_score': 5,
                        'materials': 'Organic cotton',
                        'certifications': 'GOTS certified',
                        'bulk_discount': '30% off for orders over 50 packs',
                        'condition': 'new'
                    },
                    {
                        'name': 'Bamboo Coffee Cup',
                        'description': 'Insulated bamboo coffee cup with silicone lid, perfect for hot and cold drinks',
                        'price': 16.99,
                        'category': 'Reusable Kitchenware',
                        'stock': 55,
                        'admin_id': admin.id,
                        'sustainability_score': 5,
                        'materials': 'Bamboo, food-grade silicone',
                        'certifications': 'FDA approved',
                        'bulk_discount': '25% off for orders over 20 units',
                        'condition': 'new'
                    },
                    {
                        'name': 'Recycled Paper Notebook',
                        'description': 'A5 size notebook made from 100% recycled paper with eco-friendly binding',
                        'price': 8.99,
                        'category': 'Office Supplies',
                        'stock': 100,
                        'admin_id': admin.id,
                        'sustainability_score': 5,
                        'materials': 'Recycled paper, vegetable-based ink',
                        'certifications': 'FSC certified',
                        'bulk_discount': '20% off for orders over 50 notebooks',
                        'condition': 'new'
                    }
                ]
                
                for product_data in sample_products:
                    try:
                        # Check if product already exists
                        existing_product = Product.query.filter_by(name=product_data['name']).first()
                        if not existing_product:
                            product = Product(**product_data)
                            db.session.add(product)
                            db.session.commit()
                            print(f"Created product: {product.name}")
                    except Exception as e:
                        db.session.rollback()
                        print(f"Error creating product {product_data['name']}: {e}")

        print("\nApplication startup completed successfully!")
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 

# Export app for wsgi
app = create_app()