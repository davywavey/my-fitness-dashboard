# backend/health_analyzer.py

# 健康小贴士库 - 这是您之前写的，很有价值！
HEALTH_TIPS = [
    "💡 记得运动前热身，运动后拉伸",
    "💧 保持充足水分摄入，运动时尤其重要",
    "🌙 睡前1小时避免使用电子设备",
    "🥗 均衡饮食是健康生活的基础",
    "🚶 即使不运动，也多站起来活动"
]

def get_health_tip():
    """获取随机健康小贴士"""
    import random
    return random.choice(HEALTH_TIPS)

def analyze_sport_data(data):
    """分析运动数据 - 这是您的核心算法！"""
    if len(data) < 3:
        return "需要更多数据来生成分析"
    
    # 计算平均运动时长
    avg_duration = data['运动时长(分钟)'].mean()
    
    # 您的独特分析逻辑
    if avg_duration > 45:
        return "🏆 您的运动量很充足！继续保持！"
    elif avg_duration > 25:
        return "👍 运动习惯很好，继续保持！"
    else:
        return "💪 建议逐步增加运动频率"

def analyze_sleep_data(data):
    """分析睡眠数据 - 这也是您的核心算法！"""
    avg_sleep = data['睡眠时长(小时)'].mean()
    avg_quality = data['睡眠质量'].mean()
    
    # 您的睡眠分析逻辑
    if avg_sleep >= 7.5 and avg_quality >= 4:
        return "😴 睡眠质量非常理想！"
    elif avg_sleep >= 7:
        return "😊 睡眠状况良好"
    else:
        return "🌙 建议保证7小时以上睡眠"
