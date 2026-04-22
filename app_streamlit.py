import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import json
from datetime import datetime

def save_chat_history(messages):
    """Save conversation to a JSON file with timestamp."""
    # Remove system message
    export_messages = [m for m in messages if m["role"] != "system"]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(export_messages, f, indent=2, ensure_ascii=False)
    
    return filename

def trim_conversation_history(messages, max_messages=20):
    """
    Keeps system prompt + last N messages.
    Prevents token overflow and reduces cost.
    """
    if not messages:
        return messages

    system_message = messages[0]
    conversation = messages[1:]

    if len(conversation) > max_messages:
        conversation = conversation[-max_messages:]

    return [system_message] + conversation

# ─────────────────────────────────────────
# 1. CONFIGURATION
# ─────────────────────────────────────────

# Page settings (must be the first Streamlit command)
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

SYSTEM_PROMPT = """You are a helpful, friendly, and knowledgeable AI assistant.
You give clear and concise answers. If you are unsure, you say so honestly."""

MODEL = "gpt-4o-mini"

api_key = None

try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

# This runs only ONCE when the app first loads
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# ─────────────────────────────────────────
# 4. HEADER AND SIDEBAR
# ─────────────────────────────────────────
st.title(" AI Chatbot")
st.markdown("*Powered by OpenAI GPT · Built with Python & Streamlit*")

with st.sidebar:
    st.header(" Settings")
    
    temperature = st.slider(
        "Creativity (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher = more creative. Lower = more factual."
    )
    
    max_tokens = st.slider(
        "Max Response Length",
        min_value=50,
        max_value=1000,
        value=500,
        step=50,
        help="Maximum number of words in AI response."
    )
    
    st.divider()

    st.subheader("🤖 Bot Persona")

    persona = st.selectbox(
        "Choose a persona:",
        [
            "Helpful Assistant",
            "Python Tutor",
            "Creative Writer",
            "Debate Partner",
            "Custom"
        ]
    )

    persona_prompts = {
        "Helpful Assistant": "You are a helpful, friendly AI assistant.",
        "Python Tutor": "You are an expert Python programming tutor. Explain code clearly with examples. Always encourage the student.",
        "Creative Writer": "You are a creative writing assistant. Help with stories, poems, and creative content with vivid imagination.",
        "Debate Partner": "You are a debate partner who challenges ideas thoughtfully and argues different perspectives.",
    }

    if persona == "Custom":
        system_prompt = st.text_area(
            "Write your own persona:",
            "You are a helpful assistant."
        )
    else:
        system_prompt = persona_prompts[persona]
    
    if st.button("Apply Persona", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": system_prompt}
        ]
        st.success(f"Persona set to: {persona}")
        st.rerun()
    
    # Show message count
    msg_count = len([m for m in st.session_state.messages if m["role"] != "system"])
    st.metric("Messages in history", msg_count)
    
    # Reset button
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()
    
    st.divider()

    if len(st.session_state.messages) > 1:
        export_messages = [m for m in st.session_state.messages if m["role"] != "system"]

        chat_json = json.dumps(export_messages, indent=2, ensure_ascii=False)

        st.download_button(
            label="Download Chat History",
            data=chat_json,
            file_name="chat_history.json",
            mime="application/json",
            use_container_width=True
        )
    else:
        st.warning("No messages to save yet.")


# ─────────────────────────────────────────
# 5. DISPLAY CHAT HISTORY
# ─────────────────────────────────────────
# Loop through all messages (skip the system message)
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ─────────────────────────────────────────
# 6. HANDLE NEW USER INPUT
# ─────────────────────────────────────────
# st.chat_input shows a text box at the bottom of the page
if prompt := st.chat_input("Type your message here..."):
    
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ✨ Trim history BEFORE API call
    st.session_state.messages = trim_conversation_history(st.session_state.messages)
    
    # Call the AI API and display response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=st.session_state.messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                ai_reply = response.choices[0].message.content
                st.markdown(ai_reply)
                
                # Add AI reply to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_reply
                })
                
            except Exception as e:
                error_msg = f" Error: {str(e)}"
                st.error(error_msg)
                # Remove the failed user message
                st.session_state.messages.pop()