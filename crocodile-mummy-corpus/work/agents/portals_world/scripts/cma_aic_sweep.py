"""Cleveland Museum of Art Open Access API + Art Institute of Chicago API sweep.

Enumerates all hits (CMA: limit=1000 single page; AIC: paged, limit=100) and flags
rows mentioning mumm* together with crocod*/Sobek.
"""
import json
import re
import sys

from common import get, save_raw

PM = re.compile(r"mumm", re.I)
PC = re.compile(r"crocod|sobek|souchos|suchos", re.I)

CMA = "https://openaccess-api.clevelandart.org/api/artworks/"
CMA_Q = ["crocodile", "crocodile mummy", "mummified crocodile", "Sobek", "animal mummy", "mummy"]
AIC = "https://api.artic.edu/api/v1/artworks/search"
AIC_Q = ["crocodile", "crocodile mummy", "mummified crocodile", "Sobek", "animal mummy", "mummy"]
AIC_FIELDS = "id,title,main_reference_number,artwork_type_title,department_title,place_of_origin,date_display,medium_display,dimensions,is_public_domain,image_id,credit_line,classification_titles"


def flat(x):
    if isinstance(x, dict):
        return " ".join(flat(v) for v in x.values())
    if isinstance(x, list):
        return " ".join(flat(v) for v in x)
    return str(x)


def main():
    out = {"CMA": {}, "AIC": {}}
    for q in CMA_Q:
        r, err = get(CMA, params={"q": q, "limit": 1000}, pause=1.0)
        if err or r.status_code != 200:
            out["CMA"][q] = {"error": err or r.status_code}
            continue
        d = r.json()
        rows = d.get("data", [])
        c = [{"id": x.get("id"), "accession_number": x.get("accession_number"), "title": x.get("title"),
              "type": x.get("type"), "culture": x.get("culture"), "url": x.get("url")}
             for x in rows if PM.search(flat(x)) and PC.search(flat(x))]
        egy = [{"accession_number": x.get("accession_number"), "title": x.get("title")}
               for x in rows if "Egypt" in (x.get("department") or "")]
        out["CMA"][q] = {"total": d.get("info", {}).get("total"), "retrieved": len(rows),
                         "mumm+croc": c, "egyptian_dept_hits": egy[:60]}
        print("CMA", q, d.get("info", {}).get("total"), len(rows), len(c), file=sys.stderr)
    for q in AIC_Q:
        page, rows_all, total = 1, [], None
        while True:
            r, err = get(AIC, params={"q": q, "limit": 100, "page": page, "fields": AIC_FIELDS}, pause=1.0)
            if err or r.status_code != 200:
                out["AIC"][q] = {"error": err or r.status_code}
                break
            d = r.json()
            total = d.get("pagination", {}).get("total")
            rows = d.get("data", [])
            rows_all += rows
            if page >= d.get("pagination", {}).get("total_pages", 1) or not rows or page >= 10:
                break
            page += 1
        c = [x for x in rows_all if PM.search(flat(x)) and PC.search(flat(x))]
        egy = [{"ref": x.get("main_reference_number"), "title": x.get("title")} for x in rows_all
               if (x.get("place_of_origin") or "") == "Egypt"]
        out["AIC"][q] = {"total": total, "retrieved": len(rows_all), "mumm+croc": c,
                         "egypt_hits": egy[:80]}
        print("AIC", q, total, len(rows_all), len(c), file=sys.stderr)
    save_raw("cma_aic_results.json", out)
    print(json.dumps(out, indent=1)[:6000])


if __name__ == "__main__":
    main()
