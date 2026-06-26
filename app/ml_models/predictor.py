import os
import joblib
import pandas as pd
import numpy as np
from flask import current_app

class Predictor:
    def __init__(self):
        self.dropout_model = None
        self.graduation_model = None
        self.module_model = None
        self.le_gender = None
        self.models_loaded = False
        
    def load_models(self):
        """Load pre-trained models from the models directory"""
        try:
            model_path = current_app.config.get('ML_MODELS_PATH', 'app/ml_models/models/')
            
            dropout_path = os.path.join(model_path, 'dropout_model.joblib')
            grad_path = os.path.join(model_path, 'graduation_model.joblib')
            module_path = os.path.join(model_path, 'next_module_model.joblib')
            le_gender_path = os.path.join(model_path, 'le_gender.joblib')
            
            if os.path.exists(dropout_path):
                self.dropout_model = joblib.load(dropout_path)
            if os.path.exists(grad_path):
                self.graduation_model = joblib.load(grad_path)
            if os.path.exists(module_path):
                self.module_model = joblib.load(module_path)
            if os.path.exists(le_gender_path):
                self.le_gender = joblib.load(le_gender_path)
                
            self.models_loaded = True
            return True
        except Exception as e:
            print(f"Error loading models: {e}")
            return False

    def _prepare_features(self, features):
        """Ensure features are in the correct format and encoded"""
        # Ensure we have a local copy to avoid modifying the original list
        feats = list(features)
        
        # 1. Handle Gender Encoding
        if isinstance(feats[0], str):
            if self.le_gender:
                try:
                    feats[0] = self.le_gender.transform([feats[0]])[0]
                except:
                    feats[0] = 1 if feats[0].lower() == 'male' else 0
            else:
                # Manual fallback if LabelEncoder is missing
                feats[0] = 1 if feats[0].lower() == 'male' else 0
        
        # 2. Convert all to floats (now that gender is a number)
        processed_feats = []
        for x in feats:
            try:
                processed_feats.append(float(x) if x is not None else 0.0)
            except:
                processed_feats.append(0.0)
        
        # 3. Match the 15 features used during training
        if len(processed_feats) == 17:
            indices_to_keep = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 15, 16]
            final_feats = [processed_feats[i] for i in indices_to_keep]
        else:
            final_feats = processed_feats
            
        return np.array([final_feats])


    def predict_dropout(self, student_features):
        """
        Predict dropout risk
        student_features: list or array of features matching training columns
        """
        if not self.dropout_model:
            # Fallback for demo if model not trained
            return float(np.random.random() * 0.4), "Low Confidence (Demo Mode)"
            
        try:
            processed_features = self._prepare_features(student_features)
            prob = self.dropout_model.predict_proba(processed_features)[0][1]
            return float(prob), "High Confidence"
        except Exception as e:
            print(f"Prediction Error: {e}")
            return 0.33, "Low Confidence (Demo Mode)"


    def predict_graduation(self, student_features):
        """Predict timely graduation probability"""
        if not self.graduation_model:
            return float(0.8 + np.random.random() * 0.2), "Low Confidence (Demo Mode)"
            
        processed_features = self._prepare_features(student_features)
        prob = self.graduation_model.predict_proba(processed_features)[0][1]
        return float(prob), "High Confidence"

    def predict_next_module(self, student_features):
        """Predict performance in the next module"""
        if not self.module_model:
            return "B+", "Low Confidence (Demo Mode)"
            
        processed_features = self._prepare_features(student_features)
        prediction = self.module_model.predict(processed_features)[0]
        
        # If the result is an index (from LabelEncoder), we might need to map it back
        # For simplicity, we'll assume it returns the class or label
        return str(prediction), "High Confidence"

# Global instance
predictor = Predictor()
