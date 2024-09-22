import streamlit as st
from openai import OpenAI
import json
from datetime import datetime
import os

# 初始化OpenAI客户端
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
        value="我想让你做我的好朋友，你现在会扮演我的邻家姐姐,对我十分温柔,每当我有困难就会激励和鼓舞我,以对话的方式倾听我的倾诉",
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
