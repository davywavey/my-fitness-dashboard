import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
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

# 在侧边栏配置API密钥
with st.sidebar:
    st.title("🔑 配置中心")
    st.markdown("### DeepSeek API设置")
    deepseek_api_key = st.text_input("DeepSeek API密钥", type="password")
    
    st.markdown("---")
    st.markdown("### 添加新记录")
    
    # 实时数据输入表单
    with st.form("new_record_form"):
        st.markdown("**记录今日数据**")
        date = st.date_input("日期", datetime.now())
        sport_type = st.selectbox("运动项目", ["跑步", "篮球", "游泳", "健身", "骑行", "休息"])
        duration = st.slider("运动时长（分钟）", 0, 180, 30)
        sleep_hours = st.slider("睡眠时长（小时）", 0, 12, 7)
        sleep_quality = st.slider("睡眠质量 (1-5分)", 1, 5, 4)
        notes = st.text_area("今日心得（可选）")
        
        submitted = st.form_submit_button("保存记录", type="primary")
        
        if submitted:
            if not deepseek_api_key:
                st.warning("请输入DeepSeek API密钥")
            else:
                # 保存新记录
                new_data = {
                    '日期': [date.strftime('%Y-%m-%d')],
                    '运动项目': [sport_type],
                    '运动时长(分钟)': [duration],
                    '运动感受': [st.session_state.get('feeling', 3)],
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

# DeepSeek AI健康分析函数
def get_deepseek_health_analysis(data, api_key):
    """调用DeepSeek API获取健康分析"""
    
    # 准备数据摘要
    recent_data = data.tail(7)  # 最近7天数据
    
    if len(recent_data) == 0:
        return "暂无足够数据进行AI分析"
    
    summary = f"""
    用户最近{len(recent_data)}天的健康数据统计：
    - 运动天数：{len(recent_data[recent_data['运动时长(分钟)'] > 0])}天
    - 平均运动时长：{recent_data['运动时长(分钟)'].mean():.1f}分钟
    - 平均睡眠时长：{recent_data['睡眠时长(小时)'].mean():.1f}小时  
    - 平均睡眠质量：{recent_data['睡眠质量'].mean():.1f}/5分
    - 主要运动类型：{recent_data[recent_data['运动项目'] != '休息']['运动项目'].mode().iloc[0] if len(recent_data[recent_data['运动项目'] != '休息']) > 0 else '无'}
    """
    
    # DeepSeek API请求
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": """你是一个专业、细心且充满关怀的健康顾问。请基于用户提供的健康数据，提供一段200字左右的个性化分析和建议。要求：
                1. 用亲切、鼓励的语气直接对用户说
                2. 突出积极的进步和亮点
                3. 提供具体可操作的建议
                4. 表达温暖的关怀和鼓励
                不要用列表格式，用自然的段落表达。"""
            },
            {
                "role": "user", 
                "content": f"{summary}\n\n请基于以上健康数据，为我提供个性化的健康分析和建议。"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"❌ API请求失败 (状态码: {response.status_code})\n错误信息: {response.text}"
            
    except requests.exceptions.Timeout:
        return "❌ 请求超时，请稍后重试"
    except Exception as e:
        return f"❌ 请求异常: {str(e)}"

# 主应用界面
def main():
    st.title("🏃 AI健康数据分析中心 (DeepSeek版)")
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
    
    # 第二行：AI健康分析
    st.subheader("🤖 DeepSeek健康分析")
    
    if not deepseek_api_key:
        st.warning("⚠️ 请在侧边栏输入DeepSeek API密钥以启用AI分析功能")
    else:
        analysis_col1, analysis_col2 = st.columns([3, 1])
        
        with analysis_col2:
            if st.button("🔄 生成健康分析", type="primary"):
                with st.spinner("DeepSeek正在分析您的健康数据..."):
                    ai_analysis = get_deepseek_health_analysis(data, deepseek_api_key)
                    st.session_state.ai_analysis = ai_analysis
        
        with analysis_col1:
            if 'ai_analysis' in st.session_state:
                st.success(st.session_state.ai_analysis)
            else:
                st.info("点击按钮生成个性化AI健康分析报告")
    
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
    st.dataframe(data, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
