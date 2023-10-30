import sqlite3
import logging

def create_posted_ids_table(db_path):
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        
        # Create a table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS posted_ids (
            id INTEGER PRIMARY KEY
        );
        """)
        
        # Commit the transaction
        conn.commit()
        
        # Close the connection
        conn.close()
        
        print("Table created successfully.")
        
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")

# Usage
db_path = "D:/coding/instagram/scripts/posted_ids.db"
create_posted_ids_table(db_path)