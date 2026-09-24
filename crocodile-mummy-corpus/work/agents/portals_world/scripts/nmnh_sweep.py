"""NMNH (Smithsonian National Museum of Natural History) collections search backend sweep.

The public search UIs at collections.nmnh.si.edu/search/<dept>/ are ExtJS front ends that
POST to <dept>/search.php with action=1 (AC_QUERY), qtype=1 (QT_KEYWORD), start, limit, terms.
This script enumerates all hits for each keyword query (paged, limit=100), saves the full
records of every hit that mentions crocod*/Crocodyl*/Sobek AND mumm*, plus a compact
listing of all hits.
"""
import json
import re
import sys

from common import get, save_raw
import requests
import time

BASE = "https://collections.nmnh.si.edu/search/{dept}/search.php"
DEPTS = {
    "anth": ["crocodile", "crocodile mummy", "mummied crocodile", "mummified crocodile",
             "crocodiles", "Crocodylus", "Sobek", "reptile mummy", "mummified reptiles",
             "animal mummy", "Kom Ombo", "Fayum", "Samoun", "Maabdeh", "Manfalut"],
    "herps": ["Crocodylus mummy", "mummy", "mummified", "Egypt Crocodylus", "Crocodylus niloticus"],
}
S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0"
PM = re.compile(r"mumm", re.I)
PC = re.compile(r"crocod|sobek|souchos|suchos", re.I)


def query(dept, terms):
    out, start, total = [], 0, None
    while True:
        time.sleep(1.2)
        r = S.post(BASE.format(dept=dept), data={"action": 1, "qtype": 1, "start": start,
                                                 "limit": 100, "terms": terms}, timeout=90)
        d = r.json()
        total = d.get("totalRecords", 0)
        recs = d.get("records", [])
        out += recs
        start += 100
        if start >= total or not recs or start >= 2000:
            break
    return total, out


def main():
    stats, cands = {}, {}
    for dept, qs in DEPTS.items():
        for q in qs:
            try:
                total, recs = query(dept, q)
            except Exception as exc:
                stats[f"{dept}|{q}"] = {"error": str(exc)}
                continue
            hits = []
            for rec in recs:
                blob = json.dumps(rec, ensure_ascii=False)
                c = bool(PM.search(blob) and PC.search(blob))
                hits.append({"_id": rec.get("_id"), "cat": rec.get("catbc") or rec.get("catnb"),
                             "name": rec.get("ideco") or rec.get("idetx") or rec.get("ideoj"),
                             "country": rec.get("darct"), "croc_mummy_flag": c})
                if c:
                    cands[rec.get("_id")] = rec
            stats[f"{dept}|{q}"] = {"total": total, "retrieved": len(recs),
                                    "flagged": [h for h in hits if h["croc_mummy_flag"]],
                                    "all": hits if len(hits) <= 300 else hits[:300]}
            print(dept, q, total, len(recs), sum(h["croc_mummy_flag"] for h in hits), file=sys.stderr)
    save_raw("nmnh_query_stats.json", stats)
    save_raw("nmnh_candidates_full.json", {str(k): v for k, v in cands.items()})
    for k, v in stats.items():
        print(k, v.get("total"), v.get("retrieved"), [(h["cat"], h["name"]) for h in v.get("flagged", [])])


if __name__ == "__main__":
    main()
