import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 禁用所有缓存
st.set_page_config(
    page_title="健康数据记录",
    page_icon="🏃",
    layout="wide"
)

DATA_FILE = 'my_data.csv'

# 最简单的数据操作函数
def load_data():
    """直接读取文件，不用任何缓存"""
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except:
            return pd.DataFrame(columns=['日期', '运动项目', '运动时长(分钟)', '睡眠时长(小时)', '睡眠质量', '心路历程'])
    return pd.DataFrame(columns=['日期', '运动项目', '运动时长(分钟)', '睡眠时长(小时)', '睡眠质量', '心路历程'])

def save_data(data):
    """直接保存文件"""
    try:
        data.to_csv(DATA_FILE, index=False)
        return True
    except:
        return False

st.title("🏃 健康数据记录")
st.markdown("---")

# 显示当前数据
current_data = load_data()
st.write(f"**当前记录数: {len(current_data)}**")

# 数据输入 - 使用最直接的方式
st.subheader("📝 添加新记录")

# 手动输入所有字段
date = st.text_input("日期", value=datetime.now().strftime('%Y-%m-%d'))
sport = st.text_input("运动项目", key="sport")
duration = st.text_input("运动时长(分钟)", key="duration") 
sleep_hours = st.text_input("睡眠时长(小时)", key="sleep_hours")
sleep_quality = st.text_input("睡眠质量(1-5分)", key="sleep_quality")
notes = st.text_area("心路历程", key="notes")

# 保存按钮
if st.button("💾 保存记录", type="primary", use_container_width=True):
    if not all([date, sport, duration, sleep_hours, sleep_quality]):
        st.error("请填写所有字段")
    else:
        try:
            # 创建新记录
            new_record = {
                '日期': date,
                '运动项目': sport,
                '运动时长(分钟)': float(duration),
                '睡眠时长(小时)': float(sleep_hours), 
                '睡眠质量': float(sleep_quality),
                '心路历程': notes
            }
            
            # 加载当前数据
            existing_data = load_data()
            
            # 转换为DataFrame
            new_df = pd.DataFrame([new_record])
            
            # 合并数据
            if not existing_data.empty:
                # 移除同一天的旧记录（如果存在）
                existing_data = existing_data[existing_data['日期'] != date]
                updated_data = pd.concat([existing_data, new_df], ignore_index=True)
            else:
                updated_data = new_df
            
            # 保存数据
            if save_data(updated_data):
                st.success("✅ 保存成功！")
                st.info("页面即将刷新...")
                
                # 使用JavaScript强制刷新
                st.markdown("""
                <script>
                setTimeout(function() {
                    window.location.href = window.location.href;
                }, 1500);
                </script>
                """, unsafe_allow_html=True)
            else:
                st.error("保存失败")
                
        except Exception as e:
            st.error(f"错误: {e}")

# 显示数据
st.markdown("---")
st.subheader("📊 所有记录")

data = load_data()
if not data.empty:
    st.dataframe(data, use_container_width=True)
    
    # 显示统计
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总记录", len(data))
    with col2:
        st.metric("运动天数", len(data[data['运动时长(分钟)'] > 0]))
    with col3:
        st.metric("平均睡眠", f"{data['睡眠时长(小时)'].mean():.1f}小时")
else:
    st.info("暂无数据")

# 手动刷新按钮
st.markdown("---")
if st.button("🔄 手动刷新页面", use_container_width=True):
    st.markdown("""
    <script>
    window.location.href = window.location.href;
    </script>
    """, unsafe_allow_html=True)

# 清空数据
if st.button("🗑️ 清空所有数据", use_container_width=True):
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        st.success("数据已清空")
        st.markdown("""
        <script>
        setTimeout(function() {
            window.location.href = window.location.href;
        }, 1000);
        </script>
        """, unsafe_allow_html=True)

