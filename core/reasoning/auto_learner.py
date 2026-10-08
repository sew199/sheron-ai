from dataclasses import dataclass
from collections import defaultdict
from typing import List, Dict, Any

from .parser import concept_parser
from .generalizer import generalizer


@dataclass
class LearnedPattern:
    first_relation: str
    second_relation: str
    inferred_relation: str
    confidence: float
    examples_seen: int


class AutomaticConceptLearner:
    """
    Learns reusable relationship patterns from examples.

    Example:
        sparrow is bird
        bird is animal

    Learns:
        is + is -> is
    """

    def __init__(self):
        self.patterns: Dict[tuple, LearnedPattern] = {}

    def _key(self, first, second, inferred):
        return (
            str(first).strip().lower(),
            str(second).strip().lower(),
            str(inferred).strip().lower(),
        )

    def learn_pattern(
        self,
        first_relation,
        second_relation,
        inferred_relation,
        confidence=1.0,
    ):
        key = self._key(
            first_relation,
            second_relation,
            inferred_relation,
        )

        if key in self.patterns:
            pattern = self.patterns[key]
            pattern.examples_seen += 1
            pattern.confidence = min(
                1.0,
                (pattern.confidence + float(confidence)) / 2,
            )
            return pattern

        pattern = LearnedPattern(
            first_relation=key[0],
            second_relation=key[1],
            inferred_relation=key[2],
            confidence=float(confidence),
            examples_seen=1,
        )

        self.patterns[key] = pattern

        generalizer.learn_rule(
            key[0],
            key[1],
            key[2],
            pattern.confidence,
        )

        return pattern

    def discover_patterns(self, relationships):
        """
        Discover patterns by looking for chains:

            A --R1--> B
            B --R2--> C

        and learning:

            R1 + R2 -> R3

        R3 is inferred from existing graph relationships.
        """

        discovered = []

        for first in relationships:
            if first.get("negated", False):
                continue

            for second in relationships:
                if second.get("negated", False):
                    continue

                if first.get("object") != second.get("subject"):
                    continue

                first_relation = first.get("relation")
                second_relation = second.get("relation")

                if not first_relation or not second_relation:
                    continue

                # Only create a pattern when the chain itself
                # has evidence for the resulting relationship.
                target_subject = first.get("subject")
                target_object = second.get("object")

                for candidate in relationships:
                    if candidate.get("negated", False):
                        continue

                    if (
                        candidate.get("subject") == target_subject
                        and candidate.get("object") == target_object
                    ):
                        inferred_relation = candidate.get("relation")

                        if not inferred_relation:
                            continue

                        pattern = self.learn_pattern(
                            first_relation,
                            second_relation,
                            inferred_relation,
                            confidence=min(
                                float(first.get("confidence", 1.0)),
                                float(second.get("confidence", 1.0)),
                                float(candidate.get("confidence", 1.0)),
                            ),
                        )

                        discovered.append(pattern)

        return discovered

    def learn_from_text(self, text):
        relationships = concept_parser.parse(text)

        discovered = self.discover_patterns(
            relationships
        )

        return {
            "relationships": relationships,
            "patterns": [
                {
                    "first_relation": p.first_relation,
                    "second_relation": p.second_relation,
                    "inferred_relation": p.inferred_relation,
                    "confidence": p.confidence,
                    "examples_seen": p.examples_seen,
                }
                for p in discovered
            ],
        }

    def apply(self, relationships, max_depth=10):
        return generalizer.apply(
            relationships,
            max_depth=max_depth,
        )

    def get_patterns(self):
        return [
            {
                "first_relation": p.first_relation,
                "second_relation": p.second_relation,
                "inferred_relation": p.inferred_relation,
                "confidence": p.confidence,
                "examples_seen": p.examples_seen,
            }
            for p in self.patterns.values()
        ]


auto_learner = AutomaticConceptLearner()
