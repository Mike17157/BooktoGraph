import fitz  # PyMuPDF
import PyPDF2
import io
from PIL import Image
import pytesseract
import re
import base64
from .nlp_processing import batch_correct_text

# Remove the Anthropic client initialization

def extract_content_from_pdf(pdf_path):
    chapters = []
    current_chapter = {"title": "", "content": []}
    current_paragraph = ""

    doc = fitz.open(pdf_path)
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] == 0:  # Text block
                text = " ".join([line["spans"][0]["text"] for line in block["lines"]])
                if re.match(r'^Chapter \d+', text):
                    if current_chapter["content"]:
                        chapters.append(current_chapter)
                    current_chapter = {"title": text, "content": []}
                    current_paragraph = ""
                elif current_paragraph:
                    current_paragraph += " " + text
                else:
                    current_paragraph = text
                
                if current_paragraph:
                    current_chapter["content"].append({"type": "text", "data": current_paragraph})
                    current_paragraph = ""
            
            elif block["type"] == 1:  # Image block
                image_rect = fitz.Rect(block["bbox"])
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=image_rect)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Convert image to base64
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # Extract image description (caption) if available
                caption = ""
                if block.get("lines"):
                    caption = " ".join([span["text"] for line in block["lines"] for span in line["spans"]])
                
                current_chapter["content"].append({
                    "type": "image",
                    "data": img_str,
                    "caption": caption
                })

    if current_chapter["content"]:
        chapters.append(current_chapter)

    doc.close()
    return chapters

def preprocess_text(text):
    # Remove unnecessary artifacts
    cleaned_text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespaces with a single space
    cleaned_text = re.sub(r'[^\x00-\x7F]+', '', cleaned_text)  # Remove non-ASCII characters
    cleaned_text = cleaned_text.strip()  # Remove leading and trailing whitespaces
    return cleaned_text

# Remove the correct_text_with_llm function

def extract_and_preprocess(pdf_path):
    raw_chapters = extract_content_from_pdf(pdf_path)
    preprocessed_chapters = []
    for chapter in raw_chapters:
        preprocessed_content = []
        texts_to_correct = []
        for item in chapter["content"]:
            if item["type"] == "text":
                preprocessed_text = preprocess_text(item["data"])
                texts_to_correct.append(preprocessed_text)
            elif item["type"] == "image":
                preprocessed_content.append(item)  # Keep images as they are
        
        corrected_texts = batch_correct_text(texts_to_correct)
        
        for corrected_text in corrected_texts:
            preprocessed_content.append({"type": "text", "data": corrected_text})
        
        preprocessed_chapters.append({
            "title": chapter["title"],
            "content": preprocessed_content
        })
    return preprocessed_chapters

def extract_text_with_formatting(pdf_path):
    text_blocks = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block["type"] == 0:  # Type 0 is text
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text_blocks.append({
                                "text": span["text"],
                                "font": span["font"],
                                "size": span["size"],
                                "color": span["color"]
                            })
    return text_blocks