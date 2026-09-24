#!/usr/bin/env python3
"""Fetch KHM Wien object pages (khm.at/de/objektdb/detail/<id>/) and print the key data block."""
import re, sys, time, html, requests
for oid in sys.argv[1:]:
    r = None
    for attempt in range(4):
        try:
            r = requests.get(f'https://www.khm.at/de/objektdb/detail/{oid}/', headers={'User-Agent': 'Mozilla/5.0 (research survey)'}, timeout=60)
            break
        except Exception as e:
            print('  retry', oid, type(e).__name__); time.sleep(3)
    if r is None:
        print('=====', oid, 'FAILED'); continue
    t = re.sub(r'<script.*?</script>|<style.*?</style>', '', r.text, flags=re.S)
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
    i = t.find('download', t.find('Toggle thumbnails'))
    j = t.find('Weiterstöbern')
    imgs = sorted(set(re.findall(r'https://imageapi\.khm\.at/images/\d+/[^"\s\']+\.jpg', r.text)))
    print('=====', oid, r.url)
    print(t[i + 8:j].strip())
    print('  images:', len(imgs), imgs[:3])
    time.sleep(2)
