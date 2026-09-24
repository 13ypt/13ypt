#!/usr/bin/env python3
"""Generate search_log JSONL lines from raw per-query JSON files of a portal.
Usage: python3 make_search_log.py europeana|ksamsok|dimu|cn  > out.jsonl
Relevance = item id in RELEVANT set (true crocodile mummies/bundles/parts)."""
import glob, json, os, sys, collections
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")
portal = sys.argv[1]
REL_EU = set(l.strip() for l in open(os.path.join(RAW, "europeana_relevant_ids.txt"))) if os.path.exists(os.path.join(RAW, "europeana_relevant_ids.txt")) else set()
CFG = {
 "europeana": ("europeana_q_*.json", "Europeana Search API (api.europeana.eu/record/v2/search.json, wskey=api2demo, rows=100, cursor pagination)", "id", "dataProvider"),
 "ksamsok": ("ksamsok_q_*.json", "K-samsök / Kringla API (kulturarvsdata.se/ksamsok/api method=search)", "uri", "org"),
 "dimu": ("dimu_q_*.json", "DigitaltMuseum DiMu Solr API (api.dimu.org/api/solr/select, api.key=demo; SE+NO instances)", "uid", "owner"),
 "cn": ("cn_q_*.json", "Collectie Nederland API (data.collectienederland.nl/api/search/v2, rows=20)", "doc_id", "provider"),
}
pat, db, idk, provk = CFG[portal]
REL = set(l.strip() for l in open(os.path.join(RAW, f"{portal}_relevant_ids.txt"))) if os.path.exists(os.path.join(RAW, f"{portal}_relevant_ids.txt")) else set()
for f in sorted(glob.glob(os.path.join(RAW, pat))):
    d = json.load(open(f))
    items = d.get("items", [])
    rel = [it for it in items if it.get(idk) in REL]
    byp = collections.Counter(it.get(provk) for it in rel)
    res = f"{d.get('total')} hits (fetched {len(items)})"
    if rel:
        res += "; crocodile-mummy objects: " + "; ".join(f"{p} x{c}" for p, c in byp.most_common())
    else:
        res += "; 0 crocodile-mummy objects"
    lang = "multi"
    print(json.dumps({"country": "EU" if portal == "europeana" else {"ksamsok": "SE", "dimu": "SE", "cn": "NL"}[portal],
                      "language": lang, "database_or_search_engine": db, "query": d["query"],
                      "result": res[:900], "notes": f"raw: work/agents/portals_europe/raw/{os.path.basename(f)}"}, ensure_ascii=False))
