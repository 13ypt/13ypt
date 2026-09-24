#!/usr/bin/env python3
"""Search a WordPress.com blog for a term, then print context around the term in each post.
Usage: wp_search.py <blog_base_url> <term> [maxpages]"""
import sys, time, re, requests
from bs4 import BeautifulSoup
base, term = sys.argv[1].rstrip('/'), sys.argv[2]
maxp = int(sys.argv[3]) if len(sys.argv) > 3 else 5
H = {"User-Agent": "Mozilla/5.0 (research; crocodile mummy corpus)"}
posts = []
for p in range(1, maxp + 1):
    url = f"{base}/page/{p}/?s={term}" if p > 1 else f"{base}/?s={term}"
    r = requests.get(url, headers=H, timeout=30)
    if r.status_code != 200:
        break
    soup = BeautifulSoup(r.text, "lxml")
    found = [(a.get_text(strip=True), a.get("href")) for a in soup.select("h1.entry-title a, h2.entry-title a, h1 a[rel=bookmark], h2 a[rel=bookmark]")]
    new = [f for f in found if f not in posts]
    if not new:
        break
    posts += new
    time.sleep(1)
print(f"{len(posts)} posts for '{term}'")
for title, href in posts:
    r = requests.get(href, headers=H, timeout=30)
    soup = BeautifulSoup(r.text, "lxml")
    art = soup.find("article") or soup.find("div", class_="entry-content") or soup
    t = art.get_text(" ", strip=True)
    print("\n=== ", title, "|", href)
    for m in re.finditer(r"(?i)" + term, t):
        print("  ..." + t[max(0, m.start() - 300): m.start() + 300] + "...")
    caps = [i.get("alt") for i in art.find_all("img") if i.get("alt") and re.search(term, i.get("alt"), re.I)]
    if caps:
        print("  IMG ALTS:", caps)
    time.sleep(1)
