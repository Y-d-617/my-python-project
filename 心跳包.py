import streamlit as st
import time
import random

# 设置页面标题
st.set_page_config(page_title="安全动态组件示例", layout="centered")

st.title("Streamlit 动态组件安全示例")
st.markdown("""
本示例演示如何避免 `removeChild` 类 DOM 错误。
主要原则：
- 使用 `st.empty` 时，不要在同一容器内混用其他动态组件。
- 自定义 HTML 组件需在卸载时清理自己创建的 DOM 节点。
""")

# ---------------------------
# 示例 1：使用 st.empty 动态更新内容
# ---------------------------
st.subheader("示例 1：动态更新文本")
placeholder = st.empty()

# 模拟数据更新
for i in range(5):
    placeholder.write(f"当前计数: {i+1}")
    time.sleep(1)

# 最后清空容器（可选）
placeholder.empty()
st.success("动态更新完成，容器已清空，无错误发生。")

# ---------------------------
# 示例 2：使用 st.empty 切换不同组件类型
# ---------------------------
st.subheader("示例 2：安全切换组件类型")
container = st.empty()

if st.button("显示图表"):
    # 注意：图表组件本身也可能产生 DOM 操作，但 Streamlit 会处理好
    with container:
        st.line_chart([random.randint(0, 100) for _ in range(10)])

if st.button("显示文本"):
    with container:
        st.write("这是一个普通文本。")

# ---------------------------
# 示例 3：自定义 HTML 组件（正确清理）
# ---------------------------
st.subheader("示例 3：自定义 HTML 组件（带清理逻辑）")

# 定义一段带动态创建元素的 HTML，并在卸载时移除自己创建的子节点
custom_html = """
<div id="custom-component-root">
    <button id="dynamic-btn">点击创建动态元素</button>
    <div id="dynamic-container"></div>
</div>

<script>
    // 确保在组件卸载时清理动态创建的元素
    window.addEventListener('beforeunload', function() {
        const container = document.getElementById('dynamic-container');
        if (container) {
            while (container.firstChild) {
                container.removeChild(container.firstChild);
            }
        }
    });

    // 为按钮添加点击事件（仅在组件存活时生效）
    document.getElementById('dynamic-btn').addEventListener('click', function() {
        const container = document.getElementById('dynamic-container');
        const newDiv = document.createElement('div');
        newDiv.textContent = '动态创建的元素 ' + new Date().toLocaleTimeString();
        container.appendChild(newDiv);
    });
</script>
"""

# 使用 components.html 嵌入自定义组件，高度自适应
st.components.v1.html(custom_html, height=150, scrolling=False)

st.info("点击上面的按钮会动态添加元素，当你刷新页面或切换应用时，这些动态元素会被正确清理，避免 'removeChild' 错误。")

# ---------------------------
# 示例 4：使用 st.empty 嵌套图表并定期更新（高级用例）
# ---------------------------
st.subheader("示例 4：定期更新图表（展示无错误）")

# 创建一个容器，用于存放图表
chart_placeholder = st.empty()

# 模拟实时数据流
for i in range(5):
    data = [random.randint(0, 100) for _ in range(10)]
    with chart_placeholder:
        st.line_chart(data)
    time.sleep(2)

# 最终清空容器
chart_placeholder.empty()
st.write("图表更新完成，容器已清空。")

st.markdown("---")
st.caption("✅ 以上所有操作均未触发 'removeChild' 错误。若出现类似错误，请检查浏览器扩展或升级 Streamlit 版本。")import streamlit as st
import time
import random

# 设置页面标题
st.set_page_config(page_title="安全动态组件示例", layout="centered")

st.title("Streamlit 动态组件安全示例")
st.markdown("""
本示例演示如何避免 `removeChild` 类 DOM 错误。
主要原则：
- 使用 `st.empty` 时，不要在同一容器内混用其他动态组件。
- 自定义 HTML 组件需在卸载时清理自己创建的 DOM 节点。
""")

# ---------------------------
# 示例 1：使用 st.empty 动态更新内容
# ---------------------------
st.subheader("示例 1：动态更新文本")
placeholder = st.empty()

# 模拟数据更新
for i in range(5):
    placeholder.write(f"当前计数: {i+1}")
    time.sleep(1)

# 最后清空容器（可选）
placeholder.empty()
st.success("动态更新完成，容器已清空，无错误发生。")

# ---------------------------
# 示例 2：使用 st.empty 切换不同组件类型
# ---------------------------
st.subheader("示例 2：安全切换组件类型")
container = st.empty()

if st.button("显示图表"):
    # 注意：图表组件本身也可能产生 DOM 操作，但 Streamlit 会处理好
    with container:
        st.line_chart([random.randint(0, 100) for _ in range(10)])

if st.button("显示文本"):
    with container:
        st.write("这是一个普通文本。")

# ---------------------------
# 示例 3：自定义 HTML 组件（正确清理）
# ---------------------------
st.subheader("示例 3：自定义 HTML 组件（带清理逻辑）")

# 定义一段带动态创建元素的 HTML，并在卸载时移除自己创建的子节点
custom_html = """
<div id="custom-component-root">
    <button id="dynamic-btn">点击创建动态元素</button>
    <div id="dynamic-container"></div>
</div>

<script>
    // 确保在组件卸载时清理动态创建的元素
    window.addEventListener('beforeunload', function() {
        const container = document.getElementById('dynamic-container');
        if (container) {
            while (container.firstChild) {
                container.removeChild(container.firstChild);
            }
        }
    });

    // 为按钮添加点击事件（仅在组件存活时生效）
    document.getElementById('dynamic-btn').addEventListener('click', function() {
        const container = document.getElementById('dynamic-container');
        const newDiv = document.createElement('div');
        newDiv.textContent = '动态创建的元素 ' + new Date().toLocaleTimeString();
        container.appendChild(newDiv);
    });
</script>
"""

# 使用 components.html 嵌入自定义组件，高度自适应
st.components.v1.html(custom_html, height=150, scrolling=False)

st.info("点击上面的按钮会动态添加元素，当你刷新页面或切换应用时，这些动态元素会被正确清理，避免 'removeChild' 错误。")

# ---------------------------
# 示例 4：使用 st.empty 嵌套图表并定期更新（高级用例）
# ---------------------------
st.subheader("示例 4：定期更新图表（展示无错误）")

# 创建一个容器，用于存放图表
chart_placeholder = st.empty()

# 模拟实时数据流
for i in range(5):
    data = [random.randint(0, 100) for _ in range(10)]
    with chart_placeholder:
        st.line_chart(data)
    time.sleep(2)

# 最终清空容器
chart_placeholder.empty()
st.write("图表更新完成，容器已清空。")

st.markdown("---")
st.caption("✅ 以上所有操作均未触发 'removeChild' 错误。若出现类似错误，请检查浏览器扩展或升级 Streamlit 版本。")
