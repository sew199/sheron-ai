import json
import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LEARNING_DIR = os.path.join(BASE_DIR, "data", "learning")
LEARNING_FILE = os.path.join(LEARNING_DIR, "learning.json")


def _default_data():
    return {
        "corrections": [],
        "knowledge": [],
        "solutions": [],
        "feedback": [],
    }


def _load():
    os.makedirs(LEARNING_DIR, exist_ok=True)

    if not os.path.exists(LEARNING_FILE):
        return _default_data()

    try:
        with open(LEARNING_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        base = _default_data()

        for key in base:
            if key in data and isinstance(data[key], list):
                base[key] = data[key]

        return base

    except (json.JSONDecodeError, OSError):
        return _default_data()


def _save(data):
    os.makedirs(LEARNING_DIR, exist_ok=True)

    with open(LEARNING_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )


def _add(category, record):
    data = _load()

    record["created_at"] = datetime.now().isoformat()

    data[category].append(record)

    # Keep the first version lightweight.
    data[category] = data[category][-500:]

    _save(data)


def learn_correction(
    topic,
    wrong_answer,
    correct_answer,
    source="user"
):
    """
    Store an explicit correction from the user.
    """

    _add(
        "corrections",
        {
            "topic": topic,
            "wrong_answer": wrong_answer,
            "correct_answer": correct_answer,
            "source": source,
        }
    )


def learn_knowledge(
    topic,
    information,
    source="user"
):
    """
    Store reusable factual knowledge.
    """

    _add(
        "knowledge",
        {
            "topic": topic,
            "information": information,
            "source": source,
        }
    )


def learn_solution(
    problem,
    solution,
    domain="general",
    source="user"
):
    """
    Store a successful troubleshooting solution.
    """

    _add(
        "solutions",
        {
            "problem": problem,
            "solution": solution,
            "domain": domain,
            "source": source,
        }
    )


def record_feedback(
    message,
    rating,
    reason=None
):
    """
    Store answer-quality feedback.

    rating should normally be:
    positive / negative / correction
    """

    _add(
        "feedback",
        {
            "message": message,
            "rating": rating,
            "reason": reason,
        }
    )


def search_learning(query, limit=10):
    """
    Simple relevance search over learned information.
    """

    data = _load()

    query_words = {
        word.lower()
        for word in str(query).split()
        if len(word) > 2
    }

    results = []

    for category, records in data.items():

        for record in records:

            searchable = json.dumps(
                record,
                ensure_ascii=False
            ).lower()

            score = sum(
                1
                for word in query_words
                if word in searchable
            )

            if score > 0:
                results.append({
                    "category": category,
                    "score": score,
                    "record": record,
                })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:limit]


def get_learning_stats():
    data = _load()

    return {
        "corrections": len(data["corrections"]),
        "knowledge": len(data["knowledge"]),
        "solutions": len(data["solutions"]),
        "feedback": len(data["feedback"]),
        "total": sum(
            len(items)
            for items in data.values()
        ),
    }


def export_learning():
    return _load()
