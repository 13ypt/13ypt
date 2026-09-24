#!/usr/bin/env python3
"""Extract text from a PDF with PyMuPDF and print lines matching a regex with context.
Usage: pdfgrep.py file.pdf 'regex' [context_lines]"""
import sys, re, pymupdf
doc = pymupdf.open(sys.argv[1])
rx = re.compile(sys.argv[2], re.I)
ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 1
for pno, page in enumerate(doc, 1):
    lines = page.get_text().splitlines()
    for i, l in enumerate(lines):
        if rx.search(l):
            seg = " ".join(lines[max(0, i-ctx): i+ctx+1])
            print(f"p{pno}: {seg}")
