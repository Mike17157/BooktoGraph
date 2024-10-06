import os
from typing import Dict
from neo4j import GraphDatabase
from .functions.theme_summarization import summarize_themes
from .functions.character_summarization import summarize_characters
from .functions.plot_summary import summarize_plot
from .functions.setting_analysis import analyze_setting
from .functions.symbol_motif_identification import identify_symbols_motifs
from ..concept_context.concept_context import ConceptContext

class BookSummarizer:
    def __init__(self):
        uri = os.environ.get("NEO4J_URI")
        user = os.environ.get("NEO4J_USER")
        password = os.environ.get("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def process_book(self, book_content: Dict):
        with self.driver.session() as session:
            book_id = session.write_transaction(self._create_book_node, book_content)
        return book_id

    def _create_book_node(self, tx, book_content: Dict):
        themes = summarize_themes(book_content)
        characters = summarize_characters(book_content)
        plot = summarize_plot(book_content)
        setting = analyze_setting(book_content)
        symbols_motifs = identify_symbols_motifs(book_content)

        query = (
            "CREATE (b:Book {title: $title}) "
            "CREATE (t:Themes {content: $themes}) "
            "CREATE (c:Characters {content: $characters}) "
            "CREATE (p:Plot {content: $plot}) "
            "CREATE (s:Setting {content: $setting}) "
            "CREATE (sm:SymbolsMotifs {content: $symbols_motifs}) "
            "CREATE (b)-[:HAS_THEMES]->(t) "
            "CREATE (b)-[:HAS_CHARACTERS]->(c) "
            "CREATE (b)-[:HAS_PLOT]->(p) "
            "CREATE (b)-[:HAS_SETTING]->(s) "
            "CREATE (b)-[:HAS_SYMBOLS_MOTIFS]->(sm) "
            "RETURN id(b) as book_id"
        )
        result = tx.run(query, 
                        title=book_content['title'],
                        themes=themes,
                        characters=characters,
                        plot=plot,
                        setting=setting,
                        symbols_motifs=symbols_motifs)
        return result.single()["book_id"]

    def apply_concept_context(self, book_id: int):
        concept_context = ConceptContext()
        with self.driver.session() as session:
            chapters = session.read_transaction(self._get_book_chapters, book_id)
        
        for chapter in chapters:
            concept_context.process_paragraph(chapter['content'], chapter['id'])
        
        concept_context.close()

    def _get_book_chapters(self, tx, book_id: int):
        query = (
            "MATCH (b:Book)-[:CONTAINS]->(c:Chapter) "
            "WHERE id(b) = $book_id "
            "RETURN id(c) as id, c.content as content, c.index as index "
            "ORDER BY c.index"
        )
        result = tx.run(query, book_id=book_id)
        return [dict(record) for record in result]

    def get_book_graph(self, book_id: int):
        concept_context = ConceptContext()
        structured_data = concept_context.get_structured_data(book_id)
        concept_context.close()
        return structured_data

    def close(self):
        self.driver.close()

# Example usage
# book_summarizer = BookSummarizer()
# book_id = book_summarizer.process_book(book_content)
# book_summarizer.apply_concept_context(book_id)
# book_graph = book_summarizer.get_book_graph(book_id)
# book_summarizer.close()
