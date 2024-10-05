import spacy

nlp = spacy.load("en_core_web_sm")

def process_text(text):
    doc = nlp(text)
    return doc

def extract_entities(doc):
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

def extract_key_concepts(doc):
    # This is a simple implementation. You might want to refine this based on your needs.
    concepts = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop]
    return list(set(concepts))  # Remove duplicates

def analyze_text(text):
    doc = process_text(text)
    entities = extract_entities(doc)
    concepts = extract_key_concepts(doc)
    return {
        'entities': entities,
        'concepts': concepts
    }