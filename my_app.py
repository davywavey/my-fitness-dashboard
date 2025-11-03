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
import openai
import os

# 用环境变量读取 key（在 Streamlit secrets 或系统环境变量中配置）
openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_health_data(today_data, history_data):
    """
    用 AI 分析用户的运动与睡眠情况，并生成中文总结。
    today_data: dict - 当天的输入（例如 {"date": "2025-11-03", "运动": "跑步", "时长": "40", ...}）
    history_data: list - 过去几天的记录，用于比较趋势
    """

    # 拼接提示内容
    user_prompt = f"""
    以下是用户今天的健康记录：
    {today_data}

    以下是过去五天的健康记录：
    {history_data}

    请用中文总结用户今天的运动与睡眠情况，指出趋势（例如是否变好），并给出简短的建议和一句鼓励语。
    要求：
    1. 内容清晰有条理，用编号分段。
    2. 不要输出英文或其他语言。
    3. 语气积极、自然。
    """

    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai.api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 免费或低价模型
            messages=[
                {"role": "system", "content": "你是一位健康与生活方式分析师，请用简洁自然的中文回答。"},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=600
        )

        result = response.choices[0].message.content.strip()
        return result

    except Exception as e:
        return f"⚠️ AI 分析出错： {str(e)}"



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












