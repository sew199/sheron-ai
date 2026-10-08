from .truth import truth_engine
from .generalizer import generalizer
from .auto_learner import auto_learner
from .evidence import evidence_engine


class ReasoningPipeline:

    def process(self, facts):
        """
        Complete reasoning cycle:

        facts
          ↓
        contradiction check
          ↓
        evidence/pattern learning
          ↓
        generalization
          ↓
        final result
        """

        if not isinstance(facts, list):
            raise TypeError("facts must be a list")

        # 1. Normalize facts
        normalized = []

        for fact in facts:
            if not isinstance(fact, dict):
                continue

            item = dict(fact)

            item.setdefault("confidence", 1.0)
            item.setdefault("negated", False)
            item.setdefault("source", "input")

            normalized.append(item)

        # 2. Convert to TruthValue objects
        truth_facts = []

        for fact in normalized:
            truth_facts.append(
                truth_engine.make_fact(
                    fact["subject"],
                    fact["relation"],
                    fact["object"],
                    confidence=fact["confidence"],
                    negated=fact["negated"],
                    source=fact["source"],
                )
            )

        # 3. Detect contradictions
        contradictions = truth_engine.check(
            truth_facts
        )

        # 4. Resolve contradictions
        resolved_truth = truth_engine.resolve(
            truth_facts
        )

        # 5. Convert resolved facts back to dictionaries
        resolved = []

        for fact in resolved_truth:
            resolved.append({
                "subject": fact.subject,
                "relation": fact.relation,
                "object": fact.object,
                "confidence": fact.confidence,
                "negated": fact.negated,
                "source": fact.source,
            })

        # 6. Discover patterns from positive facts
        positive_facts = [
            fact for fact in resolved
            if not fact.get("negated", False)
        ]

        patterns = auto_learner.discover_patterns(
            positive_facts
        )

        # 7. Record evidence
        evidence = []

        for pattern in patterns:
            item = evidence_engine.add_evidence(
                pattern.first_relation,
                pattern.second_relation,
                pattern.inferred_relation,
                supported=True,
            )

            evidence.append({
                "first_relation": item.first_relation,
                "second_relation": item.second_relation,
                "inferred_relation": item.inferred_relation,
                "supporting_examples":
                    item.supporting_examples,
                "contradicting_examples":
                    item.contradicting_examples,
                "confidence": item.confidence,
                "verified": item.verified,
            })

        # 8. Apply generalized reasoning
        inferred = generalizer.apply(
            positive_facts,
            max_depth=10,
        )

        # 9. Remove duplicate facts
        final = []
        seen = set()

        for fact in inferred:
            key = (
                fact.get("subject"),
                fact.get("relation"),
                fact.get("object"),
                fact.get("negated", False),
            )

            if key in seen:
                continue

            seen.add(key)
            final.append(fact)

        return {
            "input_facts": normalized,
            "contradictions": [
                {
                    "fact_a": {
                        "subject": item["fact_a"].subject,
                        "relation": item["fact_a"].relation,
                        "object": item["fact_a"].object,
                        "confidence":
                            item["fact_a"].confidence,
                        "negated":
                            item["fact_a"].negated,
                    },
                    "fact_b": {
                        "subject": item["fact_b"].subject,
                        "relation": item["fact_b"].relation,
                        "object": item["fact_b"].object,
                        "confidence":
                            item["fact_b"].confidence,
                        "negated":
                            item["fact_b"].negated,
                    },
                    "type": item["type"],
                }
                for item in contradictions
            ],
            "resolved_facts": resolved,
            "patterns": evidence,
            "inferred_facts": final,
        }


reasoning_pipeline = ReasoningPipeline()
