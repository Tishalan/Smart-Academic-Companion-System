from flask import Blueprint, jsonify, request
from app.models import Student, db
from app.ml_models.predictor import predictor

api_bp = Blueprint('api', __name__)

@api_bp.route('/predict/dropout/<int:student_id>', methods=['GET'])
def predict_dropout(student_id):
    student = Student.query.get_or_404(student_id)
    features = student.get_feature_vector()
    
    prob, confidence = predictor.predict_dropout(features)
    
    # Update student record with new risk score
    student.risk_score = prob
    db.session.commit()
    
    return jsonify({
        'student_id': student.student_id,
        'prediction_type': 'dropout',
        'probability': prob,
        'confidence': confidence,
        'status': 'success'
    })

@api_bp.route('/predict/graduation/<int:student_id>', methods=['GET'])
def predict_graduation(student_id):
    student = Student.query.get_or_404(student_id)
    features = student.get_feature_vector()
    
    prob, confidence = predictor.predict_graduation(features)
    
    student.graduation_probability = prob
    db.session.commit()
    
    return jsonify({
        'student_id': student.student_id,
        'prediction_type': 'graduation_delay',
        'probability': prob,
        'confidence': confidence,
        'status': 'success'
    })

@api_bp.route('/predict/all/<int:student_id>', methods=['GET'])
def predict_all(student_id):
    student = Student.query.get_or_404(student_id)
    features = student.get_feature_vector()
    
    dropout_prob, _ = predictor.predict_dropout(features)
    grad_prob, _ = predictor.predict_graduation(features)
    next_mod, _ = predictor.predict_next_module(features)
    
    student.risk_score = dropout_prob
    student.graduation_probability = grad_prob
    db.session.commit()
    
    return jsonify({
        'student_id': student.student_id,
        'dropout_risk': dropout_prob,
        'graduation_probability': grad_prob,
        'next_module_prediction': next_mod,
        'status': 'success'
    })

@api_bp.route('/attendance/check-in', methods=['POST'])
def attendance_check_in():
    data = request.json
    student_id_str = data.get('student_id')
    
    student = Student.query.filter_by(student_id=student_id_str).first()
    if not student:
        return jsonify({'error': 'Student not found'}), 404
        
    # Mark attendance for the most recent or ongoing lecture in their modules
    # For now, we'll mark against any lecture today for their enrolled modules
    from datetime import date, datetime
    today = date.today()
    
    # Get student's enrolled module IDs
    enrolled_module_ids = [e.module_id for e in student.enrollments.all()]
    
    # Find a lecture for these modules today
    current_lecture = Lecture.query.filter(
        Lecture.module_id.in_(enrolled_module_ids),
        Lecture.lecture_date == today
    ).order_by(Lecture.start_time.desc()).first()
    
    if current_lecture:
        # Check if already marked
        from app.models import Attendance
        existing = Attendance.query.filter_by(lecture_id=current_lecture.id, student_id=student.id).first()
        if not existing:
            new_att = Attendance(
                lecture_id=current_lecture.id,
                student_id=student.id,
                is_present=True,
                marked_at=datetime.utcnow()
            )
            db.session.add(new_att)
            db.session.commit()
    
    # Return student insights for the kiosk
    return jsonify({
        'status': 'success',
        'full_name': student.user.full_name,
        'batch_name': student.batch.name if student.batch else 'No Batch',
        'course_name': student.course.course_name if student.course else 'No Course',
        'attendance_rate': int(student.attendance_percentage or 0),
        'today_classes': Lecture.query.filter(Lecture.module_id.in_(enrolled_module_ids), Lecture.lecture_date == today).count(),
        'gpa': student.GPA
    })
