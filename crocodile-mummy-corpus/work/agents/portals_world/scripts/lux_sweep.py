"""Yale LUX (lux.collections.yale.edu) Linked Art API sweep.

LUX's CloudFront rejects curl/python default User-Agents; requests are sent with an empty
User-Agent and Accept: application/json (works as of 2026-09-24).
For each text query: page through /api/search/item (pageLength=100), fetch every object
record /data/object/<uuid>, keep label, identifiers, unit, descriptions, IIIF manifest,
images; flag records mentioning crocod*/Sobek + mumm*.
"""
import json
import re
import sys
import time
import urllib.parse

import requests

from common import save_raw

S = requests.Session()
S.headers.update({"User-Agent": "", "Accept": "application/json"})
QUERIES = ["crocodile mummy", "mummified crocodile", "Sobek", "Crocodylus", "animal mummy",
           "Krokodil", "momie crocodile"]
PM = re.compile(r"mumm|momie", re.I)
PC = re.compile(r"crocod|sobek|krokodil", re.I)


def j(url, params=None):
    time.sleep(1.1)
    r = S.get(url, params=params, timeout=90)
    r.raise_for_status()
    return r.json()


def texts(obj, key):
    out = []
    for x in obj.get(key, []) or []:
        c = x.get("content")
        lab = x.get("classified_as", [{}])[0].get("_label") if x.get("classified_as") else None
        if c:
            out.append(f"{lab}: {c}" if lab else c)
    return out


def summarize(o):
    ids = []
    for i in o.get("identified_by", []):
        lab = ",".join(c.get("_label", "") for c in i.get("classified_as", []) or [])
        ids.append(f"{i.get('type')}[{lab}]={i.get('content')}")
    members = [m.get("_label") or m.get("id") for m in o.get("member_of", []) or []]
    reps = []
    for rep in o.get("representation", []) or []:
        for dp in rep.get("digitally_shown_by", []) or []:
            for ap in dp.get("access_point", []) or []:
                reps.append(ap.get("id"))
    manifests = []
    for s in o.get("subject_of", []) or []:
        for dc in s.get("digitally_carried_by", []) or []:
            for ap in dc.get("access_point", []) or []:
                manifests.append(ap.get("id"))
    dims = [f"{d.get('classified_as', [{}])[0].get('_label') if d.get('classified_as') else ''} {d.get('value')} {d.get('unit', {}).get('_label', '')}"
            for d in o.get("dimension", []) or []]
    return {"id": o.get("id"), "label": o.get("_label"), "identifiers": ids, "member_of": members,
            "classified_as": [c.get("_label") for c in o.get("classified_as", []) or []],
            "referred_to_by": texts(o, "referred_to_by"), "images": reps, "subject_of_access_points": manifests,
            "dimensions": dims}


def main():
    out = {}
    objects = {}
    for q in QUERIES:
        qj = json.dumps({"text": q})
        page, ids, total = 1, [], None
        while True:
            d = j("https://lux.collections.yale.edu/api/search/item", {"q": qj, "page": page, "pageLength": 100})
            total = d.get("partOf", [{}])[0].get("totalItems")
            items = [x["id"] for x in d.get("orderedItems", [])]
            ids += items
            if len(ids) >= (total or 0) or not items or page >= 10:
                break
            page += 1
        flagged = []
        for u in ids:
            if "/data/object/" not in u:
                continue
            if u not in objects:
                try:
                    objects[u] = summarize(j(u))
                except Exception as exc:
                    objects[u] = {"id": u, "error": str(exc)}
            blob = json.dumps(objects[u], ensure_ascii=False)
            if PM.search(blob) and PC.search(blob):
                flagged.append(u)
        out[q] = {"total": total, "retrieved": len(ids), "flagged": flagged,
                  "labels": [(objects.get(u, {}).get("label"), u) for u in ids if u in objects][:300]}
        print(q, total, len(ids), len(flagged), file=sys.stderr)
    save_raw("lux_results.json", out)
    fl = sorted({u for v in out.values() for u in v["flagged"]})
    save_raw("lux_flagged_objects.json", {u: objects[u] for u in fl})
    for u in fl:
        print(json.dumps(objects[u], ensure_ascii=False)[:1500])


if __name__ == "__main__":
    main()
