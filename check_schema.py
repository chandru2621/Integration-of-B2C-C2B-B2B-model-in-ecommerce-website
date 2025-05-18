import pymysql
from dotenv import load_dotenv
import os

def check_and_update_schema():
    # Load environment variables
    load_dotenv()
    
    # Database connection parameters
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
        
        with connection.cursor() as cursor:
            # Check current schema
            cursor.execute("DESCRIBE products")
            columns = cursor.fetchall()
            print("\nCurrent columns in products table:")
            for column in columns:
                print(f"- {column[0]}: {column[1]}")
            
            # Add missing columns if they don't exist
            missing_columns = [
                "bulk_discount VARCHAR(100) DEFAULT NULL",
                "bulk_price FLOAT DEFAULT NULL",
                "minimum_quantity INT DEFAULT 1",
                "sustainability_score INT NOT NULL DEFAULT 0",
                "materials VARCHAR(200) DEFAULT NULL",
                "certifications VARCHAR(200) DEFAULT NULL",
                "`condition` VARCHAR(20) DEFAULT 'new'",
                "is_active BOOLEAN DEFAULT TRUE",
                "created_at DATETIME DEFAULT CURRENT_TIMESTAMP",
                "updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
            ]
            
            for column_def in missing_columns:
                column_name = column_def.split()[0].strip('`')
                try:
                    cursor.execute(f"ALTER TABLE products ADD COLUMN {column_def}")
                    print(f"✅ Added column: {column_name}")
                except pymysql.err.OperationalError as e:
                    if e.args[0] == 1060:  # Duplicate column error
                        print(f"ℹ️ Column already exists: {column_name}")
                    else:
                        raise
            
            connection.commit()
            print("\n✅ Schema update completed")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        if 'connection' in locals():
            connection.close()
            print("✅ Database connection closed")

if __name__ == '__main__':
    check_and_update_schema() 