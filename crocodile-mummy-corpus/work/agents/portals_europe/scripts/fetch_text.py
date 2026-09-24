#!/usr/bin/env python3
"""Fetch a web page and print its visible text (optionally only lines matching a regex),
so that inventory numbers / titles can be quoted verbatim from the provider page.

Usage: python3 fetch_text.py URL [REGEX] [--max N]
"""
import re
import sys

import requests
from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (X11; Linux x86_64) crocodile-mummy-corpus research (polite, <=1 req/s)"


def text_of(url, timeout=60):
    r = requests.get(url, headers={"User-Agent": UA, "Accept-Language": "en,de;q=0.8,fr;q=0.6"},
                     timeout=timeout)
    enc = r.encoding
    if not enc or enc.lower() == "iso-8859-1":
        enc = r.apparent_encoding
    html = r.content.decode(enc or "utf-8", errors="replace")
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    lines = [re.sub(r"\s+", " ", l).strip() for l in soup.get_text("\n").split("\n")]
    return r.status_code, r.url, [l for l in lines if l]


def main():
    url = sys.argv[1]
    rx = re.compile(sys.argv[2], re.I) if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
    mx = 400
    if "--max" in sys.argv:
        mx = int(sys.argv[sys.argv.index("--max") + 1])
    code, final, lines = text_of(url)
    print(f"# {code} {final} ({len(lines)} lines)")
    n = 0
    for i, l in enumerate(lines):
        if rx is None or rx.search(l):
            print(f"{i}: {l[:500]}")
            n += 1
            if n >= mx:
                break


if __name__ == "__main__":
    main()
