#!/usr/bin/env python3
"""Query the eSbírky (Czech national museum-collections portal) internal API.
Usage: esbirky_search.py "query" [maxpages] [detail_regex]
List:   POST https://internal-api.esbirky.cz/api/1/subjects  form: q=<query>&page=<n>
Detail: GET  https://internal-api.esbirky.cz/api/1/subjects/<slug>  (breadcrumbs[0] = institution)
Note: collectionPath in list results is unreliable, so institution is taken from detail.
Prints: id | name | inventoryNumber | currentCollection | [institution | description if detail fetched]
"""
import sys, time, re, requests
q = sys.argv[1]
maxp = int(sys.argv[2]) if len(sys.argv) > 2 else 20
rx = re.compile(sys.argv[3], re.I) if len(sys.argv) > 3 else None
url = "https://internal-api.esbirky.cz/api/1/subjects"
page = 1
while True:
    d = requests.post(url, data={"q": q, "page": page}, timeout=60).json()
    pg = d.get("pagination", {})
    if page == 1:
        print(f"# query={q!r} total={pg.get('totalItemCount')} pages={pg.get('numberOfPages')}")
    for it in d.get("items", []):
        cc = (it.get("currentCollection") or {}).get("name", "")
        line = f"{it['id']} | {it['name'][:90]} | {it.get('inventoryNumber')} | {cc}"
        if rx and rx.search(it["name"] + " " + cc):
            det = requests.get(f"{url}/{it['slug']}", timeout=60).json()
            bc = det.get("breadcrumbs") or []
            inst = bc[0]["name"] if bc else ""
            desc = (det.get("description") or "").replace("\n", " ")[:200]
            line += f" | INST={inst} | slug={it['slug']} | {desc}"
            time.sleep(0.7)
        print(line)
    if page >= (pg.get("numberOfPages") or 0) or page >= maxp:
        break
    page += 1
    time.sleep(1)
