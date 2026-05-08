#!/usr/bin/env python3
"""Main orchestrator: download PDF, process, generate, commit."""

import os
import sys
import urllib.request
import json

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from scripts.extract import extract_pdf
from scripts.annotate import split_into_days, annotate_text
from scripts.dictionary import Dictionary
from scripts.generate import generate_issue
from scripts.build_index import build_index

DOCS_DIR = os.path.join(PROJECT_ROOT, 'docs')
ISSUES_DIR = os.path.join(DOCS_DIR, 'issues')
DICT_PATH = os.path.join(PROJECT_ROOT, 'scripts', 'user_dictionary.json')

# GitHub repo for fetching latest Economist
SOURCE_REPO = 'hehonghui/awesome-english-ebooks'
MAX_RETAIN = 12  # Keep latest 12 issues


def download_latest_pdf(output_dir):
    """Download the latest Economist PDF from the source repo."""
    import urllib.request
    import json as json_mod

    # List latest issue directory
    api_url = f'https://api.github.com/repos/{SOURCE_REPO}/contents/01_economist'
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})

    with urllib.request.urlopen(req) as resp:
        items = json_mod.loads(resp.read())

    # Find directories matching te_YYYY.MM.DD pattern, get the latest
    import re
    issues = []
    for item in items:
        if item['type'] == 'dir' and re.match(r'te_\d{4}\.\d{2}\.\d{2}', item['name']):
            date_str = item['name'][3:].replace('.', '-')
            issues.append((date_str, item['name'], item['url']))

    if not issues:
        raise RuntimeError("No Economist issues found in source repo")

    issues.sort(key=lambda x: x[0], reverse=True)
    latest_date, latest_dir, latest_api_url = issues[0]

    # Check if already processed
    local_dir = os.path.join(ISSUES_DIR, latest_date)
    if os.path.exists(os.path.join(local_dir, 'meta.json')):
        print(f"Issue {latest_date} already processed locally. Skipping.")
        return None, None

    # Get PDF download URL from the issue directory
    req2 = urllib.request.Request(latest_api_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req2) as resp2:
        files = json_mod.loads(resp2.read())

    pdf_url = None
    for f in files:
        if f['name'].endswith('.pdf'):
            pdf_url = f['download_url']
            break

    if not pdf_url:
        raise RuntimeError(f"No PDF found in {latest_dir}")

    # Download PDF
    pdf_filename = f'economist-{latest_date}.pdf'
    pdf_path = os.path.join(output_dir, pdf_filename)

    print(f"Downloading {pdf_url}...")
    with urllib.request.urlopen(pdf_url) as resp3:
        with open(pdf_path, 'wb') as f:
            f.write(resp3.read())

    print(f"Downloaded to {pdf_path}")
    return pdf_path, latest_date


def cleanup_old_issues():
    """Remove oldest issues beyond MAX_RETAIN limit."""
    if not os.path.exists(ISSUES_DIR):
        return

    issues = []
    for name in os.listdir(ISSUES_DIR):
        meta_path = os.path.join(ISSUES_DIR, name, 'meta.json')
        if os.path.exists(meta_path):
            issues.append(name)

    issues.sort()

    while len(issues) > MAX_RETAIN:
        oldest = issues.pop(0)
        oldest_path = os.path.join(ISSUES_DIR, oldest)
        import shutil
        shutil.rmtree(oldest_path)
        print(f"Removed old issue: {oldest}")


def main():
    print("=" * 50)
    print("Economist Daily Reader - Processing")
    print("=" * 50)

    os.makedirs(ISSUES_DIR, exist_ok=True)
    tmp_dir = os.path.join(PROJECT_ROOT, '.tmp')
    os.makedirs(tmp_dir, exist_ok=True)

    # Step 1: Download latest PDF
    pdf_path, issue_date = download_latest_pdf(tmp_dir)
    if not pdf_path:
        print("No new issue to process.")
        return

    # Step 2: Generate daily pages
    date_str, total_days = generate_issue(pdf_path, ISSUES_DIR, DICT_PATH)

    # Step 3: Build index
    build_index(ISSUES_DIR, os.path.join(DOCS_DIR, 'index.html'))

    # Step 4: Cleanup old issues
    cleanup_old_issues()

    # Step 5: Clean up temp files
    if pdf_path and os.path.exists(pdf_path):
        os.remove(pdf_path)
    if os.path.exists(tmp_dir):
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print(f"\nDone! Issue {date_str} processed with {total_days} daily pages.")


if __name__ == '__main__':
    main()
