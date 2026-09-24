#!/usr/bin/env python3
import sys, pymupdf
d = pymupdf.open(sys.argv[1])
out = open(sys.argv[2], "w", encoding="utf-8")
for i, p in enumerate(d):
    out.write(f"\n=== PAGE {i+1} ===\n" + p.get_text())
print(len(d), "pages")
