import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# 页面设置
st.set_page_config(
    page_title="健康数据分析中心",
    page_icon="🏃",
    layout="wide"
)

# 数据文件路径
DATA_FILE = 'my_data.csv'

# 修复数据加载函数
def load_data():
    """安全加载数据，处理各种异常"""
    try:
        if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
            # 读取数据
            data = pd.read_csv(DATA_FILE)
            
            # 检查数据是否为空
            if data.empty:
                return pd.DataFrame()
                
            # 确保必要的列存在
            required_columns = ['日期', '运动项目', '运动时长(分钟)', '睡眠时长(小时)', '睡眠质量']
            for col in required_columns:
                if col not in data.columns:
                    st.error(f"数据文件缺少必要列: {col}")
                    return pd.DataFrame()
            
            # 转换日期格式
            try:
                data['日期'] = pd.to_datetime(data['日期'])
            except:
                # 如果日期转换失败，尝试修复格式
                st.warning("日期格式需要修复...")
                data['日期'] = pd.to_datetime(data['日期'], errors='coerce')
                # 删除无法解析的行
                data = data.dropna(subset=['日期'])
            
            return data
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return pd.DataFrame()

# 智能健康分析函数
def get_local_health_analysis(data):
    if len(data) < 3:
        return "📊 数据还在积累中，请继续记录几天后再来查看分析结果！"
    
    recent_data = data.tail(7)
    avg_duration = recent_data['运动时长(分钟)'].mean()
    avg_sleep = recent_data['睡眠时长(小时)'].mean()
    avg_quality = recent_data['睡眠质量'].mean()
    active_days = len(recent_data[recent_data['运动时长(分钟)'] > 0])
    
    # 运动分析
    if avg_duration > 45:
        sport_analysis = "你的运动量相当充足！"
    elif avg_duration > 25:
        sport_analysis = "运动习惯很好！"
    else:
        sport_analysis = "运动量还有提升空间。"
    
    # 睡眠分析
    if avg_sleep >= 7 and avg_quality >= 4:
        sleep_analysis = "睡眠质量很棒！"
    elif avg_sleep < 6:
        sleep_analysis = f"睡眠时间稍显不足。"
    else:
        sleep_analysis = "睡眠质量可以进一步优化。"
    
    analysis = f"""
**运动分析：**
最近{len(recent_data)}天中，你有{active_days}天进行了运动，平均每天{avg_duration:.1f}分钟。{sport_analysis}

**睡眠分析：**
平均每晚睡眠{avg_sleep:.1f}小时，质量评分{avg_quality:.1f}/5分。{sleep_analysis}

继续坚持记录！
"""
    return analysis

# 侧边栏 - 数据输入
with st.sidebar:
    st.title("🔧 操作中心")
    
    # 数据管理
    st.markdown("### 数据管理")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 刷新数据"):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        if st.button("🗑️ 清空数据"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
                st.cache_data.clear()
                st.success("数据已清空")
                st.rerun()
    
    # 显示当前数据状态
    current_data = load_data()
    st.info(f"当前记录数: {len(current_data)}")
    
    st.markdown("---")
    st.markdown("### 添加新记录")
    
    # 数据输入表单
    with st.form("new_record_form", clear_on_submit=True):
        date = st.date_input("日期", datetime.now())
        sport_type = st.selectbox("运动项目", ["跑步", "篮球", "游泳", "健身", "休息"])
        duration = st.slider("运动时长（分钟）", 0, 180, 30)
        sleep_hours = st.slider("睡眠时长（小时）", 0, 12, 7)
        sleep_quality = st.slider("睡眠质量 (1-5分)", 1, 5, 4)
        
        submitted = st.form_submit_button("💾 保存记录", type="primary", use_container_width=True)
        
        if submitted:
            # 创建新记录
            new_record = {
                '日期': date.strftime('%Y-%m-%d'),
                '运动项目': sport_type,
                '运动时长(分钟)': duration,
                '睡眠时长(小时)': sleep_hours,
                '睡眠质量': sleep_quality,
                '心得': ''  # 可选字段
            }
            
            try:
                # 读取现有数据
                existing_data = load_data()
                
                # 创建新DataFrame
                new_df = pd.DataFrame([new_record])
                
                # 合并数据
                if not existing_data.empty:
                    # 检查是否已存在相同日期的记录
                    existing_dates = existing_data['日期'].dt.strftime('%Y-%m-%d').tolist()
                    if new_record['日期'] in existing_dates:
                        st.warning("该日期已有记录，将更新数据")
                        # 移除旧记录
                        existing_data = existing_data[existing_data['日期'].dt.strftime('%Y-%m-%d') != new_record['日期']]
                    
                    updated_data = pd.concat([existing_data, new_df], ignore_index=True)
                else:
                    updated_data = new_df
                
                # 保存数据
                updated_data.to_csv(DATA_FILE, index=False)
                st.success("✅ 记录保存成功！")
                
                # 强制刷新
                st.cache_data.clear()
                st.rerun()
                
            except Exception as e:
                st.error(f"保存失败: {str(e)}")

# 主界面
def main():
    st.title("🏃 健康数据分析中心")
    st.markdown("---")
    
    data = load_data()
    
    if data.empty:
        st.info("📝 暂无数据，请在侧边栏添加你的健康记录！")
        return
    
    # 显示数据概览
    st.success(f"✅ 已加载 {len(data)} 条记录")
    
    # 核心指标
    st.subheader("📊 健康指标")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("平均运动时长", f"{data['运动时长(分钟)'].mean():.1f}分钟")
    with col2:
        st.metric("平均睡眠时长", f"{data['睡眠时长(小时)'].mean():.1f}小时")
    with col3:
        st.metric("平均睡眠质量", f"{data['睡眠质量'].mean():.1f}/5")
    
    st.markdown("---")
    
    # AI分析
    st.subheader("🤖 健康分析")
    if st.button("生成分析报告"):
        analysis = get_local_health_analysis(data)
        st.success(analysis)
    
    st.markdown("---")
    
    # 数据显示
    st.subheader("📋 数据记录")
    st.dataframe(data, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
