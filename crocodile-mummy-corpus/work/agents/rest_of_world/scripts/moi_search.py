#!/usr/bin/env python3
"""Query the National Portal and Digital Repository for Museums of India (museumsofindia.gov.in)
JSON search endpoint used by its own search page; paginate all results (28/page) and print
records whose title/description match a filter regex.
Usage: moi_search.py FILTER_REGEX term [term ...]   (FILTER '.' prints all)"""
import json, math, re, sys, time, requests
S = requests.Session()
S.headers['User-Agent'] = 'Mozilla/5.0'
flt = re.compile(sys.argv[1], re.I)
for term in sys.argv[2:]:
    S.get('https://www.museumsofindia.gov.in/repository/search/basic', params={'searchterm': term, 'museumId': 'all'}, timeout=60)
    page, total, hits, seen = 1, None, [], 0
    while True:
        r = S.get('https://www.museumsofindia.gov.in/repository/search/basic/fetch',
                  params={'searchterm': term, 'museumId': 'all', 'pageNo': page, 'facetFilters': '{}', 'anaglyph': ''},
                  headers={'X-Requested-With': 'XMLHttpRequest'}, timeout=60)
        d = r.json()
        total = d.get('resultSize') or 0
        recs = d.get('listOfResult') or []
        seen += len(recs)
        for rec in recs:
            txt = f"{rec.get('title','')} {rec.get('description','')}"
            if flt.search(txt):
                hits.append({k: rec.get(k) for k in ('recordIdentifier', 'title', 'description', 'museumName')})
        if page >= math.ceil(total / 28) or not recs or page >= 40:
            break
        page += 1
        time.sleep(1)
    print(f"=== term={term!r} total={total} scanned={seen} filtered_hits={len(hits)}")
    if total:
        print("    museums facet:", json.dumps((d.get('facetMap') or {}).get('MuseumName'), ensure_ascii=False)[:500])
    for h in hits:
        print('   ', json.dumps(h, ensure_ascii=False)[:500])
