import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# 页面设置
st.set_page_config(
    page_title="AI健康数据分析中心",
    page_icon="🏃",
    layout="wide"
)

# 数据文件路径
DATA_FILE = 'my_data.csv'

# 智能健康分析函数（本地版，无需API）
def get_local_health_analysis(data):
    """基于规则生成个性化健康分析"""
    
    if len(data) < 3:
        return "📊 数据还在积累中，请继续记录几天后再来查看分析结果！"
    
    # 分析最近7天数据
    recent_data = data.tail(7)
    
    # 计算关键指标
    avg_duration = recent_data['运动时长(分钟)'].mean()
    avg_sleep = recent_data['睡眠时长(小时)'].mean()
    avg_quality = recent_data['睡眠质量'].mean()
    active_days = len(recent_data[recent_data['运动时长(分钟)'] > 0])
    unique_sports = len(recent_data['运动项目'].unique())
    
    # 运动分析
    if avg_duration > 45:
        sport_analysis = "你的运动量相当充足！保持这个节奏，身体会感谢你的。"
    elif avg_duration > 25:
        sport_analysis = "运动习惯很好，建议可以适当增加一些多样性。"
    else:
        sport_analysis = "运动量还有提升空间，试着从小目标开始，比如每天多走1000步。"
    
    # 睡眠分析
    if avg_sleep >= 7 and avg_quality >= 4:
        sleep_analysis = "睡眠质量很棒！充足的休息是高效运动的基础。"
    elif avg_sleep < 6:
        sleep_analysis = f"睡眠时间稍显不足（平均{avg_sleep:.1f}小时），试着提前15分钟入睡吧。"
    else:
        sleep_analysis = "睡眠质量可以进一步优化，保持规律的作息时间会很有帮助。"
    
    # 生成个性化建议
    suggestions = []
    if unique_sports < 3:
        suggestions.append("💡 建议尝试不同运动项目，让锻炼更有趣")
    if avg_quality < 4:
        suggestions.append("🌙 睡前1小时避免使用电子设备，提升睡眠质量")
    if active_days < 4:
        suggestions.append("🚶 即使不进行正式运动，也可以多散步活动")
    
    suggestions_text = "\n".join(suggestions) if suggestions else "🎉 继续保持当前的健康生活习惯！"
    
    # 综合评估
    if active_days >= 5 and avg_quality >= 4:
        status = "🏆 优秀！你的运动睡眠平衡做得很好"
    elif active_days >= 3:
        status = "👍 良好！继续保持这个积极的生活方式"
    else:
        status = "💪 加油！从小改变开始，建立健康习惯"
    
    # 生成个性化分析报告
    analysis = f"""{status}

**运动分析：**
最近{len(recent_data)}天中，你有{active_days}天进行了运动，平均每天{avg_duration:.1f}分钟。{sport_analysis}

**睡眠分析：**
平均每晚睡眠{avg_sleep:.1f}小时，质量评分{avg_quality:.1f}/5分。{sleep_analysis}

**个性化建议：**
{suggestions_text}

继续记录，观察自己的进步轨迹！
"""
    
    return analysis

# 在侧边栏配置
with st.sidebar:
    st.title("🔧 操作中心")
    
    st.markdown("---")
    st.markdown("### 添加新记录")
    
    # 实时数据输入表单
    with st.form("new_record_form"):
        st.markdown("**记录今日数据**")
        date = st.date_input("日期", datetime.now())
        sport_type = st.selectbox("运动项目", ["跑步", "篮球", "游泳", "健身", "骑行", "休息", "羽毛球", "瑜伽"])
        duration = st.slider("运动时长（分钟）", 0, 180, 30)
        sleep_hours = st.number_input("睡眠时长（小时）", min_value=0.0, max_value=12.0, value=7.0, step=0.5)
        sleep_quality = st.slider("睡眠质量 (1-5分)", 1, 5, 4)
        notes = st.text_area("今日心得（可选）")
        
        submitted = st.form_submit_button("💾 保存记录", type="primary")
        
        if submitted:
            # 保存新记录
            new_data = {
                '日期': [date.strftime('%Y-%m-%d')],
                '运动项目': [sport_type],
                '运动时长(分钟)': [duration],
                '睡眠时长(小时)': [sleep_hours],
                '睡眠质量': [sleep_quality],
                '心得': [notes]
            }
            
            new_df = pd.DataFrame(new_data)
            
            try:
                # 读取现有数据
                if os.path.exists(DATA_FILE):
                    existing_df = pd.read_csv(DATA_FILE)
                    updated_df = pd.concat([existing_df, new_df], ignore_index=True)
                else:
                    updated_df = new_df
                
                # 保存到CSV文件
                updated_df.to_csv(DATA_FILE, index=False)
                st.success("✅ 数据保存成功！")
                
                # 清除缓存，强制重新加载数据
                st.cache_data.clear()
                
            except Exception as e:
                st.error(f"保存失败: {e}")

