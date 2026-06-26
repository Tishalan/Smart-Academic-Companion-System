import os
import sys

# Add current directory to sys.path
sys.path.append(os.getcwd())

from app import create_app
from app.models import User

def verify_reset():
    app = create_app('development')
    with app.app_context():
        print("Verifying lecturer credentials...")
        
        # Check specific user Jathu -> jathu
        jathu = User.query.filter_by(username='jathu').first()
        if jathu:
            print(f"OK: Found user 'jathu' (Full Name: {jathu.full_name})")
            if jathu.check_password('12345'):
                print("OK: 'jathu' password verified.")
            else:
                print("FAILED: 'jathu' password check failed.")
        else:
            print("FAILED: User 'jathu' not found.")
            
        # Check a few others
        lecturers = User.query.filter_by(role='lecturer').limit(5).all()
        for lecturer in lecturers:
            if lecturer.username != 'jathu':
                if lecturer.check_password('12345'):
                    print(f"OK: {lecturer.username} password verified.")
                else:
                    print(f"FAILED: {lecturer.username} password check failed.")

if __name__ == "__main__":
    verify_reset()
