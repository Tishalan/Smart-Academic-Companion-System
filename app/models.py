from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
import json

class User(UserMixin, db.Model):
    """
    User Model - Represents all accounts in the system.
    This handles authentication (login) and role management (Admin, Student, Lecturer).
    It links to specific profiles (Student or Lecturer) via relationships.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('admin', 'lecturer', 'student'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    student_profile = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    lecturer_profile = db.relationship('Lecturer', backref='user', uselist=False, cascade='all, delete-orphan')
    logs = db.relationship('SystemLog', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)
    
    def has_role(self, role):
        return self.role == role
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Student(db.Model):
    """
    Student Model - Stores academic and personal details for a student.
    Linked to the 'User' table via user_id. Contains AI prediction metrics like risk_score.
    """
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    gender = db.Column(db.Enum('Male', 'Female', 'Other'), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    intake_year = db.Column(db.Integer, nullable=False)
    family_income = db.Column(db.Numeric(10, 2))
    scholarship = db.Column(db.Boolean, default=False)
    distance_from_campus = db.Column(db.Float)
    internet_access = db.Column(db.Boolean, default=True)
    attendance_percentage = db.Column(db.Float, default=0)
    internal_marks = db.Column(db.Float, default=0)
    assignment_avg = db.Column(db.Float, default=0)
    quiz_avg = db.Column(db.Float, default=0)
    final_exam_marks = db.Column(db.Float, default=0)
    GPA = db.Column(db.Float, default=0)
    previous_fail_count = db.Column(db.Integer, default=0)
    LMS_login_frequency = db.Column(db.Integer, default=0)
    average_study_hours = db.Column(db.Float, default=0)
    forum_participation = db.Column(db.Integer, default=0)
    library_usage = db.Column(db.Float, default=0)
    current_semester = db.Column(db.Integer, default=1)
    risk_score = db.Column(db.Float, default=0)
    graduation_probability = db.Column(db.Float, default=0)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'))
    current_stage = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', backref='students')
    enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    submissions = db.relationship('Submission', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    attendance = db.relationship('Attendance', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    predictions = db.relationship('Prediction', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    
    def update_risk_score(self, score):
        self.risk_score = score
        db.session.commit()
    
    def update_graduation_probability(self, prob):
        self.graduation_probability = prob
        db.session.commit()
    
    def get_feature_vector(self):
        """Return feature vector for ML predictions"""
        return [
            self.gender,
            self.age,
            float(self.family_income) if self.family_income else 0,
            1 if self.scholarship else 0,
            self.distance_from_campus or 0,
            1 if self.internet_access else 0,
            self.attendance_percentage or 0,
            self.internal_marks or 0,
            self.assignment_avg or 0,
            self.quiz_avg or 0,
            self.previous_fail_count or 0,
            self.LMS_login_frequency or 0,
            self.average_study_hours or 0,
            self.forum_participation or 0,
            self.library_usage or 0,
            self.intake_year or 2024,
            self.GPA or 0
        ]
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'user_id': self.user_id,
            'full_name': self.user.full_name if self.user else None,
            'email': self.user.email if self.user else None,
            'department': self.department,
            'gpa': float(self.GPA) if self.GPA else 0,
            'risk_score': float(self.risk_score) if self.risk_score else 0,
            'graduation_probability': float(self.graduation_probability) if self.graduation_probability else 0,
            'attendance': self.attendance_percentage,
            'current_semester': self.current_semester,
            'course_name': self.course.course_name if self.course else 'Not Assigned',
            'course_id': self.course_id
        }

class Batch(db.Model):
    __tablename__ = 'batches'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    graduation_month = db.Column(db.String(20)) # 'February' or 'September'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', backref='batches')
    students = db.relationship('Student', backref='batch', lazy='dynamic')
    
    def get_success_prediction(self):
        students = self.students.all()
        if not students:
            return 0
        return sum(s.graduation_probability for s in students) / len(students)

class Lecturer(db.Model):
    __tablename__ = 'lecturers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    lecturer_id = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100))
    qualification = db.Column(db.String(255))
    joining_date = db.Column(db.Date)
    specialization = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    modules = db.relationship('Module', backref='lecturer', lazy='dynamic')
    assignments_created = db.relationship('Assignment', backref='creator', lazy='dynamic')
    graded_submissions = db.relationship('Submission', backref='grader', lazy='dynamic')
    attendance_marked = db.relationship('Attendance', backref='marker', lazy='dynamic')
    
    def get_workload_stats(self):
        return {
            'total_modules': self.modules.count(),
            'total_assignments': Assignment.query.filter_by(created_by=self.id).count(),
            'pending_gradings': Submission.query.filter_by(graded_by=self.id, graded_at=None).count()
        }

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    duration_semesters = db.Column(db.Integer, default=1)
    coordinator_id = db.Column(db.Integer, db.ForeignKey('lecturers.id', ondelete='SET NULL'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    modules = db.relationship('Module', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    coordinator = db.relationship('Lecturer', foreign_keys=[coordinator_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.course_code,
            'name': self.course_name,
            'department': self.department,
            'credits': self.credits,
            'modules_count': self.modules.count()
        }

class Module(db.Model):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    module_code = db.Column(db.String(20), unique=True, nullable=False)
    module_name = db.Column(db.String(200), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturers.id', ondelete='SET NULL'))
    description = db.Column(db.Text)
    syllabus = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='module', lazy='dynamic', cascade='all, delete-orphan')
    lectures = db.relationship('Lecture', backref='module', lazy='dynamic', cascade='all, delete-orphan')
    assignments = db.relationship('Assignment', backref='module', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_enrollment_count(self):
        return self.enrollments.filter_by(status='enrolled').count()
    
    def get_average_attendance(self):
        lectures = self.lectures.all()
        if not lectures:
            return 0
        total_attendance = 0
        total_lectures = len(lectures)
        for lecture in lectures:
            total_attendance += lecture.attendance.filter_by(is_present=True).count()
        return (total_attendance / (total_lectures * self.get_enrollment_count())) * 100 if self.get_enrollment_count() > 0 else 0

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='NO ACTION'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False)
    enrollment_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Enum('enrolled', 'completed', 'dropped', 'pending'), default='enrolled')
    grade = db.Column(db.Float)
    grade_letter = db.Column(db.String(2))
    grade_category = db.Column(db.String(20)) # Pass, Merit, Distinction
    is_released = db.Column(db.Boolean, default=False)
    attendance_rate = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'module_id', name='unique_enrollment'),)

class Lecture(db.Model):
    __tablename__ = 'lectures'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False)
    lecture_title = db.Column(db.String(255), nullable=False)
    lecture_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    venue = db.Column(db.String(100))
    lecture_notes = db.Column(db.Text)
    audio_file_path = db.Column(db.String(255))
    transcription = db.Column(db.Text)
    ai_summary = db.Column(db.Text)
    is_online = db.Column(db.Boolean, default=False)
    meeting_link = db.Column(db.String(255))
    is_published = db.Column(db.Boolean, default=True)
    materials_json = db.Column(db.Text) # Store as JSON: [{'type': 'pdf', 'path': '...', 'title': '...'}, ...]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attendance = db.relationship('Attendance', backref='lecture', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_attendance_count(self):
        return self.attendance.filter_by(is_present=True).count()

class Announcement(db.Model):
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturers.id'))
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    module = db.relationship('Module', backref=db.backref('announcements', lazy='dynamic'))

class Timetable(db.Model):
    __tablename__ = 'timetable'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturers.id'), nullable=True)
    day_of_week = db.Column(db.String(20), nullable=False) # 'Monday', etc.
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    venue = db.Column(db.String(100))
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=True)
    
    # Relationships
    module = db.relationship('Module', backref=db.backref('timetable_slots', lazy='dynamic'))
    lecturer = db.relationship('Lecturer', backref=db.backref('timetable_slots', lazy='dynamic'))
    batch = db.relationship('Batch', backref=db.backref('timetable_slots', lazy='dynamic'))

class PresentationAid(db.Model):
    __tablename__ = 'presentation_aids'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    ai_notes_json = db.Column(db.Text) # JSON mapping slides to detailed explanations
    pdf_report_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref=db.backref('presentation_aids', lazy='dynamic'))
    module = db.relationship('Module', backref=db.backref('presentation_aids', lazy='dynamic'))

class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    total_marks = db.Column(db.Integer, nullable=False)
    weightage = db.Column(db.Float)
    deadline = db.Column(db.DateTime, nullable=False)
    submission_type = db.Column(db.Enum('file', 'text', 'both'), default='file')
    brief_file_path = db.Column(db.String(255))
    max_file_size = db.Column(db.Integer, default=10485760)
    allowed_file_types = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('lecturers.id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submissions = db.relationship('Submission', backref='assignment', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_submission_count(self):
        return self.submissions.count()
    
    def get_average_marks(self):
        graded = self.submissions.filter(Submission.marks_obtained.isnot(None)).all()
        if not graded:
            return 0
        return sum(s.marks_obtained for s in graded) / len(graded)

class Submission(db.Model):
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='NO ACTION'), nullable=False)
    submission_text = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    marks_obtained = db.Column(db.Float)
    feedback = db.Column(db.Text)
    graded_by = db.Column(db.Integer, db.ForeignKey('lecturers.id', ondelete='SET NULL'))
    graded_at = db.Column(db.DateTime)
    is_late = db.Column(db.Boolean, default=False)
    plagiarism_score = db.Column(db.Float, default=0)
    grade_category = db.Column(db.Enum('Pass', 'Merit', 'Distinction', 'Fail'))
    is_released = db.Column(db.Boolean, default=False)
    status = db.Column(db.Enum('submitted', 'graded', 'late', 'resubmitted', 'released'), default='submitted')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('assignment_id', 'student_id', name='unique_submission'),)

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='NO ACTION'), nullable=False)
    is_present = db.Column(db.Boolean, default=False)
    marked_by = db.Column(db.Integer, db.ForeignKey('lecturers.id', ondelete='SET NULL'))
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('lecture_id', 'student_id', name='unique_attendance'),)

class Prediction(db.Model):
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    prediction_type = db.Column(db.Enum('dropout', 'graduation', 'next_module'), nullable=False)
    prediction_value = db.Column(db.String(50), nullable=False)
    probability = db.Column(db.Float)
    confidence_interval = db.Column(db.String(50))
    feature_importance = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_feature_importance(self):
        return json.loads(self.feature_importance) if self.feature_importance else {}

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # 'risk', 'attendance', 'performance'
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SharedMaterial(db.Model):
    __tablename__ = 'shared_materials'
    
    id = db.Column(db.Integer, primary_key=True)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturers.id', ondelete='CASCADE'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='NO ACTION'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id', ondelete='NO ACTION'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lecturer = db.relationship('Lecturer', backref='shared_materials')
    module = db.relationship('Module', backref='shared_materials')
    batch = db.relationship('Batch', backref='shared_materials')

class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
