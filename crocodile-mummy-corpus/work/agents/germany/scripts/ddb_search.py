#!/usr/bin/env python3
"""Query the Deutsche Digitale Bibliothek public Solr search index
(https://api.deutsche-digitale-bibliothek.de/2/search/index/search/select), which answers
without an API key. (The DDB website itself is behind an anti-bot wall and is not scraped.)

Usage: python3 ddb_search.py '<solr q>' [rows]
Prints: id | title | provider | objecttype | place
"""
import json
import sys
import requests

q = sys.argv[1]
rows = int(sys.argv[2]) if len(sys.argv) > 2 else 200
url = "https://api.deutsche-digitale-bibliothek.de/2/search/index/search/select"
r = requests.get(url, params={"q": q, "rows": rows, "wt": "json"}, timeout=90,
                 headers={"Accept": "application/json"})
d = r.json()
resp = d.get("response", {})
print(f"# q={q!r} numFound={resp.get('numFound')}", file=sys.stderr)
for doc in resp.get("docs", []):
    def g(k):
        v = doc.get(k)
        return "; ".join(v) if isinstance(v, list) else (v or "")
    print(" | ".join([doc.get("id", ""), g("title"), g("provider_fct") or g("provider"),
                      g("objecttype"), g("place")]))
