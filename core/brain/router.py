import re


class ZoroxBrainRouter:
    """
    ZOROX AI central intent router.

    This layer does not generate the final answer.
    It identifies language, domain, and useful routing signals.
    """

    def detect_language(self, text):
        if not text:
            return "unknown"

        sinhala = len(re.findall(r"[\u0D80-\u0DFF]", text))
        latin = len(re.findall(r"[A-Za-z]", text))

        if sinhala and latin:
            return "si-en"

        if sinhala:
            return "si"

        if latin:
            return "en"

        return "unknown"

    def detect_domain(self, text):
        value = text.lower()

        domains = {
            "programming": [
                "python", "javascript", "typescript", "java",
                "c++", "c#", "golang", "rust", "php", "kotlin",
                "swift", "code", "coding", "programming",
                "function", "class", "variable", "algorithm",
                "debug", "bug", "error"
            ],

            "web_development": [
                "html", "css", "website", "web app", "frontend",
                "backend", "react", "next.js", "node.js", "flask",
                "django", "api", "rest api", "web development"
            ],

            "cybersecurity": [
                "cybersecurity", "cyber security", "ethical hacking",
                "security", "vulnerability", "owasp", "firewall",
                "malware", "phishing", "soc", "siem", "ctf"
            ],

            "operating_systems": [
                "windows", "linux", "ubuntu", "debian", "termux",
                "cmd", "powershell", "bash", "terminal",
                "driver", "process", "service"
            ],

            "hardware": [
                "cpu", "gpu", "ram", "ssd", "hdd", "nvme",
                "motherboard", "bios", "uefi", "psu",
                "processor", "graphics card", "computer hardware"
            ],

            "networking": [
                "network", "networking", "router", "switch",
                "wifi", "wi-fi", "ethernet", "dns", "dhcp",
                "ip address", "tcp", "udp", "vlan", "vpn"
            ],

            "cloud": [
                "cloud", "aws", "azure", "google cloud",
                "virtual machine", "docker", "kubernetes",
                "cloud computing"
            ],

            "ai_ml": [
                "artificial intelligence", "ai", "machine learning",
                "deep learning", "neural network", "llm",
                "rag", "embedding", "model training"
            ],

            "image": [
                "image", "picture", "photo", "draw", "design",
                "generate image", "create image", "logo"
            ],

            "software_development": [
                "software", "application", "app development",
                "architecture", "database", "git", "github",
                "deployment", "devops", "testing"
            ],

            "general": []
        }

        scores = {}

        for domain, keywords in domains.items():
            score = 0

            for keyword in keywords:
                if keyword in value:
                    score += 1

            scores[domain] = score

        best_domain = max(scores, key=scores.get)

        if scores[best_domain] == 0:
            return "general"

        return best_domain

    def detect_intent(self, text):
        value = text.lower()

        if any(x in value for x in [
            "remember this",
            "remember that",
            "මතක තියාගන්න",
            "මතක තියාගන්නකෝ"
        ]):
            return "remember"

        if any(x in value for x in [
            "forget this",
            "forget that",
            "forget",
            "අමතක කරන්න"
        ]):
            return "forget"

        if any(x in value for x in [
            "fix", "error", "not working", "broken",
            "වැඩ නැහැ", "වැඩ කරන්නෙ නැහැ", "error එක"
        ]):
            return "troubleshoot"

        if any(x in value for x in [
            "how to", "how do i", "කොහොමද", "කොහොමද කරන්නෙ"
        ]):
            return "how_to"

        if any(x in value for x in [
            "what is", "what are", "explain",
            "මොකක්ද", "මොනවද", "විස්තර කරන්න"
        ]):
            return "explain"

        if any(x in value for x in [
            "create", "build", "make", "develop",
            "හදන්න", "හදමු", "develop කරන්න"
        ]):
            return "create"

        return "conversation"

    def route(self, text):
        return {
            "language": self.detect_language(text),
            "domain": self.detect_domain(text),
            "intent": self.detect_intent(text),
        }


brain_router = ZoroxBrainRouter()
