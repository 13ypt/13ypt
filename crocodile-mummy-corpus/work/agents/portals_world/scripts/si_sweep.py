"""Smithsonian Open Access API sweep (api.si.edu, DEMO_KEY, paced ~1 request / 2 s).

DEMO_KEY allows only ~30 requests/hour: run 2nd pass with SI_PAUSE=130 SI_TAG=_pass2 and the
remaining queries as argv. Pages through every query completely (rows=100, start=0,100,...), keeps a compact
summary of every hit, and flags rows whose title/freetext mention mumm* + crocod*/Sobek.
"""
import json
import re
import sys

from common import get, save_raw

BASE = "https://api.si.edu/openaccess/api/v1.0/search"
KEY = "DEMO_KEY"
QUERIES = [
    '"crocodile mummy"',
    '"mummified crocodile"',
    'crocodile AND mummy',
    'crocodile mummy',
    '"Crocodylus" mummy',
    'Crocodylus AND mummified',
    'crocodile AND mummified',
    '"Mummied Crocodile"',
    'crocodile AND unit_code:NMNHANTHRO',
    'reptile AND mummy AND unit_code:NMNHANTHRO',
    'Sobek',
    'crocodile AND Egypt',
    'Crocodylus niloticus',
    'crocodile AND unit_code:NMAfA',
    'crocodile AND unit_code:FSG',
]
PM = re.compile(r"mumm", re.I)
PC = re.compile(r"crocod|sobek|souchos|suchos", re.I)


def flat(x):
    if isinstance(x, dict):
        return " ".join(flat(v) for v in x.values())
    if isinstance(x, list):
        return " ".join(flat(v) for v in x)
    return str(x)


def main():
    import os
    queries = sys.argv[1:] or QUERIES
    pause = float(os.environ.get("SI_PAUSE", "2.0"))
    tag = os.environ.get("SI_TAG", "")
    stats = {}
    rows_all = {}
    for q in queries:
        start, hits, ids = 0, None, []
        while True:
            for attempt in range(4):
                r, err = get(BASE, params={"q": q, "rows": 100, "start": start, "api_key": KEY}, pause=pause)
                if not err and r.status_code == 429:
                    print("429, sleeping 600 s", file=sys.stderr)
                    import time
                    time.sleep(600)
                    continue
                break
            if err or r.status_code != 200:
                stats[q] = {"error": err or r.status_code, "hits_so_far": len(ids)}
                break
            resp = r.json().get("response", {})
            hits = resp.get("rowCount", 0)
            rows = resp.get("rows", [])
            for row in rows:
                ids.append(row["id"])
                if row["id"] not in rows_all:
                    rows_all[row["id"]] = row
            start += 100
            if start >= hits or not rows:
                break
        cands = [i for i in ids if PM.search(flat(rows_all[i].get("title", "")) + " " +
                                           flat(rows_all[i].get("content", {}).get("freetext", {})))
                 and PC.search(flat(rows_all[i].get("title", "")) + " " +
                               flat(rows_all[i].get("content", {}).get("freetext", {})))]
        stats.setdefault(q, {}).update({"hits": hits, "retrieved": len(ids),
                                        "mumm+croc candidates": cands})
        print(q, hits, len(ids), len(cands), file=sys.stderr)
    save_raw(f"si_query_stats{tag}.json", stats)
    summary = {i: {"title": r.get("title"), "unitCode": r.get("unitCode"),
                   "record_link": r.get("content", {}).get("descriptiveNonRepeating", {}).get("record_link")}
               for i, r in rows_all.items()}
    save_raw(f"si_all_hits_summary{tag}.json", summary)
    cand_ids = sorted({c for s in stats.values() for c in s.get("mumm+croc candidates", [])})
    save_raw(f"si_candidates_full{tag}.json", {i: rows_all[i] for i in cand_ids})
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
