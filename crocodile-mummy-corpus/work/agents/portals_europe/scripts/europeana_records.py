#!/usr/bin/env python3
"""Fetch full Europeana records (Record API v2) for candidate crocodile-mummy items
and extract the fields needed for the corpus (provider proxy values, rights,
edmIsShownAt/By, IIIF manifest). Writes ../raw/europeana_records.json.

Usage: python3 europeana_records.py ID [ID ...]   (IDs like /15502/AE_INV_292)
       python3 europeana_records.py --file ids.txt
"""
import json
import os
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(os.path.dirname(HERE), "raw")
OUT = os.path.join(RAW, "europeana_records.json")


def flat(langmap):
    if not langmap:
        return None
    if isinstance(langmap, dict):
        vals = []
        for k, v in langmap.items():
            for x in (v if isinstance(v, list) else [v]):
                vals.append(f"[{k}] {x}")
        return vals
    return langmap


def extract(rid):
    url = f"https://api.europeana.eu/record/v2{rid}.json"
    r = requests.get(url, params={"wskey": "api2demo"}, timeout=60)
    r.raise_for_status()
    d = r.json()["object"]
    prov = [p for p in d["proxies"] if not p.get("europeanaProxy")]
    p = prov[0] if prov else d["proxies"][0]
    keys = ["dcTitle", "dcIdentifier", "dcDescription", "dcType", "dcSubject", "dcDate",
            "dctermsCreated", "dctermsExtent", "dcFormat", "dctermsMedium",
            "dctermsProvenance", "dctermsSpatial", "dcSource", "dcCoverage",
            "dctermsTemporal", "dcPublisher", "dcRights", "dctermsIsPartOf",
            "dctermsAlternative"]
    rec = {"id": rid, "portal_url": f"https://www.europeana.eu/item{rid}"}
    for k in keys:
        if p.get(k):
            rec[k] = flat(p[k])
    agg = [a for a in d["aggregations"] if "/provider/" in a.get("about", "")]
    a = agg[0] if agg else d["aggregations"][0]
    rec["edmIsShownAt"] = a.get("edmIsShownAt")
    rec["edmIsShownBy"] = a.get("edmIsShownBy")
    rec["edmRights"] = flat(a.get("edmRights"))
    rec["edmDataProvider"] = flat(a.get("edmDataProvider"))
    iiif = []
    for w in a.get("webResources", []):
        for ref in w.get("dctermsIsReferencedBy", []) or []:
            if "iiif" in ref or "manifest" in ref:
                iiif.append(ref)
        if w.get("rdfType", "").startswith("http://iiif.io"):
            iiif.append(w["about"])
        for s in w.get("svcsHasService", []) or []:
            iiif.append("service:" + s)
    rec["iiif"] = sorted(set(iiif))
    orgs = d.get("organizations") or []
    rec["organizations"] = [flat(o.get("prefLabel")) for o in orgs][:3]
    return rec


def main():
    ids = sys.argv[1:]
    if ids and ids[0] == "--file":
        ids = [l.strip() for l in open(ids[1]) if l.strip()]
    store = json.load(open(OUT)) if os.path.exists(OUT) else {}
    for rid in ids:
        try:
            store[rid] = extract(rid)
            print("ok", rid)
        except Exception as exc:  # noqa
            print("FAIL", rid, exc)
        time.sleep(1)
    json.dump(store, open(OUT, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
