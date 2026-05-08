"""PDF Extractor: extract text from Economist PDF, filter blank/ad pages, segment into articles."""

import re
import fitz  # PyMuPDF

# Patterns to detect ad pages
AD_PATTERNS = [
    'Duolingo', 'Notability', 'App 推荐', 'App推荐', '英语学习',
    '高效学习', '高效省', 'AI学英语', '多邻国',
]

# Patterns to detect section headers / article titles
# These should match ONLY standalone header lines, not sentences starting with the same word
SECTION_PATTERNS = [
    r'^The world this week$',
    r'^Leaders\s*\|.*',
    r'^Leaders$',
    r'^Letters$',
    r'^Briefing$',
    r'^United States$',
    r'^The Americas$',
    r'^Europe$',
    r'^Britain$',
    r'^Middle East & Africa$',
    r'^Asia$',
    r'^China$',
    r'^India$',
    r'^International$',
    r'^Business$',
    r'^Finance & economics$',
    r'^Science & technology$',
    r'^Culture$',
    r'^Books & arts$',
    r'^Economics$',
    r'^Graphic detail$',
    r'^United Nations$',
    r'^Obituary$',
    r'^Special report$',
    r'^Technology Quarterly$',
    r'^By Invitation$',
    r'^Correspondence$',
    r'^Economic & financial indicators$',
    # Also match article title patterns like "Region | Topic"
    r'^[A-Z][\w\s]+?\s*\|\s+[A-Z]',
    r'^Politics$',
    r'^The weekly cartoon$',
    r'^Trade and the world$',
    r'^North America$',
    r'^Latin America$',
    r'^South & Central Asia$',
    r'^East Asia$',
    r'^The Persian Gulf$',
    r'^Russia and the former Soviet republics$',
    r'^Defence$',
]


def is_blank_page(text):
    """A page is blank if it has very little text."""
    return len(text.strip()) < 50


def is_ad_page(text):
    """A page is an ad if it matches known ad patterns."""
    upper = text[:500]
    return any(pattern in upper for pattern in AD_PATTERNS)


def is_section_header(line):
    """Check if a line looks like a section header."""
    line_stripped = line.strip()
    if not line_stripped:
        return False
    return any(re.match(pattern, line_stripped, re.IGNORECASE) for pattern in SECTION_PATTERNS)


def extract_pdf(pdf_path):
    """
    Extract content from a PDF file.

    Returns:
        date_str: str like "2026-05-09"
        articles: list of dicts with {title, section, body, original_pages}
    """
    doc = fitz.open(pdf_path)
    total = len(doc)

    # Extract date from first few pages
    date_str = None
    for i in range(min(5, total)):
        text = doc[i].get_text()
        m = re.search(r'(May|April|March|June|July|August|September|October|November|December|January|February)\s+(\d{1,2})(?:st|nd|rd|th)?\s+(\d{4})', text)
        if m:
            from datetime import datetime
            date_str = datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%B %d %Y").strftime("%Y-%m-%d")
            break

    if not date_str:
        # Fallback: extract from filename
        m = re.search(r'(\d{4})\.(\d{2})\.(\d{2})', pdf_path)
        if m:
            date_str = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # Classify pages
    pages_text = []
    for i in range(total):
        text = doc[i].get_text()
        pages_text.append({
            'index': i,
            'text': text,
            'is_blank': is_blank_page(text),
            'is_ad': is_ad_page(text),
        })

    # Concatenate content pages
    content_text = []
    for p in pages_text:
        if not p['is_blank'] and not p['is_ad']:
            content_text.append(p['text'])

    full_text = '\n'.join(content_text)
    lines = full_text.split('\n')

    # Segment into articles by section headers
    articles = []
    current_article = None
    current_lines = []
    current_pages = []

    page_map = []
    page_counter = 0
    for p in pages_text:
        if not p['is_blank'] and not p['is_ad']:
            page_map.append(p['index'])
        else:
            page_map.append(-1)

    for line in lines:
        stripped = line.strip()
        if is_section_header(stripped) and len(stripped) < 100:
            # Save previous article
            if current_article:
                body = '\n'.join(current_lines).strip()
                if len(body) > 100:
                    current_article['body'] = body
                    current_article['original_pages'] = list(set(current_pages))
                    articles.append(current_article)
            # Start new article
            section_match = re.match(r'^(\S+(?:\s+\S+)*?)\s*\|', stripped)
            if section_match:
                current_article = {
                    'title': stripped,
                    'section': section_match.group(1),
                    'body': '',
                    'original_pages': [],
                }
            else:
                current_article = {
                    'title': stripped,
                    'section': '',
                    'body': '',
                    'original_pages': [],
                }
            current_lines = []
        elif current_article:
            current_lines.append(line)
        else:
            # Lines before first article header
            if stripped and len(stripped) > 10:
                current_article = {
                    'title': 'The World This Week',
                    'section': '',
                    'body': '',
                    'original_pages': [],
                }
                current_lines = [line]

    # Save last article
    if current_article:
        body = '\n'.join(current_lines).strip()
        if len(body) > 100:
            current_article['body'] = body
            current_article['original_pages'] = list(set(current_pages))
            articles.append(current_article)

    # If no articles found, treat entire text as one article
    if not articles and content_text:
        articles = [{
            'title': 'The Economist',
            'section': '',
            'body': full_text,
            'original_pages': [p['index'] for p in pages_text if not p['is_blank'] and not p['is_ad']],
        }]

    # Clean up article bodies
    for article in articles:
        body = article['body']
        # Remove excessive whitespace
        body = re.sub(r'\n{3,}', '\n\n', body)
        # Remove page number artifacts (just numbers on their own line)
        body = re.sub(r'^\s*\d+\s*$', '', body, flags=re.MULTILINE)
        body = body.strip()
        article['body'] = body

    return date_str, articles
