#!/usr/bin/env python3
"""Query the MoTA egymonuments.gov.eg site search API (as used by the portal's own JS).
Usage: mota_search.py <culture en|ar> <query>...  -> prints hits and saves raw JSON to raw/"""
import json, sys, time, re, urllib.parse, subprocess, os
API = "https://egymonuments.gov.eg/Umbraco/Api/SearchResultWebAPI/GetSearchResult"
culture = sys.argv[1]
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for q in sys.argv[2:]:
    body = json.dumps({"parentContentId": -1, "pageIndex": 1, "pageSize": 100, "imageSize": "", "stringLength": 400,
                       "citiesIds": [], "dynastiesIds": [], "searchText": q}, ensure_ascii=False)
    out = subprocess.run(["curl", "-sS", "-m", "40", "-X", "POST", API, "-H", "Content-Type: application/json; charset=utf-8",
                          "-H", "culture: " + culture, "--data-binary", body], capture_output=True).stdout
    try:
        d = json.loads(out)["Data"]
    except Exception as e:
        print(f"## {culture} {q!r}: ERROR {e} {out[:200]!r}"); continue
    fn = os.path.join(here, "raw", "mota_search_%s_%s.json" % (culture, re.sub(r"\W+", "_", q)))
    json.dump(d, open(fn, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"## {culture} {q!r}: Count={d.get('Count')}")
    for x in d["ListItems"]:
        print("  -", x.get("Id"), "|", (x.get("Title") or "").strip(), "|", x.get("ContentUrlName") or x.get("Url") or "", "|", re.sub(r"\s+", " ", x.get("Description") or "")[:160])
    time.sleep(1)
