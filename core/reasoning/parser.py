import re


class ConceptParser:

    RELATION_PATTERNS = [
        # English
        ("depends_on", r"(.+?)\s+depends\s+on\s+(.+)"),
        ("made_of", r"(.+?)\s+is\s+made\s+of\s+(.+)"),
        ("part_of", r"(.+?)\s+is\s+(?:a\s+)?part\s+of\s+(.+)"),
        ("causes", r"(.+?)\s+causes\s+(.+)"),
        ("needs", r"(.+?)\s+needs\s+(.+)"),
        ("uses", r"(.+?)\s+uses\s+(.+)"),
        ("contains", r"(.+?)\s+contains\s+(.+)"),
        ("has", r"(.+?)\s+has\s+(.+)"),
        ("is", r"(.+?)\s+is\s+(?:an?\s+)?(.+)"),
        ("are", r"(.+?)\s+are\s+(?:an?\s+)?(.+)"),

        # Roman Sinhala / Singlish
        ("part_of", r"(.+?)\s+eka\s+(.+?)\s+eke\s+part\s+ekak"),
        ("part_of", r"(.+?)\s+eka\s+(.+?)\s+ge\s+part\s+ekak"),
        ("uses", r"(.+?)\s+eka\s+(.+?)\s+use\s+karanawa"),
        ("uses", r"(.+?)\s+eka\s+(.+?)\s+use\s+karanawa"),
        ("needs", r"(.+?)\s+eka\s+(.+?)\s+ona"),
        ("needs", r"(.+?)\s+eka\s+(.+?)\s+one"),
        ("depends_on", r"(.+?)\s+eka\s+(.+?)\s+matha\s+randa\s+wenawa"),
        ("made_of", r"(.+?)\s+eka\s+(.+?)\s+walin\s+hadala"),
        ("contains", r"(.+?)\s+eka\s+(.+?)\s+thiyenawa"),
        ("has", r"(.+?)\s+eka\s+(.+?)\s+thiyenawa"),
    ]

    def normalize(self, value):
        value = value.strip().lower()

        value = re.sub(
            r"[.!?,]+$",
            "",
            value
        )

        value = re.sub(
            r"^(a|an|the)\s+",
            "",
            value
        )

        return value.strip()

    def normalize_roman_sinhala(self, value):
        value = self.normalize(value)

        # Remove common Sinhala grammar markers when they
        # are attached to the concept phrase.
        value = re.sub(
            r"\s+(eka|ekak|eke|ge|ta|ka|ki|ke)$",
            "",
            value
        )

        return value.strip()

    def parse_sentence(self, sentence):
        sentence = sentence.strip()

        for relation, pattern in self.RELATION_PATTERNS:

            match = re.fullmatch(
                pattern,
                sentence,
                flags=re.IGNORECASE
            )

            if not match:
                continue

            subject = self.normalize(
                match.group(1)
            )

            object_ = self.normalize(
                match.group(2)
            )

            # Roman Sinhala cleanup
            if relation in {
                "part_of",
                "uses",
                "needs",
                "depends_on",
                "made_of",
                "contains",
                "has",
            }:
                subject = self.normalize_roman_sinhala(subject)
                object_ = self.normalize_roman_sinhala(object_)

            if not subject or not object_:
                return None

            return {
                "subject": subject,
                "relation": relation,
                "object": object_,
                "confidence": 1.0,
            }

        return None

    def parse(self, text):
        sentences = re.split(
            r"[.!?\n]+",
            str(text)
        )

        relationships = []

        for sentence in sentences:

            if not sentence.strip():
                continue

            result = self.parse_sentence(
                sentence
            )

            if result:
                relationships.append(result)

        return relationships


concept_parser = ConceptParser()
