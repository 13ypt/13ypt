#!/usr/bin/env python3
"""Keyword search of Glasgow Museums Collections Navigator (KE EMu mweb). Sets the cookies the
JS stub sets, then requests the result list. Usage: glasgow_mweb.py term -> prints result rows."""
import sys, re, time, requests
from bs4 import BeautifulSoup
term = sys.argv[1]
s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0 (research; crocodile mummy corpus)"
B = "https://collections.glasgowmuseums.com/mwebcgi/mweb"
r = s.get(B + f"?request=advanced;dtype=d;_tkeyword={term}")
m = re.search(r"escape\('(\d+)'\).*?permissions='\+escape\('(\d+)'\)", r.text)
if m:
    for k, v in {"user": m.group(1), "realname": "", "permissions": m.group(2), "screen": "1920"}.items():
        s.cookies.set(k, v, domain="collections.glasgowmuseums.com", path="/")
r = s.get(B + f"?request=advanced;dtype=d;_tkeyword={term}")
open(sys.argv[2] if len(sys.argv) > 2 else "/dev/null", "w").write(r.text)
soup = BeautifulSoup(r.text, "lxml")
print(soup.get_text(" | ", strip=True)[:3000])
for a in soup.find_all("a"):
    h = a.get("href") or ""
    if "irn" in h or "request=record" in h:
        print(a.get_text(" ", strip=True)[:100], "|", h)
