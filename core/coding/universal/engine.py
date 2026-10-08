import json
import os
import re
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
)

KNOWLEDGE_FILE = os.path.join(
    BASE_DIR,
    "data",
    "knowledge",
    "universal_programming.json"
)


LANGUAGE_PATTERNS = {

    "python": {
        "function": r"\bdef\s+\w+\s*\(",
        "loop": r"\b(for|while)\b",
        "condition": r"\b(if|elif|else)\b",
        "class": r"\bclass\s+\w+",
        "return": r"\breturn\b",
        "exception": r"\b(try|except|finally)\b",
        "variable": r"^\s*[A-Za-z_]\w*\s*=",
    },

    "javascript": {
        "function": r"\b(function\s+\w+\s*\(|=>)",
        "loop": r"\b(for|while|do)\b",
        "condition": r"\b(if|else|switch)\b",
        "class": r"\bclass\s+\w+",
        "return": r"\breturn\b",
        "exception": r"\b(try|catch|finally)\b",
        "variable": r"\b(let|const|var)\s+\w+",
    },

    "typescript": {
        "function": r"\b(function\s+\w+\s*\(|=>)",
        "loop": r"\b(for|while|do)\b",
        "condition": r"\b(if|else|switch)\b",
        "class": r"\bclass\s+\w+",
        "return": r"\breturn\b",
        "exception": r"\b(try|catch|finally)\b",
        "variable": r"\b(let|const|var)\s+\w+",
    },

    "java": {
        "function": r"\b(public|private|protected)?\s*(static\s+)?[\w<>\[\]]+\s+\w+\s*\(",
        "loop": r"\b(for|while|do)\b",
        "condition": r"\b(if|else|switch)\b",
        "class": r"\bclass\s+\w+",
        "return": r"\breturn\b",
        "exception": r"\b(try|catch|finally|throw)\b",
        "variable": r"\b(int|long|float|double|boolean|String)\s+\w+\s*=",
    },

    "c": {
        "function": r"\b[\w*]+\s+\w+\s*\([^)]*\)\s*\{",
        "loop": r"\b(for|while|do)\b",
        "condition": r"\b(if|else|switch)\b",
        "class": r"\b(struct)\b",
        "return": r"\breturn\b",
        "exception": r"\b(goto)\b",
        "variable": r"\b(int|char|float|double|long)\s+\w+\s*=",
    },

    "cpp": {
        "function": r"\b[\w:<>*&]+\s+\w+\s*\([^)]*\)\s*\{",
        "loop": r"\b(for|while|do)\b",
        "condition": r"\b(if|else|switch)\b",
        "class": r"\bclass\s+\w+",
        "return": r"\breturn\b",
        "exception": r"\b(try|catch|throw)\b",
        "variable": r"\b(int|char|float|double|long|auto)\s+\w+\s*=",
    },

    "csharp": {
        "function": r"\b(public|private|protected)?\s*(static\s+)?[\w<>\[\]]+\s+\w+\s*\(",
        "loop": r"\b(for|foreach|while|do)\b",
        "condition": r"\b(if|else|switch)\b",
        "class": r"\bclass\s+\w+",
        "return": r"\breturn\b",
        "exception": r"\b(try|catch|finally|throw)\b",
        "variable": r"\b(int|string|bool|double|float)\s+\w+\s*=",
    },

    "go": {
        "function": r"\bfunc\s+\w+\s*\(",
        "loop": r"\bfor\b",
        "condition": r"\bif\b|\bswitch\b",
        "class": r"\btype\s+\w+\s+struct\b",
        "return": r"\breturn\b",
        "exception": r"\bpanic\b|\brecover\b",
        "variable": r"\b(var|const)\s+\w+",
    },

    "rust": {
        "function": r"\bfn\s+\w+\s*\(",
        "loop": r"\b(for|while|loop)\b",
        "condition": r"\b(if|else|match)\b",
        "class": r"\bstruct\s+\w+",
        "return": r"\breturn\b",
        "exception": r"\b(Result|Option)\b",
        "variable": r"\blet\s+(mut\s+)?\w+",
    },

    "php": {
        "function": r"\bfunction\s+\w+\s*\(",
        "loop": r"\b(for|foreach|while|do)\b",
        "condition": r"\b(if|else|switch)\b",
        "class": r"\bclass\s+\w+",
        "return": r"\breturn\b",
        "exception": r"\b(try|catch|finally|throw)\b",
        "variable": r"\$\w+\s*=",
    },

    "ruby": {
        "function": r"\bdef\s+\w+",
        "loop": r"\b(for|while|until)\b",
        "condition": r"\b(if|unless|else|elsif|case)\b",
        "class": r"\bclass\s+\w+",
        "return": r"\breturn\b",
        "exception": r"\b(begin|rescue|ensure)\b",
        "variable": r"^\s*[@$A-Za-z_]\w*\s*=",
    },

    "kotlin": {
        "function": r"\bfun\s+\w+\s*\(",
        "loop": r"\b(for|while|do)\b",
        "condition": r"\b(if|else|when)\b",
        "class": r"\bclass\s+\w+",
        "return": r"\breturn\b",
        "exception": r"\b(try|catch|finally|throw)\b",
        "variable": r"\b(val|var)\s+\w+",
    },

    "swift": {
        "function": r"\bfunc\s+\w+\s*\(",
        "loop": r"\b(for|while|repeat)\b",
        "condition": r"\b(if|else|switch)\b",
        "class": r"\b(class|struct)\s+\w+",
        "return": r"\breturn\b",
        "exception": r"\b(do|catch|throw)\b",
        "variable": r"\b(let|var)\s+\w+",
    },
}


