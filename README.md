# Keyword Scraper

Scrapes a list of URLs and counts occurrences of specified keywords in the visible page text. Outputs a summary table to the terminal and optionally exports to **PDF** or **CSV**.

**Author:** Jan Ivan Simoy (<jimsimoy@gmail.com>)  
*Powered by AI*

---

## Requirements

Python 3.10+

---

## Setup

A virtual environment is already created at `venv/`. To activate it:

```bash
cd /var/www/wiredmedia/agents/dev-tools/keyword-scraper

source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

Once activated, run the tool normally:

```bash
python3 scrape.py
```

Deactivate when done:

```bash
deactivate
```

### First-time setup on a new machine

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> `venv/` is git-ignored and should not be committed.

---

## Configuration

`config.json` holds the URLs and keywords. It is git-ignored so it stays local.  
Copy the template to get started:

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

---

## Usage

### Run with config.json (default)

```bash
python3 scrape.py
```

### Explicit config file

```bash
python3 scrape.py --config path/to/config.json
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
├── requirements.txt     # Python dependencies
├── .gitignore
├── README.md
├── venv/                # Virtual environment (git-ignored)
└── tmp/                 # Output files (git-ignored)
```
