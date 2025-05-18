from extensions import db
from models import User, Product, Cart, CartItem, Order, OrderItem, Payment, Notification, Return
from flask import Flask
from config import Config
from sqlalchemy import text
import os

def init_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def init_db():
    app = init_app()
    with app.app_context():
        try:
            # Disable foreign key checks temporarily
            db.session.execute(text('SET FOREIGN_KEY_CHECKS=0'))
            
            # Drop all tables in the correct order
            db.session.execute(text('DROP TABLE IF EXISTS quotes'))
            db.session.execute(text('DROP TABLE IF EXISTS returns'))
            db.session.execute(text('DROP TABLE IF EXISTS order_items'))
            db.session.execute(text('DROP TABLE IF EXISTS cart_items'))
            db.session.execute(text('DROP TABLE IF EXISTS requirements'))
            db.session.execute(text('DROP TABLE IF EXISTS orders'))
            db.session.execute(text('DROP TABLE IF EXISTS carts'))
            db.session.execute(text('DROP TABLE IF EXISTS products'))
            db.session.execute(text('DROP TABLE IF EXISTS users'))
            db.session.execute(text('DROP TABLE IF EXISTS payments'))
            db.session.execute(text('DROP TABLE IF EXISTS proposals'))
            db.session.execute(text('DROP TABLE IF EXISTS requirement_messages'))
            db.session.execute(text('DROP TABLE IF EXISTS notifications'))
            
            print("✅ Dropped all tables")
            
            # Re-enable foreign key checks
            db.session.execute(text('SET FOREIGN_KEY_CHECKS=1'))
            
            # Create all tables
            db.create_all()
            print("✅ Created all tables")
            
            # Create admin user
            admin = User.create_admin(
                username="admin",
                email="admin@example.com",
                password="admin123"
            )
            if admin:
                print("✅ Created admin user")
            
            # Create test customer
            customer = User(
                username="customer",
                email="customer@example.com",
                role="customer",
                is_active=True
            )
            customer.set_password("customer123")
            db.session.add(customer)
            
            # Create test seller
            seller = User(
                username="seller",
                email="seller@example.com",
                role="seller",
                is_active=True
            )
            seller.set_password("seller123")
            db.session.add(seller)
            
            try:
                db.session.commit()
                print("✅ Created test users")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error creating test users: {str(e)}")
            
            # Create sample products
            products = [
                {
                    "name": "Eco-Friendly Water Bottle",
                    "description": "Reusable water bottle made from recycled materials",
                    "price": 19.99,
                    "stock": 100,
                    "category": "Reusable Kitchenware",
                    "subcategory": "Drinkware",
                    "brand": "EcoLife",
                    "sustainability_score": 8,
                    "image_url": "https://example.com/bottle.jpg",
                    "materials": "Recycled plastic",
                    "certifications": "BPA Free",
                    "admin_id": admin.id
                },
                {
                    "name": "Organic Cotton T-Shirt",
                    "description": "100% organic cotton t-shirt, fair trade certified",
                    "price": 29.99,
                    "stock": 50,
                    "category": "Reusable Fashion",
                    "subcategory": "Tops",
                    "brand": "EcoWear",
                    "sustainability_score": 9,
                    "image_url": "https://example.com/tshirt.jpg",
                    "materials": "Organic cotton",
                    "certifications": "Fair Trade",
                    "admin_id": admin.id
                }
            ]
            
            for product_data in products:
                product = Product(**product_data)
                db.session.add(product)
            
            try:
                db.session.commit()
                print("✅ Created sample products")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error creating sample products: {str(e)}")
            
            print("\nDatabase initialization completed!")
            print("\nTest accounts created:")
            print("Admin - Username: admin, Password: admin123")
            print("Customer - Username: customer, Password: customer123")
            print("Seller - Username: seller, Password: seller123")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during database initialization: {str(e)}")
            raise e
        finally:
            # Make sure foreign key checks are re-enabled
            db.session.execute(text('SET FOREIGN_KEY_CHECKS=1'))
            db.session.commit()

if __name__ == "__main__":
    init_db() 