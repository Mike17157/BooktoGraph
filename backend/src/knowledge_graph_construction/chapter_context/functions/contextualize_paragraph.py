import anthropic
import os

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def contextualize_paragraph(paragraph: str, chapter_title: str, chapter_content: str) -> str:
    prompt = f"""<context>
    <chapter_title>{chapter_title}</chapter_title>
    <chapter_content>
    {chapter_content}
    </chapter_content>
    </context>

    <paragraph>
    {paragraph}
    </paragraph>

    <instructions>
    Provide a succinct description (1-2 sentences) of what is happening in the above paragraph within the context of the chapter.
    </instructions>

    <output_format>
    Succinct description:
    </output_format>"""

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=100,
        system=[
            {
                "type": "text",
                "text": prompt,
                "cache_control": {"type": "ephemeral"}
            }
        ],
        messages=[
            {
                "role": "user",
                "content": "Contextualize the paragraph."
            }
        ],
        headers={"anthropic-beta": "prompt-caching-2024-07-31"}
    )
    return response.content[0].text.strip()