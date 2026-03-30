import streamlit as st
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="无人机心跳监测", layout="wide")
st.title("🚁 无人机通信心跳监测可视化")
st.markdown("### 实时心跳折线图 + 掉线检测")

# 初始化 session_state
if "heartbeat_data" not in st.session_state:
    st.session_state.heartbeat_data = []
if "last_time" not in st.session_state:
    st.session_state.last_time = None
if "running" not in st.session_state:
    st.session_state.running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# 侧边栏控制
with st.sidebar:
    st.header("🎮 模拟控制")
    
    start_btn = st.button("▶️ 开始模拟心跳", use_container_width=True, type="primary")
    stop_btn = st.button("⏹️ 停止模拟", use_container_width=True)
    
    if start_btn:
        st.session_state.running = True
        st.session_state.heartbeat_data = []
        st.session_state.last_time = None
        st.session_state.start_time = datetime.now()
        st.success("✅ 心跳模拟已启动")
    
    if stop_btn:
        st.session_state.running = False
        st.warning("⏸️ 心跳模拟已停止")
    
    st.divider()
    st.subheader("📊 系统参数")
    st.metric("心跳频率", "1次/秒")
    st.metric("掉线阈值", "3秒")
    st.metric("数据存储", "实时记录")

# 主区域显示
col1, col2, col3 = st.columns(3)
last_seq_placeholder = col1.empty()
last_time_placeholder = col2.empty()
alarm_placeholder = col3.empty()

# 图表占位符
chart_placeholder = st.empty()
table_placeholder = st.empty()
status_placeholder = st.empty()

# 模拟心跳生成函数
def generate_heartbeat(seq):
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    time_ms_str = now.strftime("%H:%M:%S.%f")[:-3]
    return seq, time_str, time_ms_str, now

# 主逻辑
if st.session_state.running:
    # 生成新心跳数据
    seq = len(st.session_state.heartbeat_data) + 1
    new_seq, time_str, time_ms_str, new_datetime = generate_heartbeat(seq)
    st.session_state.heartbeat_data.append((new_seq, time_str, time_ms_str, new_datetime))
    st.session_state.last_time = new_datetime
    
    # 显示最新数据
    last_seq_placeholder.metric("📊 最新心跳序号", new_seq)
    last_time_placeholder.metric("⏰ 最新心跳时间", time_ms_str)
    
    # 掉线检测
    if st.session_state.last_time:
        time_diff = (datetime.now() - st.session_state.last_time).total_seconds()
        if time_diff > 3:
            alarm_placeholder.error(f"⚠️ 掉线报警！已 {time_diff:.1f} 秒未收到心跳")
        else:
            alarm_placeholder.success(f"✅ 连接正常 (上次心跳 {time_diff:.1f} 秒前)")
    
    # 显示运行状态
    if st.session_state.start_time:
        elapsed_time = (datetime.now() - st.session_state.start_time).total_seconds()
        status_placeholder.info(f"🔄 模拟运行中... 已发送 {seq} 个心跳信号 | 运行时间: {elapsed_time:.1f} 秒")
    
    # 创建图表
    if len(st.session_state.heartbeat_data) >= 2:
        df = pd.DataFrame(st.session_state.heartbeat_data, columns=["序号", "时间", "毫秒时间", "完整时间"])
        df["序号"] = df["序号"].astype(int)
        
        # 使用 streamlit 自带的折线图
        chart_data = df.set_index("毫秒时间")["序号"]
        chart_placeholder.line_chart(chart_data, use_container_width=True)
        
        # 添加图表说明
        st.caption("📈 横轴: 时间 (时:分:秒.毫秒) | 纵轴: 心跳序号")
    else:
        chart_placeholder.info("📊 等待更多数据以显示折线图... (需要至少2个数据点)")
    
    # 显示实时数据表格
    if st.session_state.heartbeat_data:
        recent_data = st.session_state.heartbeat_data[-5:]
        df_recent = pd.DataFrame(recent_data, columns=["序号", "时间", "毫秒时间", "完整时间"])
        df_recent["序号"] = df_recent["序号"].astype(int)
        
        table_placeholder.subheader("📋 实时心跳数据 (最近5条)")
        table_placeholder.dataframe(
            df_recent[["序号", "毫秒时间"]],
            use_container_width=True,
            hide_index=True
        )
    
    # 自动刷新
    time.sleep(1)
    st.rerun()
    
