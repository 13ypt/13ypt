#!/usr/bin/env python3
"""Build object records for Medelhavsmuseet crocodile mummies from the saved K-samsok JSON."""
import json, sys
RAW = '/home/user/13ypt/crocodile-mummy-corpus/work/agents/nordic_baltic/raw/'
d = json.load(open(RAW + 'ksamsok_smvkmm_krokodil.json'))
# classification decided from DB description + (where noted) the first online photo viewed by agent
CLS = {
 'MM 30865': ('D','PARTIAL','NO','DB comment "pieces of a baby crocodile ... photo shows at least two baby crocodiles"; first online photo viewed: unwrapped fragments incl. two heads and body/tail pieces'),
 'MM 18414': ('D','PARTIAL','NO','DB description "A mummified baby crocodile without head", condition "The head is missing"; photo viewed: unwrapped headless body with tail'),
 'S.N. E 0064': ('D','PARTIAL','NO','DB object name "mummy, fragment, crocodile" (no description); photo viewed: unwrapped head and anterior body only'),
 'NME 799': ('A','WHOLE','PARTIAL','DB description "A mummified baby crocodile wrapped in linen"; photo viewed: head and tail ends exposed, mid-body bandaged, a detached tail fragment lies beside it'),
 'NME 796': ('B','UNKNOWN','YES','DB description "A bunch of young crocodiles wrapped in linen" (multiple individuals; object name includes "fragment"); photo viewed: spindle-shaped linen bundle tied with string'),
 'MM 18415': ('D','PARTIAL','UNKNOWN','DB description "Mummified head of a baby crocodile", L. 5.3 cm'),
 'NME 797': ('A','WHOLE','PARTIAL','DB description "Mummified baby crocodile"; photo viewed: anterior body wrapped in linen, tail exposed; old label reads "Balsamerad Krokodil-unge. Egypten. Kapt. Cronstrand 1842"'),
 'MM 10133': ('A','WHOLE','YES','DB description "Mummified and wrapped. Baby crocodile."; photo viewed: elongated linen-wrapped bundle with palm-rib splints protruding at one end'),
 'MM 18406': ('F','UNKNOWN','YES','DB description "A mummified baby crocodile wrapped in linen" but DB object name includes "fragment"; photo viewed: elongated fully wrapped bundle; completeness not stated'),
 'MM 10134': ('A','WHOLE','YES','DB description "Mummified and wrapped. Baby crocodile."; photo viewed: elongated fully wrapped bundle, one end darker'),
 'MM 18410': ('C','WHOLE','NO','DB description "A mummified baby crocodile"; photo viewed: unwrapped complete hatchling (head, limbs, tail)'),
 'MM 19240': ('C','WHOLE','NO','DB description "A mummified baby crocodile. Without linen wrappings."'),
 'MM 18411': ('C','WHOLE','NO','DB description "Mummified baby crocodile. Unwrapped." (Swedish: "Upplindad")'),
 'MM 18413': ('C','WHOLE','NO','DB description "A mummified baby crocodile"; photo viewed: unwrapped complete hatchling'),
 'MM 18408': ('C','WHOLE','NO','DB description "A mummified baby crocodile. Unwrapped." (Swedish "Avlindad")'),
 'MM 18412': ('C','WHOLE','NO','DB description "A mummified baby crocodile. Unwrapped." (Swedish "Upplindad")'),
 'MME 1983:013 A': ('C','WHOLE','NO','DB description "Mummified crocodile baby"; comment: linen wrapping removed by Riksmuseet staff 1983; condition "Tip of the tail is missing"'),
 'MM 18407': ('C','WHOLE','NO','DB description "A mummified baby crocodile. Unwrapped." (Swedish "Avlindad")'),
 'MM 18409': ('C','WHOLE','NO','DB description "A mummified baby crocodile without linen wrappings"'),
 'MME 1977:002': ('C','WHOLE','NO','DB description "Mummified baby crocodile without linen wraps"'),
 'MM 30721': ('A','WHOLE','PARTIAL','DB description "A mummified baby crocodile. Three splints made of palmleaves and linen wrappings."; photo viewed: head and tail exposed, body bandaged, palm splints protruding at tail end'),
 'MM 30810': ('A','WHOLE','PARTIAL','DB description "A mummified baby crocodile. Two splints made of palm leaves and linen wrappings. The head is loose."'),
}
def dget(r, key):
    return [v for t, v in r['desc'] if t == key]
