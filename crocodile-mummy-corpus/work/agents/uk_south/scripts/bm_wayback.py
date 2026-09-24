#!/usr/bin/env python3
"""Fetch archived (Wayback Machine) copies of British Museum Collection Online object
pages (live site returns 403 to curl/WebFetch) and print the structured fields.

Usage: python3 bm_wayback.py Y_EA38562 Y_EA6850 ...
Prints the archived snapshot URL and the main text block of each record.
"""
import json
import re
import subprocess
import sys
import time

from bs4 import BeautifulSoup


def curl(url, timeout=90):
    for attempt in range(4):
        r = subprocess.run(["curl", "-sS", "-m", str(timeout), "-L", url], capture_output=True)
        if r.returncode == 0 and r.stdout:
            return r.stdout.decode("utf-8", "ignore")
        time.sleep(3)
    return None


def snapshot(objid):
    api = f"https://archive.org/wayback/available?url=britishmuseum.org/collection/object/{objid}"
    txt = curl(api)
    if not txt:
        return None
    try:
        snap = json.loads(txt)["archived_snapshots"].get("closest")
    except Exception:
        return None
    if not snap:
        return None
    return snap["timestamp"], snap["url"]


def main():
    for objid in sys.argv[1:]:
        snap = snapshot(objid)
        if not snap:
            print(f"=== {objid}: NO SNAPSHOT\n")
            continue
        ts, url = snap
        raw = f"https://web.archive.org/web/{ts}id_/https://www.britishmuseum.org/collection/object/{objid}"
        html = curl(raw)
        if not html:
            print(f"=== {objid}: FETCH FAILED {raw}\n")
            continue
        soup = BeautifulSoup(html, "lxml")
        for s in soup(["script", "style", "nav", "header", "footer"]):
            s.decompose()
        t = re.sub(r"\n\s*\n+", "\n", soup.get_text("\n"))
        t = re.sub(r"[ \t]+", " ", t)
        i = t.find("Object Type")
        j = t.find("Conservation", i)
        if j < 0:
            j = i + 5000
        print(f"=== {objid} snapshot {ts} {url}")
        print(t[i:min(j + 200, i + 6000)])
        print()
        time.sleep(1.5)


if __name__ == "__main__":
    main()
