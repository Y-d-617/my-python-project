import streamlit as st
import time
import random
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ==================== 模拟无人机心跳数据 ====================
class DroneHeartbeatSimulator:
    """模拟心跳数据生成器，替代真实UDP通信"""
    def __init__(self, timeout=3):
        self.timeout = timeout
        self.seq = 0
        self.running = True
        self.data = []          # 存储历史记录
        self.last_recv_time = time.time()
        self._simulate_heartbeat()  # 开始模拟

    def _simulate_heartbeat(self):
        """模拟发送和接收逻辑（在后台线程运行）"""
        import threading
        def run():
            while self.running:
                self.seq += 1
                send_time = time.time()
                
                # 模拟网络延迟（随机 0.05~0.3 秒）
                delay = random.uniform(0.05, 0.3)
                time.sleep(delay)
                
                recv_time = time.time()
                rtt = recv_time - send_time
                
                # 随机模拟超时（约 10% 概率）
                if random.random() < 0.1:
                    # 超时
                    self.data.append({
                        "seq": self.seq,
                        "send_time": send_time,
                        "recv_time": None,
                        "rtt": None,
                        "timeout": True
                    })
                    self.last_recv_time = recv_time
                else:
                    # 正常接收
                    self.data.append({
                        "seq": self.seq,
                        "send_time": send_time,
                        "recv_time": recv_time,
                        "rtt": rtt,
                        "timeout": False
                    })
                    self.last_recv_time = recv_time
                
                # 控制心跳间隔约 1 秒
                elapsed = time.time() - send_time
                time.sleep(max(0, 1 - elapsed))
        
        threading.Thread(target=run, daemon=True).start()

    def stop(self):
        self.running = False

    def get_data(self):
        return self.data.copy()

# ==================== Streamlit 界面 ====================
st.set_page_config(page_title="无人机心跳监控模拟", layout="wide")
st.title("🚁 无人机心跳监控系统（模拟数据）")

# 侧边栏参数
with st.sidebar:
    st.header("参数设置")
    timeout_val = st.slider("超时阈值 (秒)", 1, 5, 3, step=1)
    duration = st.slider("运行时长 (秒)", 10, 60, 30, step=5)
    if st.button("启动监控"):
        st.session_state.run = True
        st.session_state.sim = DroneHeartbeatSimulator(timeout=timeout_val)
        st.session_state.start_time = time.time()
        st.session_state.duration = duration

# 初始化 session_state
if "run" not in st.session_state:
    st.session_state.run = False

# 监控主循环
if st.session_state.run:
    # 占位符
    data_placeholder = st.empty()
    chart_placeholder = st.empty()
    stop_btn = st.button("手动停止")
    
    # 动态更新
    while st.session_state.run:
        elapsed = time.time() - st.session_state.start_time
        if elapsed >= st.session_state.duration or stop_btn:
            st.session_state.sim.stop()
            st.session_state.run = False
            st.success("监控已停止")
            break
        
        data = st.session_state.sim.get_data()
        if data:
            df = pd.DataFrame(data)
            
            # 显示最新数据
            with data_placeholder.container():
                st.subheader("实时心跳记录")
                # 只显示最近 10 条
                st.dataframe(df.tail(10).style.format({"rtt": "{:.3f}"}))
                col1, col2 = st.columns(2)
                col1.metric("总心跳数", len(df))
                timeout_cnt = df["timeout"].sum()
                col2.metric("超时次数", timeout_cnt, delta=f"{timeout_cnt/len(df)*100:.1f}%")
            
            # 绘制 RTT 曲线
            fig, ax = plt.subplots(figsize=(10, 4))
            df_ok = df[df["timeout"] == False]
            if not df_ok.empty:
                ax.plot(df_ok["seq"], df_ok["rtt"], "b-o", markersize=4, label="RTT")
                ax.set_xlabel("序号")
                ax.set_ylabel("往返时间 (s)")
                ax.set_title("心跳 RTT 变化")
                ax.grid(True)
                ax.legend()
                chart_placeholder.pyplot(fig)
                plt.close(fig)
            else:
                chart_placeholder.info("暂无正常心跳数据")
        else:
            data_placeholder.info("等待数据...")
        
        time.sleep(0.5)  # 更新频率
    
else:
    st.info("点击左侧「启动监控」开始模拟无人机心跳")

# 最终统计（当程序停止后）
if not st.session_state.run and "sim" in st.session_state:
    final_data = st.session_state.sim.get_data()
    if final_data:
        st.subheader("最终统计")
        df_final = pd.DataFrame(final_data)
        ok_cnt = len(df_final) - df_final["timeout"].sum()
        timeout_cnt = df_final["timeout"].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            fig1, ax1 = plt.subplots()
            ax1.pie([ok_cnt, timeout_cnt], labels=["正常", "超时"], colors=["green","red"], autopct="%1.1f%%")
            ax1.set_title("超时比例")
            st.pyplot(fig1)
        with col2:
            fig2, ax2 = plt.subplots()
            df_ok_final = df_final[df_final["timeout"] == False]
            if not df_ok_final.empty:
                ax2.plot(df_ok_final["seq"], df_ok_final["rtt"], "g-o", markersize=4)
                ax2.set_xlabel("序号")
                ax2.set_ylabel("RTT (s)")
                ax2.set_title("RTT 曲线")
                ax2.grid(True)
            else:
                ax2.text(0.5, 0.5, "无正常数据", ha='center', va='center')
            st.pyplot(fig2)
