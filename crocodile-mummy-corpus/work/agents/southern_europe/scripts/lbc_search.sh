#!/bin/bash
# Search Lombardia Beni Culturali. Needs CA bundle + GlobalSign AlphaSSL 2025 intermediate (site omits it).
# usage: lbc_search.sh "<path?query>"
CA=${CA:-/tmp/claude-0/-home-user-13ypt/ad9aca12-8b92-579c-b245-d0074add43b4/scratchpad/cabundle_plus.pem}
curl -sS --cacert "$CA" -m 60 "https://www.lombardiabeniculturali.it$1" | python3 -c "
import sys,re,html
h=sys.stdin.read()
t=re.sub(r'<script.*?</script>','',h,flags=re.S)
m=re.search(r'([\d\.]+)\s+(?:risultat|schede|oggett)',re.sub(r'<[^>]+>',' ',t))
print('COUNT:', m.group(0) if m else '?')
seen=set()
for m in re.finditer(r'href=[\x27\"](/[a-z0-9\-]+/schede/[^\x27\"]+)[\x27\"][^>]*>(.*?)</a>',t,re.S):
    txt=' '.join(html.unescape(re.sub(r'<[^>]+>',' ',m.group(2))).split())
    if m.group(1) in seen: continue
    seen.add(m.group(1)); print(m.group(1),'|',txt[:150])
"
