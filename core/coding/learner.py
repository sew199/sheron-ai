import ast
import hashlib
import json
import os
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(__file__))
)

KNOWLEDGE_FILE = os.path.join(
    BASE_DIR,
    "data",
    "knowledge",
    "programming.json"
)


from .concepts import programming_concept_graph


class ProgrammingLearner:

    def __init__(self):
        self.knowledge = self._load()

    def _load(self):
        if not os.path.exists(KNOWLEDGE_FILE):
            return {
                "concepts": {},
                "examples": [],
                "patterns": []
            }

        try:
            with open(
                KNOWLEDGE_FILE,
                "r",
                encoding="utf-8"
            ) as file:
                return json.load(file)
        except (
            OSError,
            json.JSONDecodeError
        ):
            return {
                "concepts": {},
                "examples": [],
                "patterns": []
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

    def _hash(self, text):
        return hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()[:16]

    def analyze_python(self, code):
        """
        Analyze Python code without executing it.
        """

        try:
            tree = ast.parse(code)
        except SyntaxError as error:
            return {
                "valid": False,
                "error": str(error),
                "concepts": [],
                "patterns": []
            }

        concepts = []
        patterns = []

        for node in ast.walk(tree):

            if isinstance(node, ast.Assign):
                concepts.append("variables")

            elif isinstance(node, ast.If):
                concepts.append("conditions")

            elif isinstance(
                node,
                (ast.For, ast.While)
            ):
                concepts.append("loops")

            elif isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                concepts.append("functions")

            elif isinstance(node, ast.ClassDef):
                concepts.append("classes")

            elif isinstance(
                node,
                (ast.List, ast.Tuple, ast.Set, ast.Dict)
            ):
                concepts.append("data_structures")

            elif isinstance(
                node,
                (ast.Try, ast.ExceptHandler)
            ):
                concepts.append("exceptions")

            elif isinstance(node, ast.Import):
                concepts.append("modules")

            elif isinstance(
                node,
                ast.ImportFrom
            ):
                concepts.append("modules")

            elif isinstance(node, ast.Call):
                concepts.append("function_calls")

        concepts = sorted(set(concepts))

        if "variables" in concepts:
            patterns.append(
                "assignment creates or updates a variable"
            )

        if "conditions" in concepts:
            patterns.append(
                "condition controls which code path executes"
            )

        if "loops" in concepts:
            patterns.append(
                "loop repeats execution over a condition or iterable"
            )

        if "functions" in concepts:
            patterns.append(
                "function groups reusable behavior"
            )

        if "classes" in concepts:
            patterns.append(
                "class defines a reusable object structure"
            )

        if "exceptions" in concepts:
            patterns.append(
                "exception handling manages runtime errors"
            )

        return {
            "valid": True,
            "error": None,
            "concepts": concepts,
            "patterns": sorted(set(patterns))
        }

    def learn_python(self, code, source="example"):
        analysis = self.analyze_python(code)

        if analysis["valid"]:
            for concept in analysis["concepts"]:
                programming_concept_graph.add_concept(
                    concept,
                    category="programming",
                    description=f"Learned from Python code: {concept}"
                )

            for pattern in analysis["patterns"]:
                parts = pattern.split()

                if len(parts) >= 3:
                    subject = parts[0]
                    relation = parts[1]
                    object_ = " ".join(parts[2:])

                    programming_concept_graph.add_relationship(
                        subject,
                        relation,
                        object_,
                        confidence=0.7,
                        source="python_learner"
                    )

            programming_concept_graph.save()

        if not analysis["valid"]:
            return {
                "learned": False,
                "reason": "invalid_python",
                "analysis": analysis
            }

        code_id = self._hash(code)

        example = {
            "id": code_id,
            "language": "python",
            "source": source,
            "concepts": analysis["concepts"],
            "patterns": analysis["patterns"],
            "learned_at": datetime.now().isoformat()
        }

        existing_ids = {
            item["id"]
            for item in self.knowledge["examples"]
        }

        if code_id not in existing_ids:
            self.knowledge["examples"].append(example)

        for concept in analysis["concepts"]:
            if concept not in self.knowledge["concepts"]:
                self.knowledge["concepts"][concept] = {
                    "examples": 0,
                    "confidence": 0.0,
                    "last_seen": None
                }

            item = self.knowledge["concepts"][concept]

            item["examples"] += 1
            item["confidence"] = min(
                1.0,
                0.5 + (
                    item["examples"] * 0.1
                )
            )
            item["last_seen"] = (
                datetime.now().isoformat()
            )

        for pattern in analysis["patterns"]:
            if pattern not in self.knowledge["patterns"]:
                self.knowledge["patterns"].append(pattern)

        self._save()

        return {
            "learned": True,
            "analysis": analysis,
            "example_id": code_id
        }

    def get_knowledge(self):
        return self.knowledge


programming_learner = ProgrammingLearner()
