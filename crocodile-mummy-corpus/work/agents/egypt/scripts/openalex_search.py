#!/usr/bin/env python3
"""Search OpenAlex works (title+abstract) and print title/year/venue/DOI + abstract snippets with key terms.
Usage: openalex_search.py "query" [per_page]"""
import json, sys, urllib.parse, subprocess, re, time
q = sys.argv[1]; n = sys.argv[2] if len(sys.argv) > 2 else "50"
url = "https://api.openalex.org/works?search=" + urllib.parse.quote(q) + "&per-page=" + n + "&mailto=research-agent@example.org"
d = json.loads(subprocess.run(["curl", "-sS", "-m", "60", url], capture_output=True).stdout)
print(f"## {q!r}: count={d['meta']['count']}")
KEY = re.compile(r"(Cairo|Egyptian Museum|Kom Ombo|Crocodile Museum|Aswan|Luxor|Fayum|Fayoum|Tebtun|Madi|Narmouthis|Akoris|Tehna|Maabda|Samoun|Hawara|Qubbat|Silsila|Theadelphia|Alexandria|Minya|Tuna)", re.I)
for w in d["results"]:
    inv = w.get("abstract_inverted_index") or {}
    words = sorted(((p, k) for k, ps in inv.items() for p in ps))
    ab = " ".join(k for _, k in words)
    src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name")
    hits = sorted(set(m.group(0) for m in KEY.finditer((w.get("title") or "") + " " + ab)))
    print(f"- {w.get('publication_year')} | {w.get('title')} | {src} | {w.get('doi')} | keys={hits}")
