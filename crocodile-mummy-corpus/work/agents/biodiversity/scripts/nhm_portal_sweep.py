#!/usr/bin/env python3
"""NHM London Data Portal (CKAN datastore) sweep of the specimen collection resource.

Resource 05ff2255-c38a-40c9-b657-4ccb55ab2feb = "Collection specimens" (data.nhm.ac.uk).
Pages every crocodilian record (filters on order/family/genus) plus full-text q= searches for
mummy words and Egyptian place names; scans every field for mummy terms and Egypt terms.
Writes ../raw/nhm_query_log.jsonl, ../raw/nhm_croc_mummy_hits.json, ../raw/nhm_croc_egypt.json
"""
import json
import os
import re
import time

import requests

API = "https://data.nhm.ac.uk/api/3/action/datastore_search"
RES = "05ff2255-c38a-40c9-b657-4ccb55ab2feb"
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(os.path.dirname(HERE), "raw")

MUMMY_RE = re.compile(r"mumm|momie|momif|mumie|mumif|embalm", re.I)
CROC_RE = re.compile(r"crocod|krokod|alligat|gavial|caiman|osteolaem|mecistops|tomistoma|suchus", re.I)
EGYPT_RE = re.compile(r"egypt|thebe|ombo|fay[yo]?u?m|faiyum|manfal|maabd|samoun|hawara|labyrinth|"
                      r"gebelein|saqqar|sakkar|luxor|abydos|esna|tebt|crocodilopol|nile", re.I)

S = requests.Session()


def get(params):
    for attempt in range(6):
        try:
            r = S.get(API, params=params, timeout=90)
            if r.status_code == 200:
                return r.json()["result"]
        except requests.RequestException:
            pass
        time.sleep(3 * (attempt + 1))
    raise RuntimeError(params)


def page(params):
    offset = 0
    while True:
        res = get({**params, "resource_id": RES, "limit": 500, "offset": offset})
        for rec in res["records"]:
            yield rec, res["total"]
        offset += 500
        time.sleep(1)
        if offset >= res["total"] or not res["records"]:
            break


def main():
    queries = []
    for f in [{"order": "Crocodylia"}, {"family": "Crocodylidae"}, {"family": "Alligatoridae"},
              {"family": "Gavialidae"}, {"genus": "Crocodylus"}, {"genus": "Crocodilus"}]:
        queries.append(("filters=" + json.dumps(f), {"filters": json.dumps(f)}, "all"))
    for q in ["mummy", "mummified", "mummies", "momie", "mumie", "embalmed", "crocodile",
              "Crocodylus", "Hawara", "Kom Ombo", "Ombos", "Thebes", "Manfalut", "Maabdeh",
              "Samoun", "Fayum", "Gebelein", "Crocodilopolis", "Labyrinth"]:
        queries.append(("q=" + q, {"q": q}, "croc"))
    log = open(os.path.join(RAW, "nhm_query_log.jsonl"), "w", encoding="utf-8")
    hits, egypt = {}, {}
    for label, params, mode in queries:
        n = nm = ne = total = 0
        for rec, total in page(params):
            n += 1
            txt = json.dumps(rec, ensure_ascii=False)
            croc = mode == "all" or bool(CROC_RE.search(txt))
            if not croc:
                continue
            rec["portal_url"] = f"https://data.nhm.ac.uk/object/{rec.get('occurrenceID')}"
            if MUMMY_RE.search(txt):
                hits[rec["_id"]] = rec
                nm += 1
            if EGYPT_RE.search(txt):
                egypt[rec["_id"]] = rec
                ne += 1
        e = {"label": label, "api": API, "resource_id": RES, "count": total, "fetched": n,
             "croc_mummy_hits": nm, "croc_egypt_hits": ne, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
        print(json.dumps(e), flush=True)
        log.write(json.dumps(e) + "\n")
    json.dump(list(hits.values()), open(os.path.join(RAW, "nhm_croc_mummy_hits.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(list(egypt.values()), open(os.path.join(RAW, "nhm_croc_egypt.json"), "w"), indent=1, ensure_ascii=False)
    print("DONE", len(hits), len(egypt))


if __name__ == "__main__":
    main()
