#!/usr/bin/env python3
"""Crossref works search: crossref_search.py "query" [rows]  -> year | title | container | DOI"""
import json, sys, urllib.parse, subprocess
q = sys.argv[1]; n = sys.argv[2] if len(sys.argv) > 2 else "40"
url = "https://api.crossref.org/works?query.bibliographic=" + urllib.parse.quote(q) + "&rows=" + n + "&select=DOI,title,container-title,issued,author&mailto=research-agent@example.org"
d = json.loads(subprocess.run(["curl", "-sS", "-m", "60", url], capture_output=True).stdout)
print(f"## {q!r}: total={d['message']['total-results']}")
for w in d["message"]["items"]:
    y = (w.get("issued", {}).get("date-parts") or [[None]])[0][0]
    au = "; ".join((a.get("family") or "") for a in (w.get("author") or [])[:3])
    print(f"- {y} | {au} | {(w.get('title') or [''])[0]} | {(w.get('container-title') or [''])[0]} | {w.get('DOI')}")
