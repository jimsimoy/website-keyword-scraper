#!/usr/bin/env python3
"""
keyword-scraper — scrape URLs and count keyword occurrences in visible page text.

Usage:
  python3 scrape.py                                  # uses config.json by default
  python3 scrape.py --config config.json             # explicit config file
  python3 scrape.py --urls URL [URL ...] --keywords WORD [WORD ...]
  python3 scrape.py --url-file urls.txt --keyword-file keywords.txt
  python3 scrape.py --config config.json --output results.csv
  python3 scrape.py --config config.json --partial   # substring match

Config file (JSON):
  {
    "keywords": ["word1", "word2"],
    "urls": ["https://..."]
  }
"""

import argparse
import csv
import json
import os
import re
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

SKIP_TAGS = {"script", "style", "noscript", "head", "meta", "link"}

DEFAULT_CONFIG = os.path.join(os.path.dirname(__file__), "config.json")


def load_config(path):
    with open(path) as f:
        return json.load(f)


def load_lines(path):
    with open(path) as f:
        return [l.strip() for l in f if l.strip() and not l.startswith("#")]


def fetch(url, timeout=15):
    headers = {"User-Agent": "Mozilla/5.0 (keyword-scraper/1.0)"}
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def visible_text(html):
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(SKIP_TAGS):
        tag.decompose()
    return soup.get_text(separator=" ")


def count_keyword(text, keyword, partial=False):
    pattern = re.escape(keyword) if partial else r"\b" + re.escape(keyword) + r"\b"
    return len(re.findall(pattern, text, flags=re.IGNORECASE))


def short_url(url):
    p = urlparse(url)
    path = p.path.rstrip("/") or "/"
    return p.netloc + path


def render_table(rows, headers):
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    def fmt_row(cells):
        return "  ".join(str(c).ljust(col_widths[i]) for i, c in enumerate(cells))

    sep = "  ".join("-" * w for w in col_widths)
    lines = [fmt_row(headers), sep]
    for row in rows:
        lines.append(fmt_row(row))
    return "\n".join(lines)


def save_pdf(path, headers, rows, full_urls=None):
    doc = SimpleDocTemplate(
        path,
        pagesize=landscape(A4),
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )
    styles = getSampleStyleSheet()

    link_style = styles["Normal"].clone("link_style")
    link_style.textColor = colors.HexColor("#0563C1")

    header_style = styles["Normal"].clone("header_style")
    header_style.textColor = colors.white
    header_style.fontName = "Helvetica-Bold"

    title = Paragraph("Keyword Scraper Results", styles["h1"])
    subtitle = Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        styles["Normal"],
    )

    table_data = [[Paragraph(str(c), header_style) for c in headers]]
    for i, row in enumerate(rows):
        cells = []
        for j, cell in enumerate(row):
            if j == 0 and full_urls and i < len(full_urls):
                href = full_urls[i]
                cells.append(Paragraph(f'<a href="{href}" color="#0563C1">{cell}</a>', link_style))
            else:
                cells.append(Paragraph(str(cell), styles["Normal"]))
        table_data.append(cells)

    # URL column gets most of the width; keyword + total columns share the rest
    page_w = landscape(A4)[0] - 30 * mm
    kw_col_w = 22 * mm
    total_col_w = 18 * mm
    url_col_w = page_w - (len(headers) - 1) * kw_col_w - total_col_w
    col_widths = [url_col_w] + [kw_col_w] * (len(headers) - 2) + [total_col_w]

    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#061D41")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f4f7")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        # Highlight cells with hits > 0
        *[
            ("BACKGROUND", (col_i, row_i), (col_i, row_i), colors.HexColor("#fff3cd"))
            for row_i, row in enumerate(rows, start=1)
            for col_i, cell in enumerate(row)
            if col_i > 0 and str(cell) not in ("0", "ERR") and col_i < len(headers) - 1
        ],
    ]))

    doc.build([title, Spacer(1, 4 * mm), subtitle, Spacer(1, 6 * mm), table])


def main():
    ap = argparse.ArgumentParser(description="Scrape URLs and count keyword occurrences.")
    ap.add_argument("--config", metavar="FILE", help="JSON config file (default: config.json)")
    url_group = ap.add_mutually_exclusive_group()
    url_group.add_argument("--urls", nargs="+", metavar="URL")
    url_group.add_argument("--url-file", metavar="FILE")
    kw_group = ap.add_mutually_exclusive_group()
    kw_group.add_argument("--keywords", nargs="+", metavar="WORD")
    kw_group.add_argument("--keyword-file", metavar="FILE")
    ap.add_argument("--output", metavar="FILE", help="Save results to CSV file")
    ap.add_argument("--partial", action="store_true", help="Substring match (default: whole-word)")
    ap.add_argument("--timeout", type=int, default=15, metavar="SECS")
    args = ap.parse_args()

    # Resolve URLs
    if args.urls:
        urls = args.urls
    elif args.url_file:
        urls = load_lines(args.url_file)
    else:
        config_path = args.config or DEFAULT_CONFIG
        cfg = load_config(config_path)
        urls = cfg.get("urls", [])

    # Resolve keywords
    if args.keywords:
        keywords = args.keywords
    elif args.keyword_file:
        keywords = load_lines(args.keyword_file)
    else:
        config_path = args.config or DEFAULT_CONFIG
        cfg = load_config(config_path)
        keywords = cfg.get("keywords", [])

    if not urls:
        ap.error("No URLs provided — add them to config.json or use --urls / --url-file")
    if not keywords:
        ap.error("No keywords provided — add them to config.json or use --keywords / --keyword-file")

    headers = ["URL"] + keywords + ["TOTAL"]
    rows = []
    full_urls = []

    for url in urls:
        label = short_url(url)
        print(f"  Scraping {label} ...", end=" ", flush=True)
        try:
            html = fetch(url, timeout=args.timeout)
            text = visible_text(html)
            counts = [count_keyword(text, kw, partial=args.partial) for kw in keywords]
            total = sum(counts)
            rows.append([label] + counts + [total])
            full_urls.append(url)
            print(f"OK  (total hits: {total})")
        except Exception as e:
            rows.append([label] + ["ERR"] * len(keywords) + ["ERR"])
            full_urls.append(url)
            print(f"FAILED — {e}")

    print()
    print(render_table(rows, headers))

    if args.output:
        if args.output.lower().endswith(".pdf"):
            save_pdf(args.output, headers, rows, full_urls=full_urls)
        else:
            with open(args.output, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(headers)
                w.writerows(rows)
        print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()
