from app import create_app
from models.user import User
from models.product import Product
from models.cart import Cart
from extensions import db

def populate_database():
    app = create_app()
    with app.app_context():
        # Create admin user
        admin = User.create_admin(
            username='admin1',
            email='admin1@example.com',
            password='admin123'
        )
        if admin:
            print("Admin user created successfully!")
        else:
            print("Failed to create admin user!")

        # Create regular user
        user = User(
            username='user1',
            email='user1@example.com',
            password='user123',
            role='customer'
        )
        user.set_password('user123')
        db.session.add(user)
        db.session.commit()
        print("Regular user created successfully!")

        # Create sample products
        products = [
            {
                'name': 'Laptop',
                'description': 'High-performance laptop with 16GB RAM and 512GB SSD',
                'price': 999.99,
                'stock': 10,
                'category': 'Electronics',
                'image_url': 'https://example.com/laptop.jpg'
            },
            {
                'name': 'Smartphone',
                'description': 'Latest smartphone with 128GB storage and 5G support',
                'price': 699.99,
                'stock': 15,
                'category': 'Electronics',
                'image_url': 'https://example.com/phone.jpg'
            },
            {
                'name': 'Headphones',
                'description': 'Wireless noise-cancelling headphones',
                'price': 199.99,
                'stock': 20,
                'category': 'Electronics',
                'image_url': 'https://example.com/headphones.jpg'
            },
            {
                'name': 'Smart Watch',
                'description': 'Fitness tracker with heart rate monitor',
                'price': 149.99,
                'stock': 12,
                'category': 'Electronics',
                'image_url': 'https://example.com/watch.jpg'
            },
            {
                'name': 'Tablet',
                'description': '10-inch tablet with 64GB storage',
                'price': 299.99,
                'stock': 8,
                'category': 'Electronics',
                'image_url': 'https://example.com/tablet.jpg'
            }
        ]

        for product_data in products:
            product = Product(**product_data)
            db.session.add(product)
        
        db.session.commit()
        print("Sample products created successfully!")

if __name__ == '__main__':
    populate_database() 