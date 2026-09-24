#!/usr/bin/env python3
"""Collectie Nederland (data.collectienederland.nl search API v2) sweep.
rows>=50 is rate-limited, so paginate with rows=20.
Writes ../raw/cn_q_<slug>.json and ../raw/cn_merged.json.
Usage: python3 collectienederland_sweep.py [query ...]
"""
import json, os, re, sys, time
import requests

API = "https://data.collectienederland.nl/api/search/v2/"
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")
QUERIES = ["krokodillenmummie", "krokodil mummie", "krokodil dierenmummie", "mummie van een krokodil",
           "krokodil", "crocodile mummy", "mummified crocodile", "Krokodilmumie", "momie de crocodile",
           "Sobek", "Kom Ombo", "Fayum krokodil", "dierenmummie"]


def vals(fields, key):
    out = []
    for v in fields.get(key, []) or []:
        out.append(v.get("value") if isinstance(v, dict) else v)
    if isinstance(fields.get(key), dict):
        out = [fields[key].get("value")]
    return out


def run(q):
    start, items, total = 1, [], None
    while True:
        params = {"q": q, "format": "json", "rows": 20, "start": start}
        for a in range(4):
            try:
                r = requests.get(API, params=params, timeout=90)
                d = r.json()
                if "result" in d:
                    break
                print("  ", d.get("error"), file=sys.stderr); time.sleep(10 + 10 * a)
            except Exception as exc:  # noqa
                print("  retry", exc, file=sys.stderr); time.sleep(5)
        else:
            return {"query": q, "error": "failed", "total": total, "items": items}
        res = d["result"]
        total = res["pagination"]["numFound"]
        for it in res.get("items", []):
            f = it["item"]["fields"]
            items.append({
                "doc_id": it["item"].get("doc_id"),
                "provider": (vals(f, "edm_dataProvider") or [None])[0],
                "spec": (vals(f, "delving_spec") or [None])[0],
                "title": vals(f, "dc_title")[:2],
                "type": vals(f, "dc_type")[:3],
                "subject": vals(f, "dc_subject")[:4],
                "identifier": vals(f, "dc_identifier")[:3],
                "desc": [x[:300] for x in vals(f, "dc_description")[:2] if x],
                "extent": vals(f, "dcterms_extent")[:2],
                "rights": vals(f, "edm_rights")[:2] + vals(f, "dc_rights")[:2],
                "isShownAt": vals(f, "edm_isShownAt")[:1],
                "isShownBy": vals(f, "edm_isShownBy")[:1],
            })
        if not res["pagination"].get("hasNext") or start > 2000:
            break
        start = res["pagination"]["nextPage"]
        time.sleep(1.5)
    return {"query": q, "total": total, "fetched": len(items), "items": items}


def main():
    qs = sys.argv[1:] or QUERIES
    mp = os.path.join(RAW, "cn_merged.json")
    merged = json.load(open(mp)) if os.path.exists(mp) else {}
    for q in qs:
        res = run(q)
        slug = re.sub(r"[^a-z0-9]+", "_", q.lower()).strip("_")
        json.dump(res, open(os.path.join(RAW, f"cn_q_{slug}.json"), "w"), ensure_ascii=False)
        print(f"{q!r}: total={res.get('total')} fetched={len(res['items'])}")
        for it in res["items"]:
            m = merged.setdefault(it["doc_id"], dict(it, queries=[]))
            if q not in m["queries"]:
                m["queries"].append(q)
    json.dump(merged, open(mp, "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()
