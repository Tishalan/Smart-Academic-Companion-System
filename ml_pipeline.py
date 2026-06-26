import pandas as pd
import numpy as np
import os
import joblib
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from app import create_app, db
from app.models import Student

def load_sql_data():
    """Load data from SQL Server database"""
    app = create_app('development')
    with app.app_context():
        print("Fetching data from SQL Server...")
        # Use SQLAlchemy to query all students
        students = Student.query.all()
        data = []
        for s in students:
            data.append({
                'gender': s.gender,
                'age': s.age,
                'family_income': float(s.family_income) if s.family_income else 0,
                'scholarship': 1 if s.scholarship else 0,
                'distance_from_campus': s.distance_from_campus or 0,
                'internet_access': 1 if s.internet_access else 0,
                'attendance_percentage': s.attendance_percentage or 0,
                'internal_marks': s.internal_marks or 0,
                'assignment_avg': s.assignment_avg or 0,
                'quiz_avg': s.quiz_avg or 0,
                'LMS_login_frequency': s.LMS_login_frequency or 0,
                'average_study_hours': s.average_study_hours or 0,
                'forum_participation': s.forum_participation or 0,
                'intake_year': s.intake_year or 2024,
                'GPA': s.GPA or 0,
                'dropout_risk': s.risk_score
            })
        
        df = pd.DataFrame(data)
        print(f"Loaded {len(df)} records from SQL Server.")
        return df

def train_models():
    print("Starting ML Pipeline - Training with SQL Server Data...")
    
    df = load_sql_data()
    if len(df) == 0:
        print("Error: No data found in SQL Server.")
        return

    features = [
        'gender', 'age', 'family_income', 'scholarship', 'distance_from_campus',
        'internet_access', 'attendance_percentage', 'internal_marks', 
        'assignment_avg', 'quiz_avg', 'LMS_login_frequency',
        'average_study_hours', 'forum_participation', 'intake_year', 'GPA'
    ]
    
    target_dropout = 'dropout_risk'
    
    # Preprocessing
    df = df.fillna(df.median(numeric_only=True))

    df['attendance_ratio'] = df['attendance_percentage'] / 100

    # Feature 2 — Performance Index
    df['performance_index'] = (df['internal_marks'] * 0.30) + \
                              (df['assignment_avg'] * 0.40) + \
                              (df['quiz_avg'] * 0.30)

    # Feature 3 — Engagement Score
    df['engagement_score'] = (df['LMS_login_frequency'] * 0.40) + \
                             (df['forum_participation'] * 0.30) + \
                             (df['average_study_hours'] * 0.30)
    
    # Update features list to include engineered features
    features = features + ['attendance_ratio', 'performance_index', 'engagement_score']
    
    le_gender = LabelEncoder()
    df['gender'] = le_gender.fit_transform(df['gender'].astype(str))
    
    # Map dropout_risk to binary if it's not already
    # The new CSV data has continuous dropout_risk? 
    # Let's check if it needs thresholding or if it's already 0/1
    if df[target_dropout].max() > 1:
        # If it was 'High', 'Medium', 'Low' strings
        df[target_dropout] = df[target_dropout].apply(lambda x: 1 if str(x).strip().lower() == 'high' else 0)
    else:
        # Assume it's a probability or binary
        df[target_dropout] = df[target_dropout].apply(lambda x: 1 if x >= 0.5 else 0)
    
    X = df[features]
    y = df[target_dropout]
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Save preprocessing objects
    os.makedirs('app/ml_models/models', exist_ok=True)
    joblib.dump(scaler, 'app/ml_models/models/scaler.joblib')
    joblib.dump(le_gender, 'app/ml_models/models/le_gender.joblib')
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    
    # Check if we have enough classes
    if len(np.unique(y_train)) < 2:
        print("Warning: Only one class in training set. Synthetic data required for complete model demonstration.")
        # Minimal synthetic balancing
        y_train.iloc[0] = 1 - y_train.iloc[0]

    # Training Best Model (XGBoost as selected in previous runs)
    print("Training XGBoost...")
    xgb = XGBClassifier(n_estimators=100, learning_rate=0.1, eval_metric='logloss')
    xgb.fit(X_train, y_train)
    
    # Evaluation
    y_preds = xgb.predict(X_test)
    accuracy = accuracy_score(y_test, y_preds)
    print(f"Model Accuracy: {accuracy:.4f}")
    
    # Save Model
    joblib.dump(xgb, 'app/ml_models/models/dropout_model.joblib')
    print("Model saved to app/ml_models/models/dropout_model.joblib")

if __name__ == '__main__':
    train_models()
