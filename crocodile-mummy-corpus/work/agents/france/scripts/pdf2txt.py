#!/usr/bin/env python3
"""pdf2txt.py in.pdf out.txt  (pymupdf text extraction)"""
import sys, pymupdf
doc = pymupdf.open(sys.argv[1])
with open(sys.argv[2], "w") as f:
    for i, p in enumerate(doc):
        f.write(f"\n=== page {i+1} ===\n" + p.get_text())
print(len(doc), "pages")
