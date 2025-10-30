import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 页面设置 - 这必须是最先执行的命令
st.set_page_config(
    page_title="我的健康数据中心",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载数据
@st.cache_data
def load_data():
    try:
        data = pd.read_csv('my_data.csv')
        data['日期'] = pd.to_datetime(data['日期'])
        return data
    except:
        st.error("无法加载数据文件")
        return None

# 应用主界面
def main():
    # 侧边栏 - 导航和说明
    with st.sidebar:
        st.title("🏃 健康仪表板")
        st.markdown("---")
        st.markdown("### 关于")
        st.info("""
        这是一个个人健康数据追踪系统，用于分析：
        - 运动表现趋势
        - 睡眠质量影响  
        - 生活习惯关联
        """)
        
        # 数据统计
        st.markdown("### 📊 数据概览")
        data = load_data()
        if data is not None:
            st.metric("总记录数", len(data))
            st.metric("运动天数", len(data[data['运动时长(分钟)'] > 0]))
    
    # 主内容区
    st.title("🏃 我的个人健康数据中心")
    st.markdown("---")
    
    if data is None:
        return
    
    # 第一行：关键指标卡片
    st.subheader("📈 核心指标")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_duration = data['运动时长(分钟)'].mean()
        st.metric("平均运动时长", f"{avg_duration:.1f} 分钟")
    
    with col2:
        avg_sleep = data['睡眠时长(小时)'].mean()
        st.metric("平均睡眠时长", f"{avg_sleep:.1f} 小时")
    
    with col3:
        avg_quality = data['睡眠质量'].mean()
        st.metric("平均睡眠质量", f"{avg_quality:.1f}/5")
    
    with col4:
        favorite_sport = data[data['运动项目'] != '休息']['运动项目'].mode()
        favorite_sport = favorite_sport[0] if len(favorite_sport) > 0 else "无"
        st.metric("最爱运动", favorite_sport)
    
    st.markdown("---")
    
    # 第二行：图表
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("运动时长趋势")
        if len(data) > 1:
            fig = px.line(
                data, x='日期', y='运动时长(分钟)',
                markers=True,
                color_discrete_sequence=['#1f77b4']
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("需要更多数据来生成趋势图")
    
    with col_right:
        st.subheader("睡眠质量分析")
        if len(data) > 1:
            fig = px.bar(
                data, x='日期', y='睡眠质量',
                color_discrete_sequence=['#2ca02c']
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("需要更多数据来生成分析图")
    
    # 第三行：详细数据表
    st.markdown("---")
    st.subheader("📋 详细数据记录")
    
    # 添加一些交互功能
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        sport_filter = st.selectbox("筛选运动项目", ["全部"] + list(data['运动项目'].unique()))
    
    with col_filter2:
        min_duration = st.slider("最小运动时长", 0, 120, 0)
    
    # 应用筛选
    filtered_data = data.copy()
    if sport_filter != "全部":
        filtered_data = filtered_data[filtered_data['运动项目'] == sport_filter]
    filtered_data = filtered_data[filtered_data['运动时长(分钟)'] >= min_duration]
    
    # 显示表格
    st.dataframe(
        filtered_data,
        use_container_width=True,
        hide_index=True
    )

if __name__ == "__main__":
    main()
