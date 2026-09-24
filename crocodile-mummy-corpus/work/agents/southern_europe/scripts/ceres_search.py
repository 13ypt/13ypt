#!/usr/bin/env python3
"""CERES (Red Digital de Colecciones de Museos de España) simple search.
usage: ceres_search.py "terms" ; prints result count and rows (inventory, object, museum, link)"""
import sys, re, html, requests
q = sys.argv[1]
s = requests.Session()
s.get("http://ceres.mcu.es/pages/SimpleSearch?index=true", timeout=60)
data = {"txtSimpleSearch": q, "searchOperator": "AND", "btnSearch": "Buscar", "servletOrigen": "SimpleSearch",
        "servletDestino": "SimpleSearch", "search": "simple", "index": "true"}
r = s.post("http://ceres.mcu.es/pages/Main", data=data, timeout=90)
h = r.content.decode("utf-8", "replace")
t = re.sub(r'<script.*?</script>', '', h, flags=re.S)
txt = ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', t)).split())
m = re.search(r'(\d[\d\.]*)\s+(?:resultados|registros|objetos)', txt)
print("QUERY", q, "COUNT", m.group(0) if m else "?")
links = re.findall(r'href="(Main\?idt=\d+[^"]*)"', h)
seen = []
for l in links:
    l = html.unescape(l)
    if l not in seen: seen.append(l)
for l in seen: print("http://ceres.mcu.es/pages/" + l)
open(sys.argv[2] if len(sys.argv) > 2 else "/dev/null", "w").write(h)
