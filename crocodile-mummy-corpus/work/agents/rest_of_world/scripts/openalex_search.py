#!/usr/bin/env python3
"""Search OpenAlex works (title+abstract+fulltext 'search' param) and print title, year, venue, DOI.
Usage: openalex_search.py "query" [max]"""
import sys, time, requests
q = sys.argv[1]; mx = int(sys.argv[2]) if len(sys.argv) > 2 else 50
r = requests.get('https://api.openalex.org/works', params={'search': q, 'per-page': min(mx, 200), 'mailto': 'research@example.org'}, timeout=60)
d = r.json()
print(f"=== {q!r}: count={d.get('meta',{}).get('count')}")
for w in d.get('results', [])[:mx]:
    venue = ((w.get('primary_location') or {}).get('source') or {}).get('display_name')
    print(f"  {w.get('publication_year')} | {w.get('title')} | {venue} | {w.get('doi')} | {w.get('id')}")
