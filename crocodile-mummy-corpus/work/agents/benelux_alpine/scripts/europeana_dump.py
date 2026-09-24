#!/usr/bin/env python3
"""Print key fields of a Europeana record JSON (record/v2) file."""
import sys, json
for fn in sys.argv[1:]:
    d = json.load(open(fn))
    o = d.get('object', {})
    print('=====', fn, 'about=', o.get('about'))
    for p in o.get('proxies', []):
        if p.get('europeanaProxy'):
            continue
        for k, v in p.items():
            if k.startswith('dc') or k.startswith('dcterms') or k in ('edmCurrentLocation',):
                print(' ', k, json.dumps(v, ensure_ascii=False))
    for a in o.get('aggregations', []):
        print('  isShownAt', a.get('edmIsShownAt'), '| isShownBy', a.get('edmIsShownBy'), '| rights', a.get('edmRights'), '| provider', a.get('edmDataProvider'))
        for wr in a.get('webResources', [])[:5]:
            print('   webres', wr.get('about'))
    ea = o.get('europeanaAggregation', {})
    print('  europeana landing', ea.get('edmLandingPage'))
