# Keyword Scraper

Scrapes a list of URLs and counts occurrences of specified keywords in the visible page text. Outputs a summary table to the terminal and optionally exports to **PDF** or **CSV**.

**Author:** Jan Ivan Simoy (<jimsimoy@gmail.com>)  
*Powered by AI*

---

## Requirements

Python 3.10+ with the following packages:

```bash
pip3 install requests beautifulsoup4 lxml reportlab
```

---

## Configuration

Copy the template and fill in your URLs and keywords:

```bash
cp config.example.json config.json
```

`config.json` structure:

```json
{
  "keywords": ["enterprise", "corporation"],
  "urls": [
    "https://example.com/page-1/",
    "https://example.com/page-2/"
  ]
}
```

> `config.json` is git-ignored. Commit `config.example.json` instead.

---

## Usage

### Run with config.json (default)

```bash
python3 scrape.py
```

### Explicit config file

```bash
python3 scrape.py --config config.json
```

### Inline URLs and keywords

```bash
python3 scrape.py --urls https://example.com/page/ --keywords enterprise corporation
```

### From text files (one entry per line, `#` for comments)

```bash
python3 scrape.py --url-file urls.txt --keyword-file keywords.txt
```

### Export to PDF

```bash
python3 scrape.py --output tmp/results.pdf
```

### Export to CSV

```bash
python3 scrape.py --output tmp/results.csv
```

### Substring matching (default is whole-word)

```bash
python3 scrape.py --partial
```

---

## Output

Terminal table printed after all URLs are scraped:

```
URL                              enterprise  corporation  TOTAL
-------------------------------  ----------  -----------  -----
example.com/page-1               1           1            2
example.com/page-2               0           0            0
```

PDF output includes:
- Clickable URL links in the URL column
- Amber highlight on any cell with a keyword hit
- Alternating row shading for readability

---

## File structure

```
keyword-scraper/
├── scrape.py            # Main script
├── config.json          # Your local config (git-ignored)
├── config.example.json  # Committed template
├── .gitignore
├── README.md
└── tmp/                 # Output files (git-ignored)
```
