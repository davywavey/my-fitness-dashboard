import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
import numpy as np

# 页面设置
st.set_page_config(
    page_title="健康数据管理系统",
    page_icon="🏃",
    layout="wide"
)

# 数据文件路径
DATA_FILE = 'my_data.csv'

# 初始化数据列
def initialize_columns():
    return ['日期', '运动项目', '运动时长(分钟)', '睡眠时长(小时)', '睡眠质量', '心路历程']

# 加载数据
def load_data():
    try:
        if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
            data = pd.read_csv(DATA_FILE)
            # 确保所有列都存在
            required_columns = initialize_columns()
            for col in required_columns:
                if col not in data.columns:
                    data[col] = ""
            
            # 转换日期
            data['日期'] = pd.to_datetime(data['日期'], errors='coerce')
            data = data.dropna(subset=['日期'])
            return data
        else:
            return pd.DataFrame(columns=initialize_columns())
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return pd.DataFrame(columns=initialize_columns())

# 保存数据
def save_data(data):
    try:
        data.to_csv(DATA_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"保存失败: {e}")
        return False

# 智能分析函数
def get_health_analysis(data):
    if len(data) < 3:
        return "📊 需要至少3天数据才能生成分析报告"
    
    recent_data = data.tail(7)
    
    analysis = f"""
**数据分析报告（最近{len(recent_data)}天）**

**运动情况：**
- 运动天数：{len(recent_data[recent_data['运动时长(分钟)'] > 0])}天
- 平均时长：{recent_data['运动时长(分钟)'].mean():.1f}分钟/天
- 主要项目：{recent_data[recent_data['运动项目'] != '']['运动项目'].mode().iloc[0] if len(recent_data[recent_data['运动项目'] != '']) > 0 else '暂无'}

**睡眠情况：**
- 平均时长：{recent_data['睡眠时长(小时)'].mean():.1f}小时/晚
- 睡眠质量：{recent_data['睡眠质量'].mean():.1f}/5分

**心路历程：**
- 已记录：{len(recent_data[recent_data['心路历程'] != ''])}条感悟
"""
    return analysis

