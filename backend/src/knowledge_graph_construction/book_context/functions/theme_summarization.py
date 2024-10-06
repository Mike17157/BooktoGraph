import anthropic

client = anthropic.Anthropic()

def summarize_themes(book_content):
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        system="You are a literary analyst specializing in theme identification.",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": "Summarize the main themes of this book:", "cache_control": {"type": "ephemeral"}},
                {"type": "text", "text": book_content, "cache_control": {"type": "ephemeral"}}
            ]}
        ],
        headers={"anthropic-beta": "prompt-caching-2024-07-31"}
    )
    return response.content[0].text