out = []
for r in d:
    if not ('crocodile' in r['label'] and 'mummy' in r['label']): continue
    nums = [n for t, n in r['numbers']]
    inv = nums[0]
    oid = r['url'].rsplit('/', 1)[1]
    if oid == '3011830':
        continue  # duplicate record of MM 18414 (DB comment "same object as no MM 18414")
    cls, whole, wrap, basis = CLS[inv]
    other = [n for t, n in r['numbers'][1:] if t == 'Acquisition number']
    exhib = [n for t, n in r['numbers'][1:] if t != 'Acquisition number']
    other_s = '; '.join(['acquisition no. ' + o for o in other] + ['Egypt exhibition no. ' + e for e in exhib] + ['Carlotta object id ' + oid])
    if inv == 'MM 18414':
        other_s += '; separate Carlotta record 3011830 (MME 1961:263) is the same object'
    desc_en = dget(r, 'Description'); desc_sv = dget(r, 'Description, Swedish')
    comments = dget(r, 'Comments'); cond = dget(r, 'Condition')
    acq = dget(r, 'Acquisition'); dims = dget(r, 'Dimensions')
    loan = dget(r, 'Loan out / Current'); loantaker = dget(r, 'Name / Loantaker')
    length = [f"{m[1]} {m[2]}" for m in r['meas'] if m[0].startswith('Length')]
    width = [f"{m[1]} {m[2]}" for m in r['meas'] if m[0].startswith('Width')]
    ims = r['images']
    img_urls = ' ; '.join((i.get('highresSource') or i.get('lowresSource')) for i in ims[:3])
    desc = ' | '.join(filter(None, ['EN: ' + ' '.join(desc_en) if desc_en else '', 'SV: ' + ' '.join(desc_sv) if desc_sv else '', 'Condition: ' + ' '.join(cond) if cond else '', 'Comments: ' + ' '.join(c.replace('\n', ' ') for c in comments) if comments else '']))
    notes = []
    loanseq = [f"{t}: {v}" for t, v in r['desc'] if t.startswith('Loan out') or t.startswith('Name / Loantaker')]
    if loanseq:
        notes.append('Carlotta loan fields (verbatim, in order): ' + ' / '.join(loanseq))
    if 'Egypten 8.4' in ' '.join(v for t, v in r['desc']):
        notes.append('On display in Egypt exhibition 2014-, showcase Egypten 8.4 (label "Mummified young crocodiles")')
    notes.append('Also in Europeana (Search API) as records /91639/SMVK_MM_objekt_' + oid + ' and /91644/SMVK_MM_Egypt_' + oid)
    notes.append('Metadata CC0 (K-samsok itemLicense); images CC BY 4.0, copyright Statens museer for varldskultur (K-samsok mediaLicenseUrl)')
    if inv in ('NME 797', 'MME 1983:013 A'):
        notes.append('Both NME 797 and MME 1983:013 A are recorded as gifts of Baltzar Cronstrand 1842 (via Nationalmuseum / Riksmuseet respectively)')
    rec = {
        'museum': 'Museum of Mediterranean and Near Eastern Antiquities (Medelhavsmuseet)',
        'city': 'Stockholm', 'country': 'SE',
        'inventory_number': inv,
        'other_numbers': other_s,
        'object_title_original': r['label'],
        'object_title_english': ', '.join(n for t, n in r['names'] if t == 'Object'),
        'classification': cls, 'classification_basis': basis,
        'species_if_given': 'UNKNOWN',
        'provenance': 'Egypt (Country - Findspot); no site given',
        'acquisition': ' '.join(acq) if acq else 'UNKNOWN',
        'date_period': 'UNKNOWN',
        'length': ', '.join(length) if length else 'UNKNOWN',
        'width': ', '.join(width) if width else 'UNKNOWN',
        'other_dimensions': ' '.join(dims) if dims else 'UNKNOWN',
        'description': desc,
        'whole_or_partial': whole, 'wrapping_present': wrap,
        'online_record_url': r['url'],
        'image_urls': img_urls,
        'image_count': str(len(ims)),
        'image_license': 'CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), (c) Statens museer for varldskultur' if ims else 'UNKNOWN',
        'api_or_iiif': 'K-samsok API (Swedish national heritage API) entity http://kulturarvsdata.se/SMVK-MM/objekt/' + oid + ' returned by https://kulturarvsdata.se/ksamsok/api?method=search&query=serviceOrganization=SMVK-MM and text=krokodil; Europeana Search API; no IIIF',
        'bibliography': 'UNKNOWN',
        'source_of_identification': 'Medelhavsmuseet Carlotta DB record (object name "crocodile, mummy"), cross-checked via K-samsok API and Europeana',
        'evidence_type': 'OFFICIAL_DB;NATIONAL_PORTAL',
        'confidence': 'CONFIRMED',
        'possible_duplicate_of': 'UNKNOWN',
        'notes': '; '.join(notes),
    }
    out.append(rec)
for rec in out:
    print(json.dumps(rec, ensure_ascii=False))
print(len(out), file=sys.stderr)
