import streamlit as st
from chatbot import get_response, SYSTEM_PROMPT
from storage import load_chat, save_chat

st.set_page_config(page_title="SimpleAssist Chatbot", page_icon="🤖")

st.title("SimpleAssist Chatbot")

# --- Initialize chat memory ---
if "messages" not in st.session_state:
    saved_chat = load_chat()

    if saved_chat:
        st.session_state.messages = saved_chat
    else:
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

# --- Display chat messages ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        avatar = "🧑" if msg["role"] == "user" else "🤖"

        with st.chat_message(msg["role"], avatar=avatar):
            if "⚠️" in msg["content"]:
                st.error(msg["content"])
            else:
                st.markdown(msg["content"])

# --- Chat input (like ChatGPT) ---
user_input = st.chat_input("Type your message...")

if user_input:
    # Show user message immediately
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Show loading spinner
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            reply = get_response(st.session_state.messages)

            # Display response
            if "⚠️" in reply:
                st.error(reply)
            else:
                st.markdown(reply)

    # Save assistant reply
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    # Save to JSON
    save_chat(st.session_state.messages)

# --- Sidebar (extra polish for marks) ---
# with st.sidebar:
#     st.header("Options")

#     if st.button("Clear Chat"):
#         st.session_state.messages = [
#             {"role": "system", "content": SYSTEM_PROMPT}
#         ]
#         save_chat(st.session_state.messages)
#         st.rerun()

#     st.markdown("---")
#     st.caption("SimpleAssist Chatbot\nUsing OpenAI API")