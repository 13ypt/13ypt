#!/usr/bin/env python3
"""Search Pushkin State Museum of Fine Arts online collection (collection.pushkinmuseum.art).
POST /api/search-entities/OBJECT  json {"query":q,"start":0,"count":N,"filters":{},"sort":null,"rawDataFilters":{}}
Usage: pushkin_search.py "query" """
import sys, requests
q = sys.argv[1]
r = requests.post("https://collection.pushkinmuseum.art/api/search-entities/OBJECT",
                  json={"query": q, "start": 0, "count": 200, "filters": {}, "sort": None, "rawDataFilters": {}},
                  headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
d = r.json()
print(f"# {q!r} returned={len(d.get('data', []))} total={d.get('total', d.get('count'))}")
for o in d.get("data", []):
    print(f"{o['id']} | {o['title'][:140]}")
