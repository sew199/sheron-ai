from dataclasses import dataclass


@dataclass
class TruthValue:
    subject: str
    relation: str
    object: str
    confidence: float = 1.0
    negated: bool = False
    source: str = "learned"


class TruthEngine:

    def normalize(self, value):
        return str(value).strip().lower()

    def make_fact(
        self,
        subject,
        relation,
        object_,
        confidence=1.0,
        negated=False,
        source="learned"
    ):
        return TruthValue(
            subject=self.normalize(subject),
            relation=self.normalize(relation),
            object=self.normalize(object_),
            confidence=float(confidence),
            negated=bool(negated),
            source=source
        )

    def contradicts(self, a, b):
        return (
            a.subject == b.subject
            and a.relation == b.relation
            and a.object == b.object
            and a.negated != b.negated
        )

    def check(self, facts):
        contradictions = []

        for i, first in enumerate(facts):
            for second in facts[i + 1:]:
                if self.contradicts(first, second):
                    contradictions.append({
                        "fact_a": first,
                        "fact_b": second,
                        "type": "contradiction"
                    })

        return contradictions

    def resolve(self, facts):
        groups = {}

        for fact in facts:
            key = (
                fact.subject,
                fact.relation,
                fact.object
            )

            groups.setdefault(key, []).append(fact)

        resolved = []

        for group in groups.values():

            positive = [
                fact for fact in group
                if not fact.negated
            ]

            negative = [
                fact for fact in group
                if fact.negated
            ]

            if positive and negative:
                positive_best = max(
                    positive,
                    key=lambda x: x.confidence
                )

                negative_best = max(
                    negative,
                    key=lambda x: x.confidence
                )

                if (
                    positive_best.confidence
                    >= negative_best.confidence
                ):
                    resolved.append(
                        positive_best
                    )
                else:
                    resolved.append(
                        negative_best
                    )

            else:
                resolved.append(
                    max(
                        group,
                        key=lambda x: x.confidence
                    )
                )

        return resolved


truth_engine = TruthEngine()
