import anthropic

client = anthropic.Anthropic()

def identify_symbols_motifs(book_content):
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        system="You are a literary analyst specializing in symbol and motif identification.",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": "Identify the main symbols and motifs in this book:", "cache_control": {"type": "ephemeral"}},
                {"type": "text", "text": book_content, "cache_control": {"type": "ephemeral"}}
            ]}
        ],
        headers={"anthropic-beta": "prompt-caching-2024-07-31"}
    )
    return response.content[0].text