else:
    # 停止状态
    if st.session_state.heartbeat_data:
        last_seq = st.session_state.heartbeat_data[-1][0]
        last_time_str = st.session_state.heartbeat_data[-1][2]
        last_seq_placeholder.metric("📊 最新心跳序号", last_seq)
        last_time_placeholder.metric("⏰ 最新心跳时间", last_time_str)
        
        if st.session_state.last_time:
            diff = (datetime.now() - st.session_state.last_time).total_seconds()
            if diff > 3:
                alarm_placeholder.error(f"⚠️ 掉线报警！已 {diff:.1f} 秒未收到心跳")
            else:
                alarm_placeholder.warning("⏸️ 模拟已停止，心跳不再更新")
        
        # 显示历史图表
        if len(st.session_state.heartbeat_data) >= 2:
            df = pd.DataFrame(st.session_state.heartbeat_data, columns=["序号", "时间", "毫秒时间", "完整时间"])
            df["序号"] = df["序号"].astype(int)
            chart_data = df.set_index("毫秒时间")["序号"]
            chart_placeholder.line_chart(chart_data, use_container_width=True)
            st.caption("📈 横轴: 时间 (时:分:秒.毫秒) | 纵轴: 心跳序号")
        
        # 显示统计信息
        st.sidebar.divider()
        st.sidebar.subheader("📊 统计信息")
        st.sidebar.metric("总心跳数", len(st.session_state.heartbeat_data))
        if st.session_state.start_time:
            total_time = (datetime.now() - st.session_state.start_time).total_seconds()
            st.sidebar.metric("总运行时间", f"{total_time:.1f} 秒")
            if total_time > 0:
                st.sidebar.metric("心跳频率", f"{len(st.session_state.heartbeat_data) / total_time:.1f} 个/秒")
        
        # 显示历史数据表格
        if st.session_state.heartbeat_data:
            df_all = pd.DataFrame(st.session_state.heartbeat_data, columns=["序号", "时间", "毫秒时间", "完整时间"])
            df_all["序号"] = df_all["序号"].astype(int)
            
            table_placeholder.subheader("📋 历史心跳数据")
            table_placeholder.dataframe(
                df_all[["序号", "毫秒时间"]],
                use_container_width=True,
                hide_index=True
            )
        
    else:
        last_seq_placeholder.info("🚁 点击左侧「开始模拟心跳」启动监测")
        last_time_placeholder.info("⏰ 等待数据...")
        alarm_placeholder.info("💓 等待心跳信号...")
        chart_placeholder.info("📊 点击开始模拟后，将显示实时心跳折线图")
        
        # 使用说明
        with st.expander("📖 使用说明", expanded=True):
            st.markdown("### 功能说明")
            st.markdown("""
            **1. 模拟心跳**
            - 点击"开始模拟心跳"按钮，系统将每秒自动生成一个心跳信号
            - 每个心跳包包含序号和精确到毫秒的时间戳
            
            **2. 掉线检测**
            - 地面站持续监听心跳信号
            - 如果超过3秒未收到新信号，页面会立即显示红色报警
            
            **3. 数据可视化**
            - **折线图**: 展示心跳序号随时间的变化趋势
            - **横轴**: 显示精确到毫秒的时间
            - **纵轴**: 显示心跳序号
            - **实时数据表**: 显示最近5条心跳数据
            
            **4. 技术实现**
            - 使用 Streamlit 构建前端界面
            - 使用 Pandas 处理数据
            - 数据实时存储在 session_state 中
            """)

# 页脚
st.divider()
st.caption("🚁 无人机通信监测系统 | 心跳频率: 1Hz | 掉线阈值: 3秒 | 实时可视化")
