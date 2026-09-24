#!/usr/bin/env python3
"""Search Slovakiana (Slovak national digitised-heritage portal) cultural objects.
GET https://wcm.slovakiana.sk/culturalobject/search?searchText=..&searchByKeywords=true&size=..&page=..
Usage: slovakiana_search.py "query" [maxpages]"""
import sys, time, json, requests
q = sys.argv[1]; maxp = int(sys.argv[2]) if len(sys.argv) > 2 else 5
for page in range(maxp):
    r = requests.get("https://wcm.slovakiana.sk/culturalobject/search",
                     params=dict(sortAttribute="rank", sortDirection=1, size=50, page=page,
                                 searchText=q, searchByKeywords="true", onlyWithImage="false"), timeout=60)
    d = r.json()
    if page == 0:
        print(f"# query={q!r} total={d.get('totalCount')}")
    for it in d.get("results", []):
        tags = "; ".join(t["name"] for t in it.get("tags", []))
        cats = "; ".join(c["name"] for c in it.get("categories", []))
        print(f"{it['key']} | {it['name'][:80]} | {it.get('displayOriginDate','')} | {cats} | {tags}"[:320])
    if not d.get("hasMoreResults"):
        break
    time.sleep(1)
