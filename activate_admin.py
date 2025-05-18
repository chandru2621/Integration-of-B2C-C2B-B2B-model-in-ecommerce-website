from app import create_app
from extensions import db
from models.user import User

def activate_admin():
    app = create_app()
    with app.app_context():
        # Find admin user
        admin = User.query.filter_by(email='admin@example.com').first()
        if admin:
            print(f"Current admin user:")
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Role: {admin.role}")
            print(f"Is Active: {admin.is_active}")
            
            # Activate admin
            print("\nActivating admin user...")
            admin.is_active = True
            admin.role = 'admin'  # Ensure role is set correctly
            db.session.commit()
            print("Admin user activated!")
            
            print("\nUpdated admin user:")
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Role: {admin.role}")
            print(f"Is Active: {admin.is_active}")
        else:
            print("Admin user not found!")

if __name__ == '__main__':
    activate_admin() 