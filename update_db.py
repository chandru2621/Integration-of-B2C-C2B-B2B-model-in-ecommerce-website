import pymysql
from config import Config
import os
from dotenv import load_dotenv

def update_database():
    # Load environment variables
    load_dotenv()
    
    # Get database configuration
    host = os.getenv('MYSQL_HOST', 'localhost')
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', 'root')
    database = os.getenv('MYSQL_DB', 'ecommerce_db')
    
    try:
        # Connect to MySQL
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        print("✅ Connected to MySQL database")
        
        # Read and execute SQL script
        with open('update_schema.sql', 'r') as file:
            sql_script = file.read()
            
        with connection.cursor() as cursor:
            # Split the script into individual statements
            statements = sql_script.split(';')
            
            for statement in statements:
                if statement.strip():
                    try:
                        cursor.execute(statement)
                        print(f"✅ Executed: {statement.strip()[:50]}...")
                    except Exception as e:
                        if "Duplicate column name" in str(e):
                            print(f"ℹ️ Column already exists: {statement.strip()[:50]}...")
                        else:
                            print(f"❌ Error executing statement: {str(e)}")
                            raise
            
            # Commit the changes
            connection.commit()
            print("✅ All changes committed successfully!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise
    finally:
        if 'connection' in locals():
            connection.close()
            print("✅ Database connection closed")

if __name__ == '__main__':
    update_database() 