import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import datetime
# 在 my_app.py 的顶部，在现有代码之前添加这些函数：

def analyze_sport_data(data):
    """分析运动数据 - 临时版本"""
    if len(data) < 1:
        return "暂无运动数据"
    
    try:
        avg_duration = data['运动时长(分钟)'].mean()
        
        if avg_duration > 45:
            return "🏆 您的运动量很充足！继续保持！"
        elif avg_duration > 25:
            return "👍 运动习惯很好，继续保持！"
        else:
            return "💪 建议逐步增加运动频率"
    except:
        return "运动数据分析中..."

def analyze_sleep_data(data):
    """分析睡眠数据 - 临时版本"""
    if len(data) < 1:
        return "暂无睡眠数据"
    
    try:
        avg_sleep = data['睡眠时长(小时)'].mean()
        
        if avg_sleep >= 7.5:
            return "😴 睡眠质量非常理想！"
        elif avg_sleep >= 7:
            return "😊 睡眠状况良好"
        else:
            return "🌙 建议保证7小时以上睡眠"
    except:
        return "睡眠数据分析中..."

def get_health_tip():
    """获取健康小贴士 - 临时版本"""
    import random
    HEALTH_TIPS = [
        "💡 记得运动前热身，运动后拉伸",
        "💧 保持充足水分摄入，运动时尤其重要",
        "🌙 睡前1小时避免使用电子设备",
        "🥗 均衡饮食是健康生活的基础",
        "🚶 即使不运动，也多站起来活动"
    ]
    return random.choice(HEALTH_TIPS)

# 您现有的其他代码保持不动...
# 您现有的其他代码保持不动...
# 您现有的其他代码保持不动...

# 页面设置
st.set_page_config(
    page_title="健康数据分析平台",
    page_icon="🏃",
    layout="wide"
)

DATA_FILE = 'my_data.csv'

# 数据操作函数
def load_data():
    """直接读取文件"""
    if os.path.exists(DATA_FILE):
        try:
            data = pd.read_csv(DATA_FILE)
            if '日期' not in data.columns:
                data['日期'] = datetime.now().strftime('%Y-%m-%d')
            return data
        except:
            return pd.DataFrame(columns=['日期', '运动项目', '运动时长(分钟)', '睡眠时长(小时)', '睡眠质量', '心路历程'])
    return pd.DataFrame(columns=['日期', '运动项目', '运动时长(分钟)', '睡眠时长(小时)', '睡眠质量', '心路历程'])

def save_data(data):
    """直接保存文件"""
    try:
        data.to_csv(DATA_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"保存失败: {e}")
        return False
