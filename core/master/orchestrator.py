from core.language.detector import detect_language, language_instruction
from core.technical import technical_brain

try:
    from core.brain.router import route
except Exception:
    route = None

try:
    from core.reasoning.parser import concept_parser
except Exception:
    concept_parser = None

try:
    from core.reasoning.pipeline import reasoning_pipeline
except Exception:
    reasoning_pipeline = None

try:
    from core.coding.universal.engine import universal_programming_engine
except Exception:
    universal_programming_engine = None


class ZoroxMasterBrain:

    def __init__(self):
        self.name = "ZOROX MASTER BRAIN"
        self.version = "3.0"

    def analyze(self, message, user_id=None):
        text = str(message or "").strip()

        if not text:
            return {
                "ok": False,
                "error": "Empty input"
            }

        language = detect_language(text)
        instruction = language_instruction(text)

        domain = technical_brain.detect_domain(text)
        domain_info = technical_brain.get_domain(domain)

        concepts = []

        if concept_parser:
            try:
                concepts = concept_parser.parse(text)
            except Exception:
                concepts = []

        return {
            "ok": True,
            "brain": self.name,
            "version": self.version,
            "language": language,
            "language_instruction": instruction,
            "domain": domain,
            "domain_info": domain_info,
            "concepts": concepts,
            "user_id": user_id,
            "pipeline": [
                "perception",
                "language_detection",
                "domain_routing",
                "concept_extraction",
                "knowledge_lookup",
                "reasoning",
                "validation",
                "learning"
            ]
        }

    def learn_concepts(self, text):
        if not concept_parser or not reasoning_pipeline:
            return {
                "ok": False,
                "reason": "Reasoning engine unavailable"
            }

        relationships = concept_parser.parse(text)

        if not relationships:
            return {
                "ok": True,
                "relationships": [],
                "message": "No supported relationships detected"
            }

        try:
            result = reasoning_pipeline.process(
                relationships
            )
            return {
                "ok": True,
                "relationships": relationships,
                "reasoning": result
            }
        except Exception as error:
            return {
                "ok": False,
                "error": str(error)
            }

    def analyze_code(self, code, language=None):
        if not universal_programming_engine:
            return {
                "ok": False,
                "reason": "Programming engine unavailable"
            }

        try:
            result = universal_programming_engine.learn(
                code,
                language=language
            )

            return {
                "ok": True,
                "programming": result
            }

        except Exception as error:
            return {
                "ok": False,
                "error": str(error)
            }

    def health(self):
        return {
            "brain": self.name,
            "version": self.version,
            "status": "online",
            "technical_domains": len(
                technical_brain.taxonomy
            ),
            "general_domains": len(
                technical_brain.general_domains
            ),
            "modules": {
                "language": True,
                "technical_brain": True,
                "concept_parser": concept_parser is not None,
                "reasoning_pipeline": reasoning_pipeline is not None,
                "programming_engine": universal_programming_engine is not None
            }
        }


master_brain = ZoroxMasterBrain()
