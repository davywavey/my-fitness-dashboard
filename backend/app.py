from flask import Flask, request, jsonify
from flask_cors import CORS
from models import FitnessData
import json

app = Flask(__name__)
CORS(app)  # 允许前端跨域访问

fitness_data = FitnessData()

@app.route('/api/health/records', methods=['GET'])
def get_records():
    """获取所有健康记录"""
    data = fitness_data.get_all_data()
    return jsonify({"data": data, "count": len(data)})

@app.route('/api/health/records', methods=['POST'])
def add_record():
    """添加新的健康记录"""
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
    """获取健康分析报告"""
    analysis = fitness_data.get_recent_analysis()
    return jsonify(analysis)

@app.route('/api/health/tips', methods=['GET'])
def get_tips():
    """获取健康小贴士"""
    import random
    tips = [
        "💡 记得运动前热身，运动后拉伸",
        "💧 保持充足水分摄入，运动时尤其重要",
        "🌙 睡前1小时避免使用电子设备",
        "🥗 均衡饮食是健康生活的基础",
        "🚶 即使不运动，也多站起来活动"
    ]
    return jsonify({"tip": random.choice(tips)})

@app.route('/api/health/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    data = fitness_data.get_all_data()
    analysis = fitness_data.get_recent_analysis()
    
    return jsonify({
        "total_records": len(data),
        "analysis": analysis
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
