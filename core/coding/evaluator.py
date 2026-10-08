import json
import os
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(__file__))
)

EVALUATION_FILE = os.path.join(
    BASE_DIR,
    "data",
    "evaluations",
    "programming.json"
)


class ProgrammingEvaluator:

    def __init__(self):
        self.results = self._load()

    def _load(self):
        if not os.path.exists(EVALUATION_FILE):
            return []

        try:
            with open(
                EVALUATION_FILE,
                "r",
                encoding="utf-8"
            ) as file:
                return json.load(file)

        except (OSError, json.JSONDecodeError):
            return []

    def evaluate(
        self,
        expected_patterns,
        detected_patterns
    ):
        expected = set(expected_patterns or [])
        detected = set(detected_patterns or [])

        if not expected:
            score = 1.0 if detected else 0.0
        else:
            score = len(
                expected.intersection(detected)
            ) / len(expected)

        result = {
            "score": round(score, 3),
            "correct": score >= 0.75,
            "expected": sorted(expected),
            "detected": sorted(detected),
            "missing": sorted(expected - detected),
            "unexpected": sorted(detected - expected),
            "evaluated_at": datetime.now().isoformat()
        }

        self.results.append(result)
        self.results = self.results[-500:]
        self._save()

        return result

    def _save(self):
        os.makedirs(
            os.path.dirname(EVALUATION_FILE),
            exist_ok=True
        )

        with open(
            EVALUATION_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                self.results,
                file,
                indent=2,
                ensure_ascii=False
            )

    def stats(self):
        if not self.results:
            return {
                "evaluations": 0,
                "average_score": 0.0,
                "accuracy": 0.0
            }

        scores = [
            item.get("score", 0.0)
            for item in self.results
        ]

        correct = sum(
            1
            for item in self.results
            if item.get("correct")
        )

        return {
            "evaluations": len(self.results),
            "average_score": round(
                sum(scores) / len(scores),
                3
            ),
            "accuracy": round(
                correct / len(self.results),
                3
            )
        }


programming_evaluator = ProgrammingEvaluator()
