from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os

db = SQLAlchemy()

def init_app(app: Flask):
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize SQLAlchemy with the app
    db.init_app(app)
    
    # Create database file and tables
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Verify database connection
        try:
            db.session.execute('SELECT 1')
            print("Database connection successful!")
        except Exception as e:
            print(f"Database connection failed: {str(e)}")
            raise 