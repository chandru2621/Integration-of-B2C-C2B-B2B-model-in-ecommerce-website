from app import create_app
from extensions import db
from models.user import User
from models.product import Product
from sqlalchemy import text

def test_connection():
    app = create_app()
    with app.app_context():
        try:
            # Test database connection
            db.session.execute(text('SELECT 1'))
            print("✅ Database connection successful!")
            
            # Test if we can query users
            users = User.query.all()
            print(f"✅ Found {len(users)} users in the database")
            
            # Test if we can query products
            products = Product.query.all()
            print(f"✅ Found {len(products)} products in the database")
            
            # Print database URI (without password)
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            safe_uri = db_uri.replace(db_uri.split('@')[0], '***')
            print(f"✅ Connected to database: {safe_uri}")
            
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            raise

if __name__ == '__main__':
    test_connection() 