from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import User, Student, Lecturer, Course, Module, Enrollment, Prediction, Assignment, Lecture, Submission, Batch, Timetable
from app import db
from app.utils.timetable_utils import SLOTS, DAYS
from app.utils.ai_advisor import AIAdvisor
from app.utils.decorators import admin_required
from app.utils.pdf_utils import generate_risk_report
from app.utils.ai_utils import ai_processor
import os
from datetime import datetime
from flask import send_file, current_app

"""
Admin Routing Module (admin.py)
-------------------------------
இந்த பைல் அட்மின் (Administrator) பயன்படுத்தும் அனைத்து இணைய பக்கங்களையும் (Pages) கையாள்கிறது.
- User Management (Students, Lecturers)
- Course & Module Management
- Timetable Scheduling
- AI Analytics & Predictions View
- Assignment Mark Release (Approve grades)
"""

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_students': Student.query.count(),
        'total_lecturers': Lecturer.query.count(),
        'total_courses': Course.query.count(),
        'total_modules': Module.query.count(),
        'high_risk_count': Student.query.filter(Student.risk_score > 0.7).count()
    }
    
    # Recent predictions for the activity feed
    recent_predictions = Prediction.query.order_by(Prediction.created_at.desc()).limit(5).all()
    
    # Data for charts
    risk_distribution = {
        'low': Student.query.filter(Student.risk_score <= 0.3).count(),
        'medium': Student.query.filter((Student.risk_score > 0.3) & (Student.risk_score <= 0.7)).count(),
        'high': stats['high_risk_count']
    }
    
    return render_template('admin/dashboard.html', stats=stats, recent_predictions=recent_predictions, risk_distribution=risk_distribution)

@admin_bp.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    per_page = 20
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        full_name = request.form.get('full_name')
        
        # Profile specific fields
        id_val = request.form.get('p_id') # student_id or lecturer_id
        dept = request.form.get('department')
        gender = request.form.get('gender', 'Other')
        
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or Email already exists.")
        else:
            new_user = User(username=username, email=email, full_name=full_name, role=role)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.flush() # Get user.id
            
            if role == 'student':
                if not id_val: id_val = f"STU{new_user.id:04d}"
                course_id = request.form.get('course_id')
                student = Student(
                    user_id=new_user.id, 
                    student_id=id_val, 
                    department=dept or 'General',
                    gender=gender,
                    age=20, # Default
                    intake_year=datetime.utcnow().year,
                    course_id=course_id if course_id else None
                )
                db.session.add(student)
                
                # Automatically enroll in first semester modules of the course
                if course_id:
                    modules = Module.query.filter_by(course_id=course_id, semester=1).all()
                    for module in modules:
                        enrollment = Enrollment(student_id=student.id, module_id=module.id)
                        db.session.add(enrollment)
            elif role == 'lecturer':
                if not id_val: id_val = f"LEC{new_user.id:04d}"
                lecturer = Lecturer(
                    user_id=new_user.id, 
                    user=new_user,
                    lecturer_id=id_val, 
                    department=dept or 'General'
                )
                db.session.add(lecturer)
                
            db.session.commit()
            flash(f"User {username} and profile created successfully!")
            return redirect(url_for('admin.users'))
            
    # Query with filtering and pagination
    role_filter = request.args.get('role', '', type=str)
    query = User.query
    
    if search:
        search_filter = f"%{search}%"
        # Find student IDs matching the search term
        matching_student_user_ids = db.session.query(Student.user_id).filter(
            Student.student_id.ilike(search_filter)
        ).subquery()
        query = query.filter(
            (User.full_name.ilike(search_filter)) | 
            (User.email.ilike(search_filter)) | 
            (User.username.ilike(search_filter)) |
            (User.id.in_(matching_student_user_ids))
        )
    
    if role_filter:
        query = query.filter(User.role == role_filter)
        
    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    all_users = pagination.items
    all_courses = Course.query.all()
    
    return render_template('admin/users.html', 
                          users=all_users, 
                          courses=all_courses, 
                          pagination=pagination, 
                          search=search,
                          role_filter=role_filter)

@admin_bp.route('/users/data/<int:id>')
@login_required
@admin_required
def get_user_data(id):
    user = User.query.get_or_404(id)
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'role': user.role,
        'p_id': '',
        'department': '',
        'gender': '',
        'course_id': ''
    }
    
    if user.role == 'student' and user.student_profile:
        data['p_id'] = user.student_profile.student_id
        data['department'] = user.student_profile.department
        data['gender'] = user.student_profile.gender
        data['course_id'] = user.student_profile.course_id
    elif user.role == 'lecturer' and user.lecturer_profile:
        data['p_id'] = user.lecturer_profile.lecturer_id
        data['department'] = user.lecturer_profile.department
        
    return jsonify(data)

