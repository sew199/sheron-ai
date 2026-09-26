import json
import os
import re

MEMORY_FILE = "memory.json"
KNOWLEDGE_DIR = "knowledge"

MODE_FILES = {
    "general": None,
    "english": "english.txt",
    "coding": "coding.txt",
    "cyber": "cybersecurity.txt",
    "forex": "forex.txt",
}

MODE_NAMES = {
    "general": "General Assistant",
    "english": "English Learning",
    "coding": "Coding",
    "cyber": "Cybersecurity",
    "forex": "Forex Learning",
}

STOPWORDS = {
    "the", "is", "a", "an", "what", "how", "why", "can",
    "you", "me", "tell", "about", "to", "of", "in", "for",
    "and", "or", "i", "my", "do", "does", "are", "this"
}


def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass

    return {
        "name": "",
        "mode": "general"
    }


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def load_knowledge(mode):
    filename = MODE_FILES.get(mode)

    if not filename:
        return []

    path = os.path.join(KNOWLEDGE_DIR, filename)

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    paragraphs = re.split(r"\n\s*\n", text)

    return [p.strip() for p in paragraphs if p.strip()]


def search_knowledge(question, mode):
    paragraphs = load_knowledge(mode)

    if not paragraphs:
        return None

    words = set(
        re.findall(r"[a-zA-Z0-9+#.]+", question.lower())
    )

    words -= STOPWORDS

    if not words:
        return None

    best_answer = None
    best_score = 0

    for paragraph in paragraphs:

        paragraph_words = set(
            re.findall(
                r"[a-zA-Z0-9+#.]+",
                paragraph.lower()
            )
        )

        score = len(words & paragraph_words)

        if score > best_score:
            best_score = score
            best_answer = paragraph

    if best_score > 0:
        return best_answer

    return None


def show_help():
    print("""
Commands:

/modes              Show available modes
/mode coding        Coding mode
/mode cyber         Cybersecurity mode
/mode forex         Forex mode
/mode english       English mode
/mode general       General mode

/memory             Show saved memory
/help               Show help
/exit               Exit chatbot
""")


def main():

    memory = load_memory()

    print("=" * 45)
    print("🤖 SHERON AI V3")
    print("=" * 45)

    print("Type /help for commands.")
    print("Type /exit to quit.")
    print()

    while True:

        try:
            user = input("You: ").strip()

        except KeyboardInterrupt:
            print("\nSheron AI: Bye bro! 👋")
            break

        if not user:
            continue

        lower = user.lower()

        # EXIT
        if lower == "/exit":
            print("Sheron AI: Bye bro! 👋")
            break

        # HELP
        if lower == "/help":
            show_help()
            continue

        # MODES
        if lower == "/modes":

            print("""
Available modes:

general  - General Assistant
english  - English Learning
coding   - Coding
cyber    - Cybersecurity
forex    - Forex Learning
""")

            continue

        # MEMORY
        if lower == "/memory":

            name = memory.get("name")

            if name:
                print(f"Sheron AI: Name: {name}")
            else:
                print("Sheron AI: I don't know your name yet.")

            print(
                f"Sheron AI: Mode: "
                f"{MODE_NAMES.get(memory.get('mode'), 'General Assistant')}"
            )

            continue

        # MODE CHANGE
        if lower.startswith("/mode "):

            new_mode = lower.replace("/mode ", "").strip()

            if new_mode in MODE_FILES:

                memory["mode"] = new_mode
                save_memory(memory)

                print(
                    f"Sheron AI: Mode changed to: "
                    f"{MODE_NAMES[new_mode]}"
                )

            else:

                print(
                    "Sheron AI: Unknown mode. "
                    "Use /modes to see available modes."
                )

            continue

        # NAME MEMORY
        name_match = re.search(
            r"\bmy name is ([a-zA-Z]+)",
            user,
            re.IGNORECASE
        )

        if name_match:

            name = name_match.group(1)

            memory["name"] = name
            save_memory(memory)

            print(
                f"Sheron AI: Okay bro! "
                f"I'll remember your name as {name}."
            )

            continue

        # GREETINGS
        if lower in ["hi", "hello", "hey", "hii", "hiii"]:

            name = memory.get("name")

            if name:
                print(
                    f"Sheron AI: Hello {name} bro! 😎"
                )
            else:
                print("Sheron AI: Hello bro! 😎")

            continue

        # THANKS
        if any(word in lower for word in
               ["thank you", "thanks", "thx"]):

            print("Sheron AI: You're welcome bro! 😎")

            continue

        # KNOWLEDGE SEARCH
        mode = memory.get("mode", "general")

        answer = search_knowledge(user, mode)

        if answer:

            print()
            print("Sheron AI:", answer)
            print()

        else:

            print(
                "Sheron AI: I don't have enough local "
                "knowledge about that yet."
            )

            print(
                f"Current mode: {MODE_NAMES.get(mode)}"
            )


if __name__ == "__main__":
    main()
