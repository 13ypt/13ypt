#!/usr/bin/env python3
"""Download OCR text of ASAE volumes on archive.org (identifier ASAE-*) to a cache dir and grep crocodile terms.
Usage: asae_grep.py CACHE_DIR OUT_TSV"""
import json, subprocess, sys, os, re, time
cache, out = sys.argv[1], sys.argv[2]
os.makedirs(cache, exist_ok=True)
q = "https://archive.org/advancedsearch.php?q=identifier%3AASAE-*&fl%5B%5D=identifier&rows=200&output=json"
ids = sorted(x["identifier"] for x in json.loads(subprocess.run(["curl", "-sS", q], capture_output=True).stdout)["response"]["docs"])
PAT = re.compile(r"crocodil|Krokodil|coccodrill|تمساح|تماسيح", re.I)
with open(out, "w", encoding="utf-8") as fo:
    for i in ids:
        fn = os.path.join(cache, i + ".txt")
        if not os.path.exists(fn):
            meta = json.loads(subprocess.run(["curl", "-sS", f"https://archive.org/metadata/{i}/files"], capture_output=True).stdout)
            txts = [f["name"] for f in meta.get("result", []) if f["name"].endswith("_djvu.txt")]
            if not txts:
                print(i, "no djvu.txt"); continue
            subprocess.run(["curl", "-sSL", "-o", fn, f"https://archive.org/download/{i}/" + txts[0].replace(" ", "%20")])
            time.sleep(1)
        lines = open(fn, encoding="utf-8", errors="ignore").read().split("\n")
        n = 0
        for k, l in enumerate(lines):
            if PAT.search(l):
                ctx = " ".join(x.strip() for x in lines[max(0, k-2):k+3])
                fo.write(f"{i}\t{k}\t{ctx}\n"); n += 1
        print(i, n, flush=True)
