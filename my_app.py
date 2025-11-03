import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime

# ============= 页面配置 =============
st.set_page_config(page_title="健康数据记录系统", page_icon="🏃", layout="wide")

# ============= OpenRouter 设置 =============
import json
import requests

def analyze_health_data(new_record, all_data, model_name):
    """
    使用 OpenRouter 模型对健康数据进行中文分析（最终版）
    """
    if not OPENROUTER_API_KEY:
        return "⚠️ 未检测到 OpenRouter API Key，请在 Streamlit Secrets 中设置。"

    prompt = f"""
你是一位专业健康顾问。
以下是用户今天的健康记录：
{new_record.to_dict(orient='records')}

历史数据如下（最近5天）：
{all_data.tail(5).to_dict(orient='records')}

请用简洁自然的中文分析并输出以下内容：
1️⃣ 对当天运动和睡眠的评价；
2️⃣ 是否出现变化或趋势；
3️⃣ 改进建议；
4️⃣ 最后一行写一句鼓励语。
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://my-fitness-dashboard.streamlit.app/",
        "X-Title": "健康数据分析AI",
        "Content-Type": "application/json; charset=utf-8"
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "你是一名专业健康分析师，请用清晰的中文输出。"},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        # ✅ 关键区别：我们让 requests 直接处理 json，而不是手动 encode
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,  # 👈 让 requests 自动编码为 UTF-8 JSON
            timeout=60
        )
        res.encoding = "utf-8"

        if res.status_code == 200:
            result = res.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            return f"⚠️ AI 分析出错：{res.status_code}\n{res.text}"

    except Exception as e:
        return f"⚠️ 网络或接口错误：{e}"



# ============= 数据文件配置 =============
DATA_FILE = "my_data.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except Exception:
            return pd.DataFrame()
    else:
        return pd.DataFrame()

def save_data(data):
    try:
        data.to_csv(DATA_FILE, index=False)
        return True
    except Exception:
        return False

# ============= 主页面逻辑 =============
st.title("🏃 健康数据记录系统")
st.markdown("---")

data = load_data()
st.write(f"**当前已有 {len(data)} 条记录**")

# 模型选择下拉框
model_name = st.selectbox(
    "🤖 选择AI模型（推荐 gpt-4o-mini 或 llama-3）",
    ["gpt-4o-mini", "meta-llama/llama-3-8b-instruct", "mistralai/mixtral-8x7b"],
    index=0
)

# 表单输入
st.subheader("📝 添加新记录")

with st.form("input_form"):
    date = st.text_input("日期 (格式: 2024-01-01)", value=datetime.now().strftime('%Y-%m-%d'))
    sport = st.text_input("运动项目", placeholder="跑步、篮球等")
    duration = st.text_input("运动时长(分钟)", placeholder="30、45等")
    sleep_hours = st.text_input("睡眠时长(小时)", placeholder="7.5、8等")
    sleep_quality = st.text_input("睡眠质量(1-5分)", placeholder="1-5的数字")
    notes = st.text_area("今日心得", placeholder="记录你的感受...")

    submit = st.form_submit_button("💾 保存并分析")

    if submit:
        if not all([date, sport, duration, sleep_hours, sleep_quality]):
            st.error("请填写所有必填字段。")
        else:
            try:
                new_record = pd.DataFrame({
                    '日期': [date],
                    '运动项目': [sport],
                    '运动时长(分钟)': [float(duration)],
                    '睡眠时长(小时)': [float(sleep_hours)],
                    '睡眠质量': [float(sleep_quality)],
                    '心路历程': [notes]
                })

                if not data.empty and date in data['日期'].tolist():
                    data = data[data['日期'] != date]
                    st.warning("⚠️ 已更新该日期的记录")

                updated_data = pd.concat([data, new_record], ignore_index=True)

                if save_data(updated_data):
                    st.success("✅ 记录保存成功！")

                    # AI 分析
                    with st.spinner("🤖 AI 正在分析中，请稍候..."):
                        ai_result = analyze_health_data(new_record, updated_data, model_name)

                    st.markdown("### 🤖 AI 分析结果")
                    st.write(ai_result)
                else:
                    st.error("保存失败，请重试。")
            except Exception as e:
                st.error(f"错误: {e}")

st.markdown("---")
st.subheader("📊 当前所有记录")

data = load_data()
if not data.empty:
    st.dataframe(data, use_container_width=True)
else:
    st.info("暂无数据。")







