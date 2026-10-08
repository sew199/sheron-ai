from dataclasses import dataclass


@dataclass
class Rule:
    first_relation: str
    second_relation: str
    inferred_relation: str


class RuleEngine:

    def __init__(self):
        self.rules = []

    def add_rule(
        self,
        first_relation,
        second_relation,
        inferred_relation
    ):
        rule = Rule(
            first_relation,
            second_relation,
            inferred_relation
        )

        self.rules.append(rule)
        return rule

    def _get(self, item, key):
        if isinstance(item, dict):
            return item.get(key)

        return getattr(item, key, None)

    def infer_once(self, relationships):
        inferred = []

        for rule in self.rules:

            for first in relationships:

                if self._get(
                    first,
                    "relation"
                ) != rule.first_relation:
                    continue

                for second in relationships:

                    if self._get(
                        second,
                        "relation"
                    ) != rule.second_relation:
                        continue

                    if self._get(
                        first,
                        "object"
                    ) != self._get(
                        second,
                        "subject"
                    ):
                        continue

                    candidate = {
                        "subject": self._get(
                            first,
                            "subject"
                        ),
                        "relation": rule.inferred_relation,
                        "object": self._get(
                            second,
                            "object"
                        ),
                        "confidence": min(
                            float(
                                self._get(
                                    first,
                                    "confidence"
                                ) or 0
                            ),
                            float(
                                self._get(
                                    second,
                                    "confidence"
                                ) or 0
                            )
                        )
                    }

                    if candidate not in inferred:
                        inferred.append(candidate)

        return inferred

    def infer(
        self,
        relationships,
        max_depth=10
    ):
        all_relationships = list(
            relationships
        )

        for _ in range(max_depth):

            new_relationships = (
                self.infer_once(
                    all_relationships
                )
            )

            added = 0

            for item in new_relationships:

                if item not in all_relationships:
                    all_relationships.append(
                        item
                    )
                    added += 1

            if added == 0:
                break

        return all_relationships


def create_default_rules():
    engine = RuleEngine()

    # Type hierarchy:
    # A is B + B is C -> A is C
    engine.add_rule(
        "is",
        "is",
        "is"
    )

    # A is B + B needs C -> A needs C
    engine.add_rule(
        "is",
        "needs",
        "needs"
    )

    # A is B + B uses C -> A uses C
    engine.add_rule(
        "is",
        "uses",
        "uses"
    )

    return engine


rule_engine = create_default_rules()
