from app import create_app
from extensions import db
from models.user import User

def create_admin_user():
    app = create_app()
    with app.app_context():
        # Check if admin exists
        admin = User.query.filter_by(role='admin').first()
        if admin:
            print(f"Admin user already exists with email: {admin.email}")
            return
        
        # Create new admin
        admin = User.create_admin(
            username='admin1',
            email='admin1@example.com',
            password='admin123'
        )
        if admin:
            print("Admin user created successfully!")
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Password: admin123")
        else:
            print("Failed to create admin user!")

if __name__ == '__main__':
    create_admin_user() 