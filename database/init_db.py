import os
import sys
import sqlite3

# Add parent directory to path so we can import config and database modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from werkzeug.security import generate_password_hash
from database.connection import get_db_connection
from config import Config

def init_db():
    print("Initializing Database...")

    # Ensure instance directory exists
    os.makedirs(os.path.dirname(Config.DB_PATH), exist_ok=True)
    
    # 1. Connect (creates db if it doesn't exist)
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to SQLite database.")
        return False
    
    try:
        cursor = conn.cursor()
        
        # 2. Run schema.sql to create tables and indexes
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        if not os.path.exists(schema_path):
            print(f"Schema file not found at {schema_path}")
            return False
            
        with open(schema_path, 'r') as file:
            sql_script = file.read()
            
        # Execute multi-statement SQL script
        cursor.executescript(sql_script)
            
        print("Schema tables and indexes created successfully.")
        
        # 3. Insert initial categories only if missing (Idempotent)
        categories_to_insert = [
            "Electrical",
            "Plumbing",
            "HVAC / AC",
            "Furniture",
            "Network / IT",
            "Civil / Building",
            "Cleaning",
            "Equipment",
            "Other"
        ]
        
        for category in categories_to_insert:
            cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO categories (name) VALUES (?)", (category,))
        
        print("Initial categories seeded.")
        
        # 4. Seed default admin account idempotently
        admin_email = "admin@maintenx"
        cursor.execute("SELECT id FROM users WHERE email = ?", (admin_email,))
        existing_admin = cursor.fetchone()
        
        if not existing_admin:
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, role, is_active)
                VALUES (?, ?, ?, 'admin', 1)
            """, ("MaintenX Admin", admin_email, generate_password_hash("admin123")))
            print(f"Default admin account ({admin_email}) seeded.")
        else:
            cursor.execute("""
                UPDATE users
                SET role = 'admin', is_active = 1, password_hash = ?
                WHERE email = ?
            """, (generate_password_hash("admin123"), admin_email))
            print(f"Default admin account ({admin_email}) already exists - ensured admin credentials.")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        conn.rollback()
        return False
    finally:
        # 4. Close the connection
        if 'cursor' in locals() and cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    success = init_db()
    if success:
        print("Database initialization complete.")
        sys.exit(0)
    else:
        print("Database initialization failed.")
        sys.exit(1)
