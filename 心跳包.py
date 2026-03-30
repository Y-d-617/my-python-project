import streamlit as st
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="无人机心跳监测", layout="wide")
st.title("🚁 无人机通信心跳监测可视化")
st.markdown("### 实时心跳折线图 + 掉线检测")

# 初始化 session_state
if "heartbeat_data" not in st.session_state:
    st.session_state.heartbeat_data = []   # 存储 [(序号, 时间字符串, 毫秒时间, 完整时间)]
if "last_time" not in st.session_state:
    st.session_state.last_time = None
if "running" not in st.session_state:
    st.session_state.running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# 侧边栏控制
with st.sidebar:
    st.header("🎮 模拟控制")
    col_start, col_stop = st.columns(2)
    with col_start:
        start_btn = st.button("▶️ 开始", use_container_width=True, type="primary")
    with col_stop:
        stop_btn = st.button("⏹️ 停止", use_container_width=True)
    clear_btn = st.button("🔄 清空数据", use_container_width=True)

    if start_btn:
        st.session_state.running = True
        st.session_state.heartbeat_data = []
        st.session_state.last_time = None
        st.session_state.start_time = datetime.now()
        st.success("✅ 心跳模拟已启动")

    if stop_btn:
        st.session_state.running = False
        st.warning("⏸️ 心跳模拟已停止")

    if clear_btn:
        st.session_state.heartbeat_data = []
        st.session_state.last_time = None
        st.session_state.start_time = None
        st.session_state.running = False
        st.info("🗑️ 数据已清空")

    st.divider()
    st.subheader("📊 系统参数")
    st.metric("心跳频率", "1次/秒")
    st.metric("掉线阈值", "3秒")
    st.metric("数据存储", "实时记录")

# 主区域占位（提前声明所有占位，避免 DOM 重建）
col1, col2, col3 = st.columns(3)
last_seq_placeholder = col1.empty()
last_time_placeholder = col2.empty()
alarm_placeholder = col3.empty()

chart_placeholder = st.empty()
table_placeholder = st.empty()
status_placeholder = st.empty()

def generate_heartbeat(seq):
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    time_ms_str = now.strftime("%H:%M:%S.%f")[:-3]
    return seq, time_str, time_ms_str, now

# 自动生成心跳逻辑（运行中且距离上次生成超过1秒时才新增）
if st.session_state.running:
    current_time = datetime.now()
    if (current_time - st.session_state.last_refresh).total_seconds() >= 1:
        seq = len(st.session_state.heartbeat_data) + 1
        new_seq, time_str, time_ms_str, new_datetime = generate_heartbeat(seq)
        st.session_state.heartbeat_data.append((new_seq, time_str, time_ms_str, new_datetime))
        st.session_state.last_time = new_datetime
        st.session_state.last_refresh = current_time

# 数据展示部分
if st.session_state.heartbeat_data:
    # 显示最新数据
    last_seq = st.session_state.heartbeat_data[-1][0]
    last_time_str = st.session_state.heartbeat_data[-1][2]
    last_seq_placeholder.metric("📊 最新心跳序号", last_seq)
    last_time_placeholder.metric("⏰ 最新心跳时间", last_time_str)

    # 掉线检测
    if st.session_state.last_time:
        time_diff = (datetime.now() - st.session_state.last_time).total_seconds()
        if time_diff > 3:
            alarm_placeholder.error(f"⚠️ 掉线报警！已 {time_diff:.1f} 秒未收到心跳")
        else:
            alarm_placeholder.success(f"✅ 连接正常 (上次心跳 {time_diff:.1f} 秒前)")

    # 显示运行状态
    if st.session_state.running and st.session_state.start_time:
        elapsed_time = (datetime.now() - st.session_state.start_time).total_seconds()
        status_placeholder.info(f"🔄 模拟运行中... 已发送 {last_seq} 个心跳信号 | 运行时间: {elapsed_time:.1f} 秒")
    elif not st.session_state.running and st.session_state.start_time:
        status_placeholder.warning("⏸️ 模拟已停止，不再生成新心跳")

    # 折线图
    if len(st.session_state.heartbeat_data) >= 2:
        df = pd.DataFrame(st.session_state.heartbeat_data, columns=["序号", "时间", "毫秒时间", "完整时间"])
        df["序号"] = df["序号"].astype(int)
        chart_data = df.set_index("毫秒时间")["序号"]
        chart_placeholder.line_chart(chart_data, use_container_width=True)
        st.caption("📈 横轴: 时间 (时:分:秒.毫秒) | 纵轴: 心跳序号")
    else:
        chart_placeholder.info("📊 等待更多数据以显示折线图... (需要至少2个数据点)")

    # 数据表格
    if st.session_state.running:
        recent_data = st.session_state.heartbeat_data[-5:]
        df_recent = pd.DataFrame(recent_data, columns=["序号", "时间", "毫秒时间", "完整时间"])
        df_recent["序号"] = df_recent["序号"].astype(int)
        table_placeholder.subheader("📋 实时心跳数据 (最近5条)")
        table_placeholder.dataframe(df_recent[["序号", "毫秒时间"]], use_container_width=True, hide_index=True)
    else:
        df_all = pd.DataFrame(st.session_state.heartbeat_data, columns=["序号", "时间", "毫秒时间", "完整时间"])
        df_all["序号"] = df_all["序号"].astype(int)
        table_placeholder.subheader("📋 历史心跳数据")
        table_placeholder.dataframe(df_all[["序号", "毫秒时间"]], use_container_width=True, hide_index=True)

    # 侧边栏统计
    st.sidebar.divider()
    st.sidebar.subheader("📊 统计信息")
    st.sidebar.metric("总心跳数", len(st.session_state.heartbeat_data))
    if st.session_state.start_time:
        total_time = (datetime.now() - st.session_state.start_time).total_seconds()
        st.sidebar.metric("总运行时间", f"{total_time:.1f} 秒")
        if total_time > 0:
            freq = len(st.session_state.heartbeat_data) / total_time
            st.sidebar.metric("心跳频率", f"{freq:.1f} 个/秒")

else:
    # 初始空状态
    last_seq_placeholder.info("🚁 点击左侧「开始」启动监测")
    last_time_placeholder.info("⏰ 等待数据...")
    alarm_placeholder.info("💓 等待心跳信号...")
    chart_placeholder.info("📊 点击开始后，将显示实时心跳折线图")
    table_placeholder.empty()
    status_placeholder.empty()

    with st.expander("📖 使用说明", expanded=True):
        st.markdown("""
        **功能说明**
        1. **模拟心跳**: 点击“开始”，系统会**自动每秒生成一个心跳信号**，无需手动刷新页面
        2. **掉线检测**: 如果超过3秒未收到新信号，页面会显示红色报警
        3. **数据可视化**: 折线图展示心跳序号随时间的变化趋势，横轴为时间，纵轴为序号
        4. **数据管理**: 可随时停止模拟、清空历史数据，方便重新测试
        """)

# 页脚
st.divider()
st.caption("🚁 无人机通信监测系统 | 心跳频率: 1Hz | 掉线阈值: 3秒 | 实时可视化")

# 自动刷新页面（保持1秒间隔，避免频繁重渲染）
if st.session_state.running:
    time.sleep(0.1)  # 轻微延迟，避免页面刷新过快
    st.rerun()
