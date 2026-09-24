#!/usr/bin/env python3
"""Free-text search in a Carlotta instance; prints hit count and (identity | class) of all hits on the result page.
Usage: carlotta_search.py <base e.g. https://collections.smvk.se/carlotta-mhm> <term>"""
import sys, re, requests, warnings
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore")
base, term = sys.argv[1], sys.argv[2]
s = requests.Session(); s.headers['User-Agent'] = 'Mozilla/5.0 (research)'
s.get(base + '/web/EasySearch', timeout=60)
r = s.post(base + '/web/perform/free_search', data={'FreeSearch_TEXT_OPERAND': 'CONTAINS', 'FreeSearch_TEXT_VALUE': term}, timeout=90)
soup = BeautifulSoup(r.text, 'lxml')
txt = soup.get_text(' ', strip=True)
m = re.search(r'(\d[\d\s]*)\s*(hits|träffar)', txt)
print('STATUS', r.status_code, 'HITS', m.group(1) if m else None)
for dl in soup.find_all('dl', class_='definition_result'):
    ident = dl.find('span', class_='identity'); cl = dl.find('span', class_='class')
    print((ident.get_text(strip=True) if ident else '?'), '|', (cl.get_text(strip=True) if cl else dl.get_text(' ', strip=True)[:120]))
