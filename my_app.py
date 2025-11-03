import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
import os
from datetime import datetime

# 页面设置
st.set_page_config(
    page_title="AI健康分析平台",
    page_icon="🏃",
    layout="wide"
)

# API配置
OPENROUTER_API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# 数据文件路径
DATA_FILE = 'my_data.csv'

# 加载数据
def load_data():
    try:
        if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
            data = pd.read_csv(DATA_FILE)
            data['日期'] = pd.to_datetime(data['日期'], errors='coerce')
            data = data.dropna(subset=['日期'])
            return data
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return pd.DataFrame()

# 保存数据
def save_data(data):
    try:
        data.to_csv(DATA_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"保存失败: {e}")
        return False

# OpenRouter AI健康分析
def get_ai_health_analysis(data):
    """使用OpenRouter API进行深度健康分析"""
    
    if len(data) < 3:
        return "需要至少3天的数据才能生成有意义的分析报告"
    
    # 准备详细的数据摘要
    recent_data = data.tail(14)  # 分析最近两周
    
    summary = f"""
用户健康数据摘要（最近{len(recent_data)}天）：

**运动数据：**
- 运动天数：{len(recent_data[recent_data['运动时长(分钟)'] > 0])}天
- 平均运动时长：{recent_data['运动时长(分钟)'].mean():.1f}分钟
- 运动频率：{len(recent_data[recent_data['运动时长(分钟)'] > 0]) / len(recent_data) * 100:.1f}%
- 主要运动类型：{recent_data[recent_data['运动项目'] != '']['运动项目'].mode().iloc[0] if len(recent_data[recent_data['运动项目'] != '']) > 0 else '多样'}

**睡眠数据：**
- 平均睡眠时长：{recent_data['睡眠时长(小时)'].mean():.1f}小时
- 平均睡眠质量：{recent_data['睡眠质量'].mean():.1f}/5分
- 睡眠稳定性：标准差 {recent_data['睡眠时长(小时)'].std():.1f}小时

**趋势分析：**
- 运动时长趋势：{'上升' if len(recent_data) > 1 and recent_data['运动时长(分钟)'].iloc[-1] > recent_data['运动时长(分钟)'].iloc[0] else '下降或稳定'}
- 睡眠质量趋势：{'改善' if len(recent_data) > 1 and recent_data['睡眠质量'].iloc[-1] > recent_data['睡眠质量'].iloc[0] else '需要关注'}
"""

    # 如果有心路历程，也加入分析
    meaningful_notes = recent_data[recent_data['心路历程'].notna() & (recent_data['心路历程'] != "")]
    if len(meaningful_notes) > 0:
        summary += f"\n**心路历程记录：** {len(meaningful_notes)}条个人反思记录"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_API_KEY}"
    }

    payload = {
        "model": "google/gemini-pro-1.5",  # 可以选择其他模型如 anthropic/claude-3-sonnet
        "messages": [
            {
                "role": "system",
                "content": """你是一个专业、细心且充满关怀的健康顾问。请基于用户提供的详细健康数据，提供深度、个性化的分析报告。要求：

1. 用温暖、专业且鼓励的语气直接对用户说
2. 突出用户的进步和亮点
3. 指出需要关注的方面
4. 提供具体、可操作的建议
5. 结合运动、睡眠、心理状态进行综合分析
6. 用自然的段落表达，避免列表格式

请生成300-400字的详细分析报告。"""
            },
            {
                "role": "user",
                "content": f"{summary}\n\n请基于以上详细健康数据，为我提供深度的个性化健康分析和可行的改进建议。"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"API请求失败 (状态码: {response.status_code})\n错误信息: {response.text}"
            
    except requests.exceptions.Timeout:
        return "请求超时，请稍后重试"
    except Exception as e:
        return f"请求异常: {str(e)}"

# 快速健康建议函数
def get_quick_health_tips(data):
    """获取快速健康小贴士"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_API_KEY}"
    }

    payload = {
        "model": "google/gemini-pro-1.5",
        "messages": [
            {
                "role": "system",
                "content": "你是一个专业的健康顾问，请用1-2句话提供简洁实用的健康建议。"
            },
            {
                "role": "user",
                "content": "基于一般健康原则，给我一个今天的健康小贴士。"
            }
        ],
        "temperature": 0.8,
        "max_tokens": 100
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return "保持积极心态，健康从心开始！"
    except:
        return "今天也要记得运动和充足睡眠哦！"

# 主应用
def main():
    st.title("🏃 AI健康分析平台")
    st.markdown("---")
    
    # 加载数据
    data = load_data()
    
    # 侧边栏
    with st.sidebar:
        st.header("🔧 操作面板")
        
        # 显示数据状态
        st.info(f"📊 当前记录数: {len(data)}")
        
        # 快速建议
        if st.button("💡 今日健康小贴士"):
            tip = get_quick_health_tips(data)
            st.success(tip)
        
        st.markdown("---")
        st.header("📝 添加记录")
        
        # 简化版数据输入
        with st.form("quick_input"):
            date = st.date_input("日期", datetime.now())
            sport = st.text_input("运动项目", placeholder="跑步、瑜伽等")
            duration = st.text_input("运动时长(分钟)", placeholder="30")
            sleep = st.text_input("睡眠时长(小时)", placeholder="7.5")
            quality = st.text_input("睡眠质量(1-5)", placeholder="4")
            notes = st.text_area("今日心得", placeholder="今天的感受...")
            
            if st.form_submit_button("💾 快速保存"):
                if all([sport, duration, sleep, quality]):
                    try:
                        new_record = pd.DataFrame([{
                            '日期': date.strftime('%Y-%m-%d'),
                            '运动项目': sport,
                            '运动时长(分钟)': float(duration),
                            '睡眠时长(小时)': float(sleep),
                            '睡眠质量': float(quality),
                            '心路历程': notes
                        }])
                        
                        if not data.empty:
                            updated_data = pd.concat([data, new_record], ignore_index=True)
                        else:
                            updated_data = new_record
                            
                        if save_data(updated_data):
                            st.success("保存成功！")
                            st.rerun()
                    except Exception as e:
                        st.error(f"保存失败: {e}")
    
    # 主内容区
    if data.empty:
        st.info("📝 暂无数据，请在侧边栏添加健康记录")
        return
    
    # 核心指标
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
    
    # AI健康分析
    st.subheader("🤖 AI深度健康分析")
    
    if len(data) >= 3:
        if st.button("🔍 生成深度健康报告", type="primary"):
            with st.spinner("AI正在深度分析您的健康数据..."):
                analysis = get_ai_health_analysis(data)
                st.session_state.ai_analysis = analysis
        
        if 'ai_analysis' in st.session_state:
            st.success(st.session_state.ai_analysis)
    else:
        st.info("📊 需要至少3天数据才能生成AI分析报告")
    
    st.markdown("---")
    
    # 数据可视化
    if len(data) > 1:
        st.subheader("📈 趋势分析")
        
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.line(data, x='日期', y='运动时长(分钟)', 
                          title='运动时长趋势', markers=True)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.line(data, x='日期', y='睡眠质量',
                          title='睡眠质量趋势', markers=True)
            st.plotly_chart(fig2, use_container_width=True)
    
    # 数据表格
    st.markdown("---")
    st.subheader("📋 详细数据记录")
    st.dataframe(data, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()

