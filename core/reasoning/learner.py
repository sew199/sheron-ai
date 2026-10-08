from .parser import concept_parser
from .graph import concept_graph


class ConceptLearner:

    def learn_from_text(self, text):
        relationships = concept_parser.parse(text)

        learned = []

        for item in relationships:
            concept_graph.add_concept(
                item["subject"]
            )

            concept_graph.add_concept(
                item["object"]
            )

            concept_graph.add_relationship(
                item["subject"],
                item["relation"],
                item["object"],
                item["confidence"]
            )

            learned.append(item)

        if learned:
            concept_graph.save()

        return learned


concept_learner = ConceptLearner()
