import json
import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MEMORY_DIR = os.path.join(BASE_DIR, "data", "memory")


def _safe_user_id(user_id):
    value = str(user_id or "default").strip()

    if not value:
        value = "default"

    # Keep filenames safe
    return "".join(
        char if char.isalnum() or char in ("-", "_", ".") else "_"
        for char in value
    )


def _memory_file(user_id):
    os.makedirs(MEMORY_DIR, exist_ok=True)

    return os.path.join(
        MEMORY_DIR,
        f"{_safe_user_id(user_id)}.json"
    )


def default_memory():
    return {
        "profile": {},
        "preferences": {},
        "facts": {},
        "projects": {},
        "learning": {},
        "conversation_notes": [],
        "updated_at": None,
    }


def load_memory(user_id):
    path = _memory_file(user_id)

    if not os.path.exists(path):
        return default_memory()

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        memory = default_memory()

        for key in memory:
            if key in data:
                memory[key] = data[key]

        return memory

    except (json.JSONDecodeError, OSError):
        return default_memory()


def save_memory(user_id, memory):
    path = _memory_file(user_id)

    memory["updated_at"] = datetime.now().isoformat()

    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            memory,
            file,
            indent=2,
            ensure_ascii=False
        )


def remember_fact(user_id, key, value, source="user"):
    memory = load_memory(user_id)

    memory["facts"][key] = {
        "value": value,
        "source": source,
        "saved_at": datetime.now().isoformat(),
    }

    save_memory(user_id, memory)


def remember_preference(user_id, key, value):
    memory = load_memory(user_id)

    memory["preferences"][key] = {
        "value": value,
        "saved_at": datetime.now().isoformat(),
    }

    save_memory(user_id, memory)


def remember_project(user_id, name, details):
    memory = load_memory(user_id)

    memory["projects"][name] = {
        "details": details,
        "updated_at": datetime.now().isoformat(),
    }

    save_memory(user_id, memory)


def remember_learning(user_id, topic, progress):
    memory = load_memory(user_id)

    memory["learning"][topic] = {
        "progress": progress,
        "updated_at": datetime.now().isoformat(),
    }

    save_memory(user_id, memory)


def remember_profile(user_id, key, value):
    memory = load_memory(user_id)

    memory["profile"][key] = value

    save_memory(user_id, memory)


def add_conversation_note(user_id, note):
    memory = load_memory(user_id)

    memory["conversation_notes"].append({
        "note": note,
        "created_at": datetime.now().isoformat(),
    })

    # Keep memory lightweight
    memory["conversation_notes"] = (
        memory["conversation_notes"][-100:]
    )

    save_memory(user_id, memory)


def forget(user_id, category, key):
    memory = load_memory(user_id)

    if category not in memory:
        return False

    container = memory[category]

    if key not in container:
        return False

    del container[key]

    save_memory(user_id, memory)

    return True


def get_memory_summary(user_id):
    memory = load_memory(user_id)

    return {
        "profile": memory["profile"],
        "preferences": memory["preferences"],
        "facts": memory["facts"],
        "projects": memory["projects"],
        "learning": memory["learning"],
    }


def get_relevant_memory(user_id, query="", limit=10):
    """
    Lightweight relevance matching.

    This is intentionally simple for the first version.
    Later we can replace it with embeddings/vector retrieval.
    """

    memory = load_memory(user_id)

    query_words = set(
        str(query).lower().split()
    )

    candidates = []

    for category in (
        "preferences",
        "facts",
        "projects",
        "learning",
    ):
        for key, value in memory.get(category, {}).items():

            text = (
                f"{key} "
                f"{json.dumps(value, ensure_ascii=False)}"
            ).lower()

            score = sum(
                1 for word in query_words
                if len(word) > 2 and word in text
            )

            candidates.append({
                "category": category,
                "key": key,
                "value": value,
                "score": score,
            })

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return candidates[:limit]
