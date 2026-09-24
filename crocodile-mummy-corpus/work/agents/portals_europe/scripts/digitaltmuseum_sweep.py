#!/usr/bin/env python3
"""DigitaltMuseum (SE/NO) sweep via the DiMu Solr API (api.dimu.org, api.key=demo).
Writes ../raw/dimu_q_<slug>.json and ../raw/dimu_merged.json.
Usage: python3 digitaltmuseum_sweep.py [query ...]
"""
import json, os, re, sys, time
import requests

API = "https://api.dimu.org/api/solr/select"
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")
QUERIES = ["krokodil mumie", "krokodilmumie", "krokodillemumie", "krokodille mumie",
           "mumifierad krokodil", "mumifisert krokodille", "mumificeret krokodille", "krokodilunge",
           "krokodilleunge", "crocodile mummy", "mummified crocodile", "krokodil", "krokodille",
           "Sobek", "dyremumie", "djurmumie", "Kom Ombo"]
FL = ("identifier.id,identifier.owner,artifact.uniqueId,artifact.type,artifact.ingress.title,"
      "artifact.ingress.description,artifact.ingress.license,artifact.ingress.classification,"
      "artifact.ingress.subjects,artifact.pictureCount,artifact.ingress.production.place")


def run(q):
    start, docs, total = 0, [], None
    while True:
        params = {"q": q, "wt": "json", "rows": 100, "start": start, "api.key": "demo", "fl": FL}
        r = requests.get(API, params=params, timeout=90)
        d = r.json()["response"]
        total = d["numFound"]
        for doc in d["docs"]:
            desc = doc.get("artifact.ingress.description")
            if isinstance(desc, list):
                desc = " ".join(desc)
            docs.append({"owner": doc.get("identifier.owner"), "id": doc.get("identifier.id"),
                         "uid": doc.get("artifact.uniqueId"), "type": doc.get("artifact.type"),
                         "title": doc.get("artifact.ingress.title"),
                         "desc": (desc or "")[:300],
                         "license": doc.get("artifact.ingress.license"),
                         "subjects": doc.get("artifact.ingress.subjects"),
                         "classification": doc.get("artifact.ingress.classification"),
                         "pics": doc.get("artifact.pictureCount")})
        start += len(d["docs"])
        if not d["docs"] or start >= total or start >= 2000:
            break
        time.sleep(1)
    return {"query": q, "total": total, "fetched": len(docs), "items": docs}


def main():
    qs = sys.argv[1:] or QUERIES
    mp = os.path.join(RAW, "dimu_merged.json")
    merged = json.load(open(mp)) if os.path.exists(mp) else {}
    for q in qs:
        res = run(q)
        slug = re.sub(r"[^a-z0-9]+", "_", q.lower()).strip("_")
        json.dump(res, open(os.path.join(RAW, f"dimu_q_{slug}.json"), "w"), ensure_ascii=False)
        print(f"{q!r}: total={res['total']} fetched={res['fetched']}")
        for it in res["items"]:
            m = merged.setdefault(it["uid"], dict(it, queries=[]))
            if q not in m["queries"]:
                m["queries"].append(q)
        time.sleep(1)
    json.dump(merged, open(mp, "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()
