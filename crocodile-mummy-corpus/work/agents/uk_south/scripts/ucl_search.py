#!/usr/bin/env python3
"""Search UCL Collections Online (Axiell Internet Server: Petrie Museum, Grant Museum of
Zoology, UCL Art, Pathology, Science) and list every hit (number, object category,
detail URL) for one database, paging through /resultsnavigate/N.

Usage: python3 ucl_search.py "<query>" <db>
  db: collect art zoology jeremybentham pathology petrie science
Output: TSV lines  number<TAB>category<TAB>detail_url
"""
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

BASE = "https://collections.ucl.ac.uk"
DBS = ["collect", "art", "zoology", "jeremybentham", "pathology", "petrie", "science"]


def parse(html):
    soup = BeautifulSoup(html, "lxml")
    out = []
    for a in soup.find_all("a", href=re.compile(r"/Details/")):
        txt = a.get_text(" ", strip=True)
        if not txt:
            continue
        # category follows in the same result block
        block = a.find_parent(["li", "div", "tr"])
        cat = ""
        if block is not None:
            bt = re.sub(r"\s+", " ", block.get_text(" ", strip=True))
            m = re.search(r"Object Category (.*?)(?: Petrie Museum| Grant Museum| UCL | CC BY| Remove|$)", bt)
            if m:
                cat = m.group(1).strip()
        out.append((txt, cat, a["href"]))
    return out


def main():
    q, db = sys.argv[1], sys.argv[2]
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (crocodile-mummy-corpus research)"
    s.get(BASE + "/search/simple", timeout=60)
    data = {}
    for i, name in enumerate(DBS):
        data[f"DatabaseChoices[{i}].Selected"] = "true" if name == db else "false"
        data[f"DatabaseChoices[{i}].Name"] = name
    data["Fields[0].SearchInField"] = "False"
    data["Fields[0].FieldName"] = "Search_SearchSimple_FieldLabel"
    data["Fields[0].Value"] = q
    r = s.post(BASE + "/search/simple", data=data, timeout=90)
    m = re.search(r"(\d+) Hits", r.text)
    total = int(m.group(1)) if m else None
    pages = [int(x) for x in re.findall(r'/resultsnavigate/(\d+)', r.text)]
    last = max(pages) if pages else 1
    print(f"# query={q!r} db={db} hits={total} pages={last}", file=sys.stderr)
    seen = set()
    for p in range(1, last + 1):
        if p > 1:
            time.sleep(1)
            r = s.get(f"{BASE}/resultsnavigate/{p}", timeout=90)
        for num, cat, url in parse(r.text):
            if url in seen:
                continue
            seen.add(url)
            print(f"{num}\t{cat}\t{url}")
    print(f"# harvested {len(seen)} of {total}", file=sys.stderr)


if __name__ == "__main__":
    main()