# 加载数据
@st.cache_data
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            data = pd.read_csv(DATA_FILE)
            data['日期'] = pd.to_datetime(data['日期'])
            return data
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return pd.DataFrame()

# 主应用界面
def main():
    st.title("🏃 智能健康数据分析中心")
    st.markdown("---")
    
    data = load_data()
    
    if data.empty:
        st.info("📝 暂无数据，请在侧边栏添加你的第一条健康记录！")
        return
    
    # 第一行：核心指标
    st.subheader("📊 健康指标总览")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_duration = data['运动时长(分钟)'].mean()
        st.metric("平均运动时长", f"{avg_duration:.1f}分钟")
    
    with col2:
        avg_sleep = data['睡眠时长(小时)'].mean()
        st.metric("平均睡眠时长", f"{avg_sleep:.1f}小时")
    
    with col3:
        avg_quality = data['睡眠质量'].mean()
        st.metric("平均睡眠质量", f"{avg_quality:.1f}/5")
    
    with col4:
        active_days = len(data[data['运动时长(分钟)'] > 0])
        st.metric("运动天数", f"{active_days}/{len(data)}")
    
    st.markdown("---")
    
    # 第二行：智能健康分析
    st.subheader("🤖 智能健康分析")
    
    analysis_col1, analysis_col2 = st.columns([3, 1])
    
    with analysis_col2:
        if st.button("🔄 生成健康分析", type="primary"):
            with st.spinner("正在分析您的健康数据..."):
                ai_analysis = get_local_health_analysis(data)
                st.session_state.ai_analysis = ai_analysis
    
    with analysis_col1:
        if 'ai_analysis' in st.session_state:
            st.success(st.session_state.ai_analysis)
        else:
            st.info("点击按钮生成个性化健康分析报告")
    
    st.markdown("---")
    
    # 第三行：图表展示
    if len(data) > 1:
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("运动时长趋势")
            fig = px.line(data, x='日期', y='运动时长(分钟)', 
                         title='运动时长变化趋势', markers=True)
            st.plotly_chart(fig, use_container_width=True)
        
        with col_right:
            st.subheader("睡眠质量分析")
            fig = px.bar(data, x='日期', y='睡眠质量',
                        title='睡眠质量评分', color='睡眠质量',
                        color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)
    
    # 第四行：数据表格
    st.markdown("---")
    st.subheader("📋 历史数据记录")
    
    # 添加数据筛选功能
    col1, col2 = st.columns(2)
    with col1:
        selected_sport = st.selectbox("筛选运动项目", ["全部"] + list(data['运动项目'].unique()))
    with col2:
        date_range = st.selectbox("时间范围", ["全部", "最近7天", "最近30天"])
    
    # 应用筛选
    filtered_data = data.copy()
    if selected_sport != "全部":
        filtered_data = filtered_data[filtered_data['运动项目'] == selected_sport]
    if date_range == "最近7天":
        filtered_data = filtered_data[filtered_data['日期'] >= (datetime.now() - pd.Timedelta(days=7))]
    elif date_range == "最近30天":
        filtered_data = filtered_data[filtered_data['日期'] >= (datetime.now() - pd.Timedelta(days=30))]
    
    st.dataframe(filtered_data, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
