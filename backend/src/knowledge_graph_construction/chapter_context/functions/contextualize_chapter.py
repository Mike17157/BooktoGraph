import anthropic
import os
from typing import Dict
from .contextualize_paragraph import contextualize_paragraph
from .contextualize_image import contextualize_image

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def contextualize_chapter_content(chapter: Dict) -> Dict:
    contextualized_content = []
    chapter_content = " ".join([item['data'] for item in chapter['content'] if item['type'] == 'text'])
    
    for item in chapter['content']:
        if item['type'] == 'text':
            context = contextualize_paragraph(item['data'], chapter['title'], chapter_content)
            contextualized_content.append({
                'number': item['number'],
                'type': 'text',
                'data': item['data'],
                'context': context
            })
        elif item['type'] == 'image':
            context = contextualize_image(item['caption'], chapter['title'], chapter_content)
            contextualized_content.append({
                'number': item['number'],
                'type': 'image',
                'data': item['data'],
                'caption': item['caption'],
                'context': context
            })
    
    return {
        'title': chapter['title'],
        'content': contextualized_content
    }