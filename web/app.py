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

# Import Expert System modules
try:
    from knowledge_base import KNOWLEDGE_RULES, get_rule_stats
    from inference_engine import (InferenceEngine, run_inference,
                                  BackwardChainingEngine, run_backward_inference)
    from explanation_module import ExplanationModule, generate_explanation
    EXPERT_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Expert System modules not available: {e}")
    EXPERT_SYSTEM_AVAILABLE = False

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
    """
    Fallback prediction using approximation.
    Lưu ý: Mô hình gốc dùng Z-Score Normalization, các hệ số này chỉ là
    approximation dựa trên pattern dữ liệu.
    """
    experience_encoded = EXPERIENCE_MAPPING[data['experience_level']]
    employment_encoded = EMPLOYMENT_MAPPING[data['employment_type']]
    job_encoded = JOB_MAPPING.get(data['job_title'], 7)
    company_size_encoded = COMPANY_SIZE_MAPPING[data['company_size']]
    is_us = 1 if data['company_location'] == 'US' else 0

    # Hệ số đã được calibrated cho raw features (không qua normalization)
    # Base cho Data Engineer mid-level US, 2024, 0% remote, M company
    base = 130000

    # Experience: EN=0, MI=+15k, SE=+30k, EX=+50k
    base += experience_encoded * 15000

    # US premium
    if is_us:
        base += 35000

    # Job title multiplier (relative to Data Engineer)
    job_multipliers = {
        'Data Engineer': 0,
        'Data Scientist': 8000,
        'Data Analyst': -30000,
        'Data Architect': 20000,
        'Data Science': 12000,
        'Data Manager': 10000,
        'Data Science Manager': 50000,
        'Data Specialist': -50000,
        'Data Science Consultant': 10000,
        'Data Analytics Manager': 25000,
        'Head of Data': 80000,
        'Data Modeler': 5000,
        'Data Product Manager': 30000,
        'Director of Data Science': 75000
    }
    base += job_multipliers.get(data['job_title'], 0)

    # Work year trend: tăng nhẹ theo năm
    year_factor = (data['work_year'] - 2020) * 8000
    base += year_factor

    # Remote ratio
    if data['remote_ratio'] == 100:
        base += 2000
    elif data['remote_ratio'] == 50:
        base -= 5000

    # Company size
    if data['company_size'] == 'S':
        base -= 50000
    elif data['company_size'] == 'L':
        base -= 15000

    # Employment type
    if data['employment_type'] == 'PT':
        base *= 0.6
    elif data['employment_type'] == 'CT':
        base *= 0.95
    elif data['employment_type'] == 'FL':
        base *= 0.5

    prediction = max(15000, base)

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
        'model_available': analyzer and hasattr(analyzer, 'model') if analyzer else False,
        'expert_system_available': EXPERT_SYSTEM_AVAILABLE
    })


# ============================================================
# EXPERT SYSTEM ENDPOINTS - Hệ Chuyên Gia Tư Vấn Lương
# ============================================================

