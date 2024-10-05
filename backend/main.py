import os
from flask import Flask, request, jsonify
from neo4j import GraphDatabase
from dotenv import load_dotenv
from transformers import pipeline
from src.preprocessing.text_extraction import extract_and_preprocess
from src.preprocessing.text_segmentation import segment_text
from src.nlp_processing import analyze_text

# Change the working directory to the backend folder
os.chdir(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

app = Flask(__name__)

# Neo4j connection
uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")
driver = GraphDatabase.driver(uri, auth=(user, password))

# Load LLM
nlp = pipeline("text2text-generation", model="t5-small")

@app.teardown_appcontext
def shutdown_driver(exception=None):
    driver.close()

@app.route('/')
def read_root():
    return jsonify({"message": "Welcome to the Knowledge Graph LLM API"})

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    pdf_filename = request.json.get('pdf_filename')
    if not pdf_filename:
        return jsonify({"error": "No PDF filename provided"}), 400

    pdf_path = os.path.join('..', 'data', 'pdfs', pdf_filename)
    if not os.path.exists(pdf_path):
        return jsonify({"error": "PDF file not found"}), 404

    # Extract and preprocess text
    preprocessed_text = extract_and_preprocess(pdf_path)

    # Segment text
    segmented_text = segment_text(preprocessed_text)

    # Analyze text
    analyzed_chapters = []
    for chapter in segmented_text:
        analyzed_paragraphs = [analyze_text(para) for para in chapter['paragraphs']]
        analyzed_chapters.append({
            'chapter': chapter['chapter'],
            'analyzed_paragraphs': analyzed_paragraphs
        })

    return jsonify({"analyzed_text": analyzed_chapters})

@app.route('/query', methods=['POST'])
def query_knowledge_graph():
    query = request.json.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Process the query using the LLM
    processed_query = nlp(query, max_length=50)[0]['generated_text']

    # Query the Neo4j database
    with driver.session() as session:
        result = session.run(processed_query)
        records = [record.data() for record in result]

    return jsonify({"query": query, "processed_query": processed_query, "results": records})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)