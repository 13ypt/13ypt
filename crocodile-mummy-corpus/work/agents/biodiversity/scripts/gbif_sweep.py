#!/usr/bin/env python3
"""Systematic GBIF occurrence-API sweep for crocodile mummies catalogued as specimens.

Reproducible: run `python3 gbif_sweep.py` from any directory. Writes to ../raw/:
  gbif_query_log.jsonl   one line per query (params, total count, records fetched, hits)
  gbif_mummy_hits.json   compact records whose text matches a mummy term AND (crocodilian
                          taxon OR a crocodile word) -> candidates for manual review
  gbif_crocodylia_egypt.json  compact Crocodylia records with Egypt in country/locality text
                          (NOT mummies unless reviewed; used for leads summary)

Strategy
  A. every Crocodylia (GBIF backbone class key 11493978) record of every non-observation
     basisOfRecord is paged through completely and every text field is scanned for mummy terms
     (multilingual) and for Egypt terms.
  B. untaxoned full-text q= searches for mummy words in many languages (all basisOfRecord);
     records kept if they also mention a crocodile word or belong to Crocodylia.
  C. untaxoned q= crocodile words restricted to records whose taxon could not be matched
     precisely (issue TAXON_MATCH_HIGHERRANK / TAXON_MATCH_NONE), i.e. records such as
     "Crocodile mummy" that GBIF could not place in Crocodylia.
  D. untaxoned q= Egyptian crocodile-cult place names (Manfalut, Maabda, Samoun, Kom Ombo,
     Crocodilopolis, Gebelein, Hawara, Theben/Thebes...), kept if crocodile word/taxon present.
Polite: ~1 request/s, retries with backoff.
"""
import json
import os
import re
import sys
import time

import requests

API = "https://api.gbif.org/v1/occurrence/search"
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(os.path.dirname(HERE), "raw")
os.makedirs(RAW, exist_ok=True)

CROCODYLIA = 11493978
NONOBS = ["PRESERVED_SPECIMEN", "FOSSIL_SPECIMEN", "MATERIAL_SAMPLE", "OCCURRENCE",
          "MATERIAL_CITATION", "LIVING_SPECIMEN", "OBSERVATION"]

MUMMY_RE = re.compile(
    r"mumm|momie|momif|momia|mumie|mumif|mumia|embalm|einbalsam|balsamiert|"
    r"مومي|محنط|تحنيط",  # مومي محنط تحنيط
    re.I)
CROC_RE = re.compile(
    r"crocod|krokod|coccodr|cocodr|suchus|sobek|souchos|suchos|timsah|تمساح",
    re.I)
EGYPT_RE = re.compile(
    r"egypt|ägypt|aegypt|egypte|égypte|egitto|egipto|egypten|egipt|مصر|"
    r"thebe|thèbe|ombo|fay[yo]?u?m|faiyum|manfal|maabd|samoun|tebt|crocodilopol|gebelein|"
    r"hawara|saqqar|sakkar|luxor|karnak|abydos|esna|akoris|tehna|tuna el|beni hasan",
    re.I)

KEEP = ["key", "datasetKey", "datasetName", "publishingOrgKey", "institutionCode",
        "collectionCode", "catalogNumber", "otherCatalogNumbers", "occurrenceID",
        "scientificName", "verbatimScientificName", "acceptedScientificName", "taxonKey",
        "basisOfRecord", "country", "countryCode", "stateProvince", "locality",
        "verbatimLocality", "higherGeography", "preparations", "occurrenceRemarks",
        "eventDate", "year", "verbatimEventDate", "recordedBy", "identifiedBy",
        "fieldNumber", "references", "dynamicProperties", "associatedReferences",
        "typeStatus", "sex", "lifeStage", "individualCount", "license", "rightsHolder",
        "institutionID", "collectionID", "modified", "lastInterpreted", "issues",
        "organismRemarks", "georeferenceRemarks", "eventRemarks", "identificationRemarks",
        "disposition", "materialSampleID", "catalogNumberStr"]

session = requests.Session()
session.headers["User-Agent"] = "crocodile-mummy-corpus research (biodiversity agent)"


def get(params):
    for attempt in range(8):
        try:
            r = session.get(API, params=params, timeout=90)
            if r.status_code == 200:
                return r.json()
            print(f"  HTTP {r.status_code} for {params}", file=sys.stderr)
        except requests.RequestException as exc:
            print(f"  error {exc.__class__.__name__}; retry", file=sys.stderr)
        time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"failed: {params}")


def compact(rec):
    out = {k: rec[k] for k in KEEP if k in rec}
    media = rec.get("media") or []
    if media:
        out["media"] = [{k: m.get(k) for k in ("identifier", "references", "license", "rightsHolder", "title")}
                        for m in media[:5]]
    out["gbif_url"] = f"https://www.gbif.org/occurrence/{rec['key']}"
    return out


