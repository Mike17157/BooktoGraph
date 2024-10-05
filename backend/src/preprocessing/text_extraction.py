import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def preprocess_text(text):
    # Remove unnecessary artifacts (this is a basic implementation)
    cleaned_text = text.replace('\n', ' ').replace('\r', '')
    return ' '.join(cleaned_text.split())

def extract_and_preprocess(pdf_path):
    raw_text = extract_text_from_pdf(pdf_path)
    preprocessed_text = preprocess_text(raw_text)
    return preprocessed_text