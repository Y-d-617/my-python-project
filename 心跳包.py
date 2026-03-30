import streamlit as st
import pandas as pd
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="无人机心跳监测", layout="wide")
st.title("🚁 无人机通信心跳监测可视化")
st.markdown("### 实时心跳折线图 + 掉线检测")

# 初始化 session_state
if "heartbeat_data" not in st.session_state:
    st.session_state.heartbeat_data = []  # 存储 [(序号, 时间字符串, 完整时间对象), ...]
if "last_time" not in st.session_state:
    st.session_state.last_time = None
if "running" not in st.session_state:
    st.session_state.running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# 侧边栏控制
with st.sidebar:
    st.header("模拟控制")
    col1, col2 = st.columns(2)
    with col1:
        start_btn = st.button("🚁 开始模拟心跳", use_container_width=True)
    with col2:
        stop_btn = st.button("🛑 停止模拟", use_container_width=True)
    
    if start_btn:
        st.session_state.running = True
        st.session_state.heartbeat_data = []  # 清空旧数据
        st.session_state.last_time = None
        st.session_state.start_time = datetime.now()
        st.success("✅ 心跳模拟已启动")
    
    if stop_btn:
        st.session_state.running = False
        st.warning("⏸️ 心跳模拟已停止")
    
    st.divider()
    st.caption("📊 心跳信号说明")
    st.caption("- 每秒生成一个心跳信号")
    st.caption("- 包含序号和精确时间")
    st.caption("- 超过3秒未收到信号即报警")

# 主区域显示
col1, col2, col3 = st.columns(3)
last_seq_placeholder = col1.empty()
last_time_placeholder = col2.empty()
alarm_placeholder = col3.empty()

# 图表占位符
chart_placeholder = st.empty()

# 实时数据表格占位符
table_placeholder = st.empty()

# 模拟心跳生成函数
def generate_heartbeat(seq):
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S.%f")[:-3]  # 显示到毫秒
    return seq, time_str, now

# 创建带完整坐标轴的图表
def create_heartbeat_chart(data):
    if len(data) < 2:
        return None
    
    df = pd.DataFrame(data, columns=["序号", "时间", "完整时间"])
    df["序号"] = df["序号"].astype(int)
    
    # 使用 plotly.graph_objects 创建更美观的图表
    fig = go.Figure()
    
    # 添加折线图
    fig.add_trace(go.Scatter(
        x=df["时间"],
        y=df["序号"],
        mode='lines+markers',
        name='心跳信号',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=8, color='#ff7f0e', symbol='circle'),
        hovertemplate='<b>时间:</b> %{x}<br>' +
                      '<b>序号:</b> %{y}<br>' +
                      '<extra></extra>'
    ))
    
    # 设置图表布局
    fig.update_layout(
        title={
            'text': "📈 无人机心跳信号实时监测图",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial, sans-serif'}
        },
        xaxis_title={
            'text': "⏰ 时间 (时:分:秒)",
            'font': {'size': 14, 'family': 'Arial, sans-serif'}
        },
        yaxis_title={
            'text': "💓 心跳序号",
            'font': {'size': 14, 'family': 'Arial, sans-serif'}
        },
        hovermode='x unified',
        plot_bgcolor='rgba(240, 240, 240, 0.5)',
        paper_bgcolor='white',
        font={'family': 'Arial, sans-serif'},
        showlegend=True,
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='black',
            borderwidth=1
        ),
        xaxis=dict(
            tickangle=45,
            tickfont={'size': 10},
            gridcolor='lightgray',
            showgrid=True,
            gridwidth=0.5
        ),
        yaxis=dict(
            tickfont={'size': 11},
            gridcolor='lightgray',
            showgrid=True,
            gridwidth=0.5,
            zeroline=True,
            zerolinecolor='lightgray'
        )
    )
    
    # 添加数据范围标注
    if len(df) > 0:
        fig.add_annotation(
            x=df["时间"].iloc[-1],
            y=df["序号"].iloc[-1],
            text=f"最新: {df['序号'].iloc[-1]}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor='red',
            font=dict(size=12, color='red'),
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='red',
            borderwidth=1
        )
    
    return fig

# 如果正在运行，则每秒生成一次数据
if st.session_state.running:
    # 生成新心跳数据
    seq = len(st.session_state.heartbeat_data) + 1
    new_seq, new_time_str, new_datetime = generate_heartbeat(seq)
    st.session_state.heartbeat_data.append((new_seq, new_time_str, new_datetime))
    st.session_state.last_time = new_datetime
    
    # 实时更新显示
    last_seq_placeholder.metric("📊 最新心跳序号", new_seq)
    last_time_placeholder.metric("⏰ 最新心跳时间", new_time_str)
    
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
    
    # 绘制折线图（带完整坐标轴）
    fig = create_heartbeat_chart(st.session_state.heartbeat_data)
    if fig:
        chart_placeholder.plotly_chart(fig, use_container_width=True, key=f"chart_{seq}")
    else:
        chart_placeholder.info("📊 等待更多数据以显示折线图... (需要至少2个数据点)")
    
    # 显示实时数据表格（最新5条）
    if st.session_state.heartbeat_data:
        recent_data = st.session_state.heartbeat_data[-5:]  # 最近5条
        df_recent = pd.DataFrame(recent_data, columns=["序号", "时间", "完整时间"])
        df_recent["序号"] = df_recent["序号"].astype(int)
        df_recent["时间"] = df_recent["时间"].astype(str)
        df_recent["完整时间"] = df_recent["完整时间"].dt.strftime("%H:%M:%S.%f")[:-3]
        
        table_placeholder.subheader("📋 实时心跳数据 (最近5条)")
        table_placeholder.dataframe(
            df_recent[["序号", "时间"]],
            use_container_width=True,
            hide_index=True
        )
    
    # 自动刷新
    time.sleep(1)
    st.rerun()
    
else:
    # 停止状态，显示静态信息
    if st.session_state.heartbeat_data:
        last_seq = st.session_state.heartbeat_data[-1][0]
        last_time_str = st.session_state.heartbeat_data[-1][1]
        last_seq_placeholder.metric("📊 最新心跳序号", last_seq)
        last_time_placeholder.metric("⏰ 最新心跳时间", last_time_str)
        
        # 掉线检测（停止后）
        if st.session_state.last_time:
            diff = (datetime.now() - st.session_state.last_time).total_seconds()
            if diff > 3:
                alarm_placeholder.error(f"⚠️ 掉线报警！已 {diff:.1f} 秒未收到心跳")
            else:
                alarm_placeholder.warning("⏸️ 模拟已停止，心跳不再更新")
        
        # 显示历史图表（带完整坐标轴）
        fig = create_heartbeat_chart(st.session_state.heartbeat_data)
        if fig:
            chart_placeholder.plotly_chart(fig, use_container_width=True, key="history_chart")
        
        # 显示历史数据表格
        if st.session_state.heartbeat_data:
            df_all = pd.DataFrame(st.session_state.heartbeat_data, columns=["序号", "时间", "完整时间"])
            df_all["序号"] = df_all["序号"].astype(int)
            df_all["时间"] = df_all["时间"].astype(str)
            
            table_placeholder.subheader("📋 历史心跳数据")
            table_placeholder.dataframe(
                df_all[["序号", "时间"]],
                use_container_width=True,
                hide_index=True
            )
        
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
        
     
