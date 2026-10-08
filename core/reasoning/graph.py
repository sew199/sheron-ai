import json
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

GRAPH_FILE = os.path.join(
    BASE_DIR,
    "data",
    "knowledge",
    "concept_graph.json"
)


class ConceptGraph:

    def __init__(self):
        self.concepts = {}
        self.relationships = []

    def add_concept(self, name):
        key = str(name).strip().lower()

        if key:
            self.concepts[key] = {
                "name": name
            }

    def add_relationship(
        self,
        subject,
        relation,
        object_,
        confidence=1.0
    ):
        self.relationships.append({
            "subject": str(subject).strip().lower(),
            "relation": str(relation).strip().lower(),
            "object": str(object_).strip().lower(),
            "confidence": confidence
        })

    def save(self):
        os.makedirs(
            os.path.dirname(GRAPH_FILE),
            exist_ok=True
        )

        with open(
            GRAPH_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                {
                    "concepts": self.concepts,
                    "relationships": self.relationships
                },
                file,
                indent=2,
                ensure_ascii=False
            )

    def load(self):
        if not os.path.exists(GRAPH_FILE):
            return

        try:
            with open(
                GRAPH_FILE,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            self.concepts = data.get(
                "concepts",
                {}
            )

            self.relationships = data.get(
                "relationships",
                []
            )

        except (OSError, json.JSONDecodeError):
            pass


concept_graph = ConceptGraph()
