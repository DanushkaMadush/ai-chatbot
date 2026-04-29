import os
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
from database import init_db, save_message, get_all_courses, get_course_details, save_unknown_question, get_unknown_question_count, seed_courses
import uuid

init_db()
seed_courses()

api_key = None
session_id = str(uuid.uuid4())

try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

SYSTEM_PROMPT = """
You are an Education Counselling Assistant.

You help students choose degree programs such as:
- Software Engineering
- Cyber Security
- Network Engineering
- Business Management
- Fashion Designing

Use database facts when available.
Give clear, short, helpful answers.
"""
conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]

def handle_education_query(user_message):
    msg = user_message.lower()

    # list programs
    if "list" in msg or "program" in msg:
        courses = get_all_courses()
        if not courses:
            return "No courses available in database."

        response = "Available Degree Programs:\n"
        for c in courses:
            response += f"- {c[0]} ({c[1]}) | {c[2]} | Fees: {c[3]} | {c[4]}\n"
        return response

    if "fees" in msg or "requirement" in msg or "validity" in msg:
        for keyword in ["software", "cyber", "network", "business", "fashion"]:
            if keyword in msg:
                details = get_course_details(keyword)
                if details:
                    d = details[0]
                    return (
                        f"{d[0]}\n"
                        f"Fees: {d[1]}\n"
                        f"Requirements: {d[2]}\n"
                        f"Validity: {d[3]}"
                    )

    # recommendation
    if "recommend" in msg or "suggest" in msg:

        courses = get_all_courses()

        import re
        numbers = re.findall(r"\d+", msg)
        budget = int(numbers[0]) if numbers else None

        # keyword matching
        interest_map = {
            "it": ["software engineering", "cyber security", "network engineering"],
            "tech": ["software engineering", "cyber security", "network engineering"],
            "security": ["cyber security"],
            "network": ["network engineering"],
            "business": ["business management"],
            "management": ["business management"],
            "fashion": ["fashion designing"],
            "design": ["fashion designing"]
        }

        matched_courses = []

        for key, values in interest_map.items():
            if key in msg:
                for c in courses:
                    for v in values:
                        if v.lower() in c[0].lower():
                            matched_courses.append(c)

        if not matched_courses:
            matched_courses = courses

        if budget:
            filtered = []
            for c in matched_courses:
                try:
                    fee = int(c[3].replace("$", ""))
                    if fee <= budget:
                        filtered.append(c)
                except:
                    continue
            matched_courses = filtered
        
        if not matched_courses:
            return "No degrees found within your budget."

        # format response
        response = "Recommended Degrees for You:\n"
        for c in matched_courses:
            response += f"- {c[0]} ({c[1]}) | {c[2]} | Fees: {c[3]}\n"

        return response

    return None

def chat(user_message):

    db_response = handle_education_query(user_message)

    if db_response:
        save_message(session_id, "assistant", db_response)
        return db_response

    conversation_history.append({"role": "user", "content": user_message})

    save_message(session_id, "user", user_message)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history,
            temperature=0.7,
            max_tokens=500
        )
        ai_reply = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": ai_reply})
        save_message(session_id, "assistant", ai_reply)
        save_unknown_question(user_message)
        count = get_unknown_question_count(user_message)

        if count > 1:
            ai_reply += "\n\n(Note: This question has been asked before. The system is learning and improving its knowledge base.)"
        return ai_reply
    
    except Exception as e:
        # Remove the failed user message from history
        conversation_history.pop()
        
        error_msg = str(e)
        
        if "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
            return " Error: Invalid API key. Check your .env file."
        elif "rate_limit" in error_msg.lower():
            return " Error: Too many requests. Please wait a moment and try again."
        elif "insufficient_quota" in error_msg.lower():
            return " Error: API quota exceeded. Check your OpenAI billing."
        elif "connection" in error_msg.lower():
            return " Error: No internet connection. Please check your network."
        else:
            return f"Unexpected error: {error_msg}"
