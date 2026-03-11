from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pandas as pd
import numpy as np
import joblib
import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this in production

# Load the trained model and artifacts
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    WEBAPP_DIR = os.path.dirname(BASE_DIR)
    PROJECT_ROOT = os.path.dirname(WEBAPP_DIR)
    MODELS_DIR = os.path.join(PROJECT_ROOT, 'model')
    
    model_path = os.path.join(MODELS_DIR, 'breast_cancer_model.pkl')
    features_path = os.path.join(MODELS_DIR, 'breast_cancer_model_features.json')
    
    artifacts = joblib.load(model_path)
    model = artifacts['model']
    scaler = artifacts['scaler']
    selected_features = artifacts['selected_features']
    
    with open(features_path, 'r') as f:
        feature_info = json.load(f)
    
    print("Model and artifacts loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None
    scaler = None
    selected_features = []

# Sample doctor credentials (in production, use a proper database)
DOCTORS = {
    'doctor1': 'password123',
    'doctor2': 'password123',
    'admin': 'admin123'
}

# Feature descriptions for user guidance
FEATURE_DESCRIPTIONS = {
    'radius_mean': 'Mean of distances from center to points on the perimeter',
    'texture_mean': 'Standard deviation of gray-scale values',
    'perimeter_mean': 'Mean size of the core tumor',
    'area_mean': 'Mean area of the tumor',
    'smoothness_mean': 'Mean of local variation in radius lengths',
    'compactness_mean': 'Mean of (perimeter^2 / area) - 1.0',
    'concavity_mean': 'Mean of severity of concave portions of the contour',
    'concave points_mean': 'Mean for number of concave portions of the contour'
}

# Treatment suggestions
TREATMENT_SUGGESTIONS = {
    'Malignant': [
        "Consult with an oncologist immediately",
        "Consider surgical options (lumpectomy or mastectomy)",
        "Radiation therapy may be recommended",
        "Chemotherapy treatment options",
        "Hormone therapy for hormone receptor-positive cancers",
        "Targeted therapy based on genetic markers",
        "Regular follow-up and monitoring",
        "Supportive care and counseling"
    ],
    'Benign': [
        "Regular monitoring and follow-up",
        "Maintain healthy lifestyle",
        "Regular breast self-examinations",
        "Annual mammograms as recommended",
        "Maintain healthy weight",
        "Limit alcohol consumption",
        "Regular physical activity",
        "Discuss preventive measures with your doctor"
    ]
}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in DOCTORS and DOCTORS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Collect form data
            feature_values = {}
            for feature in selected_features:
                value = request.form.get(feature)
                if value:
                    feature_values[feature] = float(value)
                else:
                    flash(f'Please provide value for {feature}', 'warning')
                    return redirect(url_for('prediction'))
            
            # Create DataFrame with the input features
            input_df = pd.DataFrame([feature_values])
            
            # Ensure all required features are present
            for feature in selected_features:
                if feature not in input_df.columns:
                    flash(f'Missing feature: {feature}', 'danger')
                    return redirect(url_for('prediction'))
            
            # Select and scale features
            input_selected = input_df[selected_features]
            input_scaled = scaler.transform(input_selected)
            
            # Make prediction
            prediction = model.predict(input_scaled)[0]
            probability = model.predict_proba(input_scaled)[0]
            
            # Prepare results
            diagnosis = "Malignant" if prediction == 1 else "Benign"
            confidence = max(probability) * 100
            probability_benign = probability[0] * 100
            probability_malignant = probability[1] * 100
            
            # Store results in session for display
            session['prediction_result'] = {
                'diagnosis': diagnosis,
                'confidence': round(confidence, 2),
                'probability_benign': round(probability_benign, 2),
                'probability_malignant': round(probability_malignant, 2),
                'feature_values': feature_values,
                'suggestions': TREATMENT_SUGGESTIONS[diagnosis]
            }
            
            return redirect(url_for('prediction_result'))
            
        except Exception as e:
            flash(f'Error making prediction: {str(e)}', 'danger')
            return redirect(url_for('prediction'))
    
    return render_template('prediction.html', 
                         features=selected_features,
                         descriptions=FEATURE_DESCRIPTIONS)

@app.route('/prediction_result')
def prediction_result():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    result = session.get('prediction_result')
    if not result:
        flash('No prediction results found. Please make a prediction first.', 'warning')
        return redirect(url_for('prediction'))
    
    return render_template('result.html', result=result)

@app.route('/visualizations')
def visualizations():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Generate model performance visualizations
    plots = generate_visualizations()
    
    return render_template('visualizations.html', plots=plots)

def generate_visualizations():
    """Generate model performance visualizations"""
    plots = {}
    
    try:
        # Sample data for demonstration - in practice, use actual model performance data
        models = ['Random Forest', 'SVM', 'Logistic Regression', 'KNN']
        accuracy = [0.95, 0.92, 0.89, 0.87]
        precision = [0.94, 0.91, 0.88, 0.86]
        recall = [0.93, 0.90, 0.87, 0.85]
        
        # Plot 1: Model Comparison
        plt.figure(figsize=(10, 6))
        x = np.arange(len(models))
        width = 0.25
        
        plt.bar(x - width, accuracy, width, label='Accuracy', alpha=0.8)
        plt.bar(x, precision, width, label='Precision', alpha=0.8)
        plt.bar(x + width, recall, width, label='Recall', alpha=0.8)
        
        plt.xlabel('Models')
        plt.ylabel('Scores')
        plt.title('Model Performance Comparison')
        plt.xticks(x, models)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plots['model_comparison'] = plot_to_base64()
        plt.close()
        
        # Plot 2: Feature Importance
        plt.figure(figsize=(10, 6))
        features = selected_features[:8]
        importance = np.random.rand(len(features))  # Replace with actual importance
        colors = plt.cm.viridis(np.linspace(0, 1, len(features)))
        
        plt.barh(features, importance, color=colors)
        plt.xlabel('Importance Score')
        plt.title('Feature Importance')
        plt.tight_layout()
        
        plots['feature_importance'] = plot_to_base64()
        plt.close()
        
        # Plot 3: Confusion Matrix
        plt.figure(figsize=(8, 6))
        cm = np.array([[85, 5], [3, 87]])  # Sample confusion matrix
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=['Predicted Benign', 'Predicted Malignant'],
                   yticklabels=['Actual Benign', 'Actual Malignant'])
        plt.title('Confusion Matrix')
        plt.tight_layout()
        
        plots['confusion_matrix'] = plot_to_base64()
        plt.close()
        
        # Plot 4: ROC Curve
        plt.figure(figsize=(8, 6))
        fpr = np.linspace(0, 1, 100)
        tpr = np.sin(fpr * np.pi / 2)  # Sample ROC curve
        plt.plot(fpr, tpr, label='ROC Curve (AUC = 0.95)', linewidth=2)
        plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plots['roc_curve'] = plot_to_base64()
        plt.close()
        
    except Exception as e:
        print(f"Error generating visualizations: {e}")
    
    return plots

def plot_to_base64():
    """Convert matplotlib plot to base64 string for HTML embedding"""
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    return base64.b64encode(image_png).decode('utf-8')

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for predictions"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract features
        feature_values = {}
        for feature in selected_features:
            if feature in data:
                feature_values[feature] = float(data[feature])
            else:
                return jsonify({'error': f'Missing feature: {feature}'}), 400
        
        # Prepare data for prediction
        input_df = pd.DataFrame([feature_values])
        input_selected = input_df[selected_features]
        input_scaled = scaler.transform(input_selected)
        
        # Make prediction
        prediction = model.predict(input_scaled)[0]
        probability = model.predict_proba(input_scaled)[0]
        
        diagnosis = "Malignant" if prediction == 1 else "Benign"
        
        return jsonify({
            'diagnosis': diagnosis,
            'confidence': round(max(probability) * 100, 2),
            'probability_benign': round(probability[0] * 100, 2),
            'probability_malignant': round(probability[1] * 100, 2),
            'suggestions': TREATMENT_SUGGESTIONS[diagnosis]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)