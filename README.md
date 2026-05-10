# The Economist Daily Reader

A personal reading tool for The Economist magazine — auto-fetches weekly issues, annotates advanced vocabulary with phonetics and Chinese definitions, splits content into daily ~2-page reading sessions, and formats for beautiful A4 printing.

## Features

- **Auto-fetch**: GitHub Action automatically downloads the latest issue every Saturday from [awesome-english-ebooks](https://github.com/hehonghui/awesome-english-ebooks)
- **Smart filtering**: Removes blank pages and ad content automatically
- **Vocabulary annotation**: Uses a personal dictionary (4,000+ words) from Eudic, with phonetics and Chinese definitions
- **Daily sessions**: Splits each ~100-page issue into ~42 daily reading chunks (~1,800 words/day)
- **Print-ready**: Clean A4 layout optimized for printing — just click "Print"

## Quick Start

### Online Reading

Visit the [GitHub Pages site](https://qiuyanlong16.github.io/me-awesome-english-ebooks/) to browse all issues and daily reading pages.

### Local Processing

```bash
# Install dependencies
pip install pymupdf

# Process latest issue
python scripts/process.py
```

### Manual Update Trigger

Go to **Actions** → **Weekly Economist Update** → **Run workflow** to manually fetch the latest issue.

## Project Structure

```
.
├── .github/workflows/
│   └── weekly-update.yml       # Auto-fetches and processes every Saturday
├── scripts/
│   ├── process.py              # Main pipeline (download → extract → generate)
│   ├── extract.py              # PDF text extraction with blank/ad filtering
│   ├── annotate.py             # Vocabulary annotation and daily grouping
│   ├── dictionary.py           # Dictionary loader with lemmatization
│   ├── generate.py             # HTML page generation
│   ├── build_index.py          # Index page builder
│   └── user_dictionary.json    # Personal vocabulary (4,000+ words)
├── template/
│   ├── page.html               # Daily reading page template
│   └── index.html              # Issue listing template
└── docs/
    ├── index.html              # Generated index (served by GitHub Pages)
    └── issues/YYYY-MM-DD/      # Generated daily reading pages + metadata
```

## How It Works

1. **GitHub Action** runs every Saturday at 11:00 AM (China time)
2. Downloads the latest Economist PDF from the source repo
3. Extracts text, removes blank pages and ads
4. Segments articles by section headers (Leaders, Letters, Briefing, etc.)
5. Groups ~1,800 words into daily reading sessions
6. Annotates advanced words using the personal dictionary
7. Generates beautiful HTML pages with vocabulary glossaries
8. Commits everything back to the `main` branch

## Dictionary

The vocabulary comes from a personal Eudic (欧路词典) wordbook containing 4,000+ words with phonetic transcriptions and Chinese definitions. Common CET-4 words (the, be, have, etc.) are excluded from annotation.

## License

For personal study use only.

