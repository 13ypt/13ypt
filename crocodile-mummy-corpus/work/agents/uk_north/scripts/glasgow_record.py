#!/usr/bin/env python3
"""Fetch Glasgow Museums mweb record pages by id. Usage: glasgow_record.py id [id...]"""
import sys, re, time, requests
from bs4 import BeautifulSoup
s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0 (research; crocodile mummy corpus)"
B = "https://collections.glasgowmuseums.com/mwebcgi/mweb"
r = s.get(B + "?request=home")
r = s.get(B + "?request=advanced;dtype=d;_tkeyword=x")
m = re.search(r"escape\('(\d+)'\).*?permissions='\+escape\('(\d+)'\)", r.text)
if m:
    for k, v in {"user": m.group(1), "realname": "", "permissions": m.group(2), "screen": "1920"}.items():
        s.cookies.set(k, v, domain="collections.glasgowmuseums.com", path="/")
for i in sys.argv[1:]:
    url = B + f"?request=record;id={i};type=101"
    r = s.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    main = soup.find("div", class_=re.compile("record|container")) or soup
    t = soup.get_text(" | ", strip=True)
    k = t.find("Collections Search Results") ; k = t.find("Record", 0)
    print("=====", url)
    j = t.find("Accession")
    print(t[max(0, j - 800): j + 2500] if j >= 0 else t[:3000])
    for im in soup.find_all("img"):
        src = im.get("src") or ""
        if "media" in src or "irn" in src: print("IMG", src)
    time.sleep(1)
