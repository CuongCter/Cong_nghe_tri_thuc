#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask API for Data Science Salary Prediction
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import numpy as np
import os
import sys

# Force UTF-8 stdout on Windows to avoid cp1252 UnicodeEncodeError
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except (AttributeError, OSError):
    pass

# Add parent directory to path to import our analysis module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from salary_analysis import DataScienceSalaryAnalysis
except ImportError:
    print("Warning: Could not import DataScienceSalaryAnalysis. Using fallback prediction.")

app = Flask(__name__)
CORS(app)

# Model coefficients (from trained model)
MODEL_COEFFICIENTS = {
    'intercept': 136913.07,
    'work_year': 2635.11,
    'experience_level_encoded': 14263.28,
    'employment_type_encoded': -67.69,
    'job_title_encoded': 11506.27,
    'remote_ratio': 293.69,
    'company_size_encoded': -1651.69,
    'is_us': 15282.33
}

# Encoding mappings
EXPERIENCE_MAPPING = {'EN': 0, 'MI': 1, 'SE': 2, 'EX': 3}
EMPLOYMENT_MAPPING = {'FT': 0, 'PT': 1, 'CT': 2, 'FL': 3}
COMPANY_SIZE_MAPPING = {'S': 0, 'M': 1, 'L': 2}

JOB_MAPPING = {
    'Data Engineer': 0,
    'Data Scientist': 1,
    'Data Analyst': 2,
    'Data Architect': 3,
    'Data Science': 4,
    'Data Manager': 5,
    'Data Science Manager': 6,
    'Data Specialist': 7,
    'Data Science Consultant': 8,
    'Data Analytics Manager': 9,
    'Head of Data': 10,
    'Data Modeler': 11,
    'Data Product Manager': 12,
    'Director of Data Science': 13
}

# Global analyzer instance
analyzer = None

def initialize_analyzer():
    """Initialize the analyzer with the dataset"""
    global analyzer
    try:
        data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data-salary.csv')
        if os.path.exists(data_path):
            analyzer = DataScienceSalaryAnalysis(data_path)
            analyzer.load_data()
            analyzer.clean_data()
            analyzer.preprocess_data()
            analyzer.train_models()
            print("✅ Analyzer initialized successfully")
            return True
    except Exception as e:
        print(f"❌ Failed to initialize analyzer: {e}")
    return False

@app.route('/')
def index():
    """Serve the main dashboard"""
    return send_from_directory('.', 'index_new.html')

@app.route('/images/<path:filename>')
def serve_images(filename):
    """Serve images from parent directory"""
    import os
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images_path = os.path.join(parent_dir, 'images')
    return send_from_directory(images_path, filename)

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

@app.route('/api/predict', methods=['POST'])
def predict_salary():
    """Predict salary based on input parameters"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['work_year', 'experience_level', 'employment_type', 
                          'job_title', 'remote_ratio', 'company_size', 'company_location']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Use trained model if available, otherwise use fallback
        if analyzer and hasattr(analyzer, 'model'):
            prediction = predict_with_trained_model(data)
        else:
            prediction = predict_with_coefficients(data)
        
        return jsonify(prediction)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def predict_with_trained_model(data):
    """Use the trained model for prediction"""
    try:
        # Prepare features similar to training data
        features = np.array([[
            data['work_year'],
            EXPERIENCE_MAPPING[data['experience_level']],
            EMPLOYMENT_MAPPING[data['employment_type']],
            JOB_MAPPING[data['job_title']],
            data['remote_ratio'],
            COMPANY_SIZE_MAPPING[data['company_size']],
            1 if data['company_location'] == 'US' else 0
        ]])

        # IMPORTANT: Need to normalize features like in training!
        if hasattr(analyzer, 'scaler'):
            features_normalized = analyzer.scaler.transform(features)
            prediction = analyzer.model.predict(features_normalized)[0]
        else:
            # Fallback to raw features if no scaler
            prediction = analyzer.model.predict(features)[0]

        # Calculate confidence interval using model's MAE
        mae = getattr(analyzer, 'test_mae', 37641)
        confidence_lower = max(0, prediction - mae)
        confidence_upper = prediction + mae

        return {
            'prediction': round(prediction),
            'confidence_lower': round(confidence_lower),
            'confidence_upper': round(confidence_upper),
            'method': 'trained_model',
            'mae': round(mae)
        }

    except Exception as e:
        print(f"Error with trained model: {e}")
        return predict_with_coefficients(data)

def predict_with_coefficients(data):
    """Fallback prediction using hardcoded coefficients"""
    # Encode categorical variables
    experience_encoded = EXPERIENCE_MAPPING[data['experience_level']]
    employment_encoded = EMPLOYMENT_MAPPING[data['employment_type']]
    job_encoded = JOB_MAPPING[data['job_title']]
    company_size_encoded = COMPANY_SIZE_MAPPING[data['company_size']]
    is_us = 1 if data['company_location'] == 'US' else 0
    
    # Calculate prediction using linear regression formula
    prediction = (MODEL_COEFFICIENTS['intercept'] +
                 MODEL_COEFFICIENTS['work_year'] * data['work_year'] +
                 MODEL_COEFFICIENTS['experience_level_encoded'] * experience_encoded +
                 MODEL_COEFFICIENTS['employment_type_encoded'] * employment_encoded +
                 MODEL_COEFFICIENTS['job_title_encoded'] * job_encoded +
                 MODEL_COEFFICIENTS['remote_ratio'] * data['remote_ratio'] +
                 MODEL_COEFFICIENTS['company_size_encoded'] * company_size_encoded +
                 MODEL_COEFFICIENTS['is_us'] * is_us)
    
    # Calculate confidence interval (±MAE)
    mae = 37641
    confidence_lower = max(0, prediction - mae)
    confidence_upper = prediction + mae
    
    return {
        'prediction': round(prediction),
        'confidence_lower': round(confidence_lower),
        'confidence_upper': round(confidence_upper),
        'method': 'coefficients',
        'mae': mae
    }

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dataset statistics"""
    try:
        if analyzer and hasattr(analyzer, 'df_processed'):
            df = analyzer.df_processed
            stats = {
                'total_records': len(df),
                'job_titles': len(df['job_title'].unique()),
                'countries': len(df['company_location'].unique()),
                'avg_salary': round(df['salary_in_usd'].mean()),
                'median_salary': round(df['salary_in_usd'].median()),
                'salary_range': {
                    'min': round(df['salary_in_usd'].min()),
                    'max': round(df['salary_in_usd'].max())
                },
                'us_vs_non_us': {
                    'us_avg': round(df[df['company_location'] == 'US']['salary_in_usd'].mean()),
                    'non_us_avg': round(df[df['company_location'] != 'US']['salary_in_usd'].mean())
                }
            }
        else:
            # Fallback stats
            stats = {
                'total_records': 10473,
                'job_titles': 14,
                'countries': 50,
                'avg_salary': 143064,
                'median_salary': 135000,
                'salary_range': {'min': 15000, 'max': 800000},
                'us_vs_non_us': {'us_avg': 143064, 'non_us_avg': 90269}
            }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/job-titles', methods=['GET'])
def get_job_titles():
    """Get available job titles"""
    return jsonify(list(JOB_MAPPING.keys()))

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'analyzer_loaded': analyzer is not None,
        'model_available': analyzer and hasattr(analyzer, 'model') if analyzer else False
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Data Science Salary Dashboard...")
    print("📊 Initializing analyzer...")
    
    # Initialize analyzer
    if initialize_analyzer():
        print("✅ Ready with trained model")
    else:
        print("⚠️  Using fallback coefficients")
    
    print("🌐 Starting Flask server...")
    print("📱 Dashboard available at: http://localhost:5000")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
