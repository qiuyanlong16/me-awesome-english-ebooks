"""HTML Generator: generate daily reading pages and metadata."""

import os
import re
import json
from datetime import datetime
from scripts.annotate import split_into_days, annotate_text
from scripts.extract import extract_pdf
from scripts.dictionary import Dictionary


def clean_definition(def_text):
    """Clean HTML tags and truncation from definitions."""
    # Remove HTML tags
    cleaned = re.sub(r'<[^>]+>', '', def_text)
    # Remove inflection lines like "时 态:", "副 词:", "名 词:", "比较级:"
    cleaned = re.sub(r'时\s*态[:：]\s*[^,，]+', '', cleaned)
    cleaned = re.sub(r'副\s*词[:：]\s*[^,，]+', '', cleaned)
    cleaned = re.sub(r'名\s*词[:：]\s*[^,，]+', '', cleaned)
    cleaned = re.sub(r'形\s*容\s*词[:：]\s*[^,，]+', '', cleaned)
    cleaned = re.sub(r'比较级[:：]\s*[^,，]+', '', cleaned)
    # Remove orphaned punctuation at end
    cleaned = cleaned.strip().rstrip('；,，.。')
    return cleaned[:80] if cleaned else '—'


def generate_day_page(date_str, day_paras, day_num, total_days, dictionary, issue_dir):
    """Generate a single daily reading page."""
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'template', 'page.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Get title and section from first paragraph
    title = day_paras[0]['title'] if day_paras else 'Reading'
    section = day_paras[0]['section'] if day_paras else ''

    # Annotate each paragraph and collect glossary
    body_html = ''
    all_glossary = []

    for para in day_paras:
        annotated, glossary = annotate_text(para['body'], dictionary)
        all_glossary.extend(glossary)

        # Wrap paragraphs in <p> tags
        # Group consecutive paragraphs from the same article
        para_html = annotated.replace('\n', '<br>')
        body_html += f'<p>{para_html}</p>\n'

    # Generate glossary rows
    glossary_rows = ''
    for word, phonetic, pos, definition in all_glossary:
        def_clean = clean_definition(definition)
        phon = phonetic if phonetic else '—'
        pos_tag = pos if pos else ''
        glossary_rows += f'<tr><td>{word}</td><td>{phon} {pos_tag}</td><td>{def_clean}</td></tr>\n'

    # Navigation links
    prev_link = ''
    next_link = ''
    if day_num > 1:
        prev_link = f'<a href="day{day_num-1}.html" class="nav-btn">← Day {day_num-1}</a>'
    if day_num < total_days:
        next_link = f'<a href="day{day_num+1}.html" class="nav-btn">Day {day_num+1} →</a>'

    # Progress text
    progress = f'Day {day_num} of {total_days}'

    # Fill template
    today = datetime.now().strftime('%Y-%m-%d')
    html = template
    html = html.replace('{{DATE}}', date_str)
    html = html.replace('{{TITLE}}', title)
    html = html.replace('{{SECTION}}', section)
    html = html.replace('{{BODY}}', body_html)
    html = html.replace('{{GLOSSARY_ROWS}}', glossary_rows)
    html = html.replace('{{PREV_LINK}}', prev_link)
    html = html.replace('{{NEXT_LINK}}', next_link)
    html = html.replace('{{PROGRESS}}', progress)
    html = html.replace('{{GENERATED_DATE}}', today)

    # Write page
    page_path = os.path.join(issue_dir, f'day{day_num}.html')
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return len(all_glossary)


def generate_issue(pdf_path, output_base, dict_path):
    """
    Process a PDF and generate all daily reading pages.

    Args:
        pdf_path: path to the PDF file
        output_base: base directory for output (docs/issues/)
        dict_path: path to user dictionary JSON

    Returns:
        issue_date: str, date of the issue
        total_days: int
    """
    dictionary = Dictionary(dict_path)

    # Extract text
    date_str, articles = extract_pdf(pdf_path)
    issue_dir = os.path.join(output_base, date_str)
    os.makedirs(issue_dir, exist_ok=True)

    # Split into days
    days = split_into_days(articles, words_per_day=1800)
    total_days = len(days)

    # Generate each day's page
    total_vocab = 0
    for i, day_paras in enumerate(days):
        day_num = i + 1
        vocab_count = generate_day_page(
            date_str, day_paras, day_num, total_days, dictionary, issue_dir
        )
        total_vocab += vocab_count
        print(f"  Generated day {day_num}/{total_days} ({vocab_count} vocab words)")

    # Write metadata
    meta = {
        'date': date_str,
        'total_days': total_days,
        'total_articles': len(articles),
        'total_vocab': total_vocab,
        'last_read_day': 1,
    }
    meta_path = os.path.join(issue_dir, 'meta.json')
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"\nGenerated {total_days} daily pages in {issue_dir}")
    print(f"Total vocabulary annotations: {total_vocab}")

    return date_str, total_days
