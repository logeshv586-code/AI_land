"""
Database migration script to add agent assignment columns
"""
import sqlite3
import os

def migrate_database():
    """Add agent assignment columns to the users table"""
    
    db_path = "land_analysis.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 Current columns in users table: {columns}")
        
        # Add new columns if they don't exist
        if 'assigned_buyer_agent_id' not in columns:
            print("➕ Adding assigned_buyer_agent_id column...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN assigned_buyer_agent_id INTEGER 
                REFERENCES users(id)
            """)
            
        if 'assigned_seller_agent_id' not in columns:
            print("➕ Adding assigned_seller_agent_id column...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN assigned_seller_agent_id INTEGER 
                REFERENCES users(id)
            """)
        
        # Commit the changes
        conn.commit()
        print("✅ Database migration completed successfully!")
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(users)")
        new_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Updated columns in users table: {new_columns}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_database()