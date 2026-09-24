#!/bin/bash
# Search Korean e-museum (emuseum.go.kr, national portal of Korean public museum collections)
# usage: emuseum.sh "<keyword>" ; needs session cookie
D=/tmp/claude-0/-home-user-13ypt/ad9aca12-8b92-579c-b245-d0074add43b4/scratchpad/east_asia
curl -sS -m 40 -L -c $D/emcj.txt -b $D/emcj.txt -A "Mozilla/5.0" "https://www.emuseum.go.kr/main" -o /dev/null
K=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$1")
curl -sS -m 40 -L -c $D/emcj.txt -b $D/emcj.txt -A "Mozilla/5.0" -e "https://www.emuseum.go.kr/main" "https://www.emuseum.go.kr/headerSearch?category=&rows=36&pageNum=1&keyword=$K&keywordHistory=$K" -o $D/ems.html
python3 - <<'PY'
import re
h=open('/tmp/claude-0/-home-user-13ypt/ad9aca12-8b92-579c-b245-d0074add43b4/scratchpad/east_asia/ems.html',encoding='utf-8',errors='ignore').read()
t=re.sub(r'<script.*?</script>','',h,flags=re.S); t=re.sub(r'<style.*?</style>','',t,flags=re.S)
t=re.sub(r'<[^>]+>','|',t); t=re.sub(r'\s+',' ',t); t=re.sub(r'(\|\s*)+','|',t)
for m in re.finditer(r'소장품\s*\(?[\d,]+\)?|[\d,]+\s*건',t): print(m.group(0))
i=t.find('상세보기'); print(t[max(0,i-300):i+3000])
PY