@admin_bp.route('/users/edit/<int:id>', methods=['POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    user.full_name = request.form.get('full_name')
    user.email = request.form.get('email')
    
    # Update role and profile
    new_role = request.form.get('role')
    
    # If role changed, we might need to handle profile shuffling, 
    # but for now let's focus on updating existing profile fields.
    if user.role == 'student' and user.student_profile:
        user.student_profile.department = request.form.get('department')
        user.student_profile.gender = request.form.get('gender')
        user.student_profile.student_id = request.form.get('p_id')
        new_course_id = request.form.get('course_id')
        if new_course_id:
            user.student_profile.course_id = int(new_course_id)
    elif user.role == 'lecturer' and user.lecturer_profile:
        user.lecturer_profile.department = request.form.get('department')
        user.lecturer_profile.lecturer_id = request.form.get('p_id')
    
    user.role = new_role
    db.session.commit()
    flash("User and profile updated successfully.")
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully.")
    return redirect(url_for('admin.users'))

@admin_bp.route('/courses', methods=['GET', 'POST'])
@login_required
@admin_required
def courses():
    if request.method == 'POST':
        # Add Course Logic
        code = request.form.get('course_code')
        name = request.form.get('course_name')
        dept = request.form.get('department')
        credits = request.form.get('credits')
        
        new_course = Course(course_code=code, course_name=name, department=dept, credits=int(credits))
        db.session.add(new_course)
        db.session.commit()
        flash("Course added successfully!")
            
    all_courses = Course.query.all()
    return render_template('admin/courses.html', courses=all_courses)

@admin_bp.route('/courses/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    flash("Course deleted successfully.")
    return redirect(url_for('admin.courses'))

@admin_bp.route('/courses/edit/<int:id>', methods=['POST'])
@login_required
@admin_required
def edit_course(id):
    course = Course.query.get_or_404(id)
    course.course_code = request.form.get('course_code')
    course.course_name = request.form.get('course_name')
    course.department = request.form.get('department')
    course.credits = int(request.form.get('credits'))
    db.session.commit()
    flash("Course updated successfully.")
    return redirect(url_for('admin.courses'))

@admin_bp.route('/modules')
@login_required
@admin_required
def modules():
    all_courses = Course.query.all()
    return render_template('admin/modules.html', courses=all_courses)

@admin_bp.route('/modules/course/<int:course_id>')
@login_required
@admin_required
def course_modules(course_id):
    course = Course.query.get_or_404(course_id)
    modules = Module.query.filter_by(course_id=course_id).all()
    lecturers = Lecturer.query.all()
    
    # Calculate allocated credits
    allocated_credits = sum(m.credits for m in modules)
    
    return render_template('admin/course_modules.html', 
                           course=course, 
                           modules=modules, 
                           lecturers=lecturers,
                           allocated_credits=allocated_credits)

@admin_bp.route('/modules/add/<int:course_id>', methods=['POST'])
@login_required
@admin_required
def add_module(course_id):
    course = Course.query.get_or_404(course_id)
    
    code = request.form.get('module_code')
    name = request.form.get('module_name')
    semester = int(request.form.get('semester'))
    credits = int(request.form.get('credits'))
    lecturer_id = request.form.get('lecturer_id')
    description = request.form.get('description')
    
    # Validation: Credit Limit
    current_modules = Module.query.filter_by(course_id=course_id).all()
    total_allocated = sum(m.credits for m in current_modules)
    
    if total_allocated + credits > course.credits:
        flash(f"Error: Adding this module would exceed the course credit limit ({course.credits}). Currently allocated: {total_allocated}.")
        return redirect(url_for('admin.course_modules', course_id=course_id))
    
    if Module.query.filter_by(module_code=code).first():
        flash("Error: Module code already exists.")
        return redirect(url_for('admin.course_modules', course_id=course_id))

    new_module = Module(
        module_code=code,
        module_name=name,
        course_id=course_id,
        semester=semester,
        credits=credits,
        lecturer_id=lecturer_id if lecturer_id else None,
        description=description
    )
    
    db.session.add(new_module)
    db.session.commit()
    flash("Module added successfully!")
    return redirect(url_for('admin.course_modules', course_id=course_id))

@admin_bp.route('/modules/edit/<int:id>', methods=['POST'])
@login_required
@admin_required
def edit_module(id):
    module = Module.query.get_or_404(id)
    course = module.course
    
    old_credits = module.credits
    new_credits = int(request.form.get('credits'))
    
    # Validation: Credit Limit
    current_modules = Module.query.filter_by(course_id=course.id).all()
    total_allocated = sum(m.credits for m in current_modules) - old_credits
    
    if total_allocated + new_credits > course.credits:
        flash(f"Error: Updating this module would exceed the course credit limit ({course.credits}). Currently allocated (others): {total_allocated}.")
        return redirect(url_for('admin.course_modules', course_id=course.id))

    module.module_code = request.form.get('module_code')
    module.module_name = request.form.get('module_name')
    module.semester = int(request.form.get('semester'))
    module.credits = new_credits
    lecturer_id = request.form.get('lecturer_id')
    module.lecturer_id = lecturer_id if lecturer_id else None
    module.description = request.form.get('description')
    
    db.session.commit()
    flash("Module updated successfully.")
    return redirect(url_for('admin.course_modules', course_id=course.id))

@admin_bp.route('/modules/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_module(id):
    module = Module.query.get_or_404(id)
    course_id = module.course_id
    db.session.delete(module)
    db.session.commit()
    flash("Module deleted successfully.")
    return redirect(url_for('admin.course_modules', course_id=course_id))

@admin_bp.route('/assignments')
@login_required
@admin_required
def assignments():
    all_assignments = Assignment.query.all()
    return render_template('admin/assignments.html', assignments=all_assignments)

@admin_bp.route('/lectures', methods=['GET', 'POST'])
@login_required
@admin_required
def lectures():
    if request.method == 'POST':
        module_id = request.form.get('module_id')
        title = request.form.get('title')
        date_str = request.form.get('date')
        start_str = request.form.get('start_time')
        end_str = request.form.get('end_time')
        venue = request.form.get('venue')
        
        try:
            # Parse strings to time/date objects
            from datetime import datetime, time
            lecture_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_str, '%H:%M').time()
            end_time = datetime.strptime(end_str, '%H:%M').time()
            
            new_lecture = Lecture(
                module_id=module_id,
                lecture_title=title,
                lecture_date=lecture_date,
                start_time=start_time,
                end_time=end_time,
                venue=venue
            )
            db.session.add(new_lecture)
            db.session.commit()
            flash("Lecture scheduled successfully!")
        except Exception as e:
            flash(f"Error scheduling lecture: {str(e)}")
            db.session.rollback()
        return redirect(url_for('admin.lectures'))
        
    all_lectures = Lecture.query.all()
    all_modules = Module.query.all()
    return render_template('admin/lectures.html', lectures=all_lectures, modules=all_modules)

@admin_bp.route('/timetable', methods=['GET', 'POST'])
@login_required
@admin_required
def timetable():
    if request.method == 'POST':
        module_id = request.form.get('module_id')
        lecturer_id = request.form.get('lecturer_id')
        batch_id = request.form.get('batch_id')
        day = request.form.get('day')
        slot_id = int(request.form.get('slot_id'))
        venue = request.form.get('venue')
        
        # Get slot details
        slot = next((s for s in SLOTS if s['id'] == slot_id), None)
        if not slot:
            flash("Invalid time slot.")
            return redirect(url_for('admin.timetable'))
            
        start_time = datetime.strptime(slot['start'], '%H:%M').time()
        end_time = datetime.strptime(slot['end'], '%H:%M').time()
        
        # Check for conflicts (optional but recommended)
        # For simplicity, we'll just add it for now as per user request for "easy assignment"
        
        new_entry = Timetable(
            module_id=module_id,
            lecturer_id=lecturer_id,
            batch_id=batch_id,
            day_of_week=day,
            start_time=start_time,
            end_time=end_time,
            venue=venue
        )
        db.session.add(new_entry)
        db.session.commit()
        flash("Timetable entry added successfully!")
        return redirect(url_for('admin.timetable'))
        
    all_timetable = Timetable.query.all()
    all_modules = Module.query.all()
    all_lecturers = Lecturer.query.all()
    all_batches = Batch.query.all()
    
    return render_template('admin/timetable.html', 
                           timetable=all_timetable, 
                           modules=all_modules, 
                           lecturers=all_lecturers, 
                           batches=all_batches,
                           slots=SLOTS,
                           days=DAYS)

@admin_bp.route('/timetable/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_timetable_entry(id):
    entry = Timetable.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    flash("Timetable entry deleted successfully.")
    return redirect(url_for('admin.timetable'))

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    # Summarized risk data
    risk_data = {
        'low': Student.query.filter(Student.risk_score <= 0.3).count(),
        'medium': Student.query.filter((Student.risk_score > 0.3) & (Student.risk_score <= 0.7)).count(),
        'high': Student.query.filter(Student.risk_score > 0.7).count()
    }
    
    # Department performance
    dept_performance = db.session.query(
        Student.department, db.func.avg(Student.GPA).label('avg_gpa')
    ).group_by(Student.department).all()
    
    return render_template('admin/analytics.html', risk_data=risk_data, dept_performance=dept_performance)

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    return render_template('admin/reports.html')

@admin_bp.route('/reports/download/<type>')
@login_required
@admin_required
def download_report(type):
    flash(f"Generating {type} report... (Feature in progress)")
    return redirect(url_for('admin.reports'))

@admin_bp.route('/model-development')
@login_required
@admin_required
def model_development():
    import json
    metrics_path = 'app/ml_models/models/metrics.json'
    metrics = {}
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
    
    return render_template('admin/model_development.html', metrics=metrics)

@admin_bp.route('/mark-release')
@login_required
@admin_required
def mark_release():
    graded_submissions = Submission.query.filter_by(status='graded').all()
    return render_template('admin/mark_release.html', submissions=graded_submissions)

@admin_bp.route('/mark-release/approve/<int:id>', methods=['POST'])
@login_required
@admin_required
def approve_mark(id):
    submission = Submission.query.get_or_404(id)
    submission.status = 'released'
    submission.is_released = True
    
    # Also update the enrollment record for the final module grade if it's not already done
    enrollment = Enrollment.query.filter_by(student_id=submission.student_id, module_id=submission.assignment.module_id).first()
    if enrollment:
        # For simplicity, we assume one assignment per module for now or use the latest
        enrollment.grade_category = submission.grade_category
        enrollment.is_released = True
        
    db.session.commit()
    flash("Mark released to student successfully.")
    return redirect(url_for('admin.mark_release'))

@admin_bp.route('/batches')
@login_required
@admin_required
def batches():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    per_page = 20
    
    query = Batch.query
    if search:
        query = query.filter(Batch.name.contains(search))
        
    pagination = query.order_by(Batch.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    batches_list = pagination.items
    
    # stats per batch
    batch_stats = []
    for batch in batches_list:
        prediction = batch.get_success_prediction()
        batch_stats.append({
            'batch': batch,
            'prediction': f"{prediction*100:.1f}%",
            'student_count': batch.students.count(),
            'ai_insight': AIAdvisor.get_batch_insights(batch)
        })
    return render_template('admin/batches.html', batches=batch_stats, pagination=pagination, search=search)

@admin_bp.route('/batches/<int:batch_id>')
@login_required
@admin_required
def batch_detail(batch_id):
    batch = Batch.query.get_or_404(batch_id)
    students = batch.students.all()
    prediction = batch.get_success_prediction()
    insight = AIAdvisor.get_batch_insights(batch)
    return render_template('admin/batch_detail.html', batch=batch, students=students, prediction=prediction, insight=insight)
@admin_bp.route('/video-to-notes')
@login_required
@admin_required
def video_notes_page():
    return render_template('admin/video_process.html')

@admin_bp.route('/process-video-notes', methods=['POST'])
@login_required
@admin_required
def process_video_notes():
    if 'video' not in request.files:
        flash("No video file uploaded.")
        return redirect(url_for('admin.video_notes_page'))
    
    video = request.files['video']
    deep_mode = 'deep_mode' in request.form
    
    if video.filename == '':
        flash("No video selected.")
        return redirect(url_for('admin.video_notes_page'))
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    video_path = os.path.join(upload_folder, video.filename)
    video.save(video_path)
    
    report_dir = os.path.join('app', 'static', 'reports')
    os.makedirs(report_dir, exist_ok=True)
    
    try:
        transcript_pdf = ai_processor.video_to_transcript(video_path, report_dir, deep_mode=deep_mode)
        if os.path.exists(str(transcript_pdf)):
            filename = os.path.basename(transcript_pdf)
            transcript_url = url_for('static', filename=f'reports/{filename}')
            return render_template('admin/video_process.html', transcript_url=transcript_url)
        else:
            flash(f"Error processing video: {transcript_pdf}")
    except Exception as e:
        flash(f"AI Service Error: {str(e)}")
        
    return redirect(url_for('admin.video_notes_page'))
