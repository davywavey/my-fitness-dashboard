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
                
            # 确保必要的列存在，如果缺少就添加
            required_columns = ['日期', '运动项目', '运动时长(分钟)', '睡眠时长(小时)', '睡眠质量', '心路历程']
            for col in required_columns:
                if col not in data.columns:
                    data[col] = ""  # 添加缺失的列
            
            # 转换日期格式
            try:
                data['日期'] = pd.to_datetime(data['日期'])
            except:
                data['日期'] = pd.to_datetime(data['日期'], errors='coerce')
                data = data.dropna(subset=['日期'])
            
            return data
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return pd.DataFrame()

# 智能健康分析函数（包含心路历程分析）
def get_local_health_analysis(data):
    if len(data) < 3:
        return "📊 数据还在积累中，请继续记录几天后再来查看分析结果！"
    
    recent_data = data.tail(7)
    avg_duration = recent_data['运动时长(分钟)'].mean()
    avg_sleep = recent_data['睡眠时长(小时)'].mean()
    avg_quality = recent_data['睡眠质量'].mean()
    active_days = len(recent_data[recent_data['运动时长(分钟)'] > 0])
    
    # 分析心路历程
    meaningful_notes = recent_data[recent_data['心路历程'].notna() & (recent_data['心路历程'] != "")]
    notes_analysis = ""
    if len(meaningful_notes) > 0:
        notes_count = len(meaningful_notes)
        notes_analysis = f"\n**成长记录：**\n最近{len(recent_data)}天中，你有{notes_count}天记录了心得体会，这种反思习惯很棒！"
    
    # 运动分析
    if avg_duration > 45:
        sport_analysis = "你的运动量相当充足！保持这个节奏，身体会感谢你的。"
    elif avg_duration > 25:
        sport_analysis = "运动习惯很好，建议可以适当增加一些多样性。"
    else:
        sport_analysis = "运动量还有提升空间，试着从小目标开始，比如每天多走1000步。"
    
    # 睡眠分析
    if avg_sleep >= 7 and avg_quality >= 4:
        sleep_analysis = "睡眠质量很棒！充足的休息是高效运动的基础。"
    elif avg_sleep < 6:
        sleep_analysis = f"睡眠时间稍显不足（平均{avg_sleep:.1f}小时），试着提前15分钟入睡吧。"
    else:
        sleep_analysis = "睡眠质量可以进一步优化，保持规律的作息时间会很有帮助。"
    
    analysis = f"""
**运动分析：**
最近{len(recent_data)}天中，你有{active_days}天进行了运动，平均每天{avg_duration:.1f}分钟。{sport_analysis}

**睡眠分析：**
平均每晚睡眠{avg_sleep:.1f}小时，质量评分{avg_quality:.1f}/5分。{sleep_analysis}
{notes_analysis}

继续坚持记录，你的每一条心路历程都是成长的见证！
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
    
    # 数据输入表单 - 包含心路历程！
    with st.form("new_record_form", clear_on_submit=True):
        date = st.date_input("日期", datetime.now())
        sport_type = st.selectbox("运动项目", ["跑步", "篮球", "游泳", "健身", "休息", "瑜伽", "骑行", "羽毛球"])
        duration = st.slider("运动时长（分钟）", 0, 180, 30)
        sleep_hours = st.slider("睡眠时长（小时）", 0, 12, 7)
        sleep_quality = st.slider("睡眠质量 (1-5分)", 1, 5, 4)
        
        # 心路历程输入 - 这是关键部分！
        st.markdown("---")
        st.markdown("### 💭 心路历程")
        notes = st.text_area(
            "记录今天的感受和想法", 
            placeholder="例如：今天跑步时突破了自我...\n或者：虽然很累但坚持完成了训练...\n也可以是：发现了睡眠对运动状态的影响...",
            height=100
        )
        
        submitted = st.form_submit_button("💾 保存记录", type="primary", use_container_width=True)
        
        if submitted:
            # 创建新记录
            new_record = {
                '日期': date.strftime('%Y-%m-%d'),
                '运动项目': sport_type,
                '运动时长(分钟)': duration,
                '睡眠时长(小时)': sleep_hours,
                '睡眠质量': sleep_quality,
                '心路历程': notes  # 保存心路历程
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
                
                # 显示保存的心路历程预览
                if notes.strip():
                    st.info(f"💭 已保存心路历程: {notes[:50]}..." if len(notes) > 50 else f"💭 已保存心路历程: {notes}")
                
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
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("平均运动时长", f"{data['运动时长(分钟)'].mean():.1f}分钟")
    with col2:
        st.metric("平均睡眠时长", f"{data['睡眠时长(小时)'].mean():.1f}小时")
    with col3:
        st.metric("平均睡眠质量", f"{data['睡眠质量'].mean():.1f}/5")
    with col4:
        notes_count = len(data[data['心路历程'].notna() & (data['心路历程'] != "")])
        st.metric("心路记录", f"{notes_count}条")
    
    st.markdown("---")
    
    # AI分析
    st.subheader("🤖 健康分析")
    if st.button("生成分析报告"):
        analysis = get_local_health_analysis(data)
        st.success(analysis)
    
    # 心路历程展示区 - 这是重点！
    st.markdown("---")
    st.subheader("💭 心路历程回顾")
    
    meaningful_data = data[data['心路历程'].notna() & (data['心路历程'] != "")]
    
    if len(meaningful_data) > 0:
        st.success(f"🎉 你已经有 {len(meaningful_data)} 条宝贵的心路记录！")
        
        for index, row in meaningful_data.iterrows():
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.markdown(f"**{row['日期'].strftime('%m-%d')}**")
                    st.markdown(f"*{row['运动项目']}*")
                with col2:
                    st.write(f"“{row['心路历程']}”")
                st.markdown("---")
    else:
        st.info("✨ 开始记录你的心路历程吧！这些真实的感受和想法会让你的项目更加独特和有意义。")
    
    st.markdown("---")
    
    # 数据显示
    st.subheader("📋 数据记录")
    st.dataframe(data, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
