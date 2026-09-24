#!/usr/bin/env python3
"""Search OpenAlex works (title+abstract+fulltext search) and print id|year|title|venue|oa_url.
Usage: openalex_search.py "query" [n]"""
import sys, requests
q = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 25
r = requests.get("https://api.openalex.org/works", params={"search": q, "per-page": n, "mailto": "research@example.org"}, timeout=60)
d = r.json()
print(f"# {q!r} count={d.get('meta',{}).get('count')}")
for w in d.get("results", []):
    venue = ((w.get("primary_location") or {}).get("source") or {}).get("display_name")
    oa = (w.get("open_access") or {}).get("oa_url")
    print(f"{w['id'].split('/')[-1]} | {w.get('publication_year')} | {(w.get('title') or '')[:110]} | {venue} | {w.get('doi')} | {oa}")
