import streamlit as st
import requests
import json
from datetime import date

# -------------------------------
# ✅ 1️⃣ 你的 OpenRouter API key（从 https://openrouter.ai/keys 获取）
OPENROUTER_API_KEY = "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"
# -------------------------------
# ✅ 2️⃣ 调用 OpenRouter 的安全函数
def analyze_with_openrouter(payload):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json; charset=utf-8",
        "HTTP-Referer": "https://localhost",
        "X-Title": "My Fitness Dashboard"
    }

    # ✅ 防止中文乱码错误
    data_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=data_bytes,
            timeout=60
        )
        res.encoding = "utf-8"

        # ✅ 如果服务器正常返回
        if res.status_code == 200:
            try:
                return res.json()["choices"][0]["message"]["content"].strip()
            except Exception:
                return "⚠️ 返回格式异常，请检查模型或 API key 设置。"
        # ✅ 如果是权限或额度问题
        elif res.status_code == 401:
            return "❌ 授权错误：请检查你的 API Key 是否填写正确。"
        elif res.status_code == 429:
            return "⚠️ 配额不足：请前往 OpenRouter 检查额度。"
        elif res.status_code == 404:
            return "⚠️ 模型未找到：请确认你填写的模型名称是否正确。"
        else:
            return f"⚠️ 未知错误 ({res.status_code})：{res.text}"

    except requests.exceptions.Timeout:
        return "⚠️ 请求超时，请检查网络或稍后再试。"
    except Exception as e:
        return f"⚠️ 网络或接口错误：{e}"

# -------------------------------
# ✅ 3️⃣ Streamlit 页面
st.title("🏃‍♀️ 健康运动与睡眠记录仪表板")

with st.form("health_form"):
    today = st.date_input("日期", date.today())
    exercise = st.text_input("运动项目（如：跑步、篮球等）")
    duration = st.text_input("运动时长（分钟）")
    sleep_hours = st.text_input("睡眠时长（小时）")
    sleep_quality = st.text_input("睡眠质量（1-5分）")
    feeling = st.text_area("今日心情")

    submitted = st.form_submit_button("💾 保存记录")

if submitted:
    st.success("✅ 记录保存成功！")

    # ✅ 构造 AI 输入
    user_input = (
        f"今天是{today}，运动项目是{exercise}，时长{duration}分钟；"
        f"睡眠{sleep_hours}小时，质量{sleep_quality}分。"
        f"心情：{feeling}。请帮我生成一个简短的运动和睡眠分析报告。"
    )

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "你是一名健康教练，负责分析用户的运动与睡眠情况"},
            {"role": "user", "content": user_input}
        ]
    }

    st.info("⏳ AI 正在分析中，请稍候...")
    analysis = analyze_with_openrouter(payload)
    st.markdown("### 😄 AI 分析结果")
    st.write(analysis)


