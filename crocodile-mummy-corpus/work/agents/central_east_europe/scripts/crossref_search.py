#!/usr/bin/env python3
"""Search Crossref works (query.bibliographic) and print year|title|container|DOI.
Usage: crossref_search.py "query" [rows]"""
import sys, requests
q = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
r = requests.get("https://api.crossref.org/works", params={"query.bibliographic": q, "rows": n, "select": "DOI,title,container-title,issued,author"}, headers={"User-Agent": "croc-corpus-research/1.0 (mailto:research@example.org)"}, timeout=60)
d = r.json()["message"]
print(f"# {q!r} total={d.get('total-results')}")
for w in d["items"]:
    yr = (w.get("issued", {}).get("date-parts") or [[None]])[0][0]
    au = "; ".join(a.get("family", "") for a in (w.get("author") or [])[:3])
    print(f"{yr} | {au} | {(w.get('title') or [''])[0][:120]} | {(w.get('container-title') or [''])[0][:50]} | {w['DOI']}")
