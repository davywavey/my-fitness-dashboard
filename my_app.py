import json
import requests

# ✅ 你的 OpenRouter API Key（从 https://openrouter.ai/keys 获取）
OPENROUTER_API_KEY = "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"

def analyze_with_openrouter(payload):
    """调用 OpenRouter 分析 API"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json; charset=utf-8",
        "HTTP-Referer": "https://localhost",
        "X-Title": "My Fitness Dashboard"
    }

    try:
        # ✅ 关键：确保中文不乱码
        data_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        # ✅ 发送请求
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=data_bytes,
            timeout=60
        )

        res.encoding = "utf-8"

        # ✅ 正常返回
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"].strip()

        # ❌ 授权错误（API key 不对）
        elif res.status_code == 401:
            return "❌ 授权错误：请检查你的 API Key 是否填写正确。"

        # ❌ 其他网络错误
        else:
            return f"⚠️ 网络或接口错误：{res.status_code}\n{res.text}"

    except Exception as e:
        # 捕获异常
        return f"❗ 发生异常：{e}"






