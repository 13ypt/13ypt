#!/usr/bin/env python3
"""Print the field/value text of UCL Collections Online detail pages.

Usage: python3 ucl_detail.py https://collections.ucl.ac.uk/Details/petrie/17409 [...]
"""
import re
import sys
import time

import requests
from bs4 import BeautifulSoup


def main():
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (crocodile-mummy-corpus research)"
    for url in sys.argv[1:]:
        r = s.get(url, timeout=90)
        soup = BeautifulSoup(r.text, "lxml")
        for sc in soup(["script", "style", "nav", "header", "footer"]):
            sc.decompose()
        t = re.sub(r"\n\s*\n+", "\n", soup.get_text("\n"))
        t = re.sub(r"[ \t]+", " ", t)
        i = t.find("Add to selection")
        j = t.find("Loading", i)
        body = t[i + len("Add to selection"):j if j > 0 else i + 4000]
        imgs = sorted(set(re.findall(r'(?:src|href)="([^"]*(?:wwwopac|media|image|\.jpg)[^"]*)"', r.text, re.I)))
        print(f"=== {url} [{r.status_code}]")
        print(body.strip()[:4000])
        print("images:", imgs[:6])
        print()
        time.sleep(1)


if __name__ == "__main__":
    main()
