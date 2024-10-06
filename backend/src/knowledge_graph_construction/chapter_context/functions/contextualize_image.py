import anthropic
import os

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def contextualize_image(caption: str, chapter_title: str, chapter_content: str) -> str:
    prompt = f"""<context>
    <chapter_title>{chapter_title}</chapter_title>
    <chapter_content>
    {chapter_content}
    </chapter_content>
    </context>

    <image_caption>
    {caption}
    </image_caption>

    <instructions>
    Provide a succinct description (1-2 sentences) of how this image relates to the chapter content.
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
                "content": "Contextualize the image."
            }
        ],
        headers={"anthropic-beta": "prompt-caching-2024-07-31"}
    )
    return response.content[0].text.strip()