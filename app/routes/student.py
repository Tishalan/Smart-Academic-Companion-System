from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models import Student, Enrollment, Assignment, Submission, Prediction, Module, db, Batch, Timetable
from app.utils.decorators import student_required
from app.utils.ai_advisor import AIAdvisor
from app.utils.timetable_utils import SLOTS, DAYS, get_current_slot, get_day_name
import os
import time
from datetime import datetime
import json


"""
Student Routing Module (student.py)
-----------------------------------
இந்த பைல் மாணவர்கள் (Students) பயன்படுத்தும் இணைய பக்கங்களைக் கையாள்கிறது.
- Dashboard (Performance stats, Timetable)
- Course & Module Enrollments
- Submitting Assignments & Viewing Grades
- AI Study Aid (PDF/PPTX Notes processing)
"""

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    student = current_user.student_profile
    if not student:
        flash("Student profile not found.")
        return redirect(url_for('main.index'))
        
    # Auto-enroll in all modules of their course if course is assigned
    if student.course_id:
        course_modules = Module.query.filter_by(course_id=student.course_id).all()
        existing_module_ids = {e.module_id for e in student.enrollments.all()}
        new_enrollments = []
        for module in course_modules:
            if module.id not in existing_module_ids:
                new_enrollments.append(Enrollment(student_id=student.id, module_id=module.id, status='enrolled'))
        
        if new_enrollments:
            db.session.add_all(new_enrollments)
            db.session.commit()
    
    enrollments = student.enrollments.all()
    
    # If student is assigned to a course but has no enrollments yet, maybe auto-enroll or show message
    # For now, we list assignments from the specific course modules
    course_modules = Module.query.filter_by(course_id=student.course_id).all() if student.course_id else []
    module_ids = [m.id for m in course_modules]
    
    upcoming_assignments = Assignment.query.filter(
        Assignment.module_id.in_(module_ids)
    ).order_by(Assignment.deadline.asc()).limit(5).all()
    
    # Personal performance stats
    stats = {
        'gpa': student.GPA,
        'attendance': student.attendance_percentage,
        'risk_score': student.risk_score,
        'grad_prob': student.graduation_probability,
        'course_name': student.course.course_name if student.course else 'Undecided'
    }
    
    # AI Recommendations
    ai_recommendations = AIAdvisor.get_student_recommendation(student)
    
    # Timetable for today
    today_name = get_day_name()
    current_slot = get_current_slot()
    today_schedule = []
    if student.batch_id:
        today_schedule = Timetable.query.filter_by(batch_id=student.batch_id, day_of_week=today_name).all()
    
    from app.models import SharedMaterial
    shared_notes = SharedMaterial.query.filter_by(batch_id=student.batch_id).order_by(SharedMaterial.created_at.desc()).all()
    
    return render_template('student/dashboard.html', 
                         stats=stats, 
                         enrollments=enrollments, 
                         assignments=upcoming_assignments, 
                         student=student,
                         ai_recommendations=ai_recommendations,
                         today_schedule=today_schedule,
                         current_slot=current_slot,
                         shared_notes=shared_notes)

@student_bp.route('/timetable')
@login_required
@student_required
def timetable():
    student = current_user.student_profile
    if not student:
        flash("Student profile not found.")
        return redirect(url_for('main.index'))
        
    timetable_entries = []
    if student.batch_id:
        timetable_entries = Timetable.query.filter_by(batch_id=student.batch_id).all()
        
    current_slot = get_current_slot()
    today_name = get_day_name()
    
    return render_template('student/timetable.html', 
                           timetable=timetable_entries,
                           slots=SLOTS,
                           days=DAYS,
                           current_slot=current_slot,
                           today_name=today_name,
                           batch_name=student.batch.name if student.batch else "Unassigned")

@student_bp.route('/modules')
@login_required
@student_required
def modules():
    student = current_user.student_profile
    if student.course_id:
        # Show all modules in their course
        course_modules = Module.query.filter_by(course_id=student.course_id).all()
        
        # Auto-enroll in all modules of their course
        existing_module_ids = {e.module_id for e in student.enrollments.all()}
        new_enrollments = []
        for module in course_modules:
            if module.id not in existing_module_ids:
                new_enrollments.append(Enrollment(student_id=student.id, module_id=module.id, status='enrolled'))
        
        if new_enrollments:
            db.session.add_all(new_enrollments)
            db.session.commit()
        
        # Create a mapping of module_id to enrollment for easy access in template
        enrollment_map = {e.module_id: e for e in student.enrollments.all()}
        return render_template('student/modules.html', modules=course_modules, enrollment_map=enrollment_map, student=student)
    else:
        enrollments = student.enrollments.all()
        return render_template('student/modules.html', enrollments=enrollments, student=student)

