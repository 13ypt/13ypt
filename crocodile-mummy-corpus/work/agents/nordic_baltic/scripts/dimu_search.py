#!/usr/bin/env python3
"""Query the DigitaltMuseum (dimu) Solr API (SE+NO) and list hits. Usage: dimu_search.py '<solr q>'"""
import sys, json, time, requests, urllib.parse
q = sys.argv[1]
docs = []; start = 0
while True:
    u = 'https://api.dimu.org/api/solr/select?' + urllib.parse.urlencode({'q': q, 'wt': 'json', 'rows': 100, 'start': start, 'api.key': 'demo'})
    d = requests.get(u, timeout=60).json()
    n = d['response']['numFound']; batch = d['response']['docs']
    docs += batch; start += len(batch)
    if not batch or start >= n or start >= 1000: break
    time.sleep(1)
print('QUERY', q, 'numFound', n)
for x in docs:
    print(x.get('artifact.uniqueId'), '|', x.get('identifier.owner'), '|', x.get('identifier.id'), '|', x.get('artifact.ingress.title'), '|', (x.get('artifact.ingress.classification') or '') , '|', (x.get('artifact.ingress.description') or '')[:150].replace('\n',' '))
