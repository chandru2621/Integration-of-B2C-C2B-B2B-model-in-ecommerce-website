from app import create_app, db

def drop_db():
    app = create_app()
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("All database tables dropped successfully!")

if __name__ == '__main__':
    drop_db() 