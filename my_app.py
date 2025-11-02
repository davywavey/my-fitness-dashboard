import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 页面设置 - 禁用所有缓存
st.set_page_config(
    page_title="健康数据记录系统",
    page_icon="🏃",
    layout="wide"
)

# 数据文件路径
DATA_FILE = 'my_data.csv'

# 简单直接的数据加载 - 完全不用缓存
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except:
            return pd.DataFrame()
    else:
        return pd.DataFrame()

# 简单直接的数据保存
def save_data(data):
    try:
        data.to_csv(DATA_FILE, index=False)
        return True
    except:
        return False

st.title("🏃 健康数据记录系统")
st.markdown("---")

# 显示当前数据量
current_data = load_data()
st.write(f"**当前已有 {len(current_data)} 条记录**")

# 数据输入表单
st.subheader("📝 添加新记录")

with st.form("input_form"):
    # 手动输入所有字段
    date = st.text_input("日期 (格式: 2024-01-01)", value=datetime.now().strftime('%Y-%m-%d'))
    sport = st.text_input("运动项目", placeholder="跑步、篮球等")
    duration = st.text_input("运动时长(分钟)", placeholder="30、45等")
    sleep_hours = st.text_input("睡眠时长(小时)", placeholder="7.5、8等") 
    sleep_quality = st.text_input("睡眠质量(1-5分)", placeholder="1-5的数字")
    notes = st.text_area("今日心得", placeholder="记录你的感受...")
    
    # 提交按钮
    submit = st.form_submit_button("💾 保存记录")
    
    if submit:
        # 基本验证
        if not all([date, sport, duration, sleep_hours, sleep_quality]):
            st.error("请填写所有必填字段")
        else:
            try:
                # 创建新记录
                new_record = pd.DataFrame({
                    '日期': [date],
                    '运动项目': [sport],
                    '运动时长(分钟)': [float(duration)],
                    '睡眠时长(小时)': [float(sleep_hours)],
                    '睡眠质量': [float(sleep_quality)],
                    '心路历程': [notes]
                })
                
                # 合并数据
                if not current_data.empty:
                    # 检查重复日期
                    existing_dates = current_data['日期'].tolist()
                    if date in existing_dates:
                        # 删除旧记录
                        current_data = current_data[current_data['日期'] != date]
                        st.warning("已更新该日期的记录")
                    
                    updated_data = pd.concat([current_data, new_record], ignore_index=True)
                else:
                    updated_data = new_record
                
                # 保存数据
                if save_data(updated_data):
                    st.success("✅ 记录保存成功！")
                    st.info("✅ 页面将在3秒后自动刷新...")
                    
                    # 强制刷新页面
                    st.markdown("""
                    <script>
                    setTimeout(function() {
                        window.location.reload();
                    }, 3000);
                    </script>
                    """, unsafe_allow_html=True)
                else:
                    st.error("保存失败")
                    
            except Exception as e:
                st.error(f"错误: {e}")

# 显示当前所有数据
st.markdown("---")
st.subheader("📊 当前所有记录")

data = load_data()
if not data.empty:
    st.dataframe(data, use_container_width=True)
else:
    st.info("暂无数据")

# 手动刷新按钮
st.markdown("---")
if st.button("🔄 手动刷新页面"):
    st.markdown("""
    <script>
    window.location.reload();
    </script>
    """, unsafe_allow_html=True)

# 清空数据按钮
if st.button("🗑️ 清空所有数据"):
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        st.success("数据已清空")
        st.markdown("""
        <script>
        setTimeout(function() {
            window.location.reload();
        }, 1000);
        </script>
        """, unsafe_allow_html=True)
