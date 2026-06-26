-- Smart Academic System Database Schema
CREATE DATABASE IF NOT EXISTS smart_academic_system;
USE smart_academic_system;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'lecturer', 'student') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login DATETIME
);

-- Students Table
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    student_id VARCHAR(20) UNIQUE NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    age INT NOT NULL,
    department VARCHAR(100) NOT NULL,
    intake_year INT NOT NULL,
    family_income DECIMAL(10, 2),
    scholarship BOOLEAN DEFAULT FALSE,
    distance_from_campus FLOAT,
    internet_access BOOLEAN DEFAULT TRUE,
    attendance_percentage FLOAT DEFAULT 0,
    internal_marks FLOAT DEFAULT 0,
    assignment_avg FLOAT DEFAULT 0,
    quiz_avg FLOAT DEFAULT 0,
    final_exam_marks FLOAT DEFAULT 0,
    GPA FLOAT DEFAULT 0,
    previous_fail_count INT DEFAULT 0,
    LMS_login_frequency INT DEFAULT 0,
    average_study_hours FLOAT DEFAULT 0,
    forum_participation INT DEFAULT 0,
    library_usage FLOAT DEFAULT 0,
    current_semester INT DEFAULT 1,
    risk_score FLOAT DEFAULT 0,
    graduation_probability FLOAT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Lecturers Table
CREATE TABLE IF NOT EXISTS lecturers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    lecturer_id VARCHAR(20) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL,
    designation VARCHAR(100),
    qualification VARCHAR(255),
    joining_date DATE,
    specialization VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Courses Table
CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    course_name VARCHAR(200) NOT NULL,
    department VARCHAR(100) NOT NULL,
    credits INT NOT NULL,
    duration_semesters INT DEFAULT 1,
    coordinator_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (coordinator_id) REFERENCES lecturers(id) ON DELETE SET NULL
);

-- Modules Table
CREATE TABLE IF NOT EXISTS modules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    module_code VARCHAR(20) UNIQUE NOT NULL,
    module_name VARCHAR(200) NOT NULL,
    course_id INT NOT NULL,
    semester INT NOT NULL,
    credits INT NOT NULL,
    lecturer_id INT,
    description TEXT,
    syllabus TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (lecturer_id) REFERENCES lecturers(id) ON DELETE SET NULL
);

-- Enrollments Table
CREATE TABLE IF NOT EXISTS enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    module_id INT NOT NULL,
    enrollment_date DATE NOT NULL,
    status ENUM('enrolled', 'completed', 'dropped', 'pending') DEFAULT 'enrolled',
    grade FLOAT,
    grade_letter VARCHAR(2),
    attendance_rate FLOAT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_enrollment (student_id, module_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE
);

-- Predictions Table
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    prediction_type ENUM('dropout', 'graduation', 'next_module') NOT NULL,
    prediction_value VARCHAR(50) NOT NULL,
    probability FLOAT,
    confidence_interval VARCHAR(50),
    feature_importance TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_student_id ON students(student_id);
CREATE INDEX idx_module_code ON modules(module_code);
CREATE INDEX idx_user_role ON users(role);
