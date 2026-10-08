import re


SINHALA_RANGE = r"\u0D80-\u0DFF"


def detect_language(text: str) -> str:
    """
    Detect the dominant language style.

    Returns:
        si     -> Sinhala
        en     -> English
        si-en  -> Sinhala + English mixed
        roman-si -> Romanized Sinhala / Singlish-like text
        unknown -> unable to determine
    """

    if not text or not text.strip():
        return "unknown"

    text = text.strip()

    sinhala_chars = len(re.findall(f"[{SINHALA_RANGE}]", text))
    english_chars = len(re.findall(r"[A-Za-z]", text))

    words = re.findall(r"[A-Za-z]+", text.lower())

    singlish_markers = {
        "mama", "mata", "mage", "api", "ape", "oya",
        "oyata", "mokak", "mokadda", "kohomada",
        "karanna", "krnna", "thiyenawa", "thiyenne",
        "puluwanda", "puluwan", "one", "ona", "hari",
        "hri", "eka", "eke", "ekata", "kiyanna",
        "kiwwa", "dan", "dn", "wage", "wge",
        "nadda", "ne", "bro", "machan"
    }

    singlish_hits = sum(1 for word in words if word in singlish_markers)

    if sinhala_chars > 0 and english_chars > 0:
        return "si-en"

    if sinhala_chars > 0:
        return "si"

    if singlish_hits >= 2:
        return "roman-si"

    if english_chars > 0:
        return "en"

    return "unknown"


def response_language(text: str) -> str:
    """
    Decide the preferred response language.

    Technical English terms can remain in English while
    the explanation follows the user's language.
    """

    language = detect_language(text)

    if language in ("si", "si-en", "roman-si"):
        return "si"

    if language == "en":
        return "en"

    return "en"


def language_instruction(text: str) -> str:
    """
    Generate a short instruction for the response engine.
    """

    language = detect_language(text)

    if language == "si":
        return (
            "Respond mainly in clear natural Sinhala. "
            "Keep necessary technical terms in English."
        )

    if language == "roman-si":
        return (
            "Understand the user's Romanized Sinhala/Singlish. "
            "Respond in clear Sinhala mixed with necessary English "
            "technical terms."
        )

    if language == "si-en":
        return (
            "Respond naturally in Sinhala and English according "
            "to the user's mixed-language style. Keep technical "
            "terms in English when clearer."
        )

    if language == "en":
        return (
            "Respond mainly in clear natural English."
        )

    return (
        "Respond clearly and naturally. Use English technical "
        "terms when appropriate."
    )
