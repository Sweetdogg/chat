import streamlit as st
from openai import OpenAI
import json
from datetime import datetime
import os

# 初始化OpenAI客户端
use_own_api = st.checkbox("使用自己的API密钥")

if use_own_api:
    api_key = st.text_input("请输入您的API密钥", type="password")
    base_url = st.text_input("请输入API的基础URL", value="https://api.deepseek.com")
else:
    api_key = st.secrets["OPENAI_API_KEY"]
    base_url = st.secrets["API_BASE_URL"]
if api_key and base_url:
    client = OpenAI(api_key=api_key, base_url=base_url)
    st.success("OpenAI客户端初始化成功")
else:
    st.warning("请输入API密钥和基础URL以初始化OpenAI客户端")

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []

# 侧边栏：设置和历史记录
with st.sidebar:
    st.header("历史对话记录")
    saved_files = [f for f in os.listdir() if f.endswith(".json")]
    selected_file = st.selectbox("选择要加载的聊天记录", saved_files)
    if st.button("加载选中的聊天记录"):
        with open(selected_file, "r", encoding="utf-8") as f:
            st.session_state.messages = json.load(f)
        st.success("聊天记录已加载")
    
    custom_filename = st.text_input("自定义保存文件名", value="my_chat_history")
    if st.button("保存聊天记录"):
        filename = f"{custom_filename}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
        st.success(f"聊天记录已保存到 {filename}")
        
    if st.button("清除当前聊天记录"):
        st.session_state.messages = []
        st.success("聊天记录已清除")
    
    st.header("设置")
    system_content = st.text_area(
        "设置AI角色",
        value=```# 角色说明
你是一个极其聪明，具有反思能力，会一步步思考给出详尽回答的AI助手，如果内容太长了，你可以分多次发给用户，但不要省略必要的思考。你的输出格式为由三阶段组成的XML，这三部分包括：
## 第一阶段：思考与解答
1.首先，你需要对用户问题进行拆解和分析，洞察用户的意图以及解决用户问题的最佳方式；
2. 接着，你将使用该方式对用户问题进行一步步，带有思考过程的解答；
3.使用<解答></解答>标签组织你的回答。
## 第二阶段：反思
1. 在该阶段，你需要结合用户问题对用户的解答步骤和解答质量进行思考验证，判断是否正确；
2. 对第一部分获得的解答提出改进意见；
3.使用<反思></反思>标签组织你的回答。
## 第三阶段：回答
1. 在该阶段，你应该根据综合前两阶段的内容为用户提供最终准确的回答；
2.你的回答应该是结构清晰，逻辑严谨的；
3. 在回答过程中不要提及前两阶段的信息；
4.使用<output></output>标签组织你的回答。```,
        height=150
    )
    if st.button("更新AI角色"):
        st.session_state.messages = [
            {"role": "system", "content": system_content}
        ]
        st.success("AI角色已更新！")
    

# # 页面标题
# st.title("聊天机器人")

# 显示聊天历史
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入
if prompt := st.chat_input("你说:"):
    # 如果是第一次对话，添加系统消息
    if not st.session_state.messages:
        st.session_state.messages.append({"role": "system", "content": system_content})
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 获取AI响应
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
            model="deepseek-chat",
            messages=st.session_state.messages,
            stream=True
        ):
            if hasattr(response.choices[0].delta, 'content'):
                full_response += response.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
