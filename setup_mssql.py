from app import create_app, db
from app import models  # Explicitly import models to register them with SQLAlchemy
import pyodbc
import os

def setup_database():
    server = '(localdb)\\MSSQLLocalDB'
    database = 'smart_academic_system'
    
    print(f"Connecting to SQL Server LocalDB at {server}...")
    
    # Connect to master to create the database
    conn = pyodbc.connect(f'Driver={{ODBC Driver 17 for SQL Server}};Server={server};Database=master;Trusted_Connection=yes;', autocommit=True)
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute(f"SELECT name FROM sys.databases WHERE name = '{database}'")
    if cursor.fetchone():
        print(f"Database '{database}' already exists. Dropping it for a fresh start...")
        # Close any existing connections by setting to single user mode
        cursor.execute(f"ALTER DATABASE [{database}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
        cursor.execute(f"DROP DATABASE [{database}]")
    
    print(f"Creating database '{database}'...")
    cursor.execute(f"CREATE DATABASE [{database}]")
    conn.close()
    
    # Now use SQLAlchemy to create tables
    app = create_app('development')
    with app.app_context():
        print("Creating tables using SQLAlchemy...")
        db.create_all()
        print("Tables created successfully.")

if __name__ == "__main__":
    try:
        setup_database()
        print("\nSQL Server setup completed successfully!")
    except Exception as e:
        print(f"\nError during setup: {e}")
