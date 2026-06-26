import hashlib
import random
import string
from datetime import datetime, timedelta
from flask import current_app
from app import db
from app.models import SystemLog, Alert
import os

def log_activity(user_id, action, entity_type=None, entity_id=None, details=None):
    """Log system activity"""
    try:
        log = SystemLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details
        )
        db.session.add(log)
        db.session.commit()
    except:
        db.session.rollback()

def generate_password_reset_token(email):
    """Generate password reset token"""
    import jwt
    from datetime import datetime, timedelta
    
    payload = {
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_password_reset_token(token):
    """Verify password reset token"""
    import jwt
    
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['email']
    except:
        return None

def create_alert(student_id, alert_type, title, message, severity='medium'):
    """Create an alert for a student"""
    alert = Alert(
        student_id=student_id,
        alert_type=alert_type,
        title=title,
        message=message,
        severity=severity,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.session.add(alert)
    db.session.commit()
    return alert

def check_attendance_thresholds():
    """Check attendance thresholds and create alerts"""
    from app.models import Student
    
    students = Student.query.all()
    threshold = current_app.config.get('ATTENDANCE_WARNING_THRESHOLD', 75)
    
    for student in students:
        if student.attendance_percentage < threshold:
            # Check if alert already exists
            existing = Alert.query.filter_by(
                student_id=student.id,
                alert_type='attendance',
                is_read=False
            ).first()
            
            if not existing:
                create_alert(
                    student_id=student.id,
                    alert_type='attendance',
                    title='Low Attendance Warning',
                    message=f'Your attendance is {student.attendance_percentage:.1f}%, below the required {threshold}%.',
                    severity='high'
                )

def process_audio_transcription(audio_path):
    """Simulate audio transcription"""
    # In production, integrate with speech-to-text API
    return "This is a simulated transcription of the lecture audio."

def generate_ai_summary(transcription):
    """Generate AI summary from transcription"""
    # In production, integrate with NLP summarization
    return "This is an AI-generated summary of the lecture."

def send_email_alert(alert):
    """Send email alert (simulated)"""
    # In production, integrate with email service
    print(f"Email alert sent to student {alert.student_id}: {alert.title}")
    alert.is_email_sent = True
    db.session.commit()

def allowed_file(filename, allowed_extensions=None):
    """Check if file extension is allowed"""
    if allowed_extensions is None:
        allowed_extensions = {'pdf', 'docx', 'txt', 'jpg', 'png', 'mp3', 'mp4'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions