from core.master.orchestrator import ZoroxMasterBrain


class ZoroxResponseEngine:

    def __init__(self):
        self.brain = ZoroxMasterBrain()

    def generate(self, message, user_id=None, history=None):
        message = str(message or "").strip()

        if not message:
            return "Mokak hari message ekak type karanna bro."

        analysis = self.brain.analyze(
            message,
            user_id=user_id
        )

        language = analysis.get("language", "unknown")
        domain = analysis.get("domain", "general")
        concepts = analysis.get("concepts", [])

        # -------------------------------------------------
        # NORMAL CONVERSATION
        # -------------------------------------------------

        if self._is_greeting(message):
            return self._greeting(language)

        if self._is_status_question(message):
            return self._status(language)

        if self._is_thanks(message):
            return self._thanks(language)

        # -------------------------------------------------
        # REASONING
        # -------------------------------------------------

        reasoning = analysis.get("reasoning")

        if reasoning:
            inferred = reasoning.get("inferred_facts", [])

            if inferred:
                facts = []

                for fact in inferred[:10]:
                    subject = fact.get("subject", "")
                    relation = fact.get("relation", "")
                    obj = fact.get("object", "")

                    if subject and relation and obj:
                        facts.append(
                            self._natural_fact(
                                subject,
                                relation,
                                obj,
                                language
                            )
                        )

                if facts:
                    return self._reasoning_response(
                        facts,
                        language
                    )

        # -------------------------------------------------
        # CONCEPT RESPONSE
        # -------------------------------------------------

        concept_names = self._extract_concepts(concepts)

        if concept_names:
            return self._concept_response(
                concept_names,
                domain,
                language
            )

        # -------------------------------------------------
        # DOMAIN-AWARE INTERNAL RESPONSE
        # -------------------------------------------------

        return self._domain_response(
            message,
            domain,
            language
        )

    # =====================================================
    # LANGUAGE HELPERS
    # =====================================================

    def _is_sinhala(self, language):
        return language in (
            "si",
            "roman-si",
            "si-en"
        )

    # =====================================================
    # CONVERSATION
    # =====================================================

    def _is_greeting(self, message):
        text = message.lower().strip()

        greetings = {
            "hi",
            "hello",
            "hey",
            "helo",
            "hii",
            "hiii",
            "hello zorox",
            "hi zorox",
            "hey zorox",
            "yo"
        }

        return text in greetings

    def _is_status_question(self, message):
        text = message.lower().strip()

        patterns = [
            "mko wenne",
            "mokada wenne",
            "mokak wenne",
            "kohomada",
            "how are you",
            "how r u",
            "are you working",
            "zorox working",
            "zorox wada da",
            "wada da",
            "weda da"
        ]

        return any(
            pattern in text
            for pattern in patterns
        )

    def _is_thanks(self, message):
        text = message.lower().strip()

        return text in {
            "thanks",
            "thank you",
            "thx",
            "ty",
            "thanks bro",
            "thank you bro"
        }

    def _greeting(self, language):
        if self._is_sinhala(language):
            return (
                "Hello bro 👋\n\n"
                "Mama ZOROX AI.\n"
                "Dan internal ZOROX Brain eka online. "
                "Oyata questions ahanna, technical dewal "
                "explain karanna, code analyze karanna, "
                "reasoning karanna puluwan."
            )

        return (
            "Hello 👋\n\n"
            "I'm ZOROX AI.\n"
            "The internal ZOROX Brain is online and ready "
            "to analyze questions, technical problems, code, "
            "and reasoning tasks."
        )

    def _status(self, language):
        if self._is_sinhala(language):
            return (
                "Dan ZOROX AI eka hariyata wada karanawa bro. 🔥\n\n"
                "Frontend → Flask Server → ZOROX Internal Brain "
                "pipeline eka active."
            )

        return (
            "ZOROX AI is running correctly. 🔥\n\n"
            "The frontend → Flask server → internal ZOROX Brain "
            "pipeline is active."
        )

    def _thanks(self, language):
        if self._is_sinhala(language):
            return "Welcome bro 😎"

        return "You're welcome 😎"

    # =====================================================
    # REASONING RESPONSE
    # =====================================================

    def _natural_fact(
        self,
        subject,
        relation,
        obj,
        language
    ):
        relation_map = {
            "part_of": "is part of",
            "depends_on": "depends on",
            "made_of": "is made of",
            "causes": "causes",
            "needs": "needs",
            "uses": "uses",
            "contains": "contains",
            "has": "has",
            "is": "is",
            "are": "are"
        }

        relation_text = relation_map.get(
            relation,
            relation.replace("_", " ")
        )

        return f"{subject} {relation_text} {obj}"

    def _reasoning_response(
        self,
        facts,
        language
    ):
        if self._is_sinhala(language):
            return (
                "Reasoning karala baluwama:\n\n"
                + "\n".join(
                    f"• {fact}"
                    for fact in facts
                )
            )

        return (
            "Based on my internal reasoning:\n\n"
            + "\n".join(
                f"• {fact}"
                for fact in facts
            )
        )

    # =====================================================
    # CONCEPTS
    # =====================================================

    def _extract_concepts(self, concepts):
        names = []

        for concept in concepts[:10]:

            if isinstance(concept, dict):

                name = (
                    concept.get("name")
                    or concept.get("concept")
                    or concept.get("subject")
                )

                if name:
                    names.append(str(name))

            elif isinstance(concept, str):
                names.append(concept)

        return names

    def _concept_response(
        self,
        concepts,
        domain,
        language
    ):
        joined = ", ".join(concepts)

        if self._is_sinhala(language):
            return (
                f"Me request eka {domain} domain ekata "
                f"related kiyala identify una.\n\n"
                f"Main concepts: {joined}\n\n"
                "Me concepts walata adala internal knowledge "
                "saha reasoning use karala answer eka build "
                "karanna puluwan."
            )

        return (
            f"This request belongs to the {domain} domain.\n\n"
            f"Main concepts: {joined}\n\n"
            "I can use the internal knowledge and reasoning "
            "systems to work with these concepts."
        )

    # =====================================================
    # DOMAIN RESPONSE
    # =====================================================

    def _domain_response(
        self,
        message,
        domain,
        language
    ):
        if self._is_sinhala(language):

            domain_names = {
                "programming": "programming",
                "web_development": "web development",
                "software_development": "software development",
                "databases": "databases",
                "linux": "Linux",
                "termux": "Termux",
                "windows": "Windows",
                "networking": "networking",
                "servers": "servers",
                "vps": "VPS",
                "cloud": "cloud",
                "cybersecurity": "cybersecurity",
                "hardware": "hardware",
                "ai_ml": "AI/ML",
                "app_development": "app development",
                "game_development": "game development",
                "history": "history",
                "science": "science",
                "geography": "geography",
                "general_knowledge": "general knowledge"
            }

            readable = domain_names.get(
                domain,
                domain
            )

            return (
                f"Me request eka {readable} area ekata "
                f"related kiyala ZOROX Brain identify kala.\n\n"
                "Internal reasoning system eka request eka "
                "process karanna ready."
            )

        return (
            f"ZOROX identified this as a {domain} request.\n\n"
            "The internal reasoning system is ready to process it."
        )


zorox_response_engine = ZoroxResponseEngine()
