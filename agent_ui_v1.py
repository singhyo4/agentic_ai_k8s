import streamlit as st
import asyncio
from agent_k8s_action_v3 import handle_user_query  # Import backend logic

# Configure the Streamlit app
st.set_page_config(page_title="Kubernetes SRE Assistant", layout="centered")
st.title("💬 Kubernetes SRE Assistant")

# Session state to keep track of messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input field
user_input = st.chat_input("Type your Kubernetes command...")

if user_input:
    # Add user input to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Show "Analyzing..." while waiting
    with st.chat_message("assistant"):
        with st.spinner("🤖 Thinking... Please wait"):
    
    # Get response from the agent
            response = asyncio.run(handle_user_query(user_input))

    # Add assistant reply to history
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.markdown(response)

    # Clear the input field (optional UI trick)
            st.rerun()