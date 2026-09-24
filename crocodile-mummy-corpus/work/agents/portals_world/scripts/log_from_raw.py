"""Turn saved raw stats files into search_log records (run once per API after its sweep)."""
import json, sys
from common import RAW, rec

def nmnh():
    s = json.load(open(f"{RAW}/nmnh_query_stats.json"))
    out = []
    for k, v in s.items():
        dept, q = k.split("|", 1)
        fl = [f"{h['cat']} {h['name']}" for h in v.get("flagged", []) if "Bull" not in str(h["name"])]
        out.append({"country": "US", "language": "en", "database_or_search_engine": f"NMNH {dept} collections DB backend (collections.nmnh.si.edu/search/{dept}/search.php, qtype=1 keyword)",
                    "query": q, "institution_checked": "National Museum of Natural History, Smithsonian Institution",
                    "result": f"{v.get('total')} hits, all {v.get('retrieved')} retrieved; crocodile mummies: {', '.join(fl) if fl else 'none'}" if "error" not in v else f"ERROR {v['error']}",
                    "notes": "full enumeration; raw/nmnh_query_stats.json"})
    return out

def cma_aic():
    d = json.load(open(f"{RAW}/cma_aic_results.json"))
    out = []
    for q, v in d["CMA"].items():
        out.append({"country": "US", "language": "en", "database_or_search_engine": "Cleveland Museum of Art Open Access API (openaccess-api.clevelandart.org/api/artworks/?q=&limit=1000)",
                    "query": q, "institution_checked": "Cleveland Museum of Art",
                    "result": f"{v.get('total')} hits, {v.get('retrieved')} retrieved; 0 crocodile mummies" + ("; only mumm+croc text match is 1969.118 Apis Bull (sculpture)" if v.get('mumm+croc') else ""),
                    "notes": "raw/cma_aic_results.json"})
    a = json.load(open(f"{RAW}/aic_es_results.json"))
    for q, v in a.items():
        out.append({"country": "US", "language": "en", "database_or_search_engine": "Art Institute of Chicago API (POST api.artic.edu/api/v1/artworks/search, ES query_string)",
                    "query": q, "institution_checked": "Art Institute of Chicago",
                    "result": f"{v['total']} hits (all retrieved); 0 crocodile mummies (crocodile hits = amulets, Sobek statuette 1894.260, prints)",
                    "notes": "plain ?q= search returns total=133118 for any term (scores whole collection) so ES query_string used; raw/aic_es_results.json"})
    return out

def si(tag=""):
    s = json.load(open(f"{RAW}/si_query_stats{tag}.json"))
    out = []
    for q, v in s.items():
        res = (f"{v.get('hits')} hits, {v.get('retrieved')} retrieved; mumm+croc text matches: {len(v.get('mumm+croc candidates', []))}"
               if v.get("hits") is not None else f"HTTP {v.get('error')} (DEMO_KEY rate limit)")
        out.append({"country": "US", "language": "en", "database_or_search_engine": "Smithsonian Open Access API (api.si.edu/openaccess/api/v1.0/search, DEMO_KEY)",
                    "query": q, "institution_checked": "Smithsonian Institution (all units)", "result": res,
                    "notes": f"raw/si_query_stats{tag}.json"})
    return out

if __name__ == "__main__":
    which = sys.argv[1]
    recs = {"nmnh": nmnh, "cma_aic": cma_aic, "si": si, "si2": lambda: si("_pass2")}[which]()
    rec("search_log", recs)
