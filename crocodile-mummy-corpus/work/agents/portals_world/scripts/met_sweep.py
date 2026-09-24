"""Metropolitan Museum of Art Collection API sweep for crocodile mummies.

Enumerates ALL hit IDs of each query (the search endpoint returns every ID, no paging),
fetches every object record once, saves a compact JSON of the fields we need, and prints
candidates whose title/objectName/medium/classification mention mummy + crocodile/Sobek.
"""
import json
import re
import sys

from common import get, log, save_raw

BASE = "https://collectionapi.metmuseum.org/public/collection/v1"
QUERIES = [
    ({"q": "crocodile"}, "crocodile (all departments)"),
    ({"q": "crocodile mummy"}, "crocodile mummy"),
    ({"q": "mummified crocodile"}, "mummified crocodile"),
    ({"q": "Sobek"}, "Sobek"),
    ({"q": "Crocodylus"}, "Crocodylus"),
    ({"q": "Souchos"}, "Souchos"),
    ({"departmentId": 10, "q": "crocodile"}, "departmentId=10 crocodile"),
    ({"departmentId": 10, "q": "Sobek"}, "departmentId=10 Sobek"),
    ({"departmentId": 10, "q": "animal mummy"}, "departmentId=10 animal mummy"),
    ({"departmentId": 10, "q": "crocodile mummy"}, "departmentId=10 crocodile mummy"),
    ({"departmentId": 10, "q": "Fayum crocodile"}, "departmentId=10 Fayum crocodile"),
    ({"departmentId": 10, "q": "Kom Ombo"}, "departmentId=10 Kom Ombo"),
]
KEEP = ["objectID", "accessionNumber", "title", "objectName", "department", "classification",
        "culture", "period", "dynasty", "reign", "objectDate", "objectBeginDate", "objectEndDate",
        "medium", "dimensions", "creditLine", "geographyType", "city", "region", "subregion",
        "locale", "locus", "excavation", "river", "country", "isPublicDomain", "primaryImage",
        "primaryImageSmall", "additionalImages", "objectURL", "tags", "GalleryNumber",
        "accessionYear", "metadataDate", "rightsAndReproduction"]


def main():
    ids_by_query = {}
    all_ids = []
    for params, label in QUERIES:
        r, err = get(BASE + "/search", params=params, pause=1.0)
        if err or r.status_code != 200:
            log("US", "en", "Met Collection API /search", label, f"ERROR {err or r.status_code}",
                "Metropolitan Museum of Art")
            continue
        d = r.json()
        ids = d.get("objectIDs") or []
        ids_by_query[label] = ids
        for i in ids:
            if i not in all_ids:
                all_ids.append(i)
        print(label, d.get("total"), file=sys.stderr)
    save_raw("met_search_ids.json", ids_by_query)
    objs = {}
    for n, oid in enumerate(all_ids, 1):
        r, err = get(f"{BASE}/objects/{oid}", pause=0.8)
        if err or r.status_code != 200:
            objs[oid] = {"objectID": oid, "_error": err or r.status_code}
            continue
        o = r.json()
        objs[oid] = {k: o.get(k) for k in KEEP}
        if n % 50 == 0:
            print(n, "/", len(all_ids), file=sys.stderr)
    save_raw("met_objects_compact.json", objs)
    pat_m = re.compile(r"mumm", re.I)
    pat_c = re.compile(r"crocod|sobek|souchos|suchos", re.I)
    cands = []
    for oid, o in objs.items():
        text = " ".join(str(o.get(k) or "") for k in ("title", "objectName", "medium", "classification"))
        if pat_m.search(text) and pat_c.search(text):
            cands.append(oid)
    save_raw("met_candidates.json", {str(k): objs[k] for k in cands})
    # per-query stats
    stats = {}
    for label, ids in ids_by_query.items():
        stats[label] = (len(ids), [i for i in ids if i in cands])
    save_raw("met_query_stats.json", {k: {"hits": v[0], "crocodile_mummy_candidates": v[1]}
                                        for k, v in stats.items()})
    print(json.dumps({k: (v[0], v[1]) for k, v in stats.items()}, indent=1))
    print("candidates:", cands)


if __name__ == "__main__":
    main()
