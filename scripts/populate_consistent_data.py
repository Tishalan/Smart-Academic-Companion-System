import os
import sys
from datetime import datetime, timedelta

# Add current directory to sys.path
sys.path.append(os.getcwd())

from app import create_app, db
from app.models import User, Student, Module, Enrollment, Assignment, Submission, Lecturer

def seed_consistent_data():
    app = create_app('development')
    with app.app_context():
        print("Starting consistent data seeding...")
        
        # 1. Fetch test student STU000001
        student = Student.query.filter_by(student_id='STU000001').first()
        if not student:
            print("Student STU000001 not found! Make sure populate_lms_100k.py has been run.")
            return

        print(f"Found student STU000001: {student.user.full_name}")

        # Clear existing submissions and enrollments for this student to make it clean
        Submission.query.filter_by(student_id=student.id).delete()
        Enrollment.query.filter_by(student_id=student.id).delete()
        db.session.commit()

        # Let's enroll this student in 4 modules of their course (or generic modules)
        # Find first 4 modules of the course
        course_modules = Module.query.filter_by(course_id=student.course_id).limit(4).all()
        
        # If there are fewer than 4 modules, take any modules
        if len(course_modules) < 4:
            course_modules = Module.query.limit(4).all()
            
        print(f"Enrolling student in {len(course_modules)} modules...")
        for mod in course_modules:
            enroll = Enrollment(
                student_id=student.id,
                module_id=mod.id,
                status='enrolled',
                enrollment_date=datetime.now().date(),
                grade=80.0
            )
            db.session.add(enroll)
        db.session.commit()

        # Re-fetch modules from enrollments
        enrollments = student.enrollments.all()
        
        # 2. For each module, ensure an Assignment exists
        assignments = []
        for i, enroll in enumerate(enrollments):
            module = enroll.module
            # Make sure module has a lecturer
            if not module.lecturer_id:
                lecturer = Lecturer.query.first()
                if lecturer:
                    module.lecturer_id = lecturer.id
                    db.session.commit()
            
            # Find or create assignment
            assignment = Assignment.query.filter_by(module_id=module.id).first()
            if not assignment:
                assignment = Assignment(
                    module_id=module.id,
                    title=f"{module.module_name} Assignment {i+1}",
                    description=f"Please read the materials carefully and submit your final report for {module.module_name} in PDF format.",
                    total_marks=100,
                    weightage=25.0,
                    deadline=datetime.utcnow() + timedelta(days=7 + i*7),
                    is_active=True,
                    created_by=module.lecturer_id
                )
                db.session.add(assignment)
                db.session.commit()
            assignments.append(assignment)

        # 3. Create submissions in different states
        # Assignment 1: Status = 'submitted' (Waiting for Lecturer to Grade)
        sub1 = Submission(
            assignment_id=assignments[0].id,
            student_id=student.id,
            submission_text="Here is my response to Assignment 1. I have outlined the key details in the attached document.",
            file_path="dummy_report_1.pdf",
            submitted_at=datetime.utcnow() - timedelta(days=2),
            status='submitted'
        )
        db.session.add(sub1)

        # Assignment 2: Status = 'graded' (Graded by lecturer, waiting for Admin approval/release)
        sub2 = Submission(
            assignment_id=assignments[1].id,
            student_id=student.id,
            submission_text="Please find my completed assignment 2 attached. Let me know if any further changes are needed.",
            file_path="dummy_report_2.pdf",
            submitted_at=datetime.utcnow() - timedelta(days=5),
            marks_obtained=85.0,
            feedback="Excellent report. You showed strong analytical reasoning, and the results are presented clearly. Minor spelling errors in section 3.",
            graded_by=assignments[1].module.lecturer_id,
            graded_at=datetime.utcnow() - timedelta(days=1),
            status='graded',
            grade_category='Merit'
        )
        db.session.add(sub2)

        # Assignment 3: Status = 'released' (Released by Admin, visible in My Grades)
        sub3 = Submission(
            assignment_id=assignments[2].id,
            student_id=student.id,
            submission_text="Here is my final project submission for Assignment 3.",
            file_path="dummy_report_3.pdf",
            submitted_at=datetime.utcnow() - timedelta(days=10),
            marks_obtained=94.5,
            feedback="Outstanding work! The project implementation is top-notch, highly structured, and follows all design guidelines perfectly.",
            graded_by=assignments[2].module.lecturer_id,
            graded_at=datetime.utcnow() - timedelta(days=4),
            status='released',
            is_released=True,
            grade_category='Distinction'
        )
        db.session.add(sub3)

        # Assignment 4: Status = 'not submitted' (Active assignment, deadline in future)
        # We don't create a Submission object, so it will show as 'Not Submitted'

        db.session.commit()
        print("Successfully seeded consistent assignment data for student STU000001!")
        print(f"Lecturer for Assignment 1 (Submitted Queue): {assignments[0].module.lecturer.user.username}")
        print(f"Lecturer for Assignment 2 (Grading Queue): {assignments[1].module.lecturer.user.username}")
        print(f"Lecturer for Assignment 3 (Released Queue): {assignments[2].module.lecturer.user.username}")

        # Make sure student's GPA matches
        student.GPA = 3.8
        student.graduation_probability = 0.94
        db.session.commit()

if __name__ == "__main__":
    seed_consistent_data()
