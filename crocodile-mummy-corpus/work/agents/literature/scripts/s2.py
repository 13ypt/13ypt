#!/usr/bin/env python3
"""Semantic Scholar Graph API search: python3 s2.py "query" [limit]. Saves raw JSON to ../raw/s2_<slug>.json"""
import json, os, re, sys, time, requests
q = sys.argv[1]; lim = int(sys.argv[2]) if len(sys.argv) > 2 else 50
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")
for attempt in range(4):
    r = requests.get("https://api.semanticscholar.org/graph/v1/paper/search",
                     params={"query": q, "limit": lim, "fields": "title,year,venue,externalIds,openAccessPdf,authors,citationCount"}, timeout=60)
    if r.status_code == 429:
        time.sleep(5 * (attempt + 1)); continue
    break
r.raise_for_status()
js = r.json()
json.dump(js, open(os.path.join(RAW, "s2_" + re.sub(r"[^a-z0-9]+", "_", q.lower())[:60] + ".json"), "w"), ensure_ascii=False, indent=1)
print(f"# S2 '{q}': total {js.get('total')}")
for p in js.get("data", []):
    oa = (p.get("openAccessPdf") or {}).get("url")
    au = "; ".join(a["name"] for a in (p.get("authors") or [])[:4])
    print(f"{p.get('year')} | {p.get('title')} | {au} | {p.get('venue')} | DOI:{(p.get('externalIds') or {}).get('DOI')} | OA:{oa}")
