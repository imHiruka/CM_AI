import datetime
import json
import os
import time

MEMORY_FILE = "memory.json"
SAVED_CONFIG = "saved_config.json"

memory = {}

MODES = [
    'Gemini',
    "Stupid",
]

current_mode = 0

def load_memory():
    global memory
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
    else:
        memory = {}

def load_config():
    global current_mode
    if os.path.exists(SAVED_CONFIG):
        with open(SAVED_CONFIG, "r") as f:
            data = json.load(f)
            current_mode = data.get("current_mode", "Gemini")
    else:
        current_mode = "Gemini"

def save_config():
    with open(SAVED_CONFIG, "w") as f:
        json.dump({"current_mode": current_mode}, f, indent=4)

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

def add_word(word, user):
    memory[word.lower()] = {
        "author_id": user.id,
        "author_name": user.name,
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_memory()

nono_words = [
    "nigger",
    "faggot",
    "dyke",
    "tranny",
    "towelhead",
    "hitler",
    "nigga",
]