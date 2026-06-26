import pandas as pd
import numpy as np
import time
import os
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User, Student, Course, Module, Batch, Lecturer, Enrollment, Assignment, Lecture

# Tamil Names (Sri Lanka / Jaffna style)
TAMIL_FIRST_NAMES_MALE = [
    "Banushan", "Tharsan", "Piratheepan", "Sivakumar", "Arulanantham", 
    "Jeyaruban", "Koushik", "Vasanthan", "Niruban", "Sutharsan", 
    "Muralitharan", "Gunaratnam", "Ravichandran", "Rajkumar", "Selvakumar",
    "Thinesh", "Prasanna", "Abinandhan", "Vithushan", "Sharujan", 
    "Aravindhan", "Kajanan", "Logeswaran", "Senthooran", "Thanushan"
]

TAMIL_FIRST_NAMES_FEMALE = [
    "Abirami", "Thivya", "Nirubama", "Shalini", "Priyadharshini", 
    "Sivani", "Kavitha", "Arulini", "Vaishnavi", "Suganya", 
    "Dhivya", "Lavanya", "Thulasi", "Gayathri", "Madhavi",
    "Subhashini", "Pavithra", "Janani", "Abinaya", "Keerthana", 
    "Mythili", "Vithursha", "Sharmila", "Anushuya", "Krishanthi"
]

TAMIL_LAST_NAMES = [
    "Ratnam", "Nathan", "Raj", "Kumar", "Selvam", "Lingam", "Moorthy", 
    "Ganeshan", "Arul", "Jeya", "Sivan", "Pandian", "Balan", "Devan", 
    "Rajan", "Sivam", "Pillai", "Nayagam", "Lingham", "Logam"
]

TAMIL_INITIALS = ["A.", "M.", "S.", "V.", "K.", "T.", "J.", "P.", "R.", "N."]

def generate_tamil_name(gender):
    initial = random.choice(TAMIL_INITIALS)
    if str(gender).lower() == 'male':
        first = random.choice(TAMIL_FIRST_NAMES_MALE)
    elif str(gender).lower() == 'female':
        first = random.choice(TAMIL_FIRST_NAMES_FEMALE)
    else:
        first = random.choice(TAMIL_FIRST_NAMES_MALE + TAMIL_FIRST_NAMES_FEMALE)
    
    last = random.choice(TAMIL_LAST_NAMES)
    return f"{initial} {first} {last}"

