from core.master.orchestrator import ZoroxMasterBrain

class ZoroxResponseEngine:
    def __init__(self):
        self.brain = ZoroxMasterBrain()

    def generate(self, message, user_id=None, history=None):
        analysis = self.brain.analyze(message, user_id=user_id)

        language = analysis.get("language", "unknown")
        domain = analysis.get("domain", "general")
        concepts = analysis.get("concepts", [])

        # Direct knowledge/reasoning response
        if analysis.get("reasoning"):
            reasoning = analysis["reasoning"]

            inferred = reasoning.get("inferred_facts", [])

            if inferred:
                facts = []
                for fact in inferred[:10]:
                    subject = fact.get("subject", "")
                    relation = fact.get("relation", "")
                    obj = fact.get("object", "")

                    if subject and relation and obj:
                        facts.append(
                            f"{subject} {relation.replace('_', ' ')} {obj}"
                        )

                if facts:
                    return self._format_response(
                        facts,
                        language,
                        domain
                    )

        # Internal brain status response
        if concepts:
            concept_names = []

            for concept in concepts[:10]:
                if isinstance(concept, dict):
                    name = (
                        concept.get("name")
                        or concept.get("concept")
                        or concept.get("subject")
                    )
                    if name:
                        concept_names.append(str(name))

            if concept_names:
                return self._concept_response(
                    concept_names,
                    language,
                    domain
                )

        return self._fallback_response(
            message,
            language,
            domain
        )

    def _format_response(self, facts, language, domain):
        if language in ("si", "roman-si", "si-en"):
            return (
                "ZOROX Brain analysis අනුව:\n\n"
                + "\n".join(f"• {fact}" for fact in facts)
                + f"\n\nDomain: {domain}"
            )

        return (
            "According to ZOROX Brain reasoning:\n\n"
            + "\n".join(f"• {fact}" for fact in facts)
            + f"\n\nDomain: {domain}"
        )

    def _concept_response(self, concepts, language, domain):
        joined = ", ".join(concepts)

        if language in ("si", "roman-si", "si-en"):
            return (
                f"ZOROX Brain මේ request එක {domain} domain එකට "
                f"route කළා.\n\n"
                f"හඳුනාගත් concepts: {joined}"
            )

        return (
            f"ZOROX Brain routed this request to the {domain} domain.\n\n"
            f"Detected concepts: {joined}"
        )

    def _fallback_response(self, message, language, domain):
        if language in ("si", "roman-si", "si-en"):
            return (
                "ZOROX Brain request එක analyze කළා.\n\n"
                f"Domain: {domain}\n"
                "මේ knowledge area එකට තව internal knowledge "
                "සහ reasoning rules එකතු කරමින් පවතිනවා."
            )

        return (
            "ZOROX Brain analyzed the request.\n\n"
            f"Domain: {domain}\n"
            "This knowledge area is still being expanded."
        )


zorox_response_engine = ZoroxResponseEngine()
