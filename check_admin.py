from app import create_app
from extensions import db
from models.user import User

def check_admin():
    app = create_app()
    with app.app_context():
        # Check admin user
        admin = User.query.filter_by(email='admin@example.com').first()
        if admin:
            print(f"Current admin user:")
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Role: {admin.role}")
            print(f"Is Active: {admin.is_active}")
            
            # Fix role if needed
            if admin.role != 'admin':
                print("\nFixing admin role...")
                admin.role = 'admin'
                db.session.commit()
                print("Admin role fixed!")
        else:
            print("Admin user not found!")

if __name__ == '__main__':
    check_admin() 