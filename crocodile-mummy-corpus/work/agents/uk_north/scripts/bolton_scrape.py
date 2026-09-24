#!/usr/bin/env python3
"""Search Bolton's Egypt online collection (boltonsegypt.co.uk, WordPress 'object' post type)
for a set of terms, then fetch each object page and extract the 'Object details' fields.
Output: JSON lines to stdout (raw/bolton_objects.jsonl)."""
import json, re, sys, time, requests
from bs4 import BeautifulSoup
S = requests.Session(); S.headers["User-Agent"] = "Mozilla/5.0 (research; crocodile mummy corpus)"
terms = sys.argv[1:] or ["crocodile"]
urls = {}
for q in terms:
    n = 0
    for page in range(1, 20):
        base = "http://boltonsegypt.co.uk/" + (f"page/{page}/" if page > 1 else "")
        r = S.get(base, params={"s": q, "post_type": "object"}, timeout=30)
        if r.status_code != 200:
            break
        soup = BeautifulSoup(r.text, "lxml")
        links = [a.get("href") for a in soup.find_all("a") if a.get("href", "").startswith("http://boltonsegypt.co.uk/object/")]
        new = [l for l in dict.fromkeys(links) if l not in urls]
        if not links:
            break
        for l in new:
            urls[l] = q
            n += 1
        time.sleep(0.7)
    print(f"# term '{q}': {n} new object links", file=sys.stderr)
for u in urls:
    r = S.get(u, timeout=30)
    soup = BeautifulSoup(r.text, "lxml")
    m = soup.find("main") or soup
    parts = m.get_text(" | ", strip=True).split(" | ")
    rec = {"url": u, "term": urls[u], "title": parts[0] if parts else ""}
    try:
        k = parts.index("Object details")
        rec["text"] = " ".join(parts[1:k])
        det = parts[k + 1:]
    except ValueError:
        rec["text"] = " ".join(parts[1:]); det = []
    cur = None
    for p in det:
        if p.endswith(":"):
            cur = p[:-1]; rec[cur] = ""
        elif cur:
            rec[cur] = (rec[cur] + "; " + p).strip("; ")
    rec["images"] = [i.get("src") for i in m.find_all("img") if i.get("src") and "uploads" in i.get("src")]
    print(json.dumps(rec, ensure_ascii=False))
    time.sleep(0.7)