def populate_lms():
    app = create_app('development')
    csv_path = 'data/student_records_100k.csv'
    
    with app.app_context():
        print("Creating Admin Account...")
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@smart.edu', full_name='System Admin', role='admin')
            admin.set_password('12345')
            db.session.add(admin)
            db.session.commit()

        # 1. Realistic Courses
        print("Creating Realistic Courses and Modules...")
        courses_data = [
            {"name": "BSc in Computer Science", "code": "BSC-CS", "dept": "Computer Science", "credits": 360, "semesters": 6},
            {"name": "BSc in Business Management", "code": "BSC-BM", "dept": "Business", "credits": 360, "semesters": 6},
            {"name": "BSc in Data Science", "code": "BSC-DS", "dept": "Science", "credits": 360, "semesters": 6},
            {"name": "BA in Arts", "code": "BA-ARTS", "dept": "Arts", "credits": 360, "semesters": 6},
            {"name": "BEng in Engineering", "code": "BENG", "dept": "Engineering", "credits": 360, "semesters": 6}
        ]
        
        for c in courses_data:
            course = Course.query.filter_by(course_code=c['code']).first()
            if not course:
                course = Course(
                    course_code=c['code'], course_name=c['name'], department=c['dept'], 
                    credits=c['credits'], duration_semesters=c['semesters']
                )
                db.session.add(course)
                db.session.flush()
                
                # Add 4 modules per semester (total 24 modules)
                for sem in range(1, c['semesters'] + 1):
                    for mod in range(1, 5):
                        module = Module(
                            module_code=f"{c['code']}-{sem}0{mod}",
                            module_name=f"{c['dept']} Module {sem}.{mod}",
                            course_id=course.id,
                            semester=sem,
                            credits=15
                        )
                        db.session.add(module)
        db.session.commit()

        # 2. Lecturers
        print("Creating Lecturers...")
        for i in range(1, 21):
            l_id = f"LEC{i:04d}"
            if not User.query.filter_by(username=l_id).first():
                user = User(username=l_id, email=f"{l_id}@academic.com", full_name=f"Lecturer {i}", role='lecturer')
                user.set_password('12345')
                db.session.add(user)
                db.session.flush()
                
                dept = random.choice([c['dept'] for c in courses_data])
                lecturer = Lecturer(user_id=user.id, lecturer_id=l_id, department=dept, designation="Senior Lecturer")
                db.session.add(lecturer)
        db.session.commit()
        
        # Assign Lecturers to modules
        lecturers = Lecturer.query.all()
        modules = Module.query.all()
        for mod in modules:
            mod.lecturer_id = random.choice(lecturers).id
        db.session.commit()

        # 3. Import 100K Students & Enrollments
        print(f"Pre-calculating password hash for '12345'...")
        pw_hash = generate_password_hash("12345")
        
        print(f"Reading {csv_path}...")
        df = pd.read_csv(csv_path)
        total_records = len(df)
        
        # Department to Course mapping
        dept_course_map = {c.department: c for c in Course.query.all()}
        
        batch_size = 500
        start_time = time.time()
        
        print("Starting bulk import of 100K students...")
        for i in range(0, total_records, batch_size):
            batch_start = time.time()
            batch = df.iloc[i:i+batch_size]
            
            users_to_add = []
            for _, row in batch.iterrows():
                student_id = str(row['student_id'])
                gender = row['gender']
                users_to_add.append(User(
                    username=student_id,
                    email=f"{student_id}@university.edu",
                    full_name=generate_tamil_name(gender),
                    password_hash=pw_hash,
                    role='student',
                    is_active=True
                ))
            
            db.session.add_all(users_to_add)
            db.session.commit() # Commit to get IDs
            
            usernames = [u.username for u in users_to_add]
            
            # Fetch users
            user_id_map = {}
            created_users = User.query.filter(User.username.in_(usernames)).all()
            for u in created_users:
                user_id_map[u.username] = u.id
                    
            students_to_add = []
            for _, row in batch.iterrows():
                student_id = str(row['student_id'])
                dept = row['department']
                course = dept_course_map.get(dept, Course.query.first())
                
                students_to_add.append(Student(
                    user_id=user_id_map[student_id],
                    student_id=student_id,
                    gender=row['gender'],
                    age=int(row['age']),
                    department=dept,
                    intake_year=int(row['intake_year']),
                    course_id=course.id,
                    family_income=float(row['family_income']),
                    scholarship=bool(row['scholarship']),
                    distance_from_campus=float(row['distance_from_campus']),
                    internet_access=bool(row['internet_access']),
                    attendance_percentage=float(row['attendance_percentage']),
                    internal_marks=float(row['internal_marks']),
                    assignment_avg=float(row['assignment_avg']),
                    quiz_avg=float(row['quiz_avg']),
                    final_exam_marks=float(row['final_exam_marks']),
                    GPA=float(row['GPA']),
                    current_semester=1,
                    risk_score=float(row['dropout_risk']),
                    graduation_probability=float(row['graduation_probability'])
                ))
                
            db.session.add_all(students_to_add)
            db.session.commit()
            
            # Create enrollments (only 2 modules per student to save time & memory during massive insert)
            enrollments_to_add = []
            student_records = Student.query.join(User).filter(User.username.in_(usernames)).all()
            for student in student_records:
                # get sem 1 modules for this student's course
                course_mods = [m for m in modules if m.course_id == student.course_id and m.semester == 1]
                for mod in course_mods[:2]: # take first 2
                    enrollments_to_add.append(Enrollment(
                        student_id=student.id,
                        module_id=mod.id,
                        status='enrolled',
                        enrollment_date=datetime.now().date(),
                        grade=student.GPA * 20 # Mock grade based on GPA
                    ))
                    
            db.session.add_all(enrollments_to_add)
            db.session.commit()
            
            elapsed = time.time() - batch_start
            print(f"Imported {min(i+batch_size, total_records)} / {total_records} students... (Batch took {elapsed:.2f}s)")
            
        print(f"Migration completed successfully in {time.time() - start_time:.2f}s!")

if __name__ == "__main__":
    populate_lms()
