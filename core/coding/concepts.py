import json
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(__file__))
)

CONCEPT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "knowledge",
    "programming_concepts.json"
)


class ProgrammingConceptGraph:

    def __init__(self):
        self.concepts = {}
        self.relationships = []
        self.load()

    def _normalize(self, value):
        return str(value).strip().lower()

    def add_concept(
        self,
        name,
        category="programming",
        description=""
    ):
        key = self._normalize(name)

        if not key:
            return False

        if key not in self.concepts:
            self.concepts[key] = {
                "name": name,
                "category": category,
                "description": description
            }
        else:
            if description:
                self.concepts[key]["description"] = description

        return True

    def add_relationship(
        self,
        subject,
        relation,
        object_,
        confidence=1.0,
        source="learned"
    ):
        subject_key = self._normalize(subject)
        relation_key = self._normalize(relation)
        object_key = self._normalize(object_)

        self.add_concept(subject_key)
        self.add_concept(object_key)

        relationship = {
            "subject": subject_key,
            "relation": relation_key,
            "object": object_key,
            "confidence": float(confidence),
            "source": source
        }

        if relationship not in self.relationships:
            self.relationships.append(relationship)

        return relationship

    def learn_basic_concepts(self):
        concepts = {
            "variable": "Stores or references a value.",
            "condition": "Controls execution based on a condition.",
            "loop": "Repeats a block of execution.",
            "function": "Groups reusable behavior.",
            "parameter": "Receives input for a function.",
            "return_value": "Value produced by a function.",
            "list": "Ordered collection of values.",
            "dictionary": "Key-value data structure.",
            "class": "Defines a reusable object structure.",
            "object": "Instance created from a class.",
            "exception": "Represents an error or exceptional event.",
            "module": "Reusable unit of code.",
            "statement": "Instruction executed by a program.",
            "expression": "Code that produces a value.",
            "iteration": "One repeated execution of a loop."
        }

        for name, description in concepts.items():
            self.add_concept(
                name,
                description=description
            )

        relationships = [
            ("function", "has", "parameter"),
            ("function", "can_produce", "return_value"),
            ("loop", "performs", "iteration"),
            ("loop", "contains", "statement"),
            ("condition", "controls", "statement"),
            ("class", "creates", "object"),
            ("exception", "can_be_handled_by", "statement"),
            ("module", "contains", "statement"),
            ("expression", "produces", "value"),
        ]

        for subject, relation, object_ in relationships:
            self.add_relationship(
                subject,
                relation,
                object_,
                confidence=0.9,
                source="foundation"
            )

    def find_related(self, concept):
        key = self._normalize(concept)

        return [
            relationship
            for relationship in self.relationships
            if (
                relationship["subject"] == key
                or relationship["object"] == key
            )
        ]

    def save(self):
        os.makedirs(
            os.path.dirname(CONCEPT_FILE),
            exist_ok=True
        )

        with open(
            CONCEPT_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                {
                    "concepts": self.concepts,
                    "relationships": self.relationships
                },
                file,
                indent=2,
                ensure_ascii=False
            )

    def load(self):
        if not os.path.exists(CONCEPT_FILE):
            return

        try:
            with open(
                CONCEPT_FILE,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            self.concepts = data.get(
                "concepts",
                {}
            )

            self.relationships = data.get(
                "relationships",
                []
            )

        except (
            OSError,
            json.JSONDecodeError
        ):
            self.concepts = {}
            self.relationships = []

    def stats(self):
        return {
            "concepts": len(self.concepts),
            "relationships": len(self.relationships)
        }


programming_concept_graph = ProgrammingConceptGraph()
