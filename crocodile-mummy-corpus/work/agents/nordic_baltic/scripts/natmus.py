#!/usr/bin/env python3
"""Nationalmuseet Samlinger Online: keyword browse (all pages) and raw object JSON extraction.
Usage: natmus.py browse <keyword>   |   natmus.py obj <coll> <id>"""
import sys, json, time, re, requests, html as H
B = 'https://samlinger.natmus.dk'
def browse(kw):
    hits, frm = [], 0
    while True:
        d = requests.get(f'{B}/api/objectbrowse', params={'keyword': kw, 'from': frm}, timeout=60).json()
        hits += d['hits']; frm = len(hits)
        if not d['hits'] or frm >= d['total']: break
        time.sleep(1)
    return d['total'], hits
def obj(coll, oid):
    h = requests.get(f'{B}/{coll}/object/{oid}', timeout=60).text
    m = re.search(r'Rådata.*?(\{\s*"id".*?"indexId":\s*"[^"]+"\s*\})', H.unescape(re.sub(r'<[^>]+>', '', h)), re.S)
    return json.loads(m.group(1)) if m else None
if __name__ == '__main__':
    if sys.argv[1] == 'browse':
        t, hits = browse(sys.argv[2])
        print('TOTAL', t)
        for x in hits: print(x['url'], '|', x['title'], '|', x.get('img', ''))
    else:
        print(json.dumps(obj(sys.argv[2], sys.argv[3]), ensure_ascii=False))
