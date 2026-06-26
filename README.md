# Smart Academic Companion System

An intelligent, integrated academic monitoring platform combining IoT attendance tracking, AI-powered lecture summarization, and Machine Learning dropout and graduation risk prediction built to help educational institutions detect at-risk students early and take timely action.

---

## About This Project

The Smart Academic Companion System was developed as a Final Year Project for the BSc in Data Science at London Metropolitan University by Satkunam Tishalan (LMU ID - 25027320).

Traditional academic monitoring systems are reactive — problems like poor attendance or declining grades are only noticed after significant damage has occurred. This system replaces that reactive approach with an intelligent, automated, and proactive platform that brings together three cutting-edge technologies into a single unified web application.

---

## Screenshots

### Admin Dashboard
<img width="822" height="403" alt="image" src="https://github.com/user-attachments/assets/c5461edc-cde3-43c5-9234-3c354b321f34" />

The centralized control panel showing total students, lecturers, courses, high-risk student count, and real-time risk distribution analytics.

### User Management
<img width="797" height="466" alt="image" src="https://github.com/user-attachments/assets/8daa2933-1a37-4638-b482-56ef0551dda9" />

Full CRUD management for all student and lecturer accounts with role assignment, advanced search, and filtering across 100,000+ records.

### System Analytics
<img width="873" height="609" alt="image" src="https://github.com/user-attachments/assets/0ef8007a-d0cb-46e5-99fb-2ff6f321e658" />

Real-time institutional risk distribution chart, overall dropout risk percentage, average attendance, graduation confidence, and departmental GPA breakdown.

### Lecturer Dashboard
<img width="842" height="886" alt="image" src="https://github.com/user-attachments/assets/b8ed7eca-a5e5-4c37-93bf-4c25ba23389f" />


Quick overview of active modules, pending grading, at-risk students, performance trends, recent alerts, and dropout risk monitoring table.

### Student Dashboard
<img width="871" height="1178" alt="image" src="https://github.com/user-attachments/assets/ebb0b78d-ffd7-4e0f-a8bd-123ac7eba486" />


Personal academic overview including current GPA, attendance, AI-predicted dropout risk, graduation probability, enrolled modules, upcoming deadlines, and AI advisor insights.

### AI Study Aid
<img width="777" height="473" alt="image" src="https://github.com/user-attachments/assets/7554f21e-6417-44a8-8330-c5b24aaa6e43" />

Students can upload lecture slides or PDF files and let the AI generate detailed, concept-rich study notes instantly using Google Gemini AI.


---

## Key Features

### Machine Learning Risk Prediction
Predicts dropout risk, graduation probability, and next module performance for every student. Trained on a dataset of 100,000 student records using XGBoost as the primary model achieving 94.8% accuracy and 0.93 recall. Features used include attendance rate, GPA, assignment scores, quiz results, LMS login frequency, study hours, and forum participation. Automated email alerts are sent to administrators when a student is flagged as high risk.

### IoT-Based Attendance Tracking
RFID card reader connected to a microcontroller automatically records student attendance when they enter a classroom. Eliminates manual attendance marking and human error. Attendance data feeds directly into the ML prediction engine in real time. A web-based attendance kiosk is also available as a fallback interface.

### NLP Lecture Summarization
Lecturers upload video or audio recordings of their lectures. The system extracts audio using MoviePy, transcribes it using OpenAI Whisper, and generates a structured summary using Google Gemini AI. A downloadable PDF lecture summary is automatically generated using ReportLab. Students can access these summaries via their dashboard as an AI Study Aid.

### Role-Based Dashboards
Three separate interfaces tailored to each user type.

| Role | Key Capabilities |
|---|---|
| Admin | Full system overview, user management, course/batch/module management, system analytics, mark release, risk reports, AI video processing |
| Lecturer | Timetable, announcements, assignment management, grading suite, class performance charts, AI video transcript tool, voice notes |
| Student | Personal dashboard, AI Study Aid, timetable, course modules, assignment submissions, grades, performance analytics |

---

## System Architecture

The system follows a three-tier architecture.

```
Presentation Layer
HTML5, CSS3, JavaScript, Chart.js
Role-Based Dashboards (3 portals)

Application Layer
Flask (Python) with Blueprints
ML Engine | NLP Module | IoT API

Data Layer
Microsoft SQL Server
Users | Students | Predictions | Courses | Attendance
```

---

## Technologies Used

### Backend
| Technology | Purpose |
|---|---|
| Python 3.x | Core programming language |
| Flask 3.0 | Web framework and routing |
| Flask-SQLAlchemy | ORM for database interaction |
| Flask-Login | Session management and authentication |
| Flask-CORS | Cross-origin resource sharing |
| Bcrypt | Secure password hashing |

### Machine Learning
| Technology | Purpose |
|---|---|
| XGBoost | Primary dropout and graduation risk prediction model |
| scikit-learn | Random Forest, preprocessing, evaluation metrics |
| pandas | Data manipulation and feature engineering |
| NumPy | Numerical computations |
| joblib | Model serialization and loading |
| matplotlib / seaborn | Model evaluation visualizations |

### NLP and AI
| Technology | Purpose |
|---|---|
| OpenAI Whisper | Speech-to-text transcription of lecture audio |
| Google Gemini AI | AI-powered lecture summarization |
| OpenRouter API | Fallback AI provider |
| SpeechRecognition | Supplementary speech recognition |
| scikit-learn TF-IDF + NetworkX | Extractive summarization fallback |

