#!/usr/bin/env python3
"""Fulltext search in heidICON (Heidelberg University object DB, easydb 5) using an anonymous
API session (as the public web frontend does). Prints pool path and standard title.
Usage: python3 heidicon_search.py <term> [<term> ...]
"""
import json, sys, time, requests
B = "https://heidicon.ub.uni-heidelberg.de/api/v1"
tok = requests.get(f"{B}/session", timeout=60).json()["token"]
requests.post(f"{B}/session/authenticate", params={"token": tok, "method": "anonymous"}, timeout=60)
for term in sys.argv[1:]:
    off, rows, count = 0, [], None
    while True:
        body = {"limit": 200, "offset": off, "format": "standard", "objecttypes": ["objekte"],
                "search": [{"type": "match", "mode": "fulltext", "string": term, "phrase": False, "bool": "must"}]}
        d = requests.post(f"{B}/search", params={"token": tok}, data=json.dumps(body), timeout=90).json()
        count = d.get("count"); objs = d.get("objects", [])
        rows += objs; off += len(objs)
        if not objs or off >= count: break
        time.sleep(1)
    print(f"== {term}: count={count}")
    for o in rows:
        rec = o.get("objekte", {})
        pool = "/".join(p["pool"]["name"].get("de-DE", "") for p in rec.get("_pool", {}).get("_path", [])[1:])
        std = o.get("_standard", {})
        t1 = (std.get("1", {}) or {}).get("text", {}); t2 = (std.get("2", {}) or {}).get("text", {})
        title = t1.get("de-DE") or t1.get("und") or ""
        sub = t2.get("de-DE") or t2.get("und") or ""
        print("  ", o.get("_system_object_id"), "|", pool, "|", title[:120], "|", sub[:120])
