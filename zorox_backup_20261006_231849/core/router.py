TOPIC_KEYWORDS = {
    "coding": [
        "python", "code", "coding", "program", "programming",
        "javascript", "java", "c++", "html", "css", "bug",
        "error", "function", "variable", "class", "loop"
    ],

    "cybersecurity": [
        "cyber", "cybersecurity", "security", "hacking",
        "ethical hacking", "malware", "phishing", "firewall",
        "encryption", "authentication", "vulnerability",
        "owasp"
    ],

    "networking": [
        "network", "networking", "router", "switch", "ip",
        "ipv4", "ipv6", "dns", "dhcp", "tcp", "udp",
        "port", "subnet", "lan", "wan", "wifi", "ethernet"
    ],

    "cloud": [
        "cloud", "aws", "azure", "gcp", "server",
        "virtual machine", "vm", "storage", "cloud computing"
    ],

    "linux": [
        "linux", "ubuntu", "debian", "termux", "bash",
        "shell", "terminal", "chmod", "sudo", "apt",
        "package", "command"
    ],

    "forex": [
        "forex", "trading", "gold", "xauusd", "eurusd",
        "usd", "pip", "spread", "leverage", "lot",
        "cpi", "nfp", "fomc", "london session",
        "new york session"
    ],

    "history": [
        "history", "historical", "war", "empire",
        "king", "kingdom", "ancient", "civilization"
    ],

    "geography": [
        "geography", "country", "capital", "continent",
        "ocean", "mountain", "river", "world map",
        "location", "population"
    ],

    "languages": [
        "language", "english", "sinhala", "japanese",
        "korean", "chinese", "grammar", "translate",
        "translation", "meaning"
    ]
}


def detect_topic(message):
    text = message.lower()

    scores = {}

    for topic, keywords in TOPIC_KEYWORDS.items():
        score = 0

        for keyword in keywords:
            if keyword in text:
                score += 1

        if score > 0:
            scores[topic] = score

    if not scores:
        return "general"

    return max(scores, key=scores.get)
