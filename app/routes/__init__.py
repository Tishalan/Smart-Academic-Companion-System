from flask import Blueprint, request, jsonify
from app.models import Student, Attendance, Lecture, db
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/iot/attendance/mark', methods=['POST'])
def mark_iot_attendance():
    """
    Requirement 3: Flask API endpoint to receive attendance data.
    """
    data = request.get_json()
    student_uid = data.get('student_id')
    lecture_id = data.get('lecture_id')
    
    # 1. Validation Logic: Verify Student existence
    # Requirement 4: Backend validation
    student = Student.query.filter_by(student_id=student_uid).first()
    if not student:
        return jsonify({"status": "error", "message": "Student UID not registered"}), 404
        
    # 2. Check if Lecture is active
    lecture = Lecture.query.get(lecture_id)
    if not lecture:
        return jsonify({"status": "error", "message": "Invalid Lecture ID"}), 400

    # 3. SQLAlchemy Database Logging
    # Requirement 5: Log attendance into database
    try:
        new_record = Attendance(
            student_id=student.id,
            lecture_id=lecture_id,
            is_present=True,
            marked_at=datetime.utcnow()
        )
        db.session.add(new_record)
        
        # Real-time Update: Increment student's overall attendance %
        student.attendance_percentage = student.get_updated_attendance_rate()
        
        db.session.commit()
        
        # Requirement 6: Return JSON success response
        return jsonify({
            "status": "success",
            "message": f"Attendance marked for {student.user.full_name}",
            "timestamp": datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500



