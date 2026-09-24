#!/usr/bin/env python3
"""Carmentis (KMKG/MRAH Brussels, eMuseumPlus) simple search via session form POST.
Usage: carmentis_search.py <term> [lang] [detail_regex]
Prints every result (inventory | title) across all pages; for titles matching detail_regex
(default: momie|mummy|mummie) fetches the detail page and prints its text + permalink objectId."""
import re, sys, time, html, requests
term = sys.argv[1]; lang = sys.argv[2] if len(sys.argv) > 2 else 'fr'
detail_re = re.compile(sys.argv[3] if len(sys.argv) > 3 else r'momie|mummy|mummie', re.I)
s = requests.Session(); s.headers['User-Agent'] = 'Mozilla/5.0 (research survey; crocodile mummy corpus)'
B = 'https://www.carmentis.be'
r = s.get(B + '/eMP/eMuseumPlus', params={'service': 'ExternalInterface', 'module': 'collection', 'lang': lang, 'objectId': '84095'})
m = re.search(r'<form method="post" name="Form0" action="([^"]+)" id="siteSearch"', r.text)
svc = re.search(r'id="siteSearch".*?name="service" value="([^"]+)"', r.text, re.S).group(1)
time.sleep(1)
r = s.post(B + html.unescape(m.group(1)), files={'service': (None, svc), 'sp': (None, 'S0'), 'Form0': (None, 'siteSearchInput'), 'siteSearchInput': (None, term)})
def text(txt):
    t = re.sub(r'<script.*?</script>|<style.*?</style>|<!--.*?-->', '', txt, flags=re.S)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
tot = re.search(r'de (\d+)\s', text(r.text).split('Résultat')[-1] if 'Résultat' in r.text else '')
items = []
seen_pages = 0
while True:
    seen_pages += 1
    for m in re.finditer(r'<a href="([^"]+TspTitleLink[^"]+)"><span class="tspTitleLink">(.*?)</span></a>.*?<li class="inventoryNb"><span class="tspValue">(.*?)</span>', r.text, re.S):
        items.append((html.unescape(m.group(3)), html.unescape(m.group(2)), B + html.unescape(m.group(1))))
    nxt = re.search(r'href="([^"]+moduleContextFunctionBar\.navigator\.next[^"]+)"', r.text)
    if not nxt or seen_pages > 40:
        break
    time.sleep(1)
    r = s.get(B + html.unescape(nxt.group(1)))
print(f'TERM={term} results={len(items)}')
for inv, title, link in items:
    print(f'  {inv} | {title}')
for inv, title, link in items:
    if detail_re.search(title):
        time.sleep(1)
        d = s.get(link)
        t = text(d.text)
        pl = re.search(r'objectId=(\d+)', d.text)
        i = t.find('Numéro d') if 'Numéro d' in t else t.find('Inventory')
        print('----- DETAIL', inv, '| objectId', pl.group(1) if pl else '?')
        print(t[i:i + 1800])
