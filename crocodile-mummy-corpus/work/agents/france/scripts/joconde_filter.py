#!/usr/bin/env python3
"""Stream the full Joconde open-data export (Ministère de la Culture, POP; ~1.2 GB CSV,
https://ministere-culture.s3.sbg.io.cloud.ovh.net/POP/joconde.csv, listed on data.gouv.fr dataset 5b448216a3a729752eb11d6f)
without saving it, and keep rows mentioning crocodile/Sobek/Sebek/Souchos/momie+animal terms.
Output: raw/joconde_crocodile_rows.csv (+ header), raw/joconde_filter.log"""
import csv, io, sys, re, requests, os
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
URL = "https://ministere-culture.s3.sbg.io.cloud.ovh.net/POP/joconde.csv"
pat = re.compile(r"crocodil|sobek|sebek|souchos|suchos|sébek|kom[ -]?ombo", re.I)
csv.field_size_limit(10**9)
r = requests.get(URL, stream=True, timeout=120)
r.raw.decode_content = True
txt = io.TextIOWrapper(r.raw, encoding="utf-8", errors="replace", newline="")
first = txt.readline()
delim = max([";", ",", "|", "\t"], key=first.count)
reader = csv.reader(io.StringIO(first), delimiter=delim)
header = next(reader)
out = csv.writer(open(os.path.join(RAW, "joconde_crocodile_rows.csv"), "w", newline=""), delimiter=delim)
out.writerow(header)
n = k = 0
for row in csv.reader(txt, delimiter=delim):
    n += 1
    if any(pat.search(f) for f in row):
        out.writerow(row); k += 1
    if n % 100000 == 0:
        open(os.path.join(RAW, "joconde_filter.log"), "w").write(f"rows {n} kept {k}\n")
open(os.path.join(RAW, "joconde_filter.log"), "w").write(f"DONE rows {n} kept {k}; delimiter {delim!r}; header {header[:80]}\n")
