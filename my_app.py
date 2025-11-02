import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# 页面设置
st.set_page_config(
    page_title="健康数据管理系统",
    page_icon="🏃",
    layout="wide"
)

# 数据文件路径
DATA_FILE = 'my_data.csv'

# 初始化数据函数
def init_data():
    return pd.DataFrame(columns=['日期', '运动项目', '运动时长(分钟)', '睡眠时长(小时)', '睡眠质量', '心路历程'])

# 加载数据 - 不使用缓存，确保实时性
def load_data():
    try:
        if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
            data = pd.read_csv(DATA_FILE)
            # 确保所有列都存在
            required_columns = ['日期', '运动项目', '运动时长(分钟)', '睡眠时长(小时)', '睡眠质量', '心路历程']
            for col in required_columns:
                if col not in data.columns:
                    data[col] = ""
            
            # 转换日期
            data['日期'] = pd.to_datetime(data['日期'], errors='coerce')
            data = data.dropna(subset=['日期'])
            return data
        else:
            return init_data()
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return init_data()

# 保存数据
def save_data(data):
    try:
        data.to_csv(DATA_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"保存失败: {e}")
        return False

# 主应用
def main():
    st.title("🏃 个人健康数据管理系统")
    st.markdown("---")
    
    # 加载数据 - 不使用缓存
    data = load_data()
    
    # 在侧边栏显示当前数据状态
    with st.sidebar:
        st.subheader("📊 数据状态")
        st.write(f"当前记录数: **{len(data)}**")
        
        if st.button("🔄 强制刷新数据", use_container_width=True):
            # 清除可能的缓存并刷新
            if 'data' in st.session_state:
                del st.session_state['data']
            st.rerun()
        
        if st.button("🗑️ 清空所有数据", use_container_width=True):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
                st.success("数据已清空")
                st.rerun()
    
    # 主内容区 - 数据录入
    st.subheader("📝 数据录入")
    st.info("💡 所有字段都支持手动输入，保存后可立即继续输入下一条")
    
    # 使用session_state来跟踪表单状态
    if 'form_submitted' not in st.session_state:
        st.session_state.form_submitted = False
    
    # 数据录入表单
    with st.form("data_input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            date_input = st.text_input(
                "📅 日期 (格式: 2024-01-01)",
                value=datetime.now().strftime('%Y-%m-%d'),
                help="请输入日期，格式：年-月-日"
            )
            
            sport_input = st.text_input(
                "🏀 运动项目",
                placeholder="例如：跑步、篮球、游泳...",
                help="请输入运动项目名称"
            )
            
            duration_input = st.text_input(
                "⏱️ 运动时长 (分钟)",
                placeholder="例如：30、45、60...",
                help="请输入运动时长，单位：分钟"
            )
        
        with col2:
            sleep_hours_input = st.text_input(
                "😴 睡眠时长 (小时)",
                placeholder="例如：7.5、8、6.5...",
                help="请输入睡眠时长，单位：小时"
            )
            
            sleep_quality_input = st.text_input(
                "⭐ 睡眠质量 (1-5分)",
                placeholder="1-5之间的数字",
                help="请输入睡眠质量评分，1分最差，5分最好"
            )
            
            notes_input = st.text_area(
                "💭 心路历程",
                placeholder="记录今天的感受、想法或突破...",
                height=100
            )
        
        # 提交按钮
        submitted = st.form_submit_button("💾 保存记录", type="primary", use_container_width=True)
        
        if submitted:
            # 数据验证
            try:
                # 验证必填字段
                if not date_input.strip():
                    st.error("❌ 日期不能为空")
                    st.stop()
                
                if not sport_input.strip():
                    st.error("❌ 运动项目不能为空")
                    st.stop()
                
                # 转换数据
                date_val = pd.to_datetime(date_input)
                duration_val = float(duration_input) if duration_input.strip() else 0
                sleep_hours_val = float(sleep_hours_input) if sleep_hours_input.strip() else 0
                sleep_quality_val = float(sleep_quality_input) if sleep_quality_input.strip() else 0
                
                if sleep_quality_val < 0 or sleep_quality_val > 5:
                    st.error("❌ 睡眠质量必须在0-5之间")
                    st.stop()
                
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
                
                # 检查是否已存在相同日期的记录
                date_exists = False
                if not data.empty:
                    existing_dates = data['日期'].dt.strftime('%Y-%m-%d').tolist()
                    if new_record['日期'] in existing_dates:
                        date_exists = True
                        # 更新现有记录
                        data = data[data['日期'].dt.strftime('%Y-%m-%d') != new_record['日期']]
                        st.warning("⚠️ 该日期已有记录，已更新数据")
                
                # 合并数据
                if not data.empty:
                    updated_data = pd.concat([data, new_df], ignore_index=True)
                else:
                    updated_data = new_df
                
                # 保存数据
                if save_data(updated_data):
                    if not date_exists:
                        st.success("✅ 记录保存成功！")
                    else:
                        st.success("✅ 记录更新成功！")
                    
                    # 设置标志并刷新
                    st.session_state.form_submitted = True
                    st.rerun()
                
            except ValueError as e:
                st.error("❌ 数据格式错误！请检查数字字段是否正确")
            except Exception as e:
                st.error(f"❌ 保存失败: {e}")
    
    # 显示当前数据
    st.markdown("---")
    st.subheader("📋 当前数据记录")
    
    if data.empty:
        st.info("暂无数据记录")
    else:
        # 显示数据表格
        display_data = data.copy()
        display_data['日期'] = display_data['日期'].dt.strftime('%Y-%m-%d')
        st.dataframe(display_data, use_container_width=True, hide_index=True)
        
        # 显示统计信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总记录数", len(data))
        with col2:
            active_days = len(data[data['运动时长(分钟)'] > 0])
            st.metric("运动天数", active_days)
        with col3:
            notes_count = len(data[data['心路历程'] != ''])
            st.metric("心路记录", notes_count)
    
    # 数据导出功能
    st.markdown("---")
    st.subheader("📤 数据导出")
    
    if not data.empty:
        csv_data = data.to_csv(index=False)
        st.download_button(
            label="📥 下载CSV文件",
            data=csv_data,
            file_name="my_health_data.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("暂无数据可导出")

if __name__ == "__main__":
    main()
