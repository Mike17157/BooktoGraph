import re
from .nlp_processing import batch_add_context_with_cache

def segment_content(chapters):
    segmented_content = []
    for chapter in chapters:
        content = []
        for i, item in enumerate(chapter['content'], start=1):
            if item['type'] == 'text':
                content.append({
                    'number': i,
                    'type': 'text',
                    'data': item['data']
                })
            elif item['type'] == 'image':
                content.append({
                    'number': i,
                    'type': 'image',
                    'data': item['data'],
                    'caption': item['caption']
                })
        segmented_content.append({
            'chapter': chapter['title'],
            'content': content
        })
    return segmented_content

def further_segment_text(content, max_length=500):
    segmented_content = []
    for item in content:
        if item['type'] == 'image':
            segmented_content.append(item)
        elif item['type'] == 'text':
            if len(item['data']) <= max_length:
                segmented_content.append(item)
            else:
                # Split long text into smaller segments
                words = item['data'].split()
                current_segment = []
                current_length = 0
                segment_number = 1
                for word in words:
                    if current_length + len(word) + 1 > max_length:
                        segmented_content.append({
                            'number': f"{item['number']}.{segment_number}",
                            'type': 'text',
                            'data': ' '.join(current_segment)
                        })
                        current_segment = [word]
                        current_length = len(word)
                        segment_number += 1
                    else:
                        current_segment.append(word)
                        current_length += len(word) + 1
                if current_segment:
                    segmented_content.append({
                        'number': f"{item['number']}.{segment_number}",
                        'type': 'text',
                        'data': ' '.join(current_segment)
                    })
    return segmented_content

def segment_and_process(chapters, max_text_length=500):
    segmented_content = segment_content(chapters)
    for chapter in segmented_content:
        chapter['content'] = further_segment_text(chapter['content'], max_text_length)
    return segmented_content