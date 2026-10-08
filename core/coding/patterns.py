import ast
import json
import os
from collections import Counter


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(__file__))
)

PATTERN_FILE = os.path.join(
    BASE_DIR,
    "data",
    "knowledge",
    "programming_patterns.json"
)


class ProgrammingPatternLearner:

    def __init__(self):
        self.patterns = {}
        self.load()

    def _normalize(self, value):
        return str(value).strip().lower()

    def _analyze_ast(self, code):
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []

        features = []

        for node in ast.walk(tree):

            if isinstance(node, ast.FunctionDef):
                features.append("function_definition")

            elif isinstance(node, ast.For):
                features.append("for_loop")

            elif isinstance(node, ast.While):
                features.append("while_loop")

            elif isinstance(node, ast.If):
                features.append("conditional")

            elif isinstance(node, ast.Try):
                features.append("exception_handling")

            elif isinstance(node, ast.ListComp):
                features.append("list_comprehension")

            elif isinstance(node, ast.DictComp):
                features.append("dictionary_comprehension")

            elif isinstance(node, ast.ClassDef):
                features.append("class_definition")

            elif isinstance(node, ast.Return):
                features.append("return_statement")

            elif isinstance(node, ast.Call):
                features.append("function_call")

            elif isinstance(node, ast.Assign):
                features.append("assignment")

        return sorted(set(features))

    def extract_patterns(self, code):
        features = self._analyze_ast(code)
        patterns = []

        feature_set = set(features)

        if {
            "function_definition",
            "return_statement"
        }.issubset(feature_set):
            patterns.append("reusable_function")

        if {
            "for_loop",
            "function_call"
        }.issubset(feature_set):
            patterns.append("iteration_with_function_call")

        if {
            "conditional",
            "return_statement"
        }.issubset(feature_set):
            patterns.append("conditional_return")

        if {
            "assignment",
            "conditional"
        }.issubset(feature_set):
            patterns.append("conditional_assignment")

        if {
            "exception_handling",
            "function_definition"
        }.issubset(feature_set):
            patterns.append("safe_function_execution")

        if "list_comprehension" in feature_set:
            patterns.append("collection_transformation")

        if {
            "class_definition",
            "function_definition"
        }.issubset(feature_set):
            patterns.append("object_oriented_structure")

        return {
            "features": features,
            "patterns": sorted(set(patterns))
        }

    def learn(self, code, source="example"):
        analysis = self.extract_patterns(code)

        learned = []

        for pattern in analysis["patterns"]:

            key = self._normalize(pattern)

            if key not in self.patterns:
                self.patterns[key] = {
                    "name": pattern,
                    "examples_seen": 0,
                    "sources": [],
                    "confidence": 0.0
                }

            item = self.patterns[key]

            item["examples_seen"] += 1

            if source not in item["sources"]:
                item["sources"].append(source)

            item["confidence"] = min(
                1.0,
                0.5 + (
                    item["examples_seen"] * 0.1
                )
            )

            learned.append(item)

        self.save()

        return {
            "features": analysis["features"],
            "patterns": learned
        }

    def recognize(self, code):
        analysis = self.extract_patterns(code)

        results = []

        for pattern in analysis["patterns"]:

            item = self.patterns.get(
                self._normalize(pattern)
            )

            if item:
                results.append({
                    "pattern": item["name"],
                    "examples_seen": item["examples_seen"],
                    "confidence": item["confidence"]
                })
            else:
                results.append({
                    "pattern": pattern,
                    "examples_seen": 0,
                    "confidence": 0.0
                })

        return results

    def save(self):
        os.makedirs(
            os.path.dirname(PATTERN_FILE),
            exist_ok=True
        )

        with open(
            PATTERN_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                self.patterns,
                file,
                indent=2,
                ensure_ascii=False
            )

    def load(self):
        if not os.path.exists(PATTERN_FILE):
            return

        try:
            with open(
                PATTERN_FILE,
                "r",
                encoding="utf-8"
            ) as file:
                self.patterns = json.load(file)

        except (
            OSError,
            json.JSONDecodeError
        ):
            self.patterns = {}

    def stats(self):
        return {
            "patterns": len(self.patterns),
            "total_examples": sum(
                item.get("examples_seen", 0)
                for item in self.patterns.values()
            )
        }


programming_pattern_learner = ProgrammingPatternLearner()
