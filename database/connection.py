import sqlite3
import os
from config import Config

def get_db_connection(use_database=True):
    """
    Establish a connection to the SQLite database.
    If use_database is False, it still returns a connection in SQLite, 
    since SQLite databases are single files, but typically this param is ignored.
    """
    try:
        # Ensure the instance directory exists just in case
        os.makedirs(os.path.dirname(Config.DB_PATH), exist_ok=True)
        
        connection = sqlite3.connect(Config.DB_PATH)
        connection.row_factory = sqlite3.Row  # To return dict-like rows
        
        # Enable foreign key support
        connection.execute('PRAGMA foreign_keys = ON;')
        
        return connection
    except sqlite3.Error as e:
        # Don't expose sensitive info, just generic error
        print(f"Error connecting to SQLite database: {e}")
        return None
