import streamlit as st
from chatbot import get_response, SYSTEM_PROMPT
from storage import load_chat, save_chat

st.set_page_config(page_title="SimpleAssist Chatbot")

st.title("SimpleAssist Chatbot")

# Initialize session
if "messages" not in st.session_state:
    saved_chat = load_chat()
    
    if saved_chat:
        st.session_state.messages = saved_chat
    else:
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.write(f"**{msg['role'].capitalize()}:** {msg['content']}")

# Input box
user_input = st.text_input("Type your message:")

if st.button("Send"):
    if user_input.strip():
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        # Get AI response
        reply = get_response(st.session_state.messages)

        # Add AI reply
        st.session_state.messages.append({
            "role": "assistant",
            "content": reply
        })

        # Save chat locally
        save_chat(st.session_state.messages)

        # Refresh UI
        st.rerun()

# Reset button
if st.button("Reset Chat"):
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    save_chat(st.session_state.messages)
    st.rerun()