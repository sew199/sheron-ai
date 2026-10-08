import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MEMORY_FILE = os.path.join(BASE_DIR, "memory.json")


def default_memory():
    return {
        "profile": {
            "name": None,
            "birthday": None
        },
        "preferences": {},
        "facts": {},
        "history": []
    }


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return default_memory()

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Convert old memory format to the new format
        if "profile" not in data:
            old_name = data.get("name")

            data["profile"] = {
                "name": old_name,
                "birthday": None
            }

        data.setdefault("preferences", {})
        data.setdefault("facts", {})
        data.setdefault("history", [])

        if "mode" in data:
            data["preferences"]["mode"] = data["mode"]

        data.pop("name", None)
        data.pop("mode", None)

        save_memory(data)

        return data

    except (json.JSONDecodeError, OSError):
        return default_memory()


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(
            memory,
            f,
            indent=2,
            ensure_ascii=False
        )


def remember_name(name):
    memory = load_memory()
    memory["profile"]["name"] = name
    save_memory(memory)


def remember_birthday(birthday):
    memory = load_memory()
    memory["profile"]["birthday"] = birthday
    save_memory(memory)


def remember_fact(key, value):
    memory = load_memory()

    memory["facts"][key] = {
        "value": value,
        "saved_at": datetime.now().isoformat()
    }

    save_memory(memory)


def remember_preference(key, value):
    memory = load_memory()
    memory["preferences"][key] = value
    save_memory(memory)


def get_profile():
    return load_memory().get("profile", {})


def get_facts():
    return load_memory().get("facts", {})


def get_preferences():
    return load_memory().get("preferences", {})


def get_name():
    return get_profile().get("name")


def add_history(user_message, ai_response):
    memory = load_memory()

    memory["history"].append({
        "user": user_message,
        "ai": ai_response,
        "time": datetime.now().isoformat()
    })

    memory["history"] = memory["history"][-100:]

    save_memory(memory)


def get_history():
    return load_memory().get("history", [])


def clear_history():
    memory = load_memory()
    memory["history"] = []
    save_memory(memory)

