---
title: Economist Daily Reader - Design Spec
date: 2026-05-08
status: approved
---

# Economist Daily Reader - Design Spec

## Summary

A GitHub-hosted static site that auto-fetches The Economist weekly PDF, processes it (removes blank/ad pages, annotates advanced vocabulary), splits it into daily ~2-page reading chunks, and serves via GitHub Pages for A4-printable study sessions.

## Architecture

```
GitHub Action (weekly cron)
    │
    ├─ Download latest PDF from hehonghui/awesome-english-ebooks
    ├─ Extract text via PyMuPDF, filter blank/ad pages
    ├─ Split articles by section boundaries, group ~1800 words/day
    ├─ Annotate vocabulary beyond CET-4 level (~4000 words)
    ├─ Generate daily HTML pages + index
    └─ Commit to main branch → GitHub Pages auto-deploys

GitHub Pages (static site)
    ├── index.html              ← Issue list with progress
    └── issues/YYYY-MM-DD/
        ├── day1.html           ← Daily reading page
        ├── day2.html
        ├── ...
        └── meta.json           ← Issue metadata
```

## Core Components

### 1. PDF Extractor (`scripts/extract.py`)

**Purpose:** Convert raw PDF into clean, article-segmented text.

**How it works:**
- Use PyMuPDF (`fitz`) to extract text from each page
- Blank page detection: stripped text < 50 characters → skip
- Ad page detection: text contains "Duolingo", "Notability", "App 推荐" patterns → skip
- Article segmentation: detect section headers (Leaders, Letters, Briefing, country/region names, column titles)
- Concatenate article text in reading order, track original page numbers for reference

**Output:** List of article objects: `{title, section, body_text, original_pages}`

### 2. Vocabulary Annotator (`scripts/annotate.py`)

**Purpose:** Identify words beyond ~4000 vocabulary level and provide phonetic + Chinese gloss.

**How it works:**
- Load dictionary from `scripts/dictionary.py` (~3000 entries: advanced words, proper nouns, idioms)
- Dictionary format: `{word: (phonetic, part_of_speech, chinese_definition)}`
- Matching: case-insensitive word lookup, with lemmatization support (plural nouns, verb conjugations)
- Only annotate words NOT in CET-4 basic vocabulary
- Track frequency — annotate each word only on first appearance per daily page

**Output:** Annotated article text with marked words + glossary list for each day

### 3. HTML Generator (`scripts/generate.py`)

**Purpose:** Generate daily reading pages and index from processed data.

**Templates:**
- `template/page.html`: Daily reading page template
  - Date badge (red, top-left)
  - Article title + section label
  - Body text with inline vocabulary markers (red dashed underline)
  - Glossary box at bottom (word /phonetic/ POS Chinese definition)
  - Progress indicator ("Day X of Y")
  - Print-optimized CSS (A4, hide buttons, white background)
- `template/index.html`: Issue listing page
  - All processed issues sorted by date (newest first)
  - Each issue expands to show daily reading links
  - Progress bar: "Completed X/Y days"
  - "Continue from last day" link

**Annotation mode (C, user-confirmed):**
- Body: red dashed underline on annotated words
- Bottom glossary: full phonetic transcription, part of speech, Chinese definition
- Print: glossary always appears on same page or next page via `break-inside: avoid`

### 4. Index Builder (`scripts/build Index.py`)

**Purpose:** Regenerate the main index.html from all issue metadata.

**How it works:**
- Scan `docs/issues/` for all issue directories
- Read each issue's `meta.json`
- Build sorted HTML list with progress indicators
- Persist last-read-day in `meta.json` for each issue

### 5. GitHub Action (`.github/workflows/weekly-update.yml`)

**Trigger:** Weekly cron `0 3 * * 6` (Saturday 3:00 UTC / Saturday 11:00 AM China time)

**Steps:**
1. Checkout repo
2. Install Python dependencies (`pypdf`, `pymupdf`)
3. Run `scripts/extract.py` — download latest PDF, extract text
4. Run `scripts/annotate.py` — annotate vocabulary
5. Run `scripts/generate.py` — generate HTML pages
6. Run `scripts/build_index.py` — update index
7. Commit new files with message: `Add Economist issue YYYY-MM-DD`
8. Push to main branch

**Retention:** Keep latest 12 issues (~6 months). Delete older issue directories during each run to control repo size.

## Data Flow

```
PDF download
    ↓
Page classification (blank/ad/content)
    ↓
Text extraction (content pages only)
    ↓
Article segmentation by section headers
    ↓
Daily grouping (~1800 words per day, split at paragraph boundaries)
    ↓
Vocabulary matching & annotation
    ↓
HTML generation (daily pages + meta.json)
    ↓
Index rebuild
    ↓
Git commit & push
```

## Error Handling

- **PDF download failure:** Log error, skip week, exit non-zero (Action shows failure)
- **PDF parse failure:** Corrupted or encrypted PDF — log error, do not commit partial data
- **Vocabulary miss:** Word not in dictionary — skip silently, no blocking
- **No new issue detected:** If latest issue date matches last processed — skip with info log
- **Repository size guard:** If total repo size > 500MB, delete oldest issues until under limit

## File Structure

```
.
├── .github/
│   └── workflows/
│       └── weekly-update.yml
├── scripts/
│   ├── extract.py
│   ├── annotate.py
│   ├── dictionary.py
│   ├── generate.py
│   └── build_index.py
├── template/
│   ├── page.html
│   └── index.html
├── docs/
│   ├── index.html
│   └── issues/
│       └── YYYY-MM-DD/
│           ├── day1.html
│           ├── day2.html
│           ├── ...
│           └── meta.json
├── requirements.txt
└── README.md
```

## Dependencies

- Python 3.12+
- `pymupdf` >= 1.24 (PDF text extraction)
- No runtime server dependencies (pure static site)
