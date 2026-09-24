#!/usr/bin/env python3
"""J-STAGE WebAPI article search (service=3). Usage: jstage.py "<text>" [count]"""
import sys, urllib.parse, requests, re
import xml.etree.ElementTree as ET
q = sys.argv[1]; cnt = sys.argv[2] if len(sys.argv) > 2 else "50"
url = "https://api.jstage.jst.go.jp/searchapi/do?service=3&text=" + urllib.parse.quote(q) + f"&count={cnt}"
r = requests.get(url, timeout=60)
ns = {"a": "http://www.w3.org/2005/Atom", "o": "http://a9.com/-/spec/opensearch/1.1/", "p": "http://prismstandard.org/namespaces/basic/2.0/"}
root = ET.fromstring(r.content)
tot = root.find("o:totalResults", ns)
print("URL:", url, "TOTAL:", tot.text if tot is not None else "?")
for e in root.findall("a:entry", ns):
    t = e.find("a:article_title/a:ja", ns); te = e.find("a:article_title/a:en", ns)
    j = e.find("a:material_title/a:ja", ns) or e.find("a:material_title/a:en", ns)
    link = e.find("a:article_link/a:ja", ns)
    y = e.find("a:pubyear", ns)
    print("-", (t.text if t is not None and t.text else ""), "/", (te.text if te is not None and te.text else ""), "|", (j.text if j is not None else ""), "|", (y.text if y is not None else ""), "|", (link.text if link is not None else ""))
