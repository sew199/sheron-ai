import re
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Concept:
    name: str
    category: str = "general"
    properties: Dict[str, str] = field(default_factory=dict)


@dataclass
class Relationship:
    subject: str
    relation: str
    object: str
    confidence: float = 1.0


class ZoroxReasoningEngine:

    def __init__(self):
        self.concepts = {}
        self.relationships = []

    def normalize(self, text):
        return re.sub(
            r"\s+",
            " ",
            str(text).strip().lower()
        )

    def add_concept(
        self,
        name,
        category="general",
        properties=None
    ):
        key = self.normalize(name)

        if not key:
            return None

        if key not in self.concepts:
            self.concepts[key] = Concept(
                name=name,
                category=category,
                properties=properties or {}
            )
        else:
            if properties:
                self.concepts[key].properties.update(
                    properties
                )

        return self.concepts[key]

    def add_relationship(
        self,
        subject,
        relation,
        object,
        confidence=1.0
    ):
        relationship = Relationship(
            subject=self.normalize(subject),
            relation=self.normalize(relation),
            object=self.normalize(object),
            confidence=float(confidence)
        )

        self.relationships.append(relationship)

        return relationship

    def find_relationships(self, concept):
        key = self.normalize(concept)

        return [
            r for r in self.relationships
            if r.subject == key or r.object == key
        ]

    def infer_from_example(self, example):
        """
        Extract a very small number of explicit patterns
        from examples.

        This is a foundation, not a full LLM.
        """

        text = self.normalize(example)

        concepts = []

        # A causes B
        match = re.search(
            r"(.+?)\s+(?:causes|caused|leads to|results in)\s+(.+)",
            text
        )

        if match:
            subject = match.group(1).strip()
            object_ = match.group(2).strip()

            self.add_concept(subject)
            self.add_concept(object_)

            self.add_relationship(
                subject,
                "causes",
                object_
            )

            concepts.extend([
                subject,
                object_
            ])

        # A is B
        match = re.search(
            r"(.+?)\s+(?:is|are)\s+(.+)",
            text
        )

        if match:
            subject = match.group(1).strip()
            object_ = match.group(2).strip()

            self.add_concept(subject)
            self.add_concept(object_)

            self.add_relationship(
                subject,
                "is",
                object_
            )

            concepts.extend([
                subject,
                object_
            ])

        return {
            "concepts": list(dict.fromkeys(concepts)),
            "relationships": [
                {
                    "subject": r.subject,
                    "relation": r.relation,
                    "object": r.object,
                    "confidence": r.confidence
                }
                for r in self.relationships
                if r.subject in concepts
                or r.object in concepts
            ]
        }

    def reason(self, subject):
        """
        Return known relationships connected to a concept.
        """

        key = self.normalize(subject)

        direct = self.find_relationships(key)

        results = []

        for relation in direct:
            if relation.subject == key:
                results.append({
                    "type": "direct",
                    "statement": (
                        f"{relation.subject} "
                        f"{relation.relation} "
                        f"{relation.object}"
                    ),
                    "confidence": relation.confidence
                })

            else:
                results.append({
                    "type": "reverse",
                    "statement": (
                        f"{relation.object} "
                        f"is related to "
                        f"{relation.subject}"
                    ),
                    "confidence": relation.confidence
                })

        return results

    def compare(self, a, b):
        a_key = self.normalize(a)
        b_key = self.normalize(b)

        a_links = self.find_relationships(a_key)
        b_links = self.find_relationships(b_key)

        a_objects = {
            r.object
            for r in a_links
            if r.subject == a_key
        }

        b_objects = {
            r.object
            for r in b_links
            if r.subject == b_key
        }

        shared = a_objects.intersection(b_objects)

        return {
            "a": a,
            "b": b,
            "shared_relationships": list(shared),
            "similar": bool(shared)
        }

    def explain(self, subject):
        reasoning = self.reason(subject)

        if not reasoning:
            return (
                f"I don't have enough learned relationships "
                f"about {subject} yet."
            )

        lines = [
            f"Known reasoning about {subject}:"
        ]

        for item in reasoning:
            lines.append(
                f"- {item['statement']} "
                f"(confidence: {item['confidence']:.2f})"
            )

        return "\n".join(lines)


reasoning_engine = ZoroxReasoningEngine()
