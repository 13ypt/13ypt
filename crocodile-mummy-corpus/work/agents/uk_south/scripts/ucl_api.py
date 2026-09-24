#!/usr/bin/env python3
"""Query the UCL Collections Axiell WebAPI (wwwopac.ashx) directly.

Usage: python3 ucl_api.py <database> "<adlib search expression>" [out.json]
  database: petrie | zoology | collect | art | pathology | science
  e.g.  python3 ucl_api.py zoology "all" ; python3 ucl_api.py petrie "description=crocodile*"
Prints: priref | object_number | first 250 chars of all text fields concatenated
"""
import json
import sys
import time

import requests

API = "https://collections.ucl.ac.uk/AxiellWebApi/wwwopac.ashx"


def flat(v):
    out = []
    if isinstance(v, dict):
        if "text" in v and isinstance(v["text"], str):
            out.append(v["text"])
        for k, x in v.items():
            if k != "text":
                out += flat(x)
    elif isinstance(v, list):
        for x in v:
            out += flat(x)
    elif isinstance(v, str):
        pass
    return out


def main():
    db, q = sys.argv[1], sys.argv[2]
    outp = sys.argv[3] if len(sys.argv) > 3 else None
    recs, start = [], 1
    while True:
        r = requests.get(API, params={"database": db, "search": q, "output": "json",
                                      "limit": 100, "startfrom": start}, timeout=120)
        d = r.json()["adlibJSON"]
        rl = d.get("recordList") or {}
        batch = rl.get("record", []) if isinstance(rl, dict) else []
        recs += batch
        hits = d["diagnostic"]["hits"]
        if not batch or len(recs) >= hits:
            break
        start += 100
        time.sleep(1)
    print(f"# db={db} search={q!r} hits={hits} fetched={len(recs)}", file=sys.stderr)
    if outp:
        json.dump(recs, open(outp, "w"), ensure_ascii=False)
    for rec in recs:
        on = " ".join(flat(rec.get("object_number", [])))
        txt = " | ".join(t for t in flat({k: v for k, v in rec.items() if k != "object_number"}) if t)
        print(f"{rec.get('@priref')}\t{on}\t{txt[:400]}")


if __name__ == "__main__":
    main()