# 主应用
def main():
    st.title("🏃 个人健康数据管理系统")
    st.markdown("---")
    
    # 加载数据
    data = load_data()
    
    # 选项卡布局
    tab1, tab2, tab3 = st.tabs(["📝 数据录入", "📊 数据分析", "✏️ 数据管理"])
    
    with tab1:
        st.subheader("手动录入数据")
        st.info("💡 所有字段都支持手动输入，输入完成后点击保存")
        
        with st.form("data_input_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                # 手动输入日期
                date_input = st.text_input(
                    "📅 日期 (格式: 2024-01-01)",
                    value=datetime.now().strftime('%Y-%m-%d'),
                    help="请输入日期，格式：年-月-日"
                )
                
                # 手动输入运动项目
                sport_input = st.text_input(
                    "🏀 运动项目",
                    placeholder="例如：跑步、篮球、游泳、健身...",
                    help="请输入运动项目名称"
                )
                
                # 手动输入运动时长
                duration_input = st.text_input(
                    "⏱️ 运动时长 (分钟)",
                    placeholder="例如：30、45、60...",
                    help="请输入运动时长，单位：分钟"
                )
            
            with col2:
                # 手动输入睡眠时长
                sleep_hours_input = st.text_input(
                    "😴 睡眠时长 (小时)",
                    placeholder="例如：7.5、8、6.5...",
                    help="请输入睡眠时长，单位：小时"
                )
                
                # 手动输入睡眠质量
                sleep_quality_input = st.text_input(
                    "⭐ 睡眠质量 (1-5分)",
                    placeholder="1-5之间的数字",
                    help="请输入睡眠质量评分，1分最差，5分最好"
                )
                
                # 心路历程
                notes_input = st.text_area(
                    "💭 心路历程",
                    placeholder="记录今天的感受、想法或突破...",
                    height=100,
                    help="这是展现你个人特色的重要部分！"
                )
            
            # 提交按钮
            submitted = st.form_submit_button("💾 保存记录", type="primary", use_container_width=True)
            
            if submitted:
                # 数据验证和转换
                try:
                    # 验证日期
                    date_val = pd.to_datetime(date_input)
                    
                    # 验证数字字段
                    duration_val = float(duration_input) if duration_input.strip() else 0
                    sleep_hours_val = float(sleep_hours_input) if sleep_hours_input.strip() else 0
                    sleep_quality_val = float(sleep_quality_input) if sleep_quality_input.strip() else 0
                    
                    if sleep_quality_val < 1 or sleep_quality_val > 5:
                        st.error("睡眠质量必须在1-5之间")
                        return
                    
                    # 创建新记录
                    new_record = {
                        '日期': date_val.strftime('%Y-%m-%d'),
                        '运动项目': sport_input.strip(),
                        '运动时长(分钟)': duration_val,
                        '睡眠时长(小时)': sleep_hours_val,
                        '睡眠质量': sleep_quality_val,
                        '心路历程': notes_input.strip()
                    }
                    
                    # 添加到数据
                    new_df = pd.DataFrame([new_record])
                    if not data.empty:
                        # 检查重复日期
                        existing_dates = data['日期'].dt.strftime('%Y-%m-%d').tolist()
                        if new_record['日期'] in existing_dates:
                            # 更新现有记录
                            data = data[data['日期'].dt.strftime('%Y-%m-%d') != new_record['日期']]
                        
                        updated_data = pd.concat([data, new_df], ignore_index=True)
                    else:
                        updated_data = new_df
                    
                    # 保存数据
                    if save_data(updated_data):
                        st.success("✅ 记录保存成功！")
                        st.rerun()
                    
                except ValueError as e:
                    st.error("❌ 数据格式错误！请检查数字字段是否正确")
                except Exception as e:
                    st.error(f"❌ 保存失败: {e}")
    
    with tab2:
        st.subheader("数据分析与可视化")
        
        if data.empty:
            st.info("暂无数据，请在数据录入页面添加记录")
        else:
            # 显示统计信息
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("总记录数", len(data))
            with col2:
                st.metric("运动天数", len(data[data['运动时长(分钟)'] > 0]))
            with col3:
                st.metric("平均睡眠", f"{data['睡眠时长(小时)'].mean():.1f}小时")
            with col4:
                st.metric("心路记录", len(data[data['心路历程'] != '']))
            
            # 生成分析报告
            if st.button("生成分析报告"):
                analysis = get_health_analysis(data)
                st.success(analysis)
            
            # 图表展示
            if len(data) > 1:
                col1, col2 = st.columns(2)
                with col1:
                    fig1 = px.line(data, x='日期', y='运动时长(分钟)', title='运动时长趋势')
                    st.plotly_chart(fig1, use_container_width=True)
                with col2:
                    fig2 = px.bar(data, x='日期', y='睡眠质量', title='睡眠质量变化')
                    st.plotly_chart(fig2, use_container_width=True)
            
            # 心路历程展示
            st.subheader("💭 心路历程回顾")
            meaningful_data = data[data['心路历程'] != '']
            if len(meaningful_data) > 0:
                for _, row in meaningful_data.iterrows():
                    with st.expander(f"{row['日期'].strftime('%Y-%m-%d')} - {row['运动项目']}"):
                        st.write(f"**感悟：** {row['心路历程']}")
            else:
                st.info("暂无心路历程记录")
    
    with tab3:
        st.subheader("数据管理")
        
        if data.empty:
            st.info("暂无数据")
        else:
            # 显示完整数据表格
            st.write("### 所有数据记录")
            st.dataframe(data, use_container_width=True, hide_index=True)
            
            # 数据操作
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 刷新数据", use_container_width=True):
                    st.rerun()
            
            with col2:
                if st.button("📥 导出数据", use_container_width=True):
                    csv = data.to_csv(index=False)
                    st.download_button(
                        label="下载CSV文件",
                        data=csv,
                        file_name="health_data.csv",
                        mime="text/csv"
                    )
            
            with col3:
                if st.button("🗑️ 清空所有数据", use_container_width=True):
                    if os.path.exists(DATA_FILE):
                        os.remove(DATA_FILE)
                        st.success("数据已清空")
                        st.rerun()
            
            # 编辑功能
            st.write("### 编辑数据")
            st.info("要编辑数据，请先清空然后重新录入，或直接修改GitHub上的CSV文件")

if __name__ == "__main__":
    main()
