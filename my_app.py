import streamlit as st
import pandas as pd
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

DATA_FILE = 'my_data.csv'

# 数据操作函数
def load_data():
    """直接读取文件"""
    if os.path.exists(DATA_FILE):
        try:
            data = pd.read_csv(DATA_FILE)
            # 确保日期列存在
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

# OpenRouter AI分析函数
def get_ai_health_analysis(data):
    """使用OpenRouter进行健康分析"""
    if len(data) < 3:
        return "需要至少3天的数据才能生成有意义的分析报告"
    
    # 准备数据摘要
    recent_data = data.tail(7)
    
    summary = f"""
用户健康数据摘要（最近{len(recent_data)}天）：

运动数据：
- 运动天数：{len(recent_data[recent_data['运动时长(分钟)'] > 0])}天
- 平均运动时长：{recent_data['运动时长(分钟)'].mean():.1f}分钟
- 主要运动类型：{recent_data[recent_data['运动项目'] != '']['运动项目'].mode().iloc[0] if len(recent_data[recent_data['运动项目'] != '']) > 0 else '多样'}

睡眠数据：
- 平均睡眠时长：{recent_data['睡眠时长(小时)'].mean():.1f}小时
- 平均睡眠质量：{recent_data['睡眠质量'].mean():.1f}/5分
"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_API_KEY}"
    }

    payload = {
        "model": "google/gemini-pro-1.5",
        "messages": [
            {
                "role": "system",
                "content": "你是一个专业且充满关怀的健康顾问。基于用户提供的健康数据，提供个性化分析和实用建议。用温暖、鼓励的语气，突出进步亮点，指出改进空间，提供具体可行的建议。"
            },
            {
                "role": "user", 
                "content": f"{summary}\n请基于以上健康数据，为我提供个性化的健康分析和改进建议。"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"AI分析暂时不可用 (状态码: {response.status_code})"
    except Exception as e:
        return f"AI分析服务暂时不可用: {str(e)}"

# 快速健康建议
def get_quick_tip():
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
                "content": "用一句话提供简洁实用的健康建议。"
            },
            {
                "role": "user",
                "content": "给我一个今天的健康小贴士。"
            }
        ],
        "temperature": 0.8,
        "max_tokens": 50
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

st.title("🏃 AI健康分析平台")
st.markdown("---")

# 显示当前数据
current_data = load_data()
st.write(f"**当前记录数: {len(current_data)}**")

# 数据输入 - 使用表单来避免刷新问题
st.subheader("📝 添加新记录")

with st.form("data_form", clear_on_submit=True):
    # 手动输入所有字段
    date = st.text_input("日期*", value=datetime.now().strftime('%Y-%m-%d'))
    sport = st.text_input("运动项目*", placeholder="跑步、篮球等")
    duration = st.text_input("运动时长(分钟)*", placeholder="30、45等") 
    sleep_hours = st.text_input("睡眠时长(小时)*", placeholder="7.5、8等")
    sleep_quality = st.text_input("睡眠质量(1-5分)*", placeholder="1-5的数字")
    notes = st.text_area("心路历程", placeholder="记录今天的感受和想法...")
    
    # 保存按钮在表单内
    submitted = st.form_submit_button("💾 保存记录", type="primary", use_container_width=True)
    
    if submitted:
        # 检查必填字段
        missing_fields = []
        if not date.strip():
            missing_fields.append("日期")
        if not sport.strip():
            missing_fields.append("运动项目")
        if not duration.strip():
            missing_fields.append("运动时长")
        if not sleep_hours.strip():
            missing_fields.append("睡眠时长")
        if not sleep_quality.strip():
            missing_fields.append("睡眠质量")
        
        if missing_fields:
            st.error(f"请填写以下必填字段: {', '.join(missing_fields)}")
        else:
            try:
                # 验证数字格式
                duration_val = float(duration)
                sleep_hours_val = float(sleep_hours)
                sleep_quality_val = float(sleep_quality)
                
                if sleep_quality_val < 1 or sleep_quality_val > 5:
                    st.error("睡眠质量必须在1-5之间")
                else:
                    # 创建新记录
                    new_record = {
                        '日期': date.strip(),
                        '运动项目': sport.strip(),
                        '运动时长(分钟)': duration_val,
                        '睡眠时长(小时)': sleep_hours_val, 
                        '睡眠质量': sleep_quality_val,
                        '心路历程': notes.strip()
                    }
                    
                    # 加载当前数据
                    existing_data = load_data()
                    
                    # 转换为DataFrame
                    new_df = pd.DataFrame([new_record])
                    
                    # 合并数据
                    if not existing_data.empty:
                        # 移除同一天的旧记录（如果存在）
                        existing_dates = existing_data['日期'].astype(str).tolist()
                        if date.strip() in existing_dates:
                            existing_data = existing_data[existing_data['日期'].astype(str) != date.strip()]
                            st.warning("已更新该日期的记录")
                        
                        updated_data = pd.concat([existing_data, new_df], ignore_index=True)
                    else:
                        updated_data = new_df
                    
                    # 保存数据
                    if save_data(updated_data):
                        st.success("✅ 保存成功！")
                        st.balloons()  # 庆祝动画
                        
            except ValueError:
                st.error("请确保运动时长、睡眠时长和睡眠质量都是有效的数字")
            except Exception as e:
                st.error(f"保存失败: {str(e)}")

# AI分析功能
st.markdown("---")
st.subheader("🤖 AI健康分析")

# 快速小贴士
if st.button("💡 获取今日健康小贴士"):
    with st.spinner("获取小贴士中..."):
        tip = get_quick_tip()
        st.success(tip)

# 深度分析
if len(current_data) >= 3:
    if st.button("🔍 生成深度健康报告", type="secondary"):
        with st.spinner("AI正在深度分析您的健康数据..."):
            analysis = get_ai_health_analysis(current_data)
            st.session_state.ai_analysis = analysis
    
    if 'ai_analysis' in st.session_state:
        st.info(st.session_state.ai_analysis)
else:
    st.info("📊 需要至少3天数据才能生成AI分析报告")

# 显示数据
st.markdown("---")
st.subheader("📋 所有记录")

data = load_data()
if not data.empty:
    # 确保日期列显示正确
    display_data = data.copy()
    st.dataframe(display_data, use_container_width=True, hide_index=True)
    
    # 显示统计
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

# 手动刷新按钮
st.markdown("---")
if st.button("🔄 手动刷新数据", use_container_width=True):
    st.rerun()

# 清空数据
if st.button("🗑️ 清空所有数据", use_container_width=True):
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        st.success("数据已清空")
        st.rerun()
    else:
        st.info("没有数据可清空")