### IoT
| Technology | Purpose |
|---|---|
| RFID Reader + Microcontroller | Hardware attendance capture |
| REST API | Data transmission from IoT device to backend |

### Database
| Technology | Purpose |
|---|---|
| Microsoft SQL Server | Primary relational database |
| PyMySQL / pyodbc | Database drivers |

### Frontend
| Technology | Purpose |
|---|---|
| HTML5 / CSS3 | Page structure and styling |
| JavaScript (ES6+) | Client-side interactivity |
| Chart.js | Performance charts and analytics graphs |
| Jinja2 | Server-side HTML templating |

### Document and File Processing
| Technology | Purpose |
|---|---|
| ReportLab | Generating PDF lecture summary documents |
| MoviePy | Extracting audio from uploaded video files |
| PyMuPDF | PDF reading and processing |
| python-pptx | PowerPoint file support |
| openpyxl | Excel file reading |

---

## Project Structure

```
smart-academic-system/
|
|-- run.py                          Entry point
|-- config.py                       Configuration (DB, ML, email, AI settings)
|-- requirements.txt                Python dependencies
|-- setup_database.sql              Database schema setup script
|-- ml_pipeline.py                  Full ML training pipeline
|-- retrain_ml.py                   Retrain models on fresh data
|-- populate_lms_100k.py            Seed 100k student records into DB
|-- automation_tests.py             Automated test suite
|
|-- data/
|   |-- student_records_100k.csv    100,000 student training records
|   |-- student_data.xlsx           Student data in Excel format
|
|-- app/
|   |-- models.py                   SQLAlchemy DB models
|   |
|   |-- routes/
|   |   |-- admin.py                Admin portal routes
|   |   |-- lecturer.py             Lecturer portal routes
|   |   |-- student.py              Student portal routes
|   |   |-- auth.py                 Authentication routes
|   |   |-- api.py                  REST API and IoT routes
|   |
|   |-- ml_models/
|   |   |-- predictor.py            Prediction engine
|   |   |-- models/
|   |       |-- dropout_model.joblib
|   |       |-- graduation_model.joblib
|   |       |-- next_module_model.joblib
|   |       |-- scaler.joblib
|   |       |-- metrics.json
|   |
|   |-- utils/
|   |   |-- ai_utils.py             AIProcessor (Whisper, Gemini, summarization)
|   |   |-- pdf_generator.py        PDF report generation
|   |   |-- decorators.py           Role-based access control decorators
|   |   |-- helpers.py              General helper functions
|   |
|   |-- templates/
|   |   |-- admin/                  Admin portal templates
|   |   |-- lecturer/               Lecturer portal templates
|   |   |-- student/                Student portal templates
|   |
|   |-- static/
|       |-- css/style.css
|       |-- js/main.js, api.js, charts.js
|       |-- uploads/
|       |-- reports/
```

---

## Setup and Installation

### Prerequisites
- Python 3.10+
- Microsoft SQL Server or SQL Server LocalDB
- ODBC Driver 17 for SQL Server
- Gemini API key or OpenRouter API key for AI summarization

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/smart-academic-system.git
cd smart-academic-system
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```env
SECRET_KEY=your-secure-secret-key
MSSQL_SERVER=(localdb)\MSSQLLocalDB
MSSQL_DB=smart_academic_system
GEMINI_API_KEY=your-gemini-api-key
OPENROUTER_API_KEY=your-openrouter-api-key
AI_PROVIDER=gemini
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-app-password
```

### 4. Set Up the Database
```bash
sqlcmd -S (localdb)\MSSQLLocalDB -i setup_database.sql
```

### 5. Seed the Database
```bash
python populate_lms_100k.py
python generate_assignments.py
```

### 6. Train the ML Models
```bash
python ml_pipeline.py
```

### 7. Run the Application
```bash
python run.py
```

Visit http://localhost:5000 in your browser.

Windows users can run setup_windows.ps1 in PowerShell for automated setup.

---

## Testing

```bash
python automation_tests.py
```

The system was evaluated with 18 structured functional test cases covering authentication, RFID attendance, ML prediction, NLP processing, and role-based access.

### ML Model Performance (XGBoost)

| Metric | Score |
|---|---|
| Accuracy | 94.8% |
| Recall (high-risk) | 0.93 |
| ROC-AUC | 0.97 |

---

## Security

- Passwords hashed using Bcrypt
- Role-based access control enforced on every route via custom decorators
- Session cookies configured with HttpOnly, SameSite, and Secure flags
- 8-hour session lifetime with automatic expiry
- File uploads restricted to safe extensions and capped at 16MB

---

## Documentation

The full project report is included in the repository as `E225097_FINAL_PROJECT_.pdf` covering introduction, literature review, system design and architecture, implementation, testing and evaluation, and conclusions.

---

## Author

Satkunam Tishalan
BSc in Data Science, ESOFT Blended / London Metropolitan University
Student ID: E225097 | London Met ID: 25027320
Email: E225097@esoft.academy

Supervisors: Mr. E. Mithurshanan and Mr. V. Jathushan

---

## License

This project was developed for academic purposes as part of a Final Year Project submission. All rights reserved by the author.