@student_bp.route('/submissions', methods=['GET', 'POST'])
@login_required
@student_required
def submissions():
    student = current_user.student_profile
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part provided.")
            return redirect(request.url)
        
        file = request.files['file']
        assignment_id = request.form.get('assignment_id')
        
        if file.filename == '':
            flash("No file selected.")
            return redirect(request.url)
            
        if file and assignment_id:
            from werkzeug.utils import secure_filename
            original_filename = secure_filename(file.filename)
            filename = f"sub_{student.student_id}_{assignment_id}_{original_filename}"
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            # Create/Update Submission record
            submission = Submission.query.filter_by(student_id=student.id, assignment_id=assignment_id).first()
            if not submission:
                submission = Submission(student_id=student.id, assignment_id=assignment_id)
                db.session.add(submission)
            
            submission.file_path = filename
            submission.submitted_at = datetime.now()
            submission.status = 'submitted'
            db.session.commit()
            flash("Assignment submitted successfully!")
            return redirect(url_for('student.submissions'))

    enrollments = student.enrollments.all()
    module_ids = [e.module_id for e in enrollments]
    all_assignments = Assignment.query.filter(Assignment.module_id.in_(module_ids)).all()
    my_submissions = student.submissions.all()
    return render_template('student/submissions.html', assignments=all_assignments, submissions=my_submissions)

@student_bp.route('/grades')
@login_required
@student_required
def grades():
    student = current_user.student_profile
    if not student:
        flash("Student profile not found.")
        return redirect(url_for('main.index'))
    my_submissions = student.submissions.filter(Submission.status == 'released').all()
    return render_template('student/grades.html', grades=my_submissions, student=student)

@student_bp.route('/performance')
@login_required
@student_required
def performance():
    student = current_user.student_profile
    if not student:
        flash("Student profile not found.")
        return redirect(url_for('main.index'))
    return render_template('student/performance.html', student=student)

@student_bp.route('/study-aid', methods=['GET', 'POST'])
@login_required
@student_required
def study_aid():
    from app.models import PresentationAid, Module
    from app.utils.ai_utils import ai_processor
    from werkzeug.utils import secure_filename
    
    student = current_user.student_profile
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file provided.")
            return redirect(request.url)
            
        file = request.files['file']
        module_id = request.form.get('module_id')
        
        if file.filename == '' or not module_id:
            flash("File or Module not selected.")
            return redirect(request.url)
            
        # Save file
        filename = secure_filename(file.filename)
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"aid_{student.id}_{filename}")
        file.save(save_path)
        
        try:
            # 1. Extract text
            if filename.lower().endswith('.pptx'):
                slides_data = ai_processor.extract_text_from_ppt(save_path)
            elif filename.lower().endswith('.pdf'):
                slides_data = ai_processor.extract_text_from_pdf(save_path)
            else:
                flash("Unsupported file format. Please use PDF or PPTX.")
                return redirect(request.url)
            
            # 2. AI Deep-Dive (Concept Expansion)
            deep_mode = request.form.get('deep_mode') == 'on'
            module = Module.query.get(int(module_id))
            
            # Use unified academic expansion
            notes_data = ai_processor.generate_detailed_study_notes(
                slides_data, 
                module.module_name, 
                deep_mode=deep_mode
            )
            
            # 3. Generate PDF Report
            report_filename = f"Study_Guide_{module.module_code}_{int(time.time())}.pdf"
            report_path = os.path.join('app', 'static', 'reports', report_filename)
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            
            title_prefix = "DEEP Academic Guide" if deep_mode else "Study Notes"
            ai_processor.generate_pdf_report(
                notes_data, 
                report_path, 
                f"{title_prefix}: {module.module_name}",
                f"Generated for {student.user.full_name} from {filename}"
            )
            
            # 4. Save to DB
            import json
            aid = PresentationAid(
                student_id=student.id,
                module_id=module_id,
                original_filename=filename,
                file_path=save_path,
                ai_notes_json=json.dumps(notes_data),
                pdf_report_path=f"reports/{report_filename}"
            )
            db.session.add(aid)
            db.session.commit()
            
            flash("AI Study Guide generated successfully! Download your premium notes below.")
            
        except Exception as e:
            flash(f"AI Processing Error: {str(e)}")
            return redirect(request.url)
            
    my_aids = PresentationAid.query.filter_by(student_id=student.id).order_by(PresentationAid.created_at.desc()).all()
    enrollments = student.enrollments.all()
    return render_template('student/study_aid.html', aids=my_aids, enrollments=enrollments)