import re

from core.master import master_brain as zorox_master_brain


class ZoroxResponseEngine:
    def __init__(self):
        self.brain = zorox_master_brain

    def generate(self, message, user_id=None, history=None):
        text = (message or "").strip()

        if not text:
            return "Please type something and I’ll help you."

        analysis = self.brain.analyze(text, user_id=user_id)
        lang = analysis.get("language", "en")
        domain = analysis.get("domain", "general_knowledge")

        # -------------------------
        # Greetings
        # -------------------------
        if self._is_greeting(text):
            if lang in ("si", "roman-si", "si-en"):
                return (
                    "Hello bro 👋 මම ZOROX AI.\n\n"
                    "මට programming, networking, hardware, "
                    "cybersecurity, AI, science සහ general knowledge "
                    "වගේ topics ගැන help කරන්න පුළුවන්."
                )
            return (
                "Hello 👋 I’m ZOROX AI.\n\n"
                "I can help with programming, networking, hardware, "
                "cybersecurity, AI, science and general knowledge."
            )

        # -------------------------
        # Identity
        # -------------------------
        if self._is_identity_question(text):
            if lang in ("si", "roman-si", "si-en"):
                return "මගේ නම **ZOROX AI**. මම WIKRAMASINGHE TECHNOLOGIES යටතේ develop කරන AI system එක."
            return "My name is **ZOROX AI**. I’m an AI system being developed under WIKRAMASINGHE TECHNOLOGIES."

        # -------------------------
        # Status
        # -------------------------
        if self._is_status_question(text):
            if lang in ("si", "roman-si", "si-en"):
                return (
                    "මම හොඳින් වැඩ කරනවා bro 😎\n\n"
                    "දැනට ZOROX internal brain, language detection, "
                    "technical knowledge, reasoning සහ response systems online."
                )
            return (
                "I’m running normally 😎\n\n"
                "The ZOROX internal brain, language detection, "
                "technical knowledge, reasoning and response systems are online."
            )

        # -------------------------
        # Thanks
        # -------------------------
        if self._is_thanks(text):
            return "You're welcome bro 😎"

        # -------------------------
        # Direct knowledge answers
        # -------------------------
        answer = self._knowledge_answer(text, lang)
        if answer:
            return answer

        # -------------------------
        # Reasoning output
        # -------------------------
        reasoning = analysis.get("reasoning", {})
        inferred = reasoning.get("inferred_facts", [])

        if inferred:
            return self._format_reasoning(inferred, lang)

        # -------------------------
        # Domain-aware fallback
        # -------------------------
        if lang in ("si", "roman-si", "si-en"):
            return (
                f"මේක **{domain}** domain එකට අදාළ question එකක් bro.\n\n"
                "මට මේ topic එක analyze කරන්න පුළුවන්. "
                "Question එකේ exact concept එක identify කරගෙන "
                "step-by-step answer එකක් build කරන්න පුළුවන්."
            )

        return (
            f"This belongs to the **{domain}** domain.\n\n"
            "I can analyze the topic and build a step-by-step answer "
            "using the internal ZOROX systems."
        )

    # =========================================================
    # Question detection
    # =========================================================

    def _is_greeting(self, text):
        t = text.lower().strip()
        return bool(re.match(
            r"^(hello|helo|hellow|hi|hey|hey zorox|hello zorox|hi zorox|"
            r"ayubowan|good morning|good evening|good afternoon)[!. ]*$",
            t
        ))

    def _is_identity_question(self, text):
        t = text.lower().strip()

        patterns = [
            r"what is your name",
            r"what's your name",
            r"whats your name",
            r"who are you",
            r"your name",
            r"oya ge nama mokakda",
            r"oyage nama mokakda",
            r"oyage nama mokadda",
            r"oya kawda",
            r"oyā kawda",
            r"oya kauda",
        ]

        return any(re.search(p, t) for p in patterns)

    def _is_status_question(self, text):
        t = text.lower().strip()

        patterns = [
            r"^how are you",
            r"^how r u",
            r"^mko wenne",
            r"^mokada wenne",
            r"^mokakda wenne",
            r"^kohomada",
            r"^hri da",
            r"^hari da",
            r"^wada da",
            r"^working da",
        ]

        return any(re.search(p, t) for p in patterns)

    def _is_thanks(self, text):
        t = text.lower().strip()

        patterns = [
            "thank you",
            "thanks",
            "thank u",
            "tnx",
            "thx",
            "stuti",
            "sthuthi",
            "bohoma sthuthi",
        ]

        return any(p in t for p in patterns)

    # =========================================================
    # Internal knowledge answers
    # =========================================================

    def _knowledge_answer(self, text, lang):
        t = text.lower().strip()

        # -------------------------
        # Python
        # -------------------------
        if re.search(r"\bwhat is python\b|\bpython mokakda\b|\bpython kiyanne mokakda\b", t):
            if lang in ("si", "roman-si", "si-en"):
                return (
                    "**Python** කියන්නේ high-level, general-purpose programming language එකක්.\n\n"
                    "Python වලින් web development, automation, AI/ML, data science, "
                    "scripting සහ software development කරන්න පුළුවන්.\n\n"
                    "Example:\n"
                    "`print(\"Hello World\")`"
                )

            return (
                "**Python** is a high-level, general-purpose programming language.\n\n"
                "It is widely used for web development, automation, AI/ML, "
                "data science, scripting and software development.\n\n"
                "Example:\n"
                "`print(\"Hello World\")`"
            )

        # -------------------------
        # LAN
        # -------------------------
        if re.search(r"\bwhat is lan\b|\blan mokakda\b|\blan kiyanne mokakda\b", t):
            if lang in ("si", "roman-si", "si-en"):
                return (
                    "**LAN (Local Area Network)** කියන්නේ සීමිත ප්‍රදේශයක් ඇතුළත "
                    "devices එකිනෙකට connect කරන network එකක්.\n\n"
                    "උදාහරණයක් ලෙස office එකක PCs, printers සහ servers "
                    "එකම LAN එකකට connect වෙලා තියෙන්න පුළුවන්.\n\n"
                    "LAN එකක Ethernet cable හෝ Wi-Fi භාවිතා කළ හැක."
                )

            return (
                "**LAN (Local Area Network)** is a network that connects "
                "devices within a limited geographic area.\n\n"
                "For example, PCs, printers and servers in an office "
                "can communicate through the same LAN.\n\n"
                "LANs can use Ethernet or Wi-Fi."
            )

        # -------------------------
        # Internet
        # -------------------------
        if re.search(r"\bwhat is internet\b|\binternet mokakda\b", t):
            if lang in ("si", "roman-si", "si-en"):
                return (
                    "**Internet** කියන්නේ ලෝකය පුරා networks සහ devices "
                    "එකිනෙකට සම්බන්ධ කරන විශාල network එකක්.\n\n"
                    "Websites, email, online services සහ many other systems "
                    "Internet එක හරහා communicate කරනවා."
                )

            return (
                "The **Internet** is a global network of interconnected "
                "networks and devices.\n\n"
                "Websites, email, online services and many other systems "
                "communicate over the Internet."
            )

        # -------------------------
        # CPU
        # -------------------------
        if re.search(r"\bwhat is cpu\b|\bcpu mokakda\b|\bcpu kiyanne mokakda\b", t):
            if lang in ("si", "roman-si", "si-en"):
                return (
                    "**CPU (Central Processing Unit)** කියන්නේ computer එකේ "
                    "instructions execute කරන ප්‍රධාන processing unit එක.\n\n"
                    "එය calculations, logic සහ program instructions process කරනවා."
                )

            return (
                "**CPU (Central Processing Unit)** is the main processing "
                "unit that executes instructions in a computer.\n\n"
                "It performs calculations, logical operations and program instructions."
            )

        # -------------------------
        # RAM
        # -------------------------
        if re.search(r"\bwhat is ram\b|\bram mokakda\b", t):
            if lang in ("si", "roman-si", "si-en"):
                return (
                    "**RAM (Random Access Memory)** කියන්නේ computer එක "
                    "දැනට භාවිතා කරන data සහ programs තාවකාලිකව තබාගන්න memory එක.\n\n"
                    "RAM වැඩි වුණාම එකවර වැඩි applications smoothly run කරන්න "
                    "හැකියාව වැඩි වෙන්න පුළුවන්."
                )

            return (
                "**RAM (Random Access Memory)** is temporary working memory "
                "used by a computer for currently running programs and data.\n\n"
                "More RAM can allow a system to handle more applications at once."
            )

        return None

    # =========================================================
    # Reasoning formatter
    # =========================================================

    def _format_reasoning(self, facts, lang):
        if not facts:
            return None

        if lang in ("si", "roman-si", "si-en"):
            lines = ["මට මේ facts වලින් reasoning result එකක් ලැබුණා:\n"]

            for fact in facts[:8]:
                subject = fact.get("subject", "")
                relation = fact.get("relation", "")
                obj = fact.get("object", "")

                if relation == "is":
                    lines.append(f"• {subject} → {obj}")
                elif relation == "part_of":
                    lines.append(f"• {subject} → {obj} හි කොටසක්")
                elif relation == "uses":
                    lines.append(f"• {subject} → {obj} භාවිතා කරයි")
                elif relation == "depends_on":
                    lines.append(f"• {subject} → {obj} මත depend වෙනවා")
                else:
                    lines.append(f"• {subject} → {relation} → {obj}")

            return "\n".join(lines)

        lines = ["I derived these facts from the internal reasoning system:\n"]

        for fact in facts[:8]:
            subject = fact.get("subject", "")
            relation = fact.get("relation", "")
            obj = fact.get("object", "")
            lines.append(f"• {subject} → {relation} → {obj}")

        return "\n".join(lines)


zorox_response_engine = ZoroxResponseEngine()
