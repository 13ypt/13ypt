#!/usr/bin/env python3
"""Crossref bibliographic search; print year | title | container | DOI for items whose title matches a filter.
Usage: crossref_search.py "query" [filter_regex] [rows]"""
import re, sys, requests
q = sys.argv[1]; flt = re.compile(sys.argv[2] if len(sys.argv) > 2 else '.', re.I); rows = int(sys.argv[3]) if len(sys.argv) > 3 else 100
r = requests.get('https://api.crossref.org/works', params={'query.bibliographic': q, 'rows': rows, 'select': 'DOI,title,container-title,issued,author'}, headers={'User-Agent': 'croc-corpus-research/1.0 (mailto:research@example.org)'}, timeout=60)
d = r.json()['message']
print(f"=== {q!r}: total={d.get('total-results')} (showing filtered of top {rows})")
for it in d['items']:
    t = ' '.join(it.get('title') or [''])
    if flt.search(t):
        y = (it.get('issued', {}).get('date-parts') or [[None]])[0][0]
        au = '; '.join(f"{a.get('family','')}" for a in (it.get('author') or [])[:4])
        print(f"  {y} | {t[:160]} | {' '.join(it.get('container-title') or [])[:60]} | {au} | https://doi.org/{it['DOI']}")
