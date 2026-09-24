#!/usr/bin/env python3
"""Fetch Met Collection API objects for given search queries (Egyptian Art dept 10) and save compact JSON."""
import json, sys, time, requests
BASE = "https://collectionapi.metmuseum.org/public/collection/v1"
queries = sys.argv[1:] or ["crocodile"]
ids = {}
for q in queries:
    for params in ({"q": q, "departmentId": 10}, {"q": q}):
        r = requests.get(BASE + "/search", params=params, timeout=30)
        d = r.json()
        print(q, params.get("departmentId"), d.get("total"), file=sys.stderr)
        for i in d.get("objectIDs") or []:
            ids.setdefault(i, set()).add(q)
        time.sleep(1)
out = []
for i in sorted(ids):
    r = requests.get(f"{BASE}/objects/{i}", timeout=30)
    if r.status_code != 200:
        continue
    o = r.json()
    keep = {k: o.get(k) for k in ["objectID","accessionNumber","title","objectName","department","culture","period","dynasty","reign","objectDate","medium","dimensions","creditLine","geographyType","city","region","subregion","locale","locus","excavation","country","classification","objectURL","primaryImage","isPublicDomain","tags","GalleryNumber"]}
    keep["queries"] = sorted(ids[i])
    out.append(keep)
    time.sleep(0.6)
json.dump(out, sys.stdout, indent=1)
