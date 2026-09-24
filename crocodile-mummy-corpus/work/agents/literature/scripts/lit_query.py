#!/usr/bin/env python3
"""Reproducible literature discovery via OpenAlex and Crossref APIs.

Usage:
  python3 lit_query.py openalex "crocodile mummy" [per_page]
  python3 lit_query.py crossref "crocodile mummy" [rows]
  python3 lit_query.py openalex_id W123456789        # single work (with referenced_works)
  python3 lit_query.py openalex_cites W123456789     # works citing a work
  python3 lit_query.py doi 10.1371/journal.pone.0284680   # crossref record incl. references

Saves compact JSON to ../raw/<source>_<slug>.json and prints a table
(year | doi | title | venue | OA url).  Polite: 1 request per call, mailto header.
"""
import json
import os
import re
import sys
import time
import urllib.parse

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(os.path.dirname(HERE), "raw")
os.makedirs(RAW, exist_ok=True)
HEAD = {"User-Agent": "crocodile-mummy-corpus/0.1 (literature survey; research use)"}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:60]


def save(name, data):
    path = os.path.join(RAW, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    return path


def openalex(q, per_page=50, filt=None):
    params = {"search": q, "per-page": per_page,
              "select": "id,doi,title,publication_year,primary_location,open_access,authorships,type,cited_by_count"}
    if filt:
        params["filter"] = filt
    r = requests.get("https://api.openalex.org/works", params=params, headers=HEAD, timeout=60)
    r.raise_for_status()
    js = r.json()
    rows = []
    for w in js.get("results", []):
        loc = w.get("primary_location") or {}
        src = (loc.get("source") or {}).get("display_name")
        auth = "; ".join((a.get("author") or {}).get("display_name", "") for a in (w.get("authorships") or [])[:6])
        rows.append({"id": w["id"].rsplit("/", 1)[-1], "year": w.get("publication_year"), "doi": w.get("doi"),
                     "title": w.get("title"), "venue": src, "authors": auth,
                     "oa_url": (w.get("open_access") or {}).get("oa_url"), "type": w.get("type"),
                     "cited_by": w.get("cited_by_count")})
    meta = {"query": q, "filter": filt, "count": js.get("meta", {}).get("count"), "results": rows}
    p = save(f"openalex_{slug(q)}.json", meta)
    return meta, p


def openalex_id(wid):
    r = requests.get(f"https://api.openalex.org/works/{wid}", headers=HEAD, timeout=60)
    r.raise_for_status()
    w = r.json()
    refs = w.get("referenced_works") or []
    out = {"id": wid, "title": w.get("title"), "year": w.get("publication_year"), "doi": w.get("doi"),
           "referenced_works": refs}
    # resolve references in batches of 50
    resolved = []
    for i in range(0, len(refs), 50):
        ids = "|".join(x.rsplit("/", 1)[-1] for x in refs[i:i + 50])
        rr = requests.get("https://api.openalex.org/works", params={"filter": f"openalex_id:{ids}", "per-page": 50,
                          "select": "id,doi,title,publication_year,primary_location,open_access"}, headers=HEAD, timeout=60)
        rr.raise_for_status()
        for x in rr.json().get("results", []):
            loc = x.get("primary_location") or {}
            resolved.append({"id": x["id"].rsplit("/", 1)[-1], "year": x.get("publication_year"), "doi": x.get("doi"),
                             "title": x.get("title"), "venue": (loc.get("source") or {}).get("display_name"),
                             "oa_url": (x.get("open_access") or {}).get("oa_url")})
        time.sleep(1)
    out["resolved_refs"] = resolved
    p = save(f"openalex_work_{wid}.json", out)
    return out, p


def openalex_cites(wid):
    return openalex("", 100, filt=f"cites:{wid}") if False else _cites(wid)


def _cites(wid):
    r = requests.get("https://api.openalex.org/works", params={"filter": f"cites:{wid}", "per-page": 100,
                     "select": "id,doi,title,publication_year,primary_location,open_access"}, headers=HEAD, timeout=60)
    r.raise_for_status()
    js = r.json()
    rows = []
    for x in js.get("results", []):
        loc = x.get("primary_location") or {}
        rows.append({"id": x["id"].rsplit("/", 1)[-1], "year": x.get("publication_year"), "doi": x.get("doi"),
                     "title": x.get("title"), "venue": (loc.get("source") or {}).get("display_name"),
                     "oa_url": (x.get("open_access") or {}).get("oa_url")})
    meta = {"cites": wid, "count": js.get("meta", {}).get("count"), "results": rows}
    p = save(f"openalex_cites_{wid}.json", meta)
    return meta, p


def crossref(q, rows=40):
    r = requests.get("https://api.crossref.org/works", params={"query.bibliographic": q, "rows": rows,
                     "select": "DOI,title,issued,container-title,author,type"}, headers=HEAD, timeout=60)
    r.raise_for_status()
    js = r.json()["message"]
    out = []
    for it in js.get("items", []):
        yr = (it.get("issued") or {}).get("date-parts", [[None]])[0][0]
        auth = "; ".join(f"{a.get('family', '')}, {a.get('given', '')}" for a in (it.get("author") or [])[:6])
        out.append({"year": yr, "doi": it.get("DOI"), "title": (it.get("title") or [""])[0],
                    "venue": (it.get("container-title") or [""])[0] if it.get("container-title") else "",
                    "authors": auth, "type": it.get("type")})
    meta = {"query": q, "total": js.get("total-results"), "results": out}
    p = save(f"crossref_{slug(q)}.json", meta)
    return meta, p


def doi(d):
    r = requests.get(f"https://api.crossref.org/works/{urllib.parse.quote(d)}", headers=HEAD, timeout=60)
    r.raise_for_status()
    m = r.json()["message"]
    refs = m.get("reference") or []
    out = {"doi": d, "title": (m.get("title") or [""])[0], "container": (m.get("container-title") or [""])[0],
           "issued": m.get("issued"), "authors": [f"{a.get('family', '')}, {a.get('given', '')}" for a in m.get("author", [])],
           "page": m.get("page"), "volume": m.get("volume"), "issue": m.get("issue"),
           "references": [{k: x.get(k) for k in ("DOI", "unstructured", "article-title", "author", "year", "journal-title", "volume-title")} for x in refs]}
    p = save(f"crossref_doi_{slug(d)}.json", out)
    return out, p


def main():
    cmd, arg = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else None
    if cmd == "openalex":
        meta, p = openalex(arg, n or 50)
        print(f"# OpenAlex '{arg}': {meta['count']} total; saved {p}")
        for r in meta["results"]:
            print(f"{r['year']} | {r['id']} | {r['doi']} | {r['title']} | {r['venue']} | {r['authors'][:60]} | OA:{r['oa_url']}")
    elif cmd == "crossref":
        meta, p = crossref(arg, n or 40)
        print(f"# Crossref '{arg}': {meta['total']} total; saved {p}")
        for r in meta["results"]:
            print(f"{r['year']} | {r['doi']} | {r['title']} | {r['venue']} | {r['authors'][:60]}")
    elif cmd == "openalex_id":
        out, p = openalex_id(arg)
        print(f"# {out['title']} ({out['year']}) {out['doi']}: {len(out['referenced_works'])} refs; saved {p}")
        for r in out["resolved_refs"]:
            print(f"{r['year']} | {r['id']} | {r['doi']} | {r['title']} | {r['venue']} | OA:{r['oa_url']}")
    elif cmd == "openalex_cites":
        meta, p = _cites(arg)
        print(f"# works citing {arg}: {meta['count']}; saved {p}")
        for r in meta["results"]:
            print(f"{r['year']} | {r['id']} | {r['doi']} | {r['title']} | {r['venue']} | OA:{r['oa_url']}")
    elif cmd == "doi":
        out, p = doi(arg)
        print(f"# {out['title']} | {out['container']} {out['volume']}({out['issue']}) {out['page']} | {out['authors']}; {len(out['references'])} refs; saved {p}")
        for x in out["references"]:
            print(" -", x.get("unstructured") or f"{x.get('author')} {x.get('year')} {x.get('article-title') or x.get('volume-title')} {x.get('journal-title')} {x.get('DOI')}")


if __name__ == "__main__":
    main()
