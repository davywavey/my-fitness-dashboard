import streamlit as st
import pandas as pd

st.set_page_config(page_title="我的运动健康仪表板", layout="wide")
st.title('🏃 我的运动健康仪表板')
st.markdown("---")

# 1. 首先，尝试列出当前目录下的文件，用于调试
import os
files = os.listdir('.')
st.write("当前目录下的文件：", files)

# 2. 尝试用不同的方式读取CSV文件
try:
    # 方法1：直接读取
    st.header("尝试方法1: 直接读取")
    data = pd.read_csv('my_data.csv')
    st.success("✅ 数据文件加载成功！")
except Exception as e1:
    st.error(f"方法1失败: {e1}")
    
    try:
        # 方法2：使用绝对路径
        st.header("尝试方法2: 使用绝对路径")
        data = pd.read_csv('./my_data.csv')
        st.success("✅ 数据文件加载成功！")
    except Exception as e2:
        st.error(f"方法2失败: {e2}")
        st.stop() # 如果都失败了，就停止执行

# 3. 显示数据
st.header("📊 我的数据记录")
st.dataframe(data)

# 4. 显示图表
st.header("📈 运动时长变化")
st.line_chart(data.set_index('日期')['运动时长(分钟)'])

st.header("😴 睡眠质量趋势")
st.line_chart(data.set_index('日期')['睡眠质量'])

st.success("🎉 应用运行成功！")
