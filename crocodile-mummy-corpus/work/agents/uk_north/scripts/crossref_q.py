#!/usr/bin/env python3
"""Query Crossref works. Usage: crossref_q.py 'author' 'bibliographic terms' [rows]"""
import sys, json, requests
a, b = sys.argv[1], sys.argv[2]
rows = sys.argv[3] if len(sys.argv) > 3 else "40"
p = {"rows": rows, "select": "DOI,title,author,issued,container-title,type"}
if a: p["query.author"] = a
if b: p["query.bibliographic"] = b
r = requests.get("https://api.crossref.org/works", params=p, headers={"User-Agent": "croc-corpus research (mailto:none)"}, timeout=60)
for it in r.json()["message"]["items"]:
    au = "; ".join((x.get("family") or "") for x in it.get("author", []))[:80]
    y = it.get("issued", {}).get("date-parts", [[None]])[0][0]
    print(y, "|", au, "|", (it.get("title") or [""])[0][:150], "|", (it.get("container-title") or [""])[0][:60], "|", it["DOI"])