def get_local_health_analysis(data):
    """升级版智能健康分析"""
    if len(data) < 3:
        return "需要至少3天的数据才能生成有意义的分析报告"
    
    recent_data = data.tail(7)
    
    # ========== 1. 更精细的运动分析 ==========
    avg_duration = recent_data['运动时长(分钟)'].mean()
    active_days = len(recent_data[recent_data['运动时长(分钟)'] > 0])
    sport_variety = len(recent_data[recent_data['运动项目'] != '']['运动项目'].unique())
    
    # 运动评分系统
    duration_score = min(avg_duration / 45 * 100, 100)  # 45分钟为满分
    consistency_score = (active_days / 7) * 100
    variety_score = min(sport_variety * 25, 100)  # 4种运动为满分
    
    total_sport_score = (duration_score * 0.5 + consistency_score * 0.3 + variety_score * 0.2)
    
    if total_sport_score > 85:
        sport_analysis = f"🏆 运动达人！综合评分{total_sport_score:.0f}分"
    elif total_sport_score > 70:
        sport_analysis = f"👍 习惯良好！综合评分{total_sport_score:.0f}分"
    elif total_sport_score > 50:
        sport_analysis = f"💪 稳步进步！综合评分{total_sport_score:.0f}分"
    else:
        sport_analysis = f"📈 起步阶段！综合评分{total_sport_score:.0f}分"
    
    # ========== 2. 睡眠深度分析 ==========
    avg_sleep = recent_data['睡眠时长(小时)'].mean()
    avg_quality = recent_data['睡眠质量'].mean()
    
    # 睡眠评分
    sleep_duration_score = min(avg_sleep / 8 * 100, 100)  # 8小时为满分
    sleep_quality_score = (avg_quality / 5) * 100
    
    total_sleep_score = (sleep_duration_score * 0.6 + sleep_quality_score * 0.4)
    
    if total_sleep_score > 85:
        sleep_analysis = f"😴 完美睡眠！评分{total_sleep_score:.0f}分"
    elif total_sleep_score > 70:
        sleep_analysis = f"😊 睡眠良好！评分{total_sleep_score:.0f}分"
    elif total_sleep_score > 50:
        sleep_analysis = f"🌙 基本达标！评分{total_sleep_score:.0f}分"
    else:
        sleep_analysis = f"⚠️ 需要改善！评分{total_sleep_score:.0f}分"
    
    # ========== 3. 个性化建议 ==========
    suggestions = []
    
    if avg_duration < 30:
        suggestions.append("🎯 目标：逐步增加运动时长至每天30分钟")
    
    if sport_variety < 2:
        suggestions.append("🔄 建议：尝试不同的运动项目，如游泳、瑜伽")
    
    if avg_sleep < 7:
        suggestions.append("🌜 提醒：保证7小时以上睡眠有助于恢复")
    
    if avg_quality < 3:
        suggestions.append("🛌 改善：建立规律的睡前仪式，如阅读、冥想")
    
    # 如果有记录心路历程，分析情绪趋势
    if '心路历程' in recent_data.columns and recent_data['心路历程'].notna().any():
        notes_count = len(recent_data[recent_data['心路历程'].notna()])
        suggestions.append(f"📝 您记录了{notes_count}次心路历程，这对反思很有帮助")
    
    # ========== 4. 生成完整报告 ==========
    analysis = f"""
🏃 **运动分析报告**
最近7天运动数据：
• 平均时长：{avg_duration:.1f}分钟
• 运动天数：{active_days}天
• 运动种类：{sport_variety}种
{sport_analysis}

😴 **睡眠分析报告**  
平均睡眠：{avg_sleep:.1f}小时 | 质量：{avg_quality:.1f}/5分
{sleep_analysis}

💡 **个性化建议**
{chr(10).join(f"• {s}" for s in suggestions) if suggestions else "• 继续保持良好习惯！"}

📊 **综合健康指数：{(total_sport_score * 0.6 + total_sleep_score * 0.4):.0f}/100分**
"""
    
    return analysis
# 健康小贴士库
HEALTH_TIPS = [
    "💡 记得运动前热身，运动后拉伸",
    "💧 保持充足水分摄入，运动时尤其重要",
    "🌙 睡前1小时避免使用电子设备",
    "🥗 均衡饮食是健康生活的基础",
    "🚶 即使不运动，也多站起来活动",
    "😊 保持积极心态，健康从心开始",
    "📅 建立规律的运动习惯",
    "🌞 早晨的阳光有助于调节生物钟",
    "🧘 尝试冥想或深呼吸来放松",
    "🎯 设定小目标，逐步实现大目标"
]

def get_health_tip():
    """从本地库获取健康小贴士"""
    import random
    return random.choice(HEALTH_TIPS)

st.title("🏃 智能健康分析平台")
st.markdown("---")

# 显示当前数据
current_data = load_data()
st.write(f"**当前记录数: {len(current_data)}**")

# 数据输入
st.subheader("📝 添加新记录")

with st.form("data_form", clear_on_submit=True):
    date = st.text_input("日期*", value=datetime.now().strftime('%Y-%m-%d'))
    sport = st.text_input("运动项目*", placeholder="跑步、篮球等")
    duration = st.text_input("运动时长(分钟)*", placeholder="30、45等") 
    sleep_hours = st.text_input("睡眠时长(小时)*", placeholder="7.5、8等")
    sleep_quality = st.text_input("睡眠质量(1-5分)*", placeholder="1-5的数字")
    notes = st.text_area("心路历程", placeholder="记录今天的感受和想法...")
    
    submitted = st.form_submit_button("💾 保存记录", type="primary", use_container_width=True)
    
    if submitted:
        missing_fields = []
        if not date.strip(): missing_fields.append("日期")
        if not sport.strip(): missing_fields.append("运动项目")
        if not duration.strip(): missing_fields.append("运动时长")
        if not sleep_hours.strip(): missing_fields.append("睡眠时长")
        if not sleep_quality.strip(): missing_fields.append("睡眠质量")
        
        if missing_fields:
            st.error(f"请填写以下必填字段: {', '.join(missing_fields)}")
        else:
            try:
                duration_val = float(duration)
                sleep_hours_val = float(sleep_hours)
                sleep_quality_val = float(sleep_quality)
                
                if sleep_quality_val < 1 or sleep_quality_val > 5:
                    st.error("睡眠质量必须在1-5之间")
                else:
                    new_record = {
                        '日期': date.strip(),
                        '运动项目': sport.strip(),
                        '运动时长(分钟)': duration_val,
                        '睡眠时长(小时)': sleep_hours_val, 
                        '睡眠质量': sleep_quality_val,
                        '心路历程': notes.strip()
                    }
                    
                    existing_data = load_data()
                    new_df = pd.DataFrame([new_record])
                    
                    if not existing_data.empty:
                        existing_dates = existing_data['日期'].astype(str).tolist()
                        if date.strip() in existing_dates:
                            existing_data = existing_data[existing_data['日期'].astype(str) != date.strip()]
                            st.warning("已更新该日期的记录")
                        
                        updated_data = pd.concat([existing_data, new_df], ignore_index=True)
                    else:
                        updated_data = new_df
                    
                    if save_data(updated_data):
                        st.success("✅ 保存成功！")
                        st.balloons()
                        
            except ValueError:
                st.error("请确保运动时长、睡眠时长和睡眠质量都是有效的数字")
            except Exception as e:
                st.error(f"保存失败: {str(e)}")

