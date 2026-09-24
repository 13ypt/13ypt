#!/usr/bin/env python3
"""Te Papa Collections API (data.tepapa.govt.nz) using the public guest token that
the API itself returns in its 401 response. Throttled ~1 req/s.
Usage: python3 tepapa_api.py search "<query>" [size]
       python3 tepapa_api.py object <id> [<id> ...]
"""
import json
import sys
import time
import requests

BASE = "https://data.tepapa.govt.nz/collection"
S = requests.Session()


def token():
    r = S.get(f"{BASE}/object/1", timeout=60)
    return r.json().get("guestToken")


def hdr():
    return {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"}


TOKEN = token()

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "search":
        q = sys.argv[2]
        size = int(sys.argv[3]) if len(sys.argv) > 3 else 100
        time.sleep(1)
        r = S.get(f"{BASE}/search", params={"q": q, "size": size}, headers=hdr(), timeout=60)
        j = r.json()
        print(json.dumps({"q": q, "total": j.get("_metadata", {}).get("resultset", {}).get("count"),
                          "results": [{"id": x.get("id"), "type": x.get("type"),
                                       "title": x.get("title"),
                                       "identifier": x.get("identifier"),
                                       "collection": x.get("collection"),
                                       "production": [p.get("spatial", {}).get("title") if isinstance(p.get("spatial"), dict) else None for p in (x.get("production") or [])],
                                       "description": (x.get("description") or "")[:300]}
                                      for x in j.get("results", [])]}, ensure_ascii=False))
    else:
        for oid in sys.argv[2:]:
            time.sleep(1)
            r = S.get(f"{BASE}/object/{oid}", headers=hdr(), timeout=60)
            print(json.dumps(r.json(), ensure_ascii=False))
