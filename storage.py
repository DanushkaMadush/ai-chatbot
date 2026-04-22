import json
import os

FILE_NAME = "chat_history.json"

def load_chat():
    if not os.path.exists(FILE_NAME):
        return []
    
    try:
        with open(FILE_NAME, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []

def save_chat(chat_history):
    with open(FILE_NAME, "w") as file:
        json.dump(chat_history, file, indent=4)