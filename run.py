import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("SMART ACADEMIC SYSTEM STARTING...")
    print("="*60)
    print("\nServer: http://localhost:5000")
    print("\nAvailable Routes:")
    print("   -> Home: http://localhost:5000/")
    print("   -> Login: http://localhost:5000/auth/login")
    print("   -> Register: http://localhost:5000/auth/register")
    print("   -> Admin: http://localhost:5000/admin/dashboard")
    print("   -> Student: http://localhost:5000/student/dashboard")
    print("   -> Lecturer: http://localhost:5000/lecturer/dashboard")
    print("\n" + "="*60)
    # print("Demo Credentials:")
    # print("   Admin:    admin / admin123")
    # print("   Student:  student / student123")
    # print("   Lecturer: lecturer / lecturer123")
    print("="*60 + "\n")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)