def text_of(rec):
    return json.dumps(rec, ensure_ascii=False)


def page_all(params, max_records=100000):
    offset, total = 0, None
    while True:
        d = get({**params, "limit": 300, "offset": offset})
        total = d["count"]
        for rec in d["results"]:
            yield rec, total
        offset += 300
        time.sleep(1.0)
        if d.get("endOfRecords") or offset >= min(total, max_records):
            break


def is_croc(rec):
    return rec.get("classKey") == CROCODYLIA or bool(CROC_RE.search(text_of(rec)))


def run():
    queries = []
    # A. whole Crocodylia non-observation corpus
    for bor in NONOBS:
        queries.append((f"A:Crocodylia basisOfRecord={bor}",
                        {"taxonKey": CROCODYLIA, "basisOfRecord": bor}, "croc_all"))
    # also human/machine observations from Egypt (small) in case museum data mis-typed
    queries.append(("A:Crocodylia country=EG all basisOfRecord", {"taxonKey": CROCODYLIA, "country": "EG"}, "croc_all"))
    # B. mummy words, untaxoned
    for t in ["mummy", "mummified", "mummies", "mummie", "momie", "momies", "momifié", "momifie",
              "mumie", "mumien", "mumifiziert", "mummia", "mummie", "mummificato", "momia",
              "momificado", "mumia", "mumificado", "embalmed", "mumifierad", "mumificeret",
              "mumio", "mummificatie", "mumifikovaný", "مومياء", "محنط"]:
        queries.append((f"B:q={t}", {"q": t}, "mummy_croc"))
    # C. crocodile words where taxon match failed/higher rank
    for t in ["crocodile", "crocodiles", "crocodilus", "crocodylus", "krokodil", "coccodrillo",
              "cocodrilo", "krokodille", "timsah", "sobek", "suchos", "souchos", "تمساح"]:
        for iss in ["TAXON_MATCH_HIGHERRANK", "TAXON_MATCH_NONE"]:
            queries.append((f"C:q={t} issue={iss}", {"q": t, "issue": iss}, "croc_any"))
    # D. Egyptian place names, untaxoned, keep croc
    for t in ["manfalut", "manfalout", "maabda", "maabdah", "samoun", "ombos", "ombo",
              "crocodilopolis", "gebelein", "hawara", "theben", "thebes", "thèbes", "tebe",
              "tebtunis", "tebtynis", "saqqara", "sakkara", "fayum", "faiyum", "fayoum",
              "fayyum", "abydos", "esna", "akoris"]:
        queries.append((f"D:q={t} nonobs", {"q": t, "basisOfRecord": NONOBS}, "croc_any"))
    queries.append(("D:q=crocodile country=EG", {"q": "crocodile", "country": "EG"}, "croc_any"))

    only = sys.argv[1:]  # optional label prefixes to run a subset
    suffix = ("_" + "_".join(only).replace(":", "")) if only else ""
    log = open(os.path.join(RAW, f"gbif_query_log{suffix}.jsonl"), "w", encoding="utf-8")
    mummy_hits, egypt_croc = {}, {}
    for label, params, mode in queries:
        if only and not any(label.startswith(o) for o in only):
            continue
        n, n_m, n_eg, total = 0, 0, 0, 0
        for rec, total in page_all(params):
            n += 1
            txt = text_of(rec)
            croc = rec.get("classKey") == CROCODYLIA or bool(CROC_RE.search(txt))
            if MUMMY_RE.search(txt) and (mode == "croc_all" or croc):
                mummy_hits[rec["key"]] = compact(rec)
                mummy_hits[rec["key"]]["_found_by"] = label
                n_m += 1
            if croc and (rec.get("countryCode") == "EG" or EGYPT_RE.search(txt)):
                if rec["key"] not in egypt_croc:
                    egypt_croc[rec["key"]] = compact(rec)
                n_eg += 1
        entry = {"label": label, "api": API, "params": params, "count": total,
                 "fetched": n, "mummy_croc_hits": n_m, "egypt_croc_hits": n_eg,
                 "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
        print(json.dumps(entry, ensure_ascii=False), flush=True)
        log.write(json.dumps(entry, ensure_ascii=False) + "\n")
        log.flush()
    log.close()
    with open(os.path.join(RAW, f"gbif_mummy_hits{suffix}.json"), "w", encoding="utf-8") as fh:
        json.dump(list(mummy_hits.values()), fh, ensure_ascii=False, indent=1)
    with open(os.path.join(RAW, f"gbif_crocodylia_egypt{suffix}.json"), "w", encoding="utf-8") as fh:
        json.dump(list(egypt_croc.values()), fh, ensure_ascii=False, indent=1)
    print(f"DONE mummy_hits={len(mummy_hits)} egypt_croc={len(egypt_croc)}")


if __name__ == "__main__":
    run()
