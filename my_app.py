import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
from datetime import datetime, timedelta

# 页面设置
st.set_page_config(
    page_title="AI健康数据分析中心",
    page_icon="🏃",
    layout="wide"
)

# 在侧边栏配置API密钥 - 安全提示：正式部署时应使用环境变量
with st.sidebar:
    st.title("🔑 API配置")
    st.markdown("**首次使用请配置：**")
    api_key = st.text_input("请输入您的智谱AI API密钥", type="password")
    if api_key:
        st.success("✅ API密钥已设置")
    st.markdown("---")
    st.info("""
    **新功能：AI健康周报**
    - 自动分析运动睡眠趋势
    - 提供个性化健康建议
    - 识别潜在健康风险
    """)

# 加载数据
@st.cache_data
def load_data():
    try:
        data = pd.read_csv('my_data.csv')
        data['日期'] = pd.to_datetime(data['日期'])
        return data
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return None

# AI健康分析函数
def get_ai_health_insight(data, api_key):
    """调用大模型API获取健康分析"""
    
    # 准备数据摘要
    recent_data = data.tail(7)  # 最近7天数据
    
    summary = f"""
    用户最近7天的健康数据统计：
    - 运动天数：{len(recent_data[recent_data['运动时长(分钟)'] > 0])}天
    - 平均运动时长：{recent_data['运动时长(分钟)'].mean():.1f}分钟
    - 平均睡眠时长：{recent_data['睡眠时长(小时)'].mean():.1f}小时  
    - 平均睡眠质量：{recent_data['睡眠质量'].mean():.1f}/5分
    - 主要运动类型：{recent_data[recent_data['运动项目'] != '休息']['运动项目'].mode().iloc[0] if len(recent_data[recent_data['运动项目'] != '休息']) > 0 else '无'}
    """
    
    # 构建API请求
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "glm-4",  # 使用GLM-4模型
        "messages": [
            {
                "role": "system",
                "content": "你是一个专业、细心且充满关怀的健康顾问。请用亲切、鼓励的语气，基于用户提供的健康数据，提供一段不超过250字的个性化分析和建议。重点突出：1.积极的进步 2.可操作的改进建议 3.温暖的鼓励。直接对用户说，不要用列表。"
            },
            {
                "role": "user",
                "content": f"{summary}\n\n请基于以上健康数据，为我提供个性化的分析和建议。"
            }
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ AI分析暂时不可用: {str(e)}"

# 主应用界面
def main():
    st.title("🏃 AI健康数据分析中心")
    st.markdown("---")
    
    data = load_data()
    if data is None:
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
    
    # 第二行：AI健康周报
    st.subheader("🤖 AI健康周报")
    
    if not api_key:
        st.warning("⚠️ 请在侧边栏输入API密钥以启用AI分析功能")
    else:
        ai_col1, ai_col2 = st.columns([3, 1])
        with ai_col2:
            if st.button("🔄 生成健康分析", type="primary"):
                with st.spinner("AI正在分析您的健康数据..."):
                    ai_advice = get_ai_health_insight(data, api_key)
                    st.session_state.ai_advice = ai_advice
        
        with ai_col1:
            if 'ai_advice' in st.session_state:
                st.success(st.session_state.ai_advice)
            else:
                st.info("点击按钮生成您的个性化AI健康分析报告")
    
    st.markdown("---")
    
    # 第三行：图表展示
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("运动时长趋势")
        if len(data) > 1:
            fig = px.line(data, x='日期', y='运动时长(分钟)', 
                         title='近期运动时长变化', markers=True)
            st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.subheader("睡眠质量分析")
        if len(data) > 1:
            fig = px.bar(data, x='日期', y='睡眠质量',
                        title='睡眠质量评分', color='睡眠质量',
                        color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)
    
    # 第四行：数据表格
    st.markdown("---")
    st.subheader("📋 详细数据记录")
    st.dataframe(data, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
