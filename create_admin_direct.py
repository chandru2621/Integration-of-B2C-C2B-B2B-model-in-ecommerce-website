from app import create_app
from extensions import db
from models.user import User
from werkzeug.security import generate_password_hash

def create_admin_direct():
    app = create_app()
    with app.app_context():
        # Check if admin exists
        admin = User.query.filter_by(role='admin').first()
        if admin:
            print(f"Admin user already exists with email: {admin.email}")
            return
        
        # Create new admin directly
        admin = User(
            username='admin1',
            email='admin1@example.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            is_active=True
        )
        
        try:
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Password: admin123")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin user: {e}")

if __name__ == '__main__':
    create_admin_direct() 