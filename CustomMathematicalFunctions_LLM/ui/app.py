import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from agent.core import run_agent
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(page_title="Math-Q&A Agent", page_icon="🤖")
st.title("Math-Q&A Agent 🤖")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

for msg in st.session_state["chat_history"]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])

query = st.chat_input("Ask a question or type a math problem...")
if query:
    st.session_state["chat_history"].append({"role": "user", "content": query})
    # Convert chat history to BaseMessage format
    messages = []
    for item in st.session_state["chat_history"]:
        if item["role"] == "user":
            messages.append(HumanMessage(content=item["content"]))
        else:
            messages.append(AIMessage(content=item["content"]))
    response = run_agent(query, messages)
    st.session_state["chat_history"].append({"role": "assistant", "content": str(response)})
    st.chat_message("assistant").write(str(response)) 