import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a friendly and helpful AI assistant.
You remember the conversation and give clear answers.
Keep responses simple and understandable."""

def get_response(conversation_history):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history,
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        error_message = str(e)

        # Handle specific OpenAI errors
        if "quota" in error_message.lower():
            return "⚠️ API quota exceeded. Please check your OpenAI billing."

        elif "rate limit" in error_message.lower():
            return "⚠️ Too many requests. Please wait a moment and try again."

        elif "invalid api key" in error_message.lower():
            return "⚠️ Invalid API key. Please check your configuration."

        elif "insufficient_quota" in error_message.lower():
            return "⚠️ You have run out of credits."

        else:
            return f"⚠️ An unexpected error occurred: {error_message}"