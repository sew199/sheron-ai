from core.memory import (
    get_name,
    remember_name,
    remember_birthday,
    remember_fact,
    remember_preference,
    get_profile,
    get_facts,
    get_preferences,
    add_history
)

from core.knowledge import get_best_answer
from core.router import detect_topic

from calculator import calculate


def extract_name(message):
    text = message.strip()

    patterns = [
        "my name is ",
        "i am ",
        "i'm "
    ]

    lower_text = text.lower()

    for pattern in patterns:
        if lower_text.startswith(pattern):
            name = text[len(pattern):].strip()

            if name:
                return name

    return None


def extract_birthday(message):
    text = message.strip()
    lower_text = text.lower()

    patterns = [
        "my birthday is ",
        "my birthday ",
        "my dob is ",
        "my date of birth is "
    ]

    for pattern in patterns:
        if lower_text.startswith(pattern):
            birthday = text[len(pattern):].strip()

            if birthday:
                return birthday

    return None


def extract_preference(message):
    text = message.strip()
    lower_text = text.lower()

    patterns = [
        "i like ",
        "i love ",
        "i prefer ",
        "my favorite is ",
        "my favourite is "
    ]

    for pattern in patterns:
        if lower_text.startswith(pattern):
            value = text[len(pattern):].strip()

            if value:
                return value

    return None


def generate_response(message):

    message = message.strip()

    if not message:
        return "Type something bro 🙂"

    # ==========================
    # CALCULATOR
    # ==========================

    result = calculate(message)

    if result is not None:

        if isinstance(result, float):

            if result.is_integer():
                result = int(result)

        response = f"The answer is {result} 🧮"

        add_history(
            message,
            response
        )

        return response

    # ==========================
    # REMEMBER NAME
    # ==========================

    name = extract_name(message)

    if name:

        remember_name(name)

        response = (
            f"Got it bro! "
            f"I'll remember your name as {name}. 🔥"
        )

        add_history(
            message,
            response
        )

        return response

    # ==========================
    # REMEMBER BIRTHDAY
    # ==========================

    birthday = extract_birthday(message)

    if birthday:

        remember_birthday(birthday)

        response = (
            "Got it bro! 🎂 "
            "I'll remember your birthday."
        )

        add_history(
            message,
            response
        )

        return response

    # ==========================
    # REMEMBER PREFERENCE
    # ==========================

    preference = extract_preference(message)

    if preference:

        remember_preference(
            "general",
            preference
        )

        response = (
            "Got it bro! 👍 "
            "I'll remember that preference."
        )

        add_history(
            message,
            response
        )

        return response

    # ==========================
    # GREETINGS
    # ==========================

    greetings = [
        "hi",
        "hello",
        "hey",
        "hey bro",
        "hi bro",
        "hello bro"
    ]

    if message.lower() in greetings:

        saved_name = get_name()

        if saved_name:

            response = (
                f"Hey {saved_name}! 👋 "
                f"What are we learning today?"
            )

        else:

            response = (
                "Hey bro! 👋 "
                "What are we learning today?"
            )

        add_history(
            message,
            response
        )

        return response

    # ==========================
    # MEMORY QUESTIONS
    # ==========================

    lower_message = message.lower()

    if "what is my name" in lower_message:

        saved_name = get_name()

        if saved_name:

            response = (
                f"Your name is {saved_name}. 😎"
            )

        else:

            response = (
                "I don't know your name yet, bro."
            )

        add_history(
            message,
            response
        )

        return response

    if "what is my birthday" in lower_message:

        profile = get_profile()

        birthday = profile.get(
            "birthday"
        )

        if birthday:

            response = (
                f"Your birthday is {birthday}. 🎂"
            )

        else:

            response = (
                "I don't have your birthday "
                "saved yet."
            )

        add_history(
            message,
            response
        )

        return response

    # ==========================
    # CASUAL CONVERSATION
    # ==========================

    casual_responses = {

        "how are you":
            "I'm doing good bro 😎 Ready to help you.",

        "how are you?":
            "I'm doing good bro 😎 Ready to help you.",

        "how r you":
            "I'm doing good bro 😎",

        "how r u":
            "I'm doing good bro 😎",

        "what are you doing":
            "I'm here with you bro. What should we work on? 🔥",

        "what are you doing?":
            "I'm here with you bro. What should we work on? 🔥",

        "ok":
            "Alright bro 👍",

        "okay":
            "Alright bro 👍",

        "thanks":
            "You're welcome bro! 🤝",

        "thank you":
            "You're welcome bro! 🤝",

        "good morning":
            "Good morning bro! ☀️",

        "good night":
            "Good night bro! 🌙",
    }

    casual_key = lower_message.strip()

    if casual_key in casual_responses:

        response = casual_responses[
            casual_key
        ]

        add_history(
            message,
            response
        )

        return response

    # ==========================
    # DETECT TOPIC
    # ==========================

    topic = detect_topic(message)

    # ==========================
    # SEARCH LOCAL KNOWLEDGE
    # ==========================

    result = get_best_answer(
        message,
        topic
    )

    if result:

        content = result["content"]

        response = (
            f"[Topic: {topic}]\n\n"
            f"{content}"
        )

    else:

        response = (
            "I don't have enough local knowledge "
            "about that yet, bro.\n\n"
            f"Detected topic: {topic}\n\n"
            "We can add this topic to my "
            "knowledge base."
        )

    # ==========================
    # SAVE CONVERSATION
    # ==========================

    add_history(
        message,
        response
    )

    return response
