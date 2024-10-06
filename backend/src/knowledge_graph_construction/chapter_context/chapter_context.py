import os
from typing import Dict
from neo4j import GraphDatabase
from .functions.contextualize_chapter import contextualize_chapter_content
from .functions.summarize_chapter import summarize_chapter
from ..concept_context.concept_context import ConceptContext

class ChapterSummarizer:
    def __init__(self):
        uri = os.environ.get("NEO4J_URI")
        user = os.environ.get("NEO4J_USER")
        password = os.environ.get("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def process_chapter(self, chapter: Dict):
        contextualized_chapter = contextualize_chapter_content(chapter)
        summary = summarize_chapter(chapter)
        
        with self.driver.session() as session:
            chapter_id = session.write_transaction(self._create_chapter_node, contextualized_chapter, summary)
        
        return chapter_id

    def _create_chapter_node(self, tx, chapter: Dict, summary: str):
        query = (
            "CREATE (c:Chapter {title: $title, summary: $summary}) "
            "WITH c "
            "UNWIND $content AS item "
            "CREATE (p:Paragraph {text: item.data, context: item.context, index: item.index}) "
            "CREATE (c)-[:CONTAINS]->(p) "
            "RETURN id(c) as chapter_id"
        )
        content = [
            {"data": item['data'], "context": item['context'], "index": i}
            for i, item in enumerate(chapter['content'])
        ]
        result = tx.run(query, title=chapter['title'], summary=summary, content=content)
        return result.single()["chapter_id"]

    def apply_concept_context(self, chapter_id: int):
        concept_context = ConceptContext()
        with self.driver.session() as session:
            paragraphs = session.read_transaction(self._get_chapter_paragraphs, chapter_id)
        
        for paragraph in paragraphs:
            concept_context.process_paragraph(paragraph['text'], paragraph['id'])
        
        concept_context.close()

    def _get_chapter_paragraphs(self, tx, chapter_id: int):
        query = (
            "MATCH (c:Chapter)-[:CONTAINS]->(p:Paragraph) "
            "WHERE id(c) = $chapter_id "
            "RETURN id(p) as id, p.text as text, p.index as index "
            "ORDER BY p.index"
        )
        result = tx.run(query, chapter_id=chapter_id)
        return [dict(record) for record in result]

    def get_chapter_graph(self, chapter_id: int):
        concept_context = ConceptContext()
        structured_data = concept_context.get_structured_data(chapter_id)
        concept_context.close()
        return structured_data

    def close(self):
        self.driver.close()