from flask import Flask, request, jsonify
from flask_cors import CORS
from models import FitnessData
from health_analyzer import generate_per_run_ai_summary, get_health_tip
import json

app = Flask(__name__)
CORS(app)

fitness_data = FitnessData()

@app.route('/api/health/records', methods=['GET'])
def get_records():
    data = fitness_data.get_all_data()
    return jsonify({"data": data, "count": len(data)})

@app.route('/api/health/records', methods=['POST'])
def add_record():
    record = request.json
    required_fields = ['日期', '运动项目', '运动时长', '睡眠时长']
    for field in required_fields:
        if field not in record:
            return jsonify({"error": f"缺少必填字段: {field}"}), 400
    try:
        saved_record = fitness_data.add_record(record)
        return jsonify({"message": "记录添加成功", "data": saved_record})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health/analysis', methods=['GET'])
def get_analysis():
    analysis = fitness_data.get_recent_analysis()
    return jsonify(analysis)

@app.route('/api/health/analysis/per_run', methods=['GET'])
def get_per_run_analysis():
    data = fitness_data.get_all_data()
    if not data:
        return jsonify({"error": "暂无数据"})
    
    per_run_summaries = []
    for record in data:
        summary = generate_per_run_ai_summary(record, data)
        per_run_summaries.append({
            "id": record.get("id"),
            "日期": record.get("日期"),
            "运动项目": record.get("运动项目"),
            "summary": summary
        })
    return jsonify(per_run_summaries)

@app.route('/api/health/tips', methods=['GET'])
def get_tips():
    tip = get_health_tip()
    return jsonify({"tip": tip})

@app.route('/api/health/stats', methods=['GET'])
def get_stats():
    data = fitness_data.get_all_data()
    analysis = fitness_data.get_recent_analysis()
    return jsonify({
        "total_records": len(data),
        "analysis": analysis
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

