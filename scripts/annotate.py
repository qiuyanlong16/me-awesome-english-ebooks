"""Vocabulary Annotator: identify advanced words in text and annotate them."""

import re
import html
from scripts.dictionary import Dictionary

# Words that should never be annotated (too common, proper nouns, etc.)
NEVER_ANNOTATE = {
    'The', 'A', 'An', 'I', 'We', 'You', 'They', 'He', 'She', 'It',
    'Mr', 'Mrs', 'Ms', 'Dr', 'St', 'No', 'Yes',
}


def split_words(text):
    """
    Split text into word tokens with their positions.
    Returns list of (word, start_pos, end_pos).
    Only considers alphabetic words (ignores numbers, punctuation).
    """
    tokens = []
    for match in re.finditer(r"[a-zA-Z']+", text):
        word = match.group().strip("'")
        if word and all(c.isalpha() or c == "'" for c in word):
            tokens.append((word, match.start(), match.end()))
    return tokens


def annotate_text(body, dictionary, max_annotations=None):
    """
    Annotate advanced words in a text body.

    Args:
        body: str, the article text
        dictionary: Dictionary instance
        max_annotations: int, max words to annotate per body (None = unlimited)

    Returns:
        annotated_body: str with HTML spans around annotated words
        glossary: list of (word, phonetic, pos, definition) for the glossary box
    """
    tokens = split_words(body)
    annotated_words = set()
    glossary = []
    # We'll collect replacements as (start, end, replacement)
    replacements = []

    for word, start, end in tokens:
        # Skip very short words, proper nouns (capitalized in middle of sentence), etc.
        if len(word) < 3:
            continue
        if word in NEVER_ANNOTATE:
            continue
        if word.istitle() and start > 0 and body[start-1].isalpha():
            continue

        # Check if dictionary has this word
        result = dictionary.lookup(word)
        if result is None:
            continue

        phonetic, pos, definition = result
        if not phonetic and not definition:
            continue

        # Skip if already annotated
        word_lower = word.lower()
        if word_lower in annotated_words:
            continue

        annotated_words.add(word_lower)

        if max_annotations and len(glossary) >= max_annotations:
            break

        glossary.append((word_lower, phonetic, pos, definition))

        # Create HTML span for the word
        replacement = f'<span class="annot">{html.escape(word)}</span>'
        replacements.append((start, end, replacement))

    # Apply replacements in reverse order to preserve positions
    annotated = body
    for start, end, replacement in reversed(replacements):
        annotated = annotated[:start] + replacement + annotated[end:]

    return annotated, glossary


def split_into_days(articles, words_per_day=1800):
    """
    Split articles into daily reading chunks of approximately words_per_day words.
    Always splits at paragraph boundaries.

    Args:
        articles: list of article dicts
        words_per_day: target word count per day

    Returns:
        days: list of lists of (article_title, article_section, article_body_chunk)
    """
    # Flatten articles into paragraphs
    paragraphs = []
    for article in articles:
        title = article['title']
        section = article['section']
        body = article['body']
        # Split body into paragraphs
        paras = re.split(r'\n\n+', body)
        for para in paras:
            para = para.strip()
            if len(para) > 20:
                paragraphs.append({
                    'title': title,
                    'section': section,
                    'body': para,
                    'word_count': len(para.split()),
                })

    # Group into days
    days = []
    current_day = []
    current_count = 0

    for para in paragraphs:
        if current_count + para['word_count'] > words_per_day and current_day:
            days.append(current_day)
            current_day = []
            current_count = 0

        current_day.append(para)
        current_count += para['word_count']

    if current_day:
        days.append(current_day)

    return days