# 智能分析功能
st.markdown("---")
st.subheader("🤖 智能健康分析")

# 健康小贴士
if st.button("💡 获取健康小贴士"):
    tip = get_health_tip()
    st.success(tip)

# 深度分析
if len(current_data) >= 3:
    if st.button("🔍 生成健康报告", type="secondary"):
        with st.spinner("正在分析您的健康数据..."):
            # 使用新的后端分析函数！
            sport_analysis = analyze_sport_data(current_data)
            sleep_analysis = analyze_sleep_data(current_data)
            # 组合显示结果
            analysis = f"""
🏃 **运动分析**
{sport_analysis}

😴 **睡眠分析**  
{sleep_analysis}
"""
            st.session_state.health_analysis = analysis
    
    if 'health_analysis' in st.session_state:
        st.info(st.session_state.health_analysis)
else:
    st.info("📊 需要至少3天数据才能生成分析报告")

# 数据显示
st.markdown("---")
st.subheader("📋 所有记录")

data = load_data()
if not data.empty:
    display_data = data.copy()
    st.dataframe(display_data, use_container_width=True, hide_index=True)
    
    st.subheader("📊 数据统计")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总记录数", len(data))
    with col2:
        active_days = len(data[data['运动时长(分钟)'] > 0])
        st.metric("运动天数", active_days)
    with col3:
        avg_sleep = data['睡眠时长(小时)'].mean()
        st.metric("平均睡眠", f"{avg_sleep:.1f}小时")
    with col4:
        avg_quality = data['睡眠质量'].mean()
        st.metric("睡眠质量", f"{avg_quality:.1f}/5")
else:
    st.info("暂无数据，请在上面添加你的第一条记录")

# 管理功能
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 刷新数据", use_container_width=True):
        st.rerun()
with col2:
    if st.button("🗑️ 清空数据", use_container_width=True):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
            st.success("数据已清空")
            st.rerun()
            # 在my_app.py顶部添加这些函数

def get_health_tip():
    import random
    HEALTH_TIPS = [
        "💡 记得运动前热身，运动后拉伸",
        "💧 保持充足水分摄入，运动时尤其重要",
        "🌙 睡前1小时避免使用电子设备"
    ]
    return random.choice(HEALTH_TIPS)

def analyze_sport_data(data):
    """分析运动数据"""
    if len(data) < 1:
        return "暂无运动数据"
    
    avg_duration = data['运动时长(分钟)'].mean()
    
    if avg_duration > 45:
        return "🏆 您的运动量很充足！继续保持！"
    elif avg_duration > 25:
        return "👍 运动习惯很好，继续保持！"
    else:
        return "💪 建议逐步增加运动频率"

def analyze_sleep_data(data):
    """分析睡眠数据"""
    if len(data) < 1:
        return "暂无睡眠数据"
    
    avg_sleep = data['睡眠时长(小时)'].mean()
    avg_quality = data['睡眠质量'].mean()
    
    if avg_sleep >= 7.5 and avg_quality >= 4:
        return "😴 睡眠质量非常理想！"
    elif avg_sleep >= 7:
        return "😊 睡眠状况良好"
    else:
        return "🌙 建议保证7小时以上睡眠"







