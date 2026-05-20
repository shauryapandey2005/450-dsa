from notes_export import build_topic_notes_markdown, topic_notes_filename


def test_topic_notes_markdown_includes_only_questions_with_notes():
    questions = [
        {'_id': 'q1', 'problem': 'Two Sum'},
        {'_id': 'q2', 'problem': 'Missing Number'},
        {'_id': 'q3', 'problem': 'Kadane Algorithm'},
    ]
    progress = {
        'q1': {'notes': 'Use a hash map.'},
        'q2': {'notes': '   '},
        'q3': {'done': True},
    }

    markdown = build_topic_notes_markdown('Arrays', questions, progress)

    assert markdown == '# Arrays Notes\n\n## Two Sum\n\nUse a hash map.\n'
    assert 'Missing Number' not in markdown
    assert 'Kadane Algorithm' not in markdown


def test_topic_notes_markdown_falls_back_for_untitled_problem():
    markdown = build_topic_notes_markdown('Graphs', [{'_id': 'q1'}], {'q1': {'notes': 'BFS first.'}})

    assert '## Untitled Problem' in markdown
    assert 'BFS first.' in markdown


def test_topic_notes_filename_sanitizes_topic_name():
    assert topic_notes_filename('Dynamic Programming & Greedy!') == 'dynamic_programming_greedy_notes.md'
    assert topic_notes_filename('***') == 'topic_notes.md'
