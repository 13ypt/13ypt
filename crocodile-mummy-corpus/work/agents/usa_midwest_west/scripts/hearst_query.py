#!/usr/bin/env python3
"""Query the Phoebe A. Hearst Museum portal (Blacklight JSON API) and flatten records.

Usage: python3 hearst_query.py "<query>" [outfile.json] [--full]
  Lists all hits (id, title, museum number, culture, place, class).
  With --full, fetches the full record JSON for hits whose summary matches
  crocodile/reptile/mummy keywords and writes flattened records to outfile.
Polite: 1 request per second.
"""
import json
import re
import sys
import time

import requests

BASE = "https://portal.hearstmuseum.berkeley.edu"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")
S = requests.Session()
S.headers["User-Agent"] = UA


def val(a, k):
    v = a.get(k)
    if isinstance(v, dict):
        return v.get("attributes", {}).get("value", "")
    return v if isinstance(v, str) else ""


def search(q):
    out, page = [], 1
    while True:
        r = S.get(f"{BASE}/catalog.json", params={"q": q, "per_page": 100, "page": page}, timeout=60)
        r.raise_for_status()
        d = r.json()
        for rec in d["data"]:
            a = rec["attributes"]
            out.append({"id": rec["id"], "title": a.get("title"), "musno": val(a, "objmusno_s"),
                        "culture": val(a, "objassoccult_ss"), "place": val(a, "objfcp_s"),
                        "class": val(a, "objobjectclass_ss")})
        total = d["meta"]["pages"]["total_count"]
        if d["meta"]["pages"].get("last_page?") or not d["meta"]["pages"].get("next_page"):
            break
        page += 1
        time.sleep(1)
    return out, total


def full(rid):
    r = S.get(f"{BASE}/catalog/{rid}.json", timeout=60)
    r.raise_for_status()
    a = r.json()["data"]["attributes"]
    flat = {"id": rid, "url": f"{BASE}/catalog/{rid}", "title": a.get("title")}
    for k, v in a.items():
        if isinstance(v, dict):
            lab = v.get("attributes", {}).get("label", k)
            value = v.get("attributes", {}).get("value", "")
            if k == "blob_ss":
                imgs = re.findall(r'href="(https://webapps\.cspace\.berkeley\.edu/pahma/imageserver/blobs/[^"]+/content)"', value)
                m = re.search(r"object 1 of (\d+)", value)
                flat["image_count"] = m.group(1) if m else str(len(imgs))
                flat["images_first5"] = imgs[:5]
                continue
            value = re.sub(r"<[^>]+>", "", value)
            flat[lab] = value
    return flat


if __name__ == "__main__":
    q = sys.argv[1]
    hits, total = search(q)
    print(f"query={q!r} total={total}")
    kw = re.compile(r"crocod|reptil|sobek|mumm|saur|crocodylus", re.I)
    sel = []
    for h in hits:
        line = " | ".join(str(h[k]) for k in ("musno", "title", "culture", "place", "class"))
        print(line)
        if kw.search(line) and ("Egypt" in line or "Faiyum" in line or "Tebtunis" in line or not h["place"]):
            sel.append(h)
    if "--full" in sys.argv and len(sys.argv) > 2 and not sys.argv[2].startswith("--"):
        recs = []
        for h in sel:
            time.sleep(1)
            recs.append(full(h["id"]))
        json.dump(recs, open(sys.argv[2], "w"), indent=1, ensure_ascii=False)
        print(f"wrote {len(recs)} full records to {sys.argv[2]}")
