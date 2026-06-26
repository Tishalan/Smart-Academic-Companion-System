import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
import os

def retrain_models():
    print("Retraining ML models on real dataset...")
    
    # Load and merge data (same logic as migration)
    xl = pd.ExcelFile('data/student_data.xlsx')
    df = xl.parse('STUDENT_TABLE')
    df = df.merge(xl.parse('ATTENDANCE_TABLE'), on='student_id', how='left')
    df = df.merge(xl.parse('ACADEMIC_PERFORMANCE_TABLE'), on='student_id', how='left')
    df = df.merge(xl.parse('ENGAGEMENT_TABLE'), on='student_id', how='left')
    df = df.merge(xl.parse('PREDICTION_OUTPUT_TABLE'), on='student_id', how='left')
    
    # Feature Engineering
    le_gender = LabelEncoder()
    df['gender_encoded'] = le_gender.fit_transform(df['gender'])
    
    # Map risk/probability strings back to numeric if they are strings
    def to_numeric(val):
        if isinstance(val, (int, float)): return val
        val_str = str(val).lower()
        if 'high' in val_str: return 0.85
        if 'medium' in val_str: return 0.50
        if 'low' in val_str: return 0.15
        return 0.0

    df['dropout_risk_num'] = df['dropout_risk'].apply(to_numeric)
    df['grad_prob_num'] = df['graduation_probability'].apply(to_numeric)
    
    # Features for the models
    features = [
        'gender_encoded', 'age', 'family_income', 'scholarship', 'distance_from_campus', 'internet_access',
        'attendance_percentage', 'internal_marks', 'assignment_avg', 'quiz_avg', 'previous_fail_count',
        'LMS_login_frequency', 'average_study_hours', 'forum_participation', 'library_usage', 'GPA'
    ]
    
    X = df[features].fillna(0)
    
    # 1. Dropout Risk Model (Classification)
    y_dropout = (df['dropout_risk_num'] > 0.5).astype(int)
    model_dropout = RandomForestClassifier(n_estimators=100, random_state=42)
    model_dropout.fit(X, y_dropout)
    
    # 2. Graduation Probability Model (Regression)
    y_grad = df['grad_prob_num']
    model_grad = GradientBoostingRegressor(n_estimators=100, random_state=42)
    model_grad.fit(X, y_grad)
    
    # 3. Next Module Performance (Classification)
    le_next = LabelEncoder()
    y_next = le_next.fit_transform(df['next_module_prediction'].astype(str))
    model_next = RandomForestClassifier(n_estimators=100, random_state=42)
    model_next.fit(X, y_next)
    
    # Save Models
    model_dir = 'app/ml_models/models'
    os.makedirs(model_dir, exist_ok=True)
    
    joblib.dump(model_dropout, os.path.join(model_dir, 'dropout_model.joblib'))
    joblib.dump(model_grad, os.path.join(model_dir, 'graduation_model.joblib'))
    joblib.dump(model_next, os.path.join(model_dir, 'next_module_model.joblib'))
    joblib.dump(le_gender, os.path.join(model_dir, 'le_gender.joblib'))
    joblib.dump(le_next, os.path.join(model_dir, 'le_next_module.joblib'))
    
    print("All models retrained and saved successfully!")

if __name__ == "__main__":
    retrain_models()
