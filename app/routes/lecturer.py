from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from app.models import Module, Assignment, Submission, Student, Lecture, Announcement, Attendance, Timetable, db
from app.utils.decorators import lecturer_required
from app.utils.ai_utils import ai_processor
from app.utils.timetable_utils import SLOTS, DAYS, get_current_slot, get_day_name
import os
from datetime import datetime
import json

"""
Lecturer Routing Module (lecturer.py)
-------------------------------------
இந்த பைல் ஆசிரியர்கள் (Lecturers) பயன்படுத்தும் இணைய பக்கங்களைக் கையாள்கிறது.
- Dashboard & Modules overview
- Assignment Creation & Grading (அசைன்மென்ட் திருத்துதல்)
- AI Video to Text Processing (லெக்சர் வீடியோவில் இருந்து நோட்ஸ் எடுத்தல்)
"""

lecturer_bp = Blueprint('lecturer', __name__)

@lecturer_bp.route('/dashboard')
@login_required
@lecturer_required
def dashboard():
    lecturer = current_user.lecturer_profile
    if not lecturer:
        flash("Lecturer profile not found.")
        return redirect(url_for('main.index'))
        
    modules = lecturer.modules.all()
    
    stats = {
        'total_modules': len(modules),
        'total_assignments': Assignment.query.filter(Assignment.module_id.in_([m.id for m in modules])).count(),
        'pending_grading': Submission.query.filter(
            Submission.assignment_id.in_(
                db.session.query(Assignment.id).filter(Assignment.module_id.in_([m.id for m in modules]))
            ),
            Submission.status == 'submitted'
        ).count()
    }
    
    at_risk_students = Student.query.filter(Student.risk_score > 0.5).limit(5).all()
    return render_template('lecturer/dashboard.html', stats=stats, modules=modules, at_risk_students=at_risk_students)

@lecturer_bp.route('/modules')
@login_required
@lecturer_required
def modules():
    lecturer = current_user.lecturer_profile
    modules = lecturer.modules.all()
    return render_template('lecturer/modules.html', modules=modules)

@lecturer_bp.route('/lectures', methods=['GET'])
@login_required
@lecturer_required
def lectures():
    lecturer = current_user.lecturer_profile
    modules = lecturer.modules.all()
    
    if request.method == 'POST':
        flash("Manual scheduling is disabled. Please contact Admin for timetable changes.")
        return redirect(url_for('lecturer.lectures'))
        
    all_lectures = Lecture.query.filter(Lecture.module_id.in_([m.id for m in modules])).all()
    timetable_entries = Timetable.query.filter_by(lecturer_id=lecturer.id).all()
    
    current_slot = get_current_slot()
    today_name = get_day_name()
    
    return render_template('lecturer/lectures.html', 
                           lectures=all_lectures, 
                           modules=modules, 
                           timetable=timetable_entries,
                           slots=SLOTS,
                           days=DAYS,
                           current_slot=current_slot,
                           today_name=today_name)

@lecturer_bp.route('/lecture/toggle-publish/<int:id>')
@login_required
@lecturer_required
def toggle_publish_lecture(id):
    lecture = Lecture.query.get_or_404(id)
    lecture.is_published = not lecture.is_published
    db.session.commit()
    flash(f"Lecture {'published' if lecture.is_published else 'unpublished'} successfully.")
    return redirect(url_for('lecturer.lectures'))

@lecturer_bp.route('/lecture/add-material/<int:id>', methods=['POST'])
@login_required
@lecturer_required
def add_material(id):
    lecture = Lecture.query.get_or_404(id)
    if 'file' not in request.files:
        flash("No file part")
        return redirect(url_for('lecturer.lectures'))
    
    file = request.files['file']
    material_type = request.form.get('type') # 'pdf', 'ppt', 'video', 'audio'
    title = request.form.get('title')
    
    if file.filename == '':
        flash("No selected file")
        return redirect(url_for('lecturer.lectures'))
        
    if file:
        from werkzeug.utils import secure_filename
        filename = secure_filename(file.filename)
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"lex_{id}_{filename}")
        file.save(save_path)
        
        # Update materials_json
        materials = json.loads(lecture.materials_json) if lecture.materials_json else []
        materials.append({
            'type': material_type,
            'title': title or filename,
            'path': f"lex_{id}_{filename}",
            'added_at': datetime.now().isoformat()
        })
        lecture.materials_json = json.dumps(materials)
        db.session.commit()
        flash("Material added successfully!")
        
    return redirect(url_for('lecturer.lectures'))

