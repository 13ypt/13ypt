#!/usr/bin/env python3
"""Filter the Joconde full export streamed on stdin:
curl -sS https://ministere-culture.s3.sbg.io.cloud.ovh.net/POP/joconde.csv | python3 joconde_filter2.py
Each physical line of the export is one record wrapped in quotes with '|' separators (as observed); multi-line
records are handled by csv module. Keeps records matching the regex; writes raw/joconde_crocodile_rows2.csv and a log."""
import csv, sys, re, os
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
pat = re.compile(r"crocodil|sobek|sebek|sébek|souchos|suchos|kom[ -]?ombo|k[oô]m[ -]ombo", re.I)
csv.field_size_limit(10**9)
sys.stdin.reconfigure(encoding="utf-8", errors="replace", newline="")
out = open(os.path.join(RAW, "joconde_crocodile_rows2.csv"), "w", newline="")
n = k = nbytes = 0
for line in sys.stdin:
    n += 1; nbytes += len(line)
    if n == 1 or pat.search(line):
        out.write(line); k += 1
    if n % 200000 == 0:
        open(os.path.join(RAW, "joconde_filter2.log"), "w").write(f"lines {n} kept {k} chars {nbytes}\n")
open(os.path.join(RAW, "joconde_filter2.log"), "w").write(f"DONE lines {n} kept {k} chars {nbytes}\n")
