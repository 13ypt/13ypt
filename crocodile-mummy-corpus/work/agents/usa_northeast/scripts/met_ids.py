#!/usr/bin/env python3
"""Fetch Met API search results (Egyptian Art, departmentId=10) for several queries; output compact JSON of objects."""
import json, sys, time, requests
BASE = "https://collectionapi.metmuseum.org/public/collection/v1"
ids = {}
for q in sys.argv[1:]:
    r = requests.get(f"{BASE}/search?departmentId=10&q={requests.utils.quote(q)}", timeout=30).json()
    print(q, r.get("total"), file=sys.stderr)
    for i in r.get("objectIDs") or []:
        ids.setdefault(i, []).append(q)
    time.sleep(1)
out = []
for i in sorted(ids):
    try:
        o = requests.get(f"{BASE}/objects/{i}", timeout=30).json()
    except Exception as e:
        continue
    out.append({k: o.get(k) for k in ["objectID","accessionNumber","title","objectName","period","dynasty","objectDate","medium","dimensions","creditLine","excavation","locale","locus","subregion","region","objectURL","primaryImage","additionalImages","isPublicDomain","GalleryNumber"]} | {"queries": ids[i]})
    time.sleep(0.5)
json.dump(out, sys.stdout, indent=1)
