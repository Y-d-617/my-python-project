import streamlit as st
import socket
import threading
import time
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

# 无人机心跳监控类（自发自收、超时检测、数据记录）
class DroneHeartbeat:
    def __init__(self, local_ip="127.0.0.1", port=5006, timeout=3):
        self.local_ip = local_ip
        self.port = port
        self.timeout_threshold = timeout
        self.seq = 0
        self.running = True
        self.heartbeat_data = []
        self.last_recv_time = time.time()
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.2)
        self.sock.bind((local_ip, port))
        
        self.lock = threading.Lock()

    def send_heartbeat(self):
        while self.running:
            start = time.time()
            self.seq += 1
            send_time = time.time()
            msg = f"{self.seq},{send_time}"
            try:
                self.sock.sendto(msg.encode(), (self.local_ip, self.port))
            except Exception as e:
                print(f"发送失败: {e}")
            cost = time.time() - start
            time.sleep(max(0, 1 - cost))

    def recv_and_check(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(1024)
                recv_time = time.time()
                msg = data.decode().split(",")
                if len(msg) == 2:
                    seq = int(msg[0])
                    send_time = float(msg[1])
                    rtt = recv_time - send_time
                    with self.lock:
                        self.last_recv_time = recv_time
                        self.heartbeat_data.append({
                            "seq": seq,
                            "send_time": send_time,
                            "recv_time": recv_time,
                            "rtt": rtt,
                            "timeout": False
                        })
            except socket.timeout:
                now = time.time()
                with self.lock:
                    if now - self.last_recv_time > self.timeout_threshold:
                        # 超时记录：使用当前未收到的序号（self.seq 可能已被更新，这里用最近发送的序号）
                        timeout_seq = self.seq
                        self.heartbeat_data.append({
                            "seq": timeout_seq,
                            "send_time": now - self.timeout_threshold,
                            "recv_time": None,
                            "rtt": None,
                            "timeout": True
                        })
                        self.last_recv_time = now
            except Exception as e:
                if self.running:
                    print(f"接收异常: {e}")

    def start(self):
        threading.Thread(target=self.send_heartbeat, daemon=True).start()
        threading.Thread(target=self.recv_and_check, daemon=True).start()

    def stop(self):
        self.running = False
        time.sleep(0.5)
        try:
            self.sock.close()
        except:
            pass

    def get_data(self):
        with self.lock:
            return self.heartbeat_data.copy()

# ==================== Streamlit 界面 ====================
st.set_page_config(page_title="无人机心跳监控", layout="wide")
st.title("🚁 无人机心跳监控系统")

# 侧边栏配置
with st.sidebar:
    st.header("参数设置")
    timeout_val = st.slider("超时阈值 (秒)", 1, 10, 3, step=1)
    duration = st.slider("运行时长 (秒)", 5, 60, 30, step=5)
    if st.button("启动监控"):
        st.session_state.run = True
        st.session_state.heartbeat = DroneHeartbeat(timeout=timeout_val)
        st.session_state.heartbeat.start()
        st.session_state.start_time = time.time()
        st.session_state.duration = duration

# 初始化 session_state
if "run" not in st.session_state:
    st.session_state.run = False

# 监控状态展示
if st.session_state.run:
    # 创建占位符用于动态更新
    data_placeholder = st.empty()
    chart_placeholder = st.empty()
    stop_btn = st.button("手动停止")

    # 循环更新
    while st.session_state.run:
        elapsed = time.time() - st.session_state.start_time
        if elapsed >= st.session_state.duration or stop_btn:
            st.session_state.heartbeat.stop()
            st.session_state.run = False
            st.success("监控已停止")
            break

        # 获取最新数据
        data = st.session_state.heartbeat.get_data()
        if data:
            df = pd.DataFrame(data)
            # 显示最近10条记录
            with data_placeholder.container():
                st.subheader("实时心跳记录")
                st.dataframe(df.tail(10).style.format({"rtt": "{:.3f}"}))
                st.metric("总心跳数", len(df))
                timeout_cnt = df["timeout"].sum()
                st.metric("超时次数", timeout_cnt)

            # 绘制RTT曲线
            fig, ax = plt.subplots(figsize=(10, 4))
            df_ok = df[df["timeout"] == False]
            ax.plot(df_ok["seq"], df_ok["rtt"], "b-o", markersize=3, label="RTT")
            ax.set_xlabel("序号")
            ax.set_ylabel("往返时间 (s)")
            ax.set_title("心跳 RTT 变化")
            ax.grid(True)
            ax.legend()
            chart_placeholder.pyplot(fig)
            plt.close(fig)
        else:
            data_placeholder.info("等待数据...")

        time.sleep(0.5)  # 更新频率

else:
    st.info("点击左侧「启动监控」开始模拟无人机心跳")

# 如果程序结束，展示最终统计图（可选）
if not st.session_state.run and "heartbeat" in st.session_state:
    final_data = st.session_state.heartbeat.get_data()
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
            ax2.plot(df_final[df_final["timeout"]==False]["seq"], 
                     df_final[df_final["timeout"]==False]["rtt"], "g-o", markersize=4)
            ax2.set_xlabel("序号")
            ax2.set_ylabel("RTT (s)")
            ax2.set_title("RTT 曲线")
            ax2.grid(True)
            st.pyplot(fig2)
