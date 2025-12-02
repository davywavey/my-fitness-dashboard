import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import datetime
# 在 my_app.py 的顶部，在现有代码之前添加这些函数：



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
    """恢复并增强您原来的智能分析逻辑"""
    if len(data) < 3:
        return "需要至少3天的数据才能生成有意义的分析报告"
    
    recent_data = data.tail(7)
    
    # ========== 1. 运动分析（恢复您原来的逻辑） ==========
    avg_duration = recent_data['运动时长(分钟)'].mean()
    active_days = len(recent_data[recent_data['运动时长(分钟)'] > 0])
    sport_variety = len(recent_data[recent_data['运动项目'] != '']['运动项目'].unique())
    
    # 您原来的运动分析逻辑
    if avg_duration > 45:
        sport_analysis = f"你的运动量相当充足！保持这个节奏对身体很有益。"
        sport_emoji = "🏆"
    elif avg_duration > 25:
        sport_analysis = "运动习惯很好，继续保持！"
        sport_emoji = "👍"
    else:
        sport_analysis = "运动量还有提升空间，建议逐步增加运动频率。"
        sport_emoji = "💪"
    
    # ========== 2. 睡眠分析（恢复您原来的逻辑） ==========
    avg_sleep = recent_data['睡眠时长(小时)'].mean()
    avg_quality = recent_data['睡眠质量'].mean()
    
    # 您原来的睡眠分析逻辑
    if avg_sleep >= 7.5 and avg_quality >= 4:
        sleep_analysis = "睡眠质量非常理想，这对运动恢复很重要。"
        sleep_emoji = "😴"
    elif avg_sleep >= 7:
        sleep_analysis = "睡眠状况良好，可以继续保持。"
        sleep_emoji = "😊"
    else:
        sleep_analysis = "睡眠时间稍显不足，建议保证7小时以上睡眠。"
        sleep_emoji = "🌙"
    
    # ========== 3. 运动多样性（恢复您原来的逻辑） ==========
    if sport_variety >= 3:
        variety_analysis = "运动项目多样，这有助于全面锻炼身体。"
        variety_emoji = "🎯"
    elif sport_variety == 2:
        variety_analysis = "可以尝试更多不同的运动项目。"
        variety_emoji = "🔁"
    else:
        variety_analysis = "建议增加运动种类，让锻炼更有趣。"
        variety_emoji = "🔄"
    
    # ========== 4. 趋势分析（恢复您原来的逻辑） ==========
    if len(data) > 5:
        trend = "数据显示你正在建立良好的健康习惯"
        trend_emoji = "📈"
    else:
        trend = "继续坚持记录，很快就会看到进步"
        trend_emoji = "🌟"
    
    # ========== 5. 新增：深度洞察 ==========
    insights = []
    
    # 洞察1：运动与睡眠关系
    if avg_duration > 30 and avg_quality >= 4:
        insights.append("💡 发现：您的充足运动似乎对睡眠质量有积极影响")
    
    # 洞察2：规律性评估
    consistency_rate = active_days / 7 * 100
    if consistency_rate >= 85:
        insights.append("📅 亮点：运动习惯非常规律，保持得很好！")
    elif consistency_rate >= 60:
        insights.append("🔄 提示：运动频率可以更规律一些")
    
    # 洞察3：进步空间
    if len(data) >= 14:  # 有2周数据时
        first_half = data.head(7)['运动时长(分钟)'].mean()
        second_half = data.tail(7)['运动时长(分钟)'].mean()
        if second_half > first_half * 1.2:
            insights.append("🚀 进步：最近一周运动量有明显提升！")
    
    # ========== 6. 生成完整报告 ==========
    analysis = f"""
{sport_emoji} **运动分析**
最近{len(recent_data)}天中，你有{active_days}天进行了运动，平均每天{avg_duration:.1f}分钟。{sport_analysis}

{sleep_emoji} **睡眠分析**
平均每晚睡眠{avg_sleep:.1f}小时，质量评分{avg_quality:.1f}/5分。{sleep_analysis}

{variety_emoji} **运动多样性**
你进行了{sport_variety}种不同的运动。{variety_analysis}

{trend_emoji} **总体趋势**
{trend}。建议继续保持记录，观察长期变化。

🔍 **深度洞察**
{chr(10).join(f"• {insight}" for insight in insights) if insights else "• 继续记录，系统会发现更多个性化洞察"}

🎯 **个性化建议**
{'🏃 尝试新的运动项目，让锻炼更有趣' if sport_variety < 3 else ''}
{'🌜 建立规律的睡眠时间表' if avg_sleep < 7 else ''}
{'📝 多记录心路历程，反思运动感受' if '心路历程' in recent_data.columns and len(recent_data[recent_data['心路历程'] != '']) < 3 else ''}
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