@lecturer_bp.route('/announcements', methods=['GET', 'POST'])
@login_required
@lecturer_required
def announcements():
    lecturer = current_user.lecturer_profile
    modules = lecturer.modules.all()
    
    if request.method == 'POST':
        module_id = request.form.get('module_id')
        title = request.form.get('title')
        content = request.form.get('content')
        
        new_ann = Announcement(
            module_id=module_id,
            lecturer_id=lecturer.id,
            title=title,
            content=content
        )
        db.session.add(new_ann)
        db.session.commit()
        flash("Announcement broadcasted successfully!")
        
    all_ann = Announcement.query.filter(Announcement.module_id.in_([m.id for m in modules])).all()
    return render_template('lecturer/announcements.html', announcements=all_ann, modules=modules)

@lecturer_bp.route('/assignments', methods=['GET', 'POST'])
@login_required
@lecturer_required
def assignments():
    lecturer = current_user.lecturer_profile
    modules = lecturer.modules.all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        module_id = request.form.get('module_id')
        
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            new_assignment = Assignment(
                title=title, 
                description=description, 
                deadline=due_date, 
                module_id=module_id
            )
            db.session.add(new_assignment)
            db.session.commit()
            flash("Assignment created successfully!")
        except Exception as e:
            flash(f"Error creating assignment: {str(e)}")
            db.session.rollback()
        
    all_assignments = Assignment.query.filter(Assignment.module_id.in_([m.id for m in modules])).all()
    return render_template('lecturer/assignments.html', assignments=all_assignments, modules=modules)

@lecturer_bp.route('/grading')
@login_required
@lecturer_required
def grading():
    lecturer = current_user.lecturer_profile
    modules = lecturer.modules.all()
    pending_submissions = Submission.query.filter(
        Submission.assignment_id.in_(
            db.session.query(Assignment.id).filter(Assignment.module_id.in_([m.id for m in modules]))
        ),
        Submission.status == 'submitted'
    ).all()
    return render_template('lecturer/grading.html', submissions=pending_submissions)

@lecturer_bp.route('/grade-submission/<int:id>', methods=['POST'])
@login_required
@lecturer_required
def grade_submission(id):
    submission = Submission.query.get_or_404(id)
    marks = request.form.get('marks')
    category = request.form.get('category')
    feedback = request.form.get('feedback')
    
    submission.marks_obtained = float(marks) if marks else 0
    submission.grade_category = category
    submission.feedback = feedback
    submission.status = 'graded'
    submission.is_released = False
    submission.graded_by = current_user.lecturer_profile.id
    submission.graded_at = datetime.utcnow()
    
    db.session.commit()
    flash("Submission graded successfully! It is now pending Admin approval.")
    return redirect(url_for('lecturer.grading'))

@lecturer_bp.route('/performance')
@login_required
@lecturer_required
def performance():
    lecturer = current_user.lecturer_profile
    modules = lecturer.modules.all()
    return render_template('lecturer/performance.html', modules=modules)

@lecturer_bp.route('/video-process')
@login_required
@lecturer_required
def video_process_page():
    lecturer = current_user.lecturer_profile
    # Get modules assigned to this lecturer
    modules = lecturer.modules.all()
    # Get unique batches from his timetable
    timetable_slots = Timetable.query.filter_by(lecturer_id=lecturer.id).all()
    # Create a list of (module, batch) pairs
    assignments = []
    seen = set()
    for slot in timetable_slots:
        pair = (slot.module_id, slot.batch_id)
        if pair not in seen:
            assignments.append({
                'module_id': slot.module_id,
                'module_name': slot.module.module_name,
                'batch_id': slot.batch_id,
                'batch_name': slot.batch.name if slot.batch else "General"
            })
            seen.add(pair)
            
    return render_template('lecturer/video_process.html', assignments=assignments)

