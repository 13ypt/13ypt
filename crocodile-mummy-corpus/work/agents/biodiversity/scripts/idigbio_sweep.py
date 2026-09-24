#!/usr/bin/env python3
"""iDigBio search-API sweep (search.idigbio.org/v2/search/records).

Pages every crocodilian record (family/genus/order filters, split by basisofrecord when large)
and full-text mummy-word searches; scans the raw Darwin Core ("data") of each record for
mummy terms and Egypt terms. Writes ../raw/idigbio_query_log.jsonl,
../raw/idigbio_croc_mummy_hits.json, ../raw/idigbio_croc_egypt.json
"""
import json
import os
import re
import time

import requests

API = "https://search.idigbio.org/v2/search/records"
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(os.path.dirname(HERE), "raw")
MUMMY_RE = re.compile(r"mumm|momie|momif|momia|mumie|mumif|embalm", re.I)
CROC_RE = re.compile(r"crocod|krokod|coccodr|cocodr|alligat|gavial|caiman|osteolaem|suchus|sobek", re.I)
EGYPT_GEO = re.compile(r"egypt|ägypt|thebe|thèbe|kom ombo|ombos|fay[yo]?u?m|faiyum|manfal|maabd|"
                       r"samoun|hawara|gebelein|saqqar|sakkar|luxor|abydos|esna|tebt|crocodilopol|\bnile\b", re.I)
GEO_KEYS = ["dwc:country", "dwc:locality", "dwc:higherGeography", "dwc:stateProvince",
            "dwc:verbatimLocality", "dwc:county", "dwc:waterBody", "dwc:countryCode"]
S = requests.Session()


def post(body):
    for attempt in range(6):
        try:
            r = S.post(API, json=body, timeout=120)
            if r.status_code == 200:
                return r.json()
            print("HTTP", r.status_code, body)
        except requests.RequestException as exc:
            print("err", exc)
        time.sleep(3 * (attempt + 1))
    raise RuntimeError(body)


def page(rq):
    offset = 0
    while True:
        d = post({"rq": rq, "limit": 1000, "offset": offset})
        for it in d["items"]:
            yield it, d["itemCount"]
        offset += 1000
        time.sleep(1)
        if offset >= d["itemCount"] or not d["items"]:
            break


def compact(it):
    data = it.get("data", {})
    keep = {k: v for k, v in data.items() if not k.startswith("dwc:associatedMedia")}
    return {"uuid": it["uuid"], "idigbio_url": f"https://portal.idigbio.org/portal/records/{it['uuid']}",
            "recordset": it.get("indexTerms", {}).get("recordset"), "data": keep}


def main():
    queries = []
    for fam in ["crocodylidae", "alligatoridae", "gavialidae"]:
        n = post({"rq": {"family": fam}, "limit": 0})["itemCount"]
        if n > 9000:
            for bor in ["preservedspecimen", "fossilspecimen", "materialsample", "occurrence",
                        "humanobservation", "machineobservation", "livingspecimen"]:
                queries.append((f"family={fam} basisofrecord={bor}", {"family": fam, "basisofrecord": bor}, "all"))
            queries.append((f"family={fam} basisofrecord missing", {"family": fam, "basisofrecord": {"type": "missing"}}, "all"))
        else:
            queries.append((f"family={fam}", {"family": fam}, "all"))
    queries.append(("family missing, genus=crocodylus", {"genus": "crocodylus", "family": {"type": "missing"}}, "all"))
    queries.append(("order=crocodilia family missing", {"order": "crocodilia", "family": {"type": "missing"}}, "all"))
    for t in ["mummy", "mummified", "mummies", "momie", "momifie", "mumie", "mumifiziert", "mummia",
              "momia", "embalmed", "crocodile mummy", "mummified crocodile", "crocodile", "crocodilus",
              "sobek"]:
        queries.append((f"fulltext={t}", {"data": {"type": "fulltext", "value": t}}, "croc"))
    queries.append(("country=egypt fulltext=crocodile", {"country": "egypt", "data": {"type": "fulltext", "value": "crocodile"}}, "croc"))
    queries.append(("country=egypt fulltext=crocodylus", {"country": "egypt", "data": {"type": "fulltext", "value": "crocodylus"}}, "croc"))
    log = open(os.path.join(RAW, "idigbio_query_log.jsonl"), "w", encoding="utf-8")
    hits, egypt = {}, {}
    for label, rq, mode in queries:
        n = nm = ne = total = 0
        for it, total in page(rq):
            n += 1
            data = it.get("data", {})
            txt = json.dumps(data, ensure_ascii=False)
            if mode != "all" and not CROC_RE.search(txt):
                continue
            if MUMMY_RE.search(txt):
                hits[it["uuid"]] = compact(it)
                nm += 1
            geo = " ".join(str(data.get(k, "")) for k in GEO_KEYS)
            if EGYPT_GEO.search(geo) or str(data.get("dwc:countryCode", "")).upper() == "EG":
                egypt[it["uuid"]] = compact(it)
                ne += 1
        e = {"label": label, "api": API, "rq": rq, "count": total, "fetched": n,
             "croc_mummy_hits": nm, "croc_egypt_hits": ne, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
        print(json.dumps(e), flush=True)
        log.write(json.dumps(e) + "\n")
    json.dump(list(hits.values()), open(os.path.join(RAW, "idigbio_croc_mummy_hits.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(list(egypt.values()), open(os.path.join(RAW, "idigbio_croc_egypt.json"), "w"), indent=1, ensure_ascii=False)
    print("DONE", len(hits), len(egypt))


if __name__ == "__main__":
    main()
