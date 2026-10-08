import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")


STOP_WORDS = {
    "a", "an", "the", "is", "are", "am", "was", "were",
    "what", "who", "where", "when", "why", "how",
    "my", "me", "i", "you", "your", "to", "of", "for",
    "in", "on", "and", "or", "do", "does", "did",
    "can", "could", "would", "should", "please",
    "tell", "about"
}


def load_knowledge():
    knowledge = {}

    if not os.path.exists(KNOWLEDGE_DIR):
        return knowledge

    for filename in os.listdir(KNOWLEDGE_DIR):

        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(KNOWLEDGE_DIR, filename)
        topic = filename[:-4]

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                knowledge[topic] = f.read()

        except OSError:
            continue

    return knowledge


def clean_words(text):

    words = re.findall(
        r"[a-zA-Z0-9_]+",
        text.lower()
    )

    return {
        word for word in words
        if word not in STOP_WORDS
        and len(word) > 1
    }


def split_into_chunks(content):

    lines = content.splitlines()

    chunks = []
    current = []

    for line in lines:

        line = line.strip()

        if not line:
            if current:
                chunks.append(" ".join(current))
                current = []

            continue

        current.append(line)

    if current:
        chunks.append(" ".join(current))

    return chunks


def search_knowledge(question, topic=None, max_results=3):

    knowledge = load_knowledge()

    if topic and topic != "general":

        if topic in knowledge:
            knowledge = {
                topic: knowledge[topic]
            }

    if not knowledge:
        return []

    question_words = clean_words(question)

    if not question_words:
        return []

    results = []

    for topic_name, content in knowledge.items():

        chunks = split_into_chunks(content)

        for chunk in chunks:

            chunk_words = clean_words(chunk)

            matches = question_words.intersection(
                chunk_words
            )

            if not matches:
                continue

            score = len(matches)

            results.append({
                "topic": topic_name,
                "score": score,
                "content": chunk
            })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:max_results]


def get_best_answer(question, topic=None):

    results = search_knowledge(
        question,
        topic=topic,
        max_results=3
    )

    if not results:
        return None

    return results[0]
