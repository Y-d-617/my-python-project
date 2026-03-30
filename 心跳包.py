import streamlit as st
import pandas as pd
import time
from datetime import datetime

# 尝试导入plotly，如果没有安装则使用备用方案
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ Plotly未安装，将使用简化版图表")

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
    col1, col2 = st.columns(2)
    with col1:
        start_btn = st.button("▶️ 开始模拟心跳", use_container_width=True, type="primary")
    with col2:
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
    st.subheader("📊 系统状态")
    st.info("心跳频率: 1次/秒")
    st.info("掉线阈值: 3秒")
    st.info("数据存储: 实时记录")

# 主区域显示
col1, col2, col3 = st.columns(3)
last_seq_placeholder = col1.empty()
last_time_placeholder = col2.empty()
alarm_placeholder = col3.empty()

# 图表占位符
chart_placeholder = st.empty()
table_placeholder = st.empty()

# 模拟心跳生成函数
def generate_heartbeat(seq):
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    time_ms_str = now.strftime("%H:%M:%S.%f")[:-3]
    return seq, time_str, time_ms_str, now

# 创建图表的函数
def create_chart(data):
    if len(data) < 2:
        return None
    
    df = pd.DataFrame(data, columns=["序号", "时间", "毫秒时间", "完整时间"])
    df["序号"] = df["序号"].astype(int)
    
    if PLOTLY_AVAILABLE:
        # 使用plotly创建专业图表
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df["毫秒时间"],
            y=df["序号"],
            mode='lines+markers',
            name='心跳信号',
            line=dict(color='#00BFFF', width=3),
            marker=dict(size=10, color='#FF6B6B', symbol='circle'),
            hovertemplate='时间: %{x}<br>序号: %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': "📈 无人机心跳信号实时监测图",
                'x': 0.5,
                'font': {'size': 20}
            },
            xaxis_title={
                'text': "⏰ 时间 (时:分:秒.毫秒)",
                'font': {'size': 14}
            },
            yaxis_title={
                'text': "💓 心跳序号",
                'font': {'size': 14}
            },
            plot_bgcolor='rgba(240, 240, 240, 0.3)',
            hovermode='x unified',
            height=500
        )
        
        # 添加最新数据点标注
        if len(df) > 0:
            fig.add_annotation(
                x=df["毫秒时间"].iloc[-1],
                y=df["序号"].iloc[-1],
                text=f"最新: {df['序号'].iloc[-1]}",
                showarrow=True,
                arrowhead=2,
                arrowcolor='red'
            )
        
        return fig
    else:
        # 使用matplotlib的简化版本
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df["时间"], df["序号"], 'b-o', linewidth=2, markersize=8)
        ax.set_xlabel("时间", fontsize=12)
        ax.set_ylabel("心跳序号", fontsize=12)
        ax.set_title("无人机心跳信号监测图", fontsize=14)
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig

# 主逻辑
if st.session_state.running:
    # 生成新心跳数据
    seq = len(st.session_state.heartbeat_data) + 1
    new_seq, time_str, time_ms_str, new_datetime = generate_heartbeat(seq)
    st.session_state.heartbeat_data.append((new_seq, time_str, time_ms_str, new_datetime))
    st.session_state.last_time = new_datetime
    
    # 显示最新数据
    last_seq_placeholder.metric("📊 最新心跳序号", new_seq, delta=f"+{seq-1 if seq>1 else 0}")
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
        st.info(f"🔄 模拟运行中... 已发送 {seq} 个心跳信号 | 运行时间: {elapsed_time:.1f} 秒")
    
    # 绘制图表
    fig = create_chart(st.session_state.heartbeat_data)
    if fig:
        if PLOTLY_AVAILABLE:
            chart_placeholder.plotly_chart(fig, use_container_width=True, key=f"chart_{seq}")
        else:
            chart_placeholder.pyplot(fig, use_container_width=True)
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
            hide_index=True,
            column_config={
                "序号": "心跳序号",
                "毫秒时间": "接收时间"
            }
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
        fig = create_chart(st.session_state.heartbeat_data)
        if fig:
            if PLOTLY_AVAILABLE:
                chart_placeholder.plotly_chart(fig, use_container_width=True, key="history_chart")
            else:
                chart_placeholder.pyplot(fig, use_container_width=True)
        
        # 显示统计信息
        st.sidebar.divider()
        st.sidebar.subheader("📊 统计信息")
        st.sidebar.metric("总心跳数", len(st.session_state.heartbeat_data))
        if st.session_state.start_time:
            total_time = (datetime.now() - st.session_state.start_time).total_seconds()
            st.sidebar.metric("总运行时间", f"{total_time:.1f} 秒")
            if total_time > 0:
                st.sidebar.metric("心跳频率", f"{len(st.session_state.heartbeat_data) / total_time:.1f} 个/秒")
        
    else:
        last_seq_placeholder.info("🚁 点击左侧「开始模拟心跳」启动监测")
        last_time_placeholder.info("⏰ 等待数据...")
        alarm_placeholder.info("💓 等待心跳信号...")
        chart_placeholder.info("📊 点击开始模拟后，将显示实时心跳折线图")
        
      
