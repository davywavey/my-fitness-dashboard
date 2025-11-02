import streamlit as st
import pandas as pd
import os
from datetime import datetime
import openai

# ============= 基本设置 =============
st.set_page_config(
    page_title="健康数据记录系统",
    page_icon="🏃",
    layout="wide"
)

# 从环境变量读取 OpenAI Key
openai.api_key = os.getenv("OPENAI_API_KEY")
st.sidebar.write("🔑 OpenAI Key 已检测到" if openai.api_key else "❌ 未检测到 OpenAI Key")


# 数据文件路径
DATA_FILE = "my_data.csv"

# ============= 数据加载与保存函数 =============
def load_data():
    """读取本地 CSV 数据"""
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except Exception:
            return pd.DataFrame()
    else:
        return pd.DataFrame()

def save_data(data):
    """保存到 CSV"""
    try:
        data.to_csv(DATA_FILE, index=False)
        return True
    except Exception:
        return False

# ============= AI 分析函数 =============
from openai import OpenAI

# 初始化 OpenAI 客户端
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_health_data(new_record, all_data):
    """
    调用 OpenAI 模型，对用户健康数据进行全面分析（新版接口）
    """
    try:
        prompt = f"""
你是一名专业健康顾问。
以下是用户当天的健康记录：
{new_record.to_dict(orient='records')}

历史数据如下（最近5天）：
{all_data.tail(5).to_dict(orient='records')}

请你综合分析并回答：
1️⃣ 对当天的运动与睡眠进行简要评价；
2️⃣ 如果和过去几天有变化，说明趋势；
3️⃣ 给出改善建议；
4️⃣ 最后一句写一句鼓励性的话。

请使用简洁自然的中文表达。
"""
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ AI 分析出错：{e}"

# ============= 页面主逻辑 =============
st.title("🏃 健康数据记录系统")
st.markdown("---")

# 加载当前数据
current_data = load_data()
st.write(f"**当前已有 {len(current_data)} 条记录**")

# ============= 表单输入部分 =============
st.subheader("📝 添加新记录")

with st.form("input_form"):
    date = st.text_input("日期 (格式: 2024-01-01)", value=datetime.now().strftime('%Y-%m-%d'))
    sport = st.text_input("运动项目", placeholder="跑步、篮球等")
    duration = st.text_input("运动时长(分钟)", placeholder="30、45等")
    sleep_hours = st.text_input("睡眠时长(小时)", placeholder="7.5、8等")
    sleep_quality = st.text_input("睡眠质量(1-5分)", placeholder="1-5的数字")
    notes = st.text_area("今日心得", placeholder="记录你的感受...")

    submit = st.form_submit_button("💾 保存记录")

    if submit:
        # 验证输入
        if not all([date, sport, duration, sleep_hours, sleep_quality]):
            st.error("请填写所有必填字段")
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

                # 检查重复日期并更新
                if not current_data.empty and date in current_data['日期'].tolist():
                    current_data = current_data[current_data['日期'] != date]
                    st.warning("⚠️ 已更新该日期的记录")

                updated_data = pd.concat([current_data, new_record], ignore_index=True)

                # 保存数据
                               # 保存数据
                if save_data(updated_data):
                    st.success("✅ 记录保存成功！")

                    # 调用 AI 分析
                    with st.spinner("🤖 AI 正在分析中，请稍候..."):
                        ai_result = analyze_health_data(new_record, updated_data)

                    st.markdown("### 🤖 AI 分析结果")
                    st.write(ai_result)

                    st.info("✅ 如需更新页面，请点击下方“🔄 手动刷新页面”。")
               

                else:
                    st.error("保存失败，请重试。")

            except Exception as e:
                st.error(f"错误: {e}")

# ============= 显示数据表格 =============
st.markdown("---")
st.subheader("📊 当前所有记录")

data = load_data()
if not data.empty:
    st.dataframe(data, use_container_width=True)
else:
    st.info("暂无数据")

# ============= 操作按钮 =============
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 手动刷新页面"):
        st.rerun()

with col2:
    if st.button("🗑️ 清空所有数据"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
            st.success("数据已清空")
            st.rerun()








