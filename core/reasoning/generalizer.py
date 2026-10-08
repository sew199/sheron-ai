from dataclasses import dataclass
from typing import List, Dict


@dataclass
class GeneralizedRule:
    relation: str
    parent_relation: str
    inferred_relation: str
    confidence: float = 1.0


class ConceptGeneralizer:

    def __init__(self):
        self.rules: List[GeneralizedRule] = []

    def learn_rule(
        self,
        relation,
        parent_relation,
        inferred_relation=None,
        confidence=1.0
    ):
        """
        Learn a reusable relationship pattern.

        Example:
            is + is -> is

        This means:
            A is B
            B is C
            therefore
            A is C
        """

        if inferred_relation is None:
            inferred_relation = relation

        rule = GeneralizedRule(
            relation=str(relation).strip().lower(),
            parent_relation=str(parent_relation).strip().lower(),
            inferred_relation=str(inferred_relation).strip().lower(),
            confidence=float(confidence)
        )

        if rule not in self.rules:
            self.rules.append(rule)

        return rule

    def apply(
        self,
        relationships,
        max_depth=10
    ):
        """
        Apply learned general rules to NEW relationships.
        """

        facts = []

        for item in relationships:
            if not isinstance(item, dict):
                continue

            fact = dict(item)
            fact.setdefault("confidence", 1.0)
            fact.setdefault("negated", False)
            fact.setdefault("source", "learned")

            if fact not in facts:
                facts.append(fact)

        for _ in range(max_depth):

            new_facts = []

            for rule in self.rules:

                first_matches = [
                    fact for fact in facts
                    if fact.get("relation") == rule.relation
                    and not fact.get("negated", False)
                ]

                second_matches = [
                    fact for fact in facts
                    if fact.get("relation") == rule.parent_relation
                    and not fact.get("negated", False)
                ]

                for first in first_matches:
                    for second in second_matches:

                        if first.get("object") != second.get("subject"):
                            continue

                        confidence = min(
                            float(first.get("confidence", 1.0)),
                            float(second.get("confidence", 1.0)),
                            rule.confidence
                        )

                        candidate = {
                            "subject": first.get("subject"),
                            "relation": rule.inferred_relation,
                            "object": second.get("object"),
                            "confidence": confidence,
                            "negated": False,
                            "source": "generalized"
                        }

                        if candidate not in facts and candidate not in new_facts:
                            new_facts.append(candidate)

            if not new_facts:
                break

            facts.extend(new_facts)

        return facts


generalizer = ConceptGeneralizer()

# Basic reusable concept hierarchy rule.
generalizer.learn_rule(
    "is",
    "is",
    "is"
)
