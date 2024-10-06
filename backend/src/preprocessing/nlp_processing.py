import spacy
import anthropic
from typing import List
import os

# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def batch_correct_text(texts: List[str], batch_size: int = 10) -> List[str]:
    corrected_texts = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        prompt = "Human: Correct any obvious errors in the following texts without changing their meaning or adding new information. Separate each corrected text with '---'.\n\n"
        for text in batch:
            prompt += f"Text: {text}\n\n"
        prompt += "Assistant: Here are the corrected texts, separated by '---':\n\n"
        
        response = client.completions.create(
            model="claude-2.0-haiku",
            prompt=prompt,
            max_tokens_to_sample=1000 * len(batch),
            temperature=0.3,
        )
        
        corrected_batch = response.completion.strip().split("---")
        corrected_texts.extend([text.strip() for text in corrected_batch])
    
    return corrected_texts