@lecturer_bp.route('/process-video', methods=['POST'])
@login_required
@lecturer_required
def process_video():
    if 'video' not in request.files:
        flash("No video file uploaded.")
        return redirect(url_for('lecturer.video_process_page'))
    
    video = request.files['video']
    if video.filename == '':
        flash("No selected file.")
        return redirect(url_for('lecturer.video_process_page'))
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    video_path = os.path.join(upload_folder, video.filename)
    video.save(video_path)
    
    report_dir = os.path.join('app', 'static', 'reports')
    os.makedirs(report_dir, exist_ok=True)
    
    try:
        # Use deep mode if selected
        deep_mode = 'deep_mode' in request.form
        transcript_pdf = ai_processor.video_to_transcript(video_path, report_dir, deep_mode=deep_mode)
        
        if os.path.exists(str(transcript_pdf)):
            filename = os.path.basename(transcript_pdf)
            transcript_url = url_for('static', filename=f'reports/{filename}')
            
            # Fetch assignments again for the template
            lecturer = current_user.lecturer_profile
            timetable_slots = Timetable.query.filter_by(lecturer_id=lecturer.id).all()
            assignments = []
            seen = set()
            for slot in timetable_slots:
                pair = (slot.module_id, slot.batch_id)
                if pair not in seen:
                    assignments.append({
                        'module_id': slot.module_id,
                        'module_name': slot.module.module_name,
                        'batch_id': slot.batch_id,
                        'batch_name': slot.batch.name if slot.batch else "General"
                    })
                    seen.add(pair)
            
            return render_template('lecturer/video_process.html', 
                                 transcript_url=transcript_url, 
                                 raw_pdf_path=f"reports/{filename}",
                                 assignments=assignments)
        else:
            flash(f"Error processing video: {transcript_pdf}")
    except Exception as e:
        flash(f"AI Service Error: {str(e)}")
        
    return redirect(url_for('lecturer.video_process_page'))

@lecturer_bp.route('/share-ai-notes', methods=['POST'])
@login_required
@lecturer_required
def share_ai_notes():
    from app.models import SharedMaterial, Alert, Student
    
    lecturer = current_user.lecturer_profile
    module_id = request.form.get('module_id')
    batch_id = request.form.get('batch_id')
    file_path = request.form.get('file_path')
    title = request.form.get('title', 'AI Generated Study Notes')
    
    if not all([module_id, batch_id, file_path]):
        flash("Please select both Module and Batch.")
        return redirect(url_for('lecturer.video_process_page'))
    
    try:
        # 1. Create SharedMaterial record
        shared = SharedMaterial(
            lecturer_id=lecturer.id,
            module_id=int(module_id),
            batch_id=int(batch_id),
            title=title,
            file_path=file_path
        )
        db.session.add(shared)
        
        # 2. Alert all students in this batch
        from app.models import Student, Alert
        students = Student.query.filter_by(batch_id=int(batch_id)).all()
        for student in students:
            alert = Alert(
                student_id=student.id,
                alert_type='material',
                message=f"New AI Study Material: '{title}' has been shared with your batch."
            )
            db.session.add(alert)
        
        db.session.commit()
        flash(f"Notes shared successfully with {len(students)} students!")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error sharing notes: {str(e)}")
        
    return redirect(url_for('lecturer.video_process_page'))

@lecturer_bp.route('/voice-note')
@login_required
@lecturer_required
def voice_note_page():
    return render_template('lecturer/voice_note.html')

@lecturer_bp.route('/process-voice', methods=['POST'])
@login_required
@lecturer_required
def process_voice():
    if 'audio' not in request.files:
        flash("No audio file uploaded.")
        return redirect(url_for('lecturer.voice_note_page'))
    
    audio = request.files['audio']
    if audio.filename == '':
        flash("No selected file.")
        return redirect(url_for('lecturer.voice_note_page'))
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    audio_path = os.path.join(upload_folder, audio.filename)
    audio.save(audio_path)
    
    try:
        transcript = ai_processor.speech_to_text(audio_path)
        return render_template('lecturer/voice_note.html', transcript=transcript)
    except Exception as e:
        flash(f"Speech Service Error: {str(e)}")
        
    return redirect(url_for('lecturer.voice_note_page'))