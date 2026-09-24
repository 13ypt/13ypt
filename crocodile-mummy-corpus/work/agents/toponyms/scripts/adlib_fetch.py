#!/usr/bin/env python3
"""Fetch all records from an Adlib/Axiell wwwopac API for a search; flatten; save JSONL.
usage: adlib_fetch.py <base_url> <database> "<search>" <out.jsonl>"""
import sys, json, time, requests
base, db, search, out = sys.argv[1:5]
def flat(x):
    if isinstance(x, dict):
        if "spans" in x: return " ".join(s.get("text", "") for s in x["spans"])
        if "value" in x and len(x) <= 3: return str(x["value"])
        return {k: flat(v) for k, v in x.items()}
    if isinstance(x, list): return [flat(i) for i in x]
    return x
recs, start = [], 1
while True:
    r = requests.get(base, params={"database": db, "search": search, "output": "json", "xmltype": "grouped", "limit": 100, "startfrom": start},
                     headers={"User-Agent": "Mozilla/5.0"}, timeout=120)
    d = r.json()["adlibJSON"]
    hits = d["diagnostic"].get("hits", 0)
    rl = (d.get("recordList") or {}).get("record", [])
    recs += [flat(x) for x in rl]
    if not rl or len(recs) >= hits: break
    start += 100; time.sleep(1)
with open(out, "w") as fh:
    for x in recs: fh.write(json.dumps(x, ensure_ascii=False) + "\n")
print("hits", hits, "saved", len(recs))
