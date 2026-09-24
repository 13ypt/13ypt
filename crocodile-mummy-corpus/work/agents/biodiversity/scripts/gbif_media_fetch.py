#!/usr/bin/env python3
"""Fetch GBIF-cached copies of occurrence images for visual checking (kept outside the project).
Usage: gbif_media_fetch.py OUTDIR [--max N] gbifKey [gbifKey ...]
Uses https://api.gbif.org/v1/image/cache/occurrence/{key}/media/{md5(identifier)} because some
publishers' media servers (e.g. mediaphoto.mnhn.fr) answer 403 to scripted requests."""
import hashlib, os, sys, time, requests

def get(url):
    for a in range(6):
        try:
            r = requests.get(url, timeout=90)
            if r.status_code in (200, 404):
                return r
        except requests.RequestException:
            pass
        time.sleep(3 * (a + 1))
    return None

args = sys.argv[1:]
out = args.pop(0); os.makedirs(out, exist_ok=True)
mx = 99
if args and args[0] == "--max":
    mx = int(args[1]); args = args[2:]
for key in args:
    r = get(f"https://api.gbif.org/v1/occurrence/{key}")
    occ = r.json() if r is not None and r.status_code == 200 else {}
    cat = str(occ.get("catalogNumber", key)).replace("/", "_").replace(" ", "_").replace(":", "_")
    for i, m in enumerate(occ.get("media", [])[:mx]):
        ident = m.get("identifier")
        if not ident:
            continue
        fn = os.path.join(out, f"{cat}_{i}.jpg")
        if os.path.exists(fn):
            continue
        url = f"https://api.gbif.org/v1/image/cache/occurrence/{key}/media/{hashlib.md5(ident.encode()).hexdigest()}"
        r = get(url)
        ok = r is not None and r.status_code == 200 and "image" in r.headers.get("content-type", "")
        if ok:
            open(fn, "wb").write(r.content)
        print(key, cat, i, ident, "OK" if ok else "FAIL")
        time.sleep(0.5)
