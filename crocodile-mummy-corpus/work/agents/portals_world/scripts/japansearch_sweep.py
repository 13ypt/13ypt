"""Japan Search cross-search API sweep (jpsearch.go.jp/api/item/search/jps-cross).

Pages through all hits (size=100, from=0,100,...; capped at 1000 per query), and flags
records whose title/description contain a crocodile term AND a mummy term.
"""
import json
import re
import sys

from common import get, save_raw

BASE = "https://jpsearch.go.jp/api/item/search/jps-cross"
QUERIES = ["ワニ ミイラ", "鰐 ミイラ", "鰐木乃伊", "ワニのミイラ", "クロコダイル ミイラ", "鰐 木乃伊",
           "動物ミイラ", "セベク", "ソベク", "crocodile mummy", "mummified crocodile", "エジプト 鰐",
           "エジプト ワニ", "木乃伊"]
PC = re.compile(r"鰐|ワニ|わに|クロコダイル|crocod|セベク|ソベク|sobek", re.I)
PM = re.compile(r"ミイラ|木乃伊|mumm", re.I)


def main():
    out = {}
    for q in QUERIES:
        frm, total, flagged, n = 0, None, [], 0
        while True:
            r, err = get(BASE, params={"keyword": q, "size": 100, "from": frm}, pause=1.2)
            if err or r.status_code != 200:
                out[q] = {"error": err or r.status_code}
                break
            d = r.json()
            total = d.get("hit", 0)
            lst = d.get("list", [])
            n += len(lst)
            for x in lst:
                blob = json.dumps(x, ensure_ascii=False)
                c = x.get("common", {})
                title = str(c.get("title"))
                if PC.search(title) and PM.search(title) or (PC.search(blob) and PM.search(blob) and
                                                               c.get("contentsType") != "文書・図書"):
                    flagged.append({"id": x.get("id"), "title": c.get("title"), "database": c.get("database"),
                                    "provider": c.get("provider"), "linkUrl": c.get("linkUrl"),
                                    "contentsType": c.get("contentsType"),
                                    "thumbnailUrl": c.get("thumbnailUrl"), "contentsRightsType": c.get("contentsRightsType")})
            frm += 100
            if frm >= total or not lst or frm >= 1000:
                break
        if "error" not in out.get(q, {}):
            out[q] = {"total": total, "retrieved": n, "flagged": flagged}
        print(q, total, n, len(flagged), file=sys.stderr)
    save_raw("japansearch_results.json", out)
    for q, v in out.items():
        print("==", q, v.get("total"), v.get("retrieved"), v.get("error", ""))
        for f in v.get("flagged", []):
            print("   ", f["id"], "|", f["title"], "|", f["provider"], "|", f["contentsType"], "|", f["linkUrl"])


if __name__ == "__main__":
    main()
