"""DigitalNZ API sweep (api.digitalnz.org/records.json, no key needed for basic search).

Enumerates all result pages (per_page=100) for each query, keeps every non-newspaper
record (museum/collection records) and prints them; newspaper hits are only counted.
"""
import json
import sys

from common import get, save_raw

BASE = "https://api.digitalnz.org/records.json"
QUERIES = ["crocodile mummy", "mummified crocodile", "mummy crocodile", "crocodile egypt",
           "Sobek", "crocodile mummies", "animal mummy", "mummy, crocodile", "crocodile"]


def main():
    out = {}
    for q in QUERIES:
        page, total, keep, news = 1, None, [], 0
        while True:
            r, err = get(BASE, params={"text": q, "per_page": 100, "page": page}, pause=1.2)
            if err or r.status_code != 200:
                out[q] = {"error": err or r.status_code}
                break
            s = r.json()["search"]
            total = s.get("result_count")
            res = s.get("results", [])
            for x in res:
                if "Newspapers" in (x.get("category") or []):
                    news += 1
                    continue
                keep.append({k: x.get(k) for k in ("id", "title", "content_partner", "display_collection",
                                                     "category", "landing_url", "source_url",
                                                     "thumbnail_url", "rights_url", "usage", "description")})
            if page * 100 >= (total or 0) or not res or page >= 20:
                break
            page += 1
        out[q] = {"total": total, "newspaper_hits": news, "non_newspaper": keep}
        print(q, total, news, len(keep), file=sys.stderr)
    save_raw("digitalnz_results.json", out)
    for q, v in out.items():
        print("==", q, v.get("total"), "news:", v.get("newspaper_hits"))
        for x in v.get("non_newspaper", []):
            if q == "crocodile" and "mumm" not in json.dumps(x).lower():
                continue
            print("  ", x["id"], "|", x["title"], "|", x["content_partner"], "|", x["landing_url"])


if __name__ == "__main__":
    main()
