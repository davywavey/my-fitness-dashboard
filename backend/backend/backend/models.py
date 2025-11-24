import json
import pandas as pd
from datetime import datetime, timedelta
import os

class FitnessData:
    def __init__(self):
        self.data_file = 'data/fitness_data.json'
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """确保数据文件存在"""
        os.makedirs('data', exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def get_all_data(self):
        """获取所有数据"""
        with open(self.data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def add_record(self, record):
        """添加新记录"""
        data = self.get_all_data()
        
        # 为记录添加ID和时间戳
        record['id'] = len(data) + 1
        record['created_at'] = datetime.now().isoformat()
        
        data.append(record)
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return record
    
    def get_recent_analysis(self):
        """健康分析 - 基于您原来的逻辑"""
        data = self.get_all_data()
        if not data:
            return {"error": "暂无数据"}
        
        df = pd.DataFrame(data)
        
        # 运动分析
        if '运动时长' in df.columns:
            avg_duration = df['运动时长'].mean()
            active_days = len(df[df['运动时长'] > 0])
            sport_variety = len(df['运动项目'].unique()) if '运动项目' in df.columns else 0
            
            if avg_duration > 45:
                sport_analysis = "🏆 运动量很充足！继续保持！"
            elif avg_duration > 25:
                sport_analysis = "👍 运动习惯很好！"
            else:
                sport_analysis = "💪 建议增加运动频率"
        else:
            sport_analysis = "暂无运动数据"
            avg_duration = 0
            active_days = 0
            sport_variety = 0
        
        # 睡眠分析
        if '睡眠时长' in df.columns:
            avg_sleep = df['睡眠时长'].mean()
            avg_quality = df['睡眠质量'].mean() if '睡眠质量' in df.columns else 0
            
            if avg_sleep >= 7.5 and avg_quality >= 4:
                sleep_analysis = "😴 睡眠质量非常理想！"
            elif avg_sleep >= 7:
                sleep_analysis = "😊 睡眠状况良好"
            else:
                sleep_analysis = "🌙 建议保证7小时以上睡眠"
        else:
            sleep_analysis = "暂无睡眠数据"
            avg_sleep = 0
        
        return {
            "sport_analysis": sport_analysis,
            "sleep_analysis": sleep_analysis,
            "stats": {
                "avg_duration": round(avg_duration, 1),
                "active_days": active_days,
                "sport_variety": sport_variety,
                "avg_sleep": round(avg_sleep, 1),
                "total_records": len(data)
            }
        }
