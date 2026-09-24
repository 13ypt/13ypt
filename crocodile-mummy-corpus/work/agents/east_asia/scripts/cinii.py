#!/usr/bin/env python3
"""CiNii Research OpenSearch (JSON). Usage: cinii.py "<q>" [type: all|articles|books|data|dissertations] [count]"""
import sys, urllib.parse, requests
q = sys.argv[1]; typ = sys.argv[2] if len(sys.argv) > 2 else "all"; cnt = sys.argv[3] if len(sys.argv) > 3 else "100"
url = f"https://cir.nii.ac.jp/opensearch/{typ}?q=" + urllib.parse.quote(q) + f"&count={cnt}&format=json"
d = requests.get(url, timeout=60).json()
print("URL:", url, "TOTAL:", d.get("opensearch:totalResults"))
for it in d.get("items", []):
    au = "; ".join(a.get("foaf:name", "") if isinstance(a, dict) else str(a) for a in it.get("dc:creator", [])[:4]) if isinstance(it.get("dc:creator"), list) else it.get("dc:creator")
    pub = it.get("prism:publicationName", "")
    print("-", it.get("title"), "|", au, "|", pub, it.get("prism:volume", ""), it.get("prism:startingPage", ""), "|", it.get("prism:publicationDate", it.get("dc:date", "")), "|", it.get("@id", it.get("link", {}).get("@id") if isinstance(it.get("link"), dict) else ""))
