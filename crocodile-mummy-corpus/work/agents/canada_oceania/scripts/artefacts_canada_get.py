#!/usr/bin/env python3
"""Artefacts Canada Humanities results via GET URL (t=any|all|exact), paginated. ~1 req/s.
Usage: python3 artefacts_canada_get.py <t> "<words>" [lang]
Prints total and each record's text block (one line per record)."""
import re, sys, time, requests
from bs4 import BeautifulSoup
U = "https://app.pch.gc.ca/application/artefacts_hum/humaines_humanities.app"
S = requests.Session(); S.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) Chrome/124.0"
t, w = sys.argv[1], sys.argv[2]; lang = sys.argv[3] if len(sys.argv) > 3 else "en"
page, total = 1, None
while True:
    p = {"t": t, "i": "false", "n": "0", "pID": str(page), "r": "100", "s": "1", "v": "none", "lang": lang, "w": w}
    for attempt in range(4):
        try:
            r = S.get(U, params=p, timeout=90); time.sleep(1)
        except Exception as e:
            print("ERR", type(e).__name__, flush=True); time.sleep(5); continue
        m = re.search(r"document.cookie='([^=]+)=([^;]+);", r.text)
        if m and len(r.text) < 500:
            S.cookies.set(m.group(1), m.group(2), domain="app.pch.gc.ca"); continue
        break
    s = BeautifulSoup(r.text, "lxml")
    for x in s(["script", "style"]): x.decompose()
    txt = s.get_text(" | ", strip=True)
    if total is None:
        m = re.search(r"([\d,]+) (records|notices|fiches)", txt)
        total = int(m.group(1).replace(",", "")) if m else 0
        print("TOTAL", total, flush=True)
    i = txt.find("Data for the record")
    body = txt[i:]
    recs = re.split(r" \| (?=\d+ \| (?:For © contact:|Object Name:|Title:|Nom de l))", body)
    if len(recs) <= 1: break
    for rec in recs[1:]:
        print(re.sub(r"\s+", " ", rec)[:1500], flush=True)
    if page * 100 >= total: break
    page += 1
