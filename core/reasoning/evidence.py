from dataclasses import dataclass
from collections import defaultdict


@dataclass
class PatternEvidence:
    first_relation: str
    second_relation: str
    inferred_relation: str
    supporting_examples: int = 0
    contradicting_examples: int = 0
    confidence: float = 0.0
    verified: bool = False


class EvidenceEngine:

    def __init__(self):
        self.evidence = {}

    def _key(self, first, second, inferred):
        return (
            str(first).strip().lower(),
            str(second).strip().lower(),
            str(inferred).strip().lower(),
        )

    def add_evidence(
        self,
        first_relation,
        second_relation,
        inferred_relation,
        supported=True,
    ):
        key = self._key(
            first_relation,
            second_relation,
            inferred_relation,
        )

        if key not in self.evidence:
            self.evidence[key] = PatternEvidence(
                first_relation=key[0],
                second_relation=key[1],
                inferred_relation=key[2],
            )

        item = self.evidence[key]

        if supported:
            item.supporting_examples += 1
        else:
            item.contradicting_examples += 1

        item.confidence = self.calculate_confidence(item)

        item.verified = (
            item.supporting_examples >= 2
            and item.confidence >= 0.75
            and item.contradicting_examples == 0
        )

        return item

    def calculate_confidence(self, item):
        total = (
            item.supporting_examples
            + item.contradicting_examples
        )

        if total == 0:
            return 0.0

        return item.supporting_examples / total

    def get(self, first, second, inferred):
        return self.evidence.get(
            self._key(first, second, inferred)
        )

    def all(self):
        return list(self.evidence.values())


evidence_engine = EvidenceEngine()
