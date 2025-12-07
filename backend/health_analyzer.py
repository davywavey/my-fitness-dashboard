import random
import pandas as pd

HEALTH_TIPS = [
    "💡 记得运动前热身，运动后拉伸",
    "💧 保持充足水分摄入，运动时尤其重要",
    "🌙 睡前1小时避免使用电子设备",
    "🥗 均衡饮食是健康生活的基础",
    "🚶 即使不运动，也多站起来活动"
]

def get_health_tip():
    return random.choice(HEALTH_TIPS)

def generate_per_run_ai_summary(record, all_data):
    """
    生成单条运动记录的 AI 小结。
    record: 单条记录
    all_data: 所有记录，用于计算4周平均/统计
    """
    df = pd.DataFrame(all_data)
    
    # 计算4周平均 pace
    if '运动时长' in df.columns and '运动项目' in df.columns:
        avg_duration = df['运动时长'].mean()
    else:
        avg_duration = 0

    # 简单占位逻辑，可换成 DeepSeek / OpenAI 调用
    pace = record.get('运动时长', 0)
    if pace > avg_duration:
        trend = "比过去平均稍长，注意控制运动强度"
    else:
        trend = "比过去平均稍短，表现不错"

    summary = {
        "observations": [
            f"您在{record.get('日期')}的{record.get('运动项目')}记录被保存。",
            f"运动时长: {record.get('运动时长')}分钟，{trend}",
            f"睡眠时长: {record.get('睡眠时长')}小时，睡眠质量: {record.get('睡眠质量', '未填写')}"
        ],
        "suggestions": [
            "保持规律运动，结合睡眠和饮食优化效果。",
            "可适当调整运动强度，避免疲劳积累。"
        ]
    }
    return summary