CONCEPT_NAMES = {
    "function": "function",
    "loop": "loop",
    "condition": "condition",
    "class": "class",
    "return": "return_value",
    "exception": "exception_handling",
    "variable": "variable",
}


class UniversalProgrammingEngine:

    def __init__(self):
        self.knowledge = self._load()

    def _load(self):
        if not os.path.exists(KNOWLEDGE_FILE):
            return {
                "languages": {},
                "concepts": {},
                "observations": []
            }

        try:
            with open(
                KNOWLEDGE_FILE,
                "r",
                encoding="utf-8"
            ) as file:
                return json.load(file)

        except (OSError, json.JSONDecodeError):
            return {
                "languages": {},
                "concepts": {},
                "observations": []
            }

    def _save(self):
        os.makedirs(
            os.path.dirname(KNOWLEDGE_FILE),
            exist_ok=True
        )

        with open(
            KNOWLEDGE_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                self.knowledge,
                file,
                indent=2,
                ensure_ascii=False
            )

    def detect_language(self, code):
        scores = {}

        for language, patterns in LANGUAGE_PATTERNS.items():
            score = 0

            for pattern in patterns.values():
                if re.search(
                    pattern,
                    code,
                    flags=re.MULTILINE
                ):
                    score += 1

            scores[language] = score

        best_language = max(
            scores,
            key=scores.get
        )

        if scores[best_language] == 0:
            return {
                "language": "unknown",
                "scores": scores
            }

        return {
            "language": best_language,
            "scores": scores
        }

    def extract_concepts(self, code, language=None):

        if language is None:
            language = self.detect_language(
                code
            )["language"]

        patterns = LANGUAGE_PATTERNS.get(
            language,
            {}
        )

        concepts = []

        for feature, pattern in patterns.items():

            if re.search(
                pattern,
                code,
                flags=re.MULTILINE
            ):
                concepts.append(
                    CONCEPT_NAMES[feature]
                )

        return sorted(set(concepts))

    def learn(self, code, language=None):

        detection = self.detect_language(
            code
        )

        if language is None:
            language = detection["language"]

        concepts = self.extract_concepts(
            code,
            language
        )

        if language not in self.knowledge["languages"]:
            self.knowledge["languages"][language] = {
                "examples": 0,
                "concepts": {}
            }

        language_data = self.knowledge["languages"][language]
        language_data["examples"] += 1

        for concept in concepts:

            language_data["concepts"][concept] = (
                language_data["concepts"].get(
                    concept,
                    0
                ) + 1
            )

            self.knowledge["concepts"][concept] = (
                self.knowledge["concepts"].get(
                    concept,
                    0
                ) + 1
            )

        self.knowledge["observations"].append({
            "language": language,
            "concepts": concepts,
            "learned_at": datetime.now().isoformat()
        })

        self.knowledge["observations"] = (
            self.knowledge["observations"][-1000:]
        )

        self._save()

        return {
            "language": language,
            "concepts": concepts,
            "confidence": min(
                1.0,
                0.5 + len(concepts) * 0.1
            )
        }

    def compare_languages(
        self,
        language_a,
        language_b
    ):
        a = self.knowledge["languages"].get(
            language_a,
            {}
        ).get("concepts", {})

        b = self.knowledge["languages"].get(
            language_b,
            {}
        ).get("concepts", {})

        shared = sorted(
            set(a).intersection(b)
        )

        return {
            "language_a": language_a,
            "language_b": language_b,
            "shared_concepts": shared
        }

    def stats(self):
        return {
            "languages": len(
                self.knowledge["languages"]
            ),
            "universal_concepts": len(
                self.knowledge["concepts"]
            ),
            "observations": len(
                self.knowledge["observations"]
            )
        }


universal_programming_engine = (
    UniversalProgrammingEngine()
)
