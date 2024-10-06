import anthropic
import os
from typing import Dict

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def summarize_chapter(chapter: Dict) -> str:
    chapter_text = ' '.join([item['data'] for item in chapter['content'] if item['type'] == 'text'])
    
    prompt = f"""Provide a succinct summary of the following chapter. Focus on the main characters and key themes. Do not include any information that is not explicitly stated in the chapter content.

    Chapter Title: {chapter['title']}

    Chapter Content:
    {chapter_text}

    Succinct Summary (Focusing on characters and themes):"""

    response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()