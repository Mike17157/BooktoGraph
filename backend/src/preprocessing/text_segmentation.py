import re

def segment_by_chapters(text):
    # This is a simple implementation. You might need to adjust the regex pattern
    # based on the specific structure of your PDF
    chapters = re.split(r'\nChapter \d+', text)
    return [chapter.strip() for chapter in chapters if chapter.strip()]

def segment_by_paragraphs(text):
    # Split by double newlines or other paragraph indicators
    paragraphs = re.split(r'\n\n|\n(?=\s)', text)
    return [para.strip() for para in paragraphs if para.strip()]

def segment_text(text):
    chapters = segment_by_chapters(text)
    segmented_text = []
    for chapter in chapters:
        paragraphs = segment_by_paragraphs(chapter)
        segmented_text.append({
            'chapter': chapter,
            'paragraphs': paragraphs
        })
    return segmented_text