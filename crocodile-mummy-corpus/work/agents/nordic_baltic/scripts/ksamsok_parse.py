#!/usr/bin/env python3
"""Parse a K-samsok search XML result into a compact per-record dump."""
import sys, re, json
from lxml import etree
NS={'k':'http://kulturarvsdata.se/ksamsok#','rdf':'http://www.w3.org/1999/02/22-rdf-syntax-ns#','pres':'http://kulturarvsdata.se/presentation#','dcterms':'http://purl.org/dc/terms/'}
t=etree.parse(sys.argv[1])
out=[]
for rdf in t.iter('{%s}RDF'%NS['rdf']):
    ent=rdf.find('k:Entity',NS)
    r={'uri':ent.get('{%s}about'%NS['rdf']),
       'url':(ent.findtext('k:url',namespaces=NS) or ''),
       'label':ent.findtext('k:itemLabel',namespaces=NS),
       'org':ent.findtext('k:serviceOrganization',namespaces=NS)}
    r['desc']=[(d.findtext('k:type',namespaces=NS),d.findtext('k:desc',namespaces=NS)) for d in rdf.findall('k:ItemDescription',NS)]
    r['names']=[(d.findtext('k:type',namespaces=NS),d.findtext('k:name',namespaces=NS)) for d in rdf.findall('k:ItemName',NS)]
    r['numbers']=[(d.findtext('k:type',namespaces=NS),d.findtext('k:number',namespaces=NS)) for d in rdf.findall('k:ItemNumber',NS)]
    r['meas']=[(m.findtext('k:type',namespaces=NS),m.findtext('k:value',namespaces=NS),m.findtext('k:unit',namespaces=NS),m.findtext('k:qualifier',namespaces=NS)) for m in rdf.findall('k:ItemMeasurement',NS)]
    r['ctx']=[]
    for c in rdf.findall('k:Context',NS):
        r['ctx'].append({ch.tag.split('}')[1]:(ch.text or ch.get('{%s}resource'%NS['rdf'])) for ch in c})
    r['images']=[]
    for im in rdf.findall('k:Image',NS):
        r['images'].append({ch.tag.split('}')[1]:(ch.text or ch.get('{%s}resource'%NS['rdf'])) for ch in im})
    lic=ent.find('k:itemLicense',NS)
    r['itemLicense']=lic.get('{%s}resource'%NS['rdf']) if lic is not None else None
    out.append(r)
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
for r in out:
    print(r['url'],'|',r['label'],'|',[n for t,n in r['numbers']])
