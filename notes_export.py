import re


def build_topic_notes_markdown(topic_name, questions, progress):
    lines = [f'# {topic_name} Notes']

    for question in questions:
        question_id = str(question.get('_id'))
        note = (progress.get(question_id, {}) or {}).get('notes', '').strip()
        if not note:
            continue

        problem = question.get('problem') or 'Untitled Problem'
        lines.extend(['', f'## {problem}', '', note])

    return '\n'.join(lines) + '\n'


def topic_notes_filename(topic_name):
    slug = re.sub(r'[^a-zA-Z0-9]+', '_', topic_name).strip('_').lower()
    return f'{slug or "topic"}_notes.md'
