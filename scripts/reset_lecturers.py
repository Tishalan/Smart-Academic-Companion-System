import os
import sys
import re
import unicodedata

# Add current directory to sys.path to ensure modules can be found
sys.path.append(os.getcwd())

from app import create_app, db
from app.models import User

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens (or dots in this case for usernames).
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s\.]', '', value).strip().lower()
    value = re.sub(r'[\s]+', '.', value)
    return value

def reset_lecturer_credentials():
    # Load development configuration
    app = create_app('development')
    
    with app.app_context():
        # Find all users with the 'lecturer' role
        lecturers = User.query.filter_by(role='lecturer').all()
        
        if not lecturers:
            print("No lecturers found in the database.")
            return
            
        print(f"Found {len(lecturers)} lecturers. Updating usernames and passwords...")
        
        for lecturer in lecturers:
            old_username = lecturer.username
            new_username = slugify(lecturer.full_name)
            
            # Update username and password
            lecturer.username = new_username
            lecturer.set_password('12345')
            
            print(f"Reset: {old_username} -> {new_username}")
            
        try:
            db.session.commit()
            print("\nSuccessfully updated all lecturer usernames and passwords.")
        except Exception as e:
            db.session.rollback()
            print(f"\nError committing changes: {e}")

if __name__ == "__main__":
    reset_lecturer_credentials()
