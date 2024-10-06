import os
import spacy
from collections import defaultdict
from neo4j import GraphDatabase

nlp = spacy.load("en_core_web_sm")

class ConceptContext:
    def __init__(self):
        uri = os.environ.get("NEO4J_URI")
        user = os.environ.get("NEO4J_USER")
        password = os.environ.get("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.subject_significance = defaultdict(int)

    def process_paragraph(self, paragraph_text, paragraph_id):
        doc = nlp(paragraph_text)
        
        with self.driver.session() as session:
            session.write_transaction(self._process_paragraph_transaction, doc, paragraph_id)

    def _process_paragraph_transaction(self, tx, doc, paragraph_id):
        for sent in doc.sents:
            self._extract_elements(tx, sent, paragraph_id)

    def _extract_elements(self, tx, sentence, paragraph_id):
        subjects = []
        actions = []
        for token in sentence:
            if token.dep_ == "nsubj":
                subject = self._get_span_with_objects(token)
                action = self._get_verb_phrase(token.head)
                subjects.append(subject)
                actions.append(action)
                self._add_subject_action(tx, subject, action, paragraph_id)
            elif token.dep_ == "ROOT" and token.pos_ == "VERB":
                action = self._get_verb_phrase(token)
                actions.append(action)

        self._extract_relationships(tx, sentence, paragraph_id, subjects, actions)

    def _get_span_with_objects(self, token):
        span = [token]
        for child in token.subtree:
            if child.dep_ in ["dobj", "pobj"]:
                span.extend(list(child.subtree))
        return " ".join([t.text for t in sorted(span, key=lambda x: x.i)])

    def _get_verb_phrase(self, verb):
        phrase = [verb]
        for child in verb.children:
            if child.dep_ in ["aux", "neg", "prt"]:
                phrase.append(child)
        return " ".join([t.text for t in sorted(phrase, key=lambda x: x.i)])

    def _add_subject_action(self, tx, subject, action, paragraph_id):
        query = (
            "MERGE (s:Subject {name: $subject}) "
            "ON CREATE SET s.paragraphs = [$paragraph_id] "
            "ON MATCH SET s.paragraphs = s.paragraphs + $paragraph_id "
            "MERGE (a:Action {name: $action}) "
            "ON CREATE SET a.paragraphs = [$paragraph_id] "
            "ON MATCH SET a.paragraphs = a.paragraphs + $paragraph_id "
            "MERGE (s)-[:PERFORMS]->(a) "
            "WITH s "
            "MATCH (p:Paragraph {index: $paragraph_id}) "
            "MERGE (p)-[:CONTAINS]->(s)"
        )
        tx.run(query, subject=subject, action=action, paragraph_id=paragraph_id)
        self.subject_significance[subject] += 1

    def _extract_relationships(self, tx, sentence, paragraph_id, subjects, actions):
        for token in sentence:
            if token.dep_ in ["prep", "agent"]:
                head = token.head.text
                tail = list(token.children)[0].text if list(token.children) else token.text
                relation = token.text
                
                if head in subjects or head in actions:
                    query = (
                        "MATCH (h {name: $head}) "
                        "MERGE (t:Object {name: $tail}) "
                        "ON CREATE SET t.paragraphs = [$paragraph_id] "
                        "ON MATCH SET t.paragraphs = t.paragraphs + $paragraph_id "
                        "MERGE (h)-[:RELATES {type: $relation}]->(t) "
                        "WITH t "
                        "MATCH (p:Paragraph {index: $paragraph_id}) "
                        "MERGE (p)-[:CONTAINS]->(t)"
                    )
                    tx.run(query, head=head, tail=tail, relation=relation, paragraph_id=paragraph_id)

    def get_structured_data(self, chapter_id):
        with self.driver.session() as session:
            return session.read_transaction(self._get_structured_data_transaction, chapter_id)

    def _get_structured_data_transaction(self, tx, chapter_id):
        query = (
            "MATCH (c:Chapter)-[:CONTAINS]->(p:Paragraph)-[:CONTAINS]->(n) "
            "WHERE id(c) = $chapter_id "
            "RETURN p.index AS paragraph_index, collect(n) AS nodes, "
            "collect((n)-[r]->(m) WHERE m <> p) AS relationships"
        )
        result = tx.run(query, chapter_id=chapter_id)
        structured_data = {
            "paragraph_graphs": {},
            "global_graph": {"nodes": [], "links": []},
            "subject_significance": dict(self.subject_significance)
        }

        for record in result:
            paragraph_index = record["paragraph_index"]
            nodes = record["nodes"]
            relationships = record["relationships"]

            paragraph_graph = {"nodes": [], "links": []}
            for node in nodes:
                node_data = dict(node)
                paragraph_graph["nodes"].append(node_data)
                structured_data["global_graph"]["nodes"].append(node_data)

            for rel in relationships:
                rel_data = {
                    "source": rel.start_node["name"],
                    "target": rel.end_node["name"],
                    "type": rel.type
                }
                paragraph_graph["links"].append(rel_data)
                structured_data["global_graph"]["links"].append(rel_data)

            structured_data["paragraph_graphs"][paragraph_index] = paragraph_graph

        return structured_data

    def close(self):
        self.driver.close()

# Example usage
# concept_context = ConceptContext()
# concept_context.process_paragraph("John quickly ran to the store. He bought some milk.", 0)
# concept_context.process_paragraph("The store was closing soon. John hurried back home.", 1)
# structured_data = concept_context.get_structured_data()
# concept_context.close()
