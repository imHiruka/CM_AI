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
    "Commands"
]

nono_words = []

current_mode = "Gemini"
global min_chance_to_say_something
global max_chance_to_say_something
global max_words_to_collect
global reply_timeout

def load_memory():
    global memory
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
    else:
        memory = {}

def load_config():
    global current_mode
    global nono_words
    global min_chance_to_say_something
    global max_chance_to_say_something
    global max_words_to_collect
    global reply_timeout
    if os.path.exists(SAVED_CONFIG):
        with open(SAVED_CONFIG, "r") as f:
            data = json.load(f)
            current_mode = data.get("current_mode", "Gemini")
            nono_words = data.get("nono_words", [])
            min_chance_to_say_something = data.get("min_chance_to_say_something", 1)
            max_chance_to_say_something = data.get("max_chance_to_say_something", 10)
            max_words_to_collect = data.get("max_words_to_collect", 20)
            reply_timeout = data.get("reply_timeout", 15.0)
    else:
        print("Configuration file not found.")

def save_config():
    with open(SAVED_CONFIG, "w") as f:
        json.dump({
            "current_mode": current_mode,
            "nono_words": nono_words,
            "min_chance_to_say_something": min_chance_to_say_something,
            "max_chance_to_say_something": max_chance_to_say_something,
            "max_words_to_collect": max_words_to_collect,
            "reply_timeout": reply_timeout
        }, f, indent=4)

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