@app.route('/api/recommend', methods=['POST'])
def expert_recommend():
    """
    Endpoint chính của Hệ Chuyên Gia:
    - Forward chaining qua Knowledge Base
    - Kết hợp ML prediction
    - Trả về recommendation + explanation

    Input JSON giống /api/predict
    Output: JSON với recommendation, rules_fired, explanation
    """
    if not EXPERT_SYSTEM_AVAILABLE:
        return jsonify({
            'error': 'Expert System modules not available',
            'fallback': 'Use /api/predict instead'
        }), 503

    try:
        data = request.json

        # Validate required fields
        required_fields = ['work_year', 'experience_level', 'employment_type',
                          'job_title', 'remote_ratio', 'company_size', 'company_location']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Chuẩn bị facts cho inference engine (chuyển location thành is_us)
        facts = dict(data)
        facts['is_us'] = 1 if data['company_location'] == 'US' else 0

        # Chọn ML predictor
        ml_predictor = predict_with_trained_model if (analyzer and hasattr(analyzer, 'model')) else predict_with_coefficients

        # Chạy inference engine
        recommendation = run_inference(facts, ml_predictor)

        # Sinh explanation
        explanation_data = generate_explanation(recommendation)

        return jsonify({
            'recommendation': recommendation,
            'explanation': explanation_data['explanation'],
            'display': explanation_data['display'],
            'metadata': {
                'system_type': 'Hybrid Expert System (ML + Rules)',
                'rules_total': len(KNOWLEDGE_RULES),
                'rules_fired': recommendation.get('rules_fired_count', 0),
                'overall_confidence': recommendation.get('overall_confidence', 0),
                'categories_evaluated': list(recommendation.get('category_confidences', {}).keys())
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/rules', methods=['GET'])
def get_knowledge_base():
    """Lấy tất cả luật trong Knowledge Base"""
    if not EXPERT_SYSTEM_AVAILABLE:
        return jsonify({'error': 'Expert System not available'}), 503

    try:
        category = request.args.get('category', None)
        rule_id = request.args.get('id', None)

        if rule_id:
            rules = [r for r in KNOWLEDGE_RULES if r['id'] == rule_id]
        elif category:
            rules = [r for r in KNOWLEDGE_RULES if r['category'] == category]
        else:
            rules = KNOWLEDGE_RULES

        return jsonify({
            'rules': rules,
            'stats': get_rule_stats(),
            'total': len(rules)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Lấy tất cả categories"""
    if not EXPERT_SYSTEM_AVAILABLE:
        return jsonify({'error': 'Expert System not available'}), 503
    return jsonify(get_rule_stats())


@app.route('/api/explain-rule/<rule_id>', methods=['GET'])
def explain_rule(rule_id):
    """Giải thích chi tiết một luật cụ thể"""
    if not EXPERT_SYSTEM_AVAILABLE:
        return jsonify({'error': 'Expert System not available'}), 503

    for r in KNOWLEDGE_RULES:
        if r['id'] == rule_id:
            return jsonify({
                'rule': r,
                'explanation': {
                    'description': r.get('description', ''),
                    'category': r['category'],
                    'certainty_factor': r['cf'],
                    'cf_percentage': f"{r['cf']*100:.0f}%",
                    'source': r.get('source', ''),
                    'priority': r.get('priority', 5)
                }
            })
    return jsonify({'error': f'Rule {rule_id} not found'}), 404


@app.route('/api/expert-stats', methods=['GET'])
def expert_stats():
    """Thống kê về Expert System"""
    if not EXPERT_SYSTEM_AVAILABLE:
        return jsonify({'error': 'Expert System not available'}), 503

    stats = get_rule_stats()
    return jsonify({
        'knowledge_base': stats,
        'engine_info': {
            'type': 'Forward Chaining with Certainty Factor',
            'cf_method': 'MYCIN-style combination',
            'conflict_resolution': 'Priority-based'
        },
        'status': 'operational'
    })


@app.route('/api/recommend-reverse', methods=['POST'])
def expert_recommend_reverse():
    """
    BACKWARD CHAINING: Từ ngân sách (target_salary) → tìm vị trí phù hợp.

    Input:
        {
            "target_salary": 150000,      # bắt buộc: mức lương mong muốn
            "company_location": "US",      # tùy chọn: ràng buộc địa lý
            "employment_type": "FT",       # tùy chọn: ràng buộc loại hợp đồng
            "remote_ratio": 100,          # tùy chọn: ràng buộc remote
            "top_k": 5                    # tùy chọn: số kết quả (mặc định 5)
        }

    Output:
        {
            "target_salary": 150000,
            "min_salary": 120000,
            "max_salary": 180000,
            "constraints": {...},
            "candidates": [
                {
                    "job_title": "Data Scientist",
                    "experience_level": "SE",
                    "company_location": "US",
                    "predicted_salary": 237000,
                    "distance_from_target": 87000,
                    "tier": "...",
                    "match_score": 0.71,
                    "explanations": [...]
                },
                ...
            ],
            "total_matches": 12,
            "evaluated": 2016,
            "search_log": [...]
        }
    """
    if not EXPERT_SYSTEM_AVAILABLE:
        return jsonify({
            'error': 'Expert System modules not available',
            'fallback': 'Use /api/recommend for forward prediction'
        }), 503

    try:
        data = request.json

        # Validate target_salary
        if 'target_salary' not in data:
            return jsonify({'error': 'Missing required field: target_salary'}), 400

        target_salary = int(data['target_salary'])
        if target_salary < 10000 or target_salary > 1000000:
            return jsonify({'error': 'target_salary must be between $10,000 and $1,000,000'}), 400

        # Optional constraints
        company_location = data.get('company_location')
        employment_type = data.get('employment_type')
        remote_ratio = data.get('remote_ratio')
        top_k = min(int(data.get('top_k', 5)), 10)  # Max 10 results

        # Run backward chaining
        result = run_backward_inference(
            target_salary=target_salary,
            company_location=company_location,
            employment_type=employment_type,
            remote_ratio=remote_ratio,
            top_k=top_k
        )

        return jsonify({
            'recommendations': result,
            'metadata': {
                'engine': 'Backward Chaining',
                'mode': 'budget_to_position',
                'constraints_applied': {
                    k: v for k, v in {
                        'company_location': company_location,
                        'employment_type': employment_type,
                        'remote_ratio': remote_ratio
                    }.items() if v is not None
                }
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/salary-range', methods=['POST'])
def expert_salary_range():
    """
    Tìm khoảng lương hợp lý cho một profile cụ thể.
    Input giống /api/recommend
    Output: khoảng lương breakdown theo tier
    """
    if not EXPERT_SYSTEM_AVAILABLE:
        return jsonify({'error': 'Expert System not available'}), 503

    try:
        data = request.json

        # Validate
        required_fields = ['job_title', 'experience_level', 'company_location']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Forward chaining để lấy tier
        facts = dict(data)
        facts['is_us'] = 1 if data['company_location'] == 'US' else 0
        if 'work_year' not in facts:
            facts['work_year'] = 2024
        if 'employment_type' not in facts:
            facts['employment_type'] = 'FT'
        if 'remote_ratio' not in facts:
            facts['remote_ratio'] = 50
        if 'company_size' not in facts:
            facts['company_size'] = 'M'

        ml_predictor = predict_with_trained_model if (analyzer and hasattr(analyzer, 'model')) else predict_with_coefficients
        recommendation = run_inference(facts, ml_predictor)
        ml = recommendation.get('ml_prediction', {})

        # Tính salary ranges theo percentiles
        pred = ml.get('prediction', 0)
        mae = ml.get('mae', 37641)

        return jsonify({
            'profile': {
                'job_title': data['job_title'],
                'experience_level': data['experience_level'],
                'company_location': data['company_location']
            },
            'salary_ranges': {
                'conservative': {'min': ml.get('confidence_lower', max(0, pred - mae)), 'max': pred},
                'target': {'min': pred, 'max': pred},
                'aggressive': {'min': pred, 'max': ml.get('confidence_upper', pred + mae)},
                'full_range': {
                    'min': max(0, pred - 2 * mae),
                    'max': pred + 2 * mae
                }
            },
            'tier': recommendation.get('tier', 'Unknown'),
            'overall_confidence': recommendation.get('overall_confidence', 0),
            'market_context': recommendation.get('explanation', {}).get('market_context', {})
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
