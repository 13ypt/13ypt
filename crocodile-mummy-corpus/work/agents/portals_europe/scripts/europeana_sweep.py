#!/usr/bin/env python3
"""Europeana Search API sweep for crocodile mummies (agent portals_europe).

Runs every query term separately against the Europeana Search API (demo key
api2demo), paginates with cursor, and writes a compact per-query JSON plus a
merged, de-duplicated item table to ../raw/.

Usage: python3 europeana_sweep.py            # all queries
       python3 europeana_sweep.py "extra q"  # extra ad-hoc query
"""
import json
import os
import re
import sys
import time

import requests

API = "https://api.europeana.eu/record/v2/search.json"
KEY = "api2demo"
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(os.path.dirname(HERE), "raw")
os.makedirs(RAW, exist_ok=True)

QUERIES = [
    "crocodile mummy",
    "mummified crocodile",
    '"crocodile" AND mummy',
    "Krokodilmumie",
    "Krokodil Mumie",
    '"mumifiziertes Krokodil"',
    '"momie de crocodile"',
    '"crocodile momifié"',
    '"mummia di coccodrillo"',
    '"coccodrillo mummificato"',
    '"momia de cocodrilo"',
    "krokodillenmummie",
    '"krokodil mummie"',
    "krokodilmumie",
    '"mumia krokodyla"',
    '"mumie krokodýla"',
    '"krokodil múmia"',
    "Crocodylus mummy",
    "Sobek mummy",
    '"Kom Ombo" crocodile',
    "Tebtunis crocodile",
]

MAX_PER_QUERY = 3000  # safety cap


def slug(q):
    return re.sub(r"[^a-z0-9]+", "_", q.lower()).strip("_")[:60]


def first(v):
    if isinstance(v, list):
        return v[0] if v else None
    return v


def compact(item):
    desc = item.get("dcDescription") or []
    return {
        "id": item.get("id"),
        "title": item.get("title"),
        "dataProvider": first(item.get("dataProvider")),
        "provider": first(item.get("provider")),
        "country": first(item.get("country")),
        "type": item.get("type"),
        "year": item.get("year"),
        "rights": item.get("rights"),
        "edmIsShownAt": first(item.get("edmIsShownAt")),
        "edmIsShownBy": first(item.get("edmIsShownBy")),
        "guid": item.get("guid"),
        "dataset": first(item.get("edmDatasetName")),
        "desc": [d[:300] for d in desc][:12],
    }


def run(query, profile="standard"):
    cursor = "*"
    out, total = [], None
    while cursor and len(out) < MAX_PER_QUERY:
        params = {"wskey": KEY, "query": query, "rows": 100, "cursor": cursor,
                  "profile": profile}
        for attempt in range(4):
            try:
                r = requests.get(API, params=params, timeout=60)
                r.raise_for_status()
                js = r.json()
                break
            except Exception as exc:  # noqa
                print("  retry", attempt, exc, file=sys.stderr)
                time.sleep(3 + attempt * 3)
        else:
            return {"query": query, "error": "failed", "items": out, "total": total}
        total = js.get("totalResults")
        out.extend(compact(i) for i in js.get("items", []))
        cursor = js.get("nextCursor")
        time.sleep(1.0)
        if not js.get("items"):
            break
    return {"query": query, "profile": profile, "total": total, "fetched": len(out),
            "items": out}


def main():
    queries = sys.argv[1:] or QUERIES
    merged_path = os.path.join(RAW, "europeana_merged.json")
    merged = {}
    if os.path.exists(merged_path):
        merged = json.load(open(merged_path))
    summary = []
    for q in queries:
        res = run(q)
        fn = os.path.join(RAW, f"europeana_q_{slug(q)}.json")
        json.dump(res, open(fn, "w"), ensure_ascii=False, indent=0)
        print(f"{q!r}: total={res.get('total')} fetched={len(res['items'])}")
        summary.append((q, res.get("total"), len(res["items"])))
        for it in res["items"]:
            m = merged.setdefault(it["id"], dict(it, queries=[]))
            if q not in m["queries"]:
                m["queries"].append(q)
    json.dump(merged, open(merged_path, "w"), ensure_ascii=False, indent=0)
    json.dump(summary, open(os.path.join(RAW, "europeana_query_totals_last.json"), "w"),
              ensure_ascii=False)


if __name__ == "__main__":
    main()
