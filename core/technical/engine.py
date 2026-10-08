import re
from .taxonomy import TECHNICAL_TAXONOMY, GENERAL_DOMAINS


class TechnicalKnowledgeEngine:

    def __init__(self):
        self.taxonomy = TECHNICAL_TAXONOMY
        self.general_domains = GENERAL_DOMAINS
        self.concepts = {}

    def normalize(self, text):
        text = str(text or "").lower().strip()
        text = re.sub(r"\s+", "_", text)
        return text

    def detect_domain(self, text):
        text = self.normalize(text)

        aliases = {
            "programming": [
                "python", "javascript", "typescript", "java",
                "c++", "c#", "rust", "go", "php", "ruby",
                "kotlin", "swift", "programming", "coding", "code"
            ],
            "web_development": [
                "html", "css", "frontend", "backend",
                "website", "web", "api", "http"
            ],
            "databases": [
                "database", "sql", "mysql", "postgresql",
                "sqlite", "mongodb", "redis", "nosql"
            ],
            "linux": [
                "linux", "ubuntu", "debian", "bash", "shell"
            ],
            "termux": [
                "termux", "android_terminal"
            ],
            "windows": [
                "windows", "cmd", "powershell"
            ],
            "networking": [
                "network", "tcp", "ip", "dns", "router",
                "switch", "subnet", "firewall"
            ],
            "servers": [
                "server", "nginx", "apache", "deployment"
            ],
            "cloud": [
                "cloud", "aws", "azure", "gcp",
                "docker", "container"
            ],
            "vps": [
                "vps", "ssh", "virtual_private_server"
            ],
            "cybersecurity": [
                "cybersecurity", "security", "vulnerability",
                "ethical_hacking", "ctf", "secure_coding"
            ],
            "hardware": [
                "cpu", "gpu", "ram", "ssd", "hdd",
                "motherboard", "laptop", "pc", "hardware"
            ],
            "ai_ml": [
                "ai", "artificial_intelligence",
                "machine_learning", "neural_network",
                "nlp", "computer_vision"
            ],
            "vscode": [
                "vscode", "visual_studio_code", "extension"
            ],
            "app_development": [
                "android_app", "ios_app", "mobile_app",
                "app_development"
            ],
            "game_development": [
                "game", "game_development", "unity", "unreal"
            ]
        }

        for domain, keywords in aliases.items():
            if any(keyword in text for keyword in keywords):
                return domain

        for domain in GENERAL_DOMAINS:
            if domain in text:
                return domain

        return "general_knowledge"

    def register_concept(
        self,
        name,
        domain,
        topic="",
        level="basic",
        description="",
        confidence=1.0
    ):
        key = (
            f"{self.normalize(domain)}::"
            f"{self.normalize(name)}"
        )

        self.concepts[key] = {
            "name": str(name),
            "domain": self.normalize(domain),
            "topic": self.normalize(topic),
            "level": self.normalize(level),
            "description": str(description),
            "confidence": max(
                0.0,
                min(1.0, float(confidence))
            )
        }

        return self.concepts[key]

    def get_domain(self, domain):
        domain = self.normalize(domain)

        if domain in self.taxonomy:
            return {
                "priority": "core",
                "levels": [
                    "basic",
                    "intermediate",
                    "advanced"
                ],
                "topics": self.taxonomy[domain]
            }

        if domain in self.general_domains:
            return {
                "priority": "supporting",
                "levels": [
                    "basic",
                    "intermediate",
                    "advanced"
                ],
                "topics": []
            }

        return None

    def search_concepts(self, query, domain=None, limit=20):
        query = self.normalize(query)
        results = []

        for concept in self.concepts.values():

            if domain:
                if concept["domain"] != self.normalize(domain):
                    continue

            haystack = self.normalize(
                " ".join([
                    concept["name"],
                    concept["topic"],
                    concept["description"]
                ])
            )

            score = sum(
                1
                for word in query.split("_")
                if len(word) > 1 and word in haystack
            )

            if score:
                item = dict(concept)
                item["score"] = score
                results.append(item)

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results[:max(1, int(limit))]

    def stats(self):
        return {
            "technical_domains": len(
                self.taxonomy
            ),
            "general_domains": len(
                self.general_domains
            ),
            "registered_concepts": len(
                self.concepts
            )
        }


technical_brain = TechnicalKnowledgeEngine()
