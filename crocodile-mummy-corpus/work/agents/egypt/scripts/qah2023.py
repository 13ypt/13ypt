#!/usr/bin/env python3
"""Object records for the Qubbat al-Hawa crocodiles (De Cupere et al. 2023, PLOS ONE e0279137).
Usage: python3 qah2023.py | python3 crocodile-mummy-corpus/scripts/rec.py egypt objects"""
import json
URL = "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0279137"
BIB = "De Cupere, Van Neer, Barba Colmenero, Jiménez Serrano & Dardeniz Arikan 2023, PLOS ONE 18(1): e0279137"
base = dict(museum="Qubbat al-Hawa Project (Universidad de Jaén) – on-site store, tomb QH34ll", city="Aswan (West Bank)", country="EG",
            provenance="Qubbat al-Hawa (Aswan), tomb QH34ll, stratum EU 445, excavated 2019",
            date_period="undated; preparation method suggests pre-Ptolemaic date (paper)",
            online_record_url=URL, image_license="CC BY 4.0 (article figures)", api_or_iiif="NO",
            bibliography=BIB, source_of_identification="Peer-reviewed article: studied on site, 'currently stored there'",
            evidence_type="PEER_REVIEWED;EXCAVATION_REPORT", confidence="CONFIRMED", acquisition="Excavation 2019, Universidad de Jaén mission (Qubbat al-Hawa Project), under MoTA permit")
spp = "C. niloticus / C. suchus both present in assemblage; per-individual attribution tentative (skull ratio), see paper Table 2"
items = [
 ("crocodile #5", "C", "WHOLE", "PARTIAL", "Crocodylus niloticus (scute arrangement: six nuchals in two rows)",
  "Best preserved, still largely articulated mummified specimen, lifted in three pieces (head+anterior body; mid-body; tail with end missing). Skin almost undamaged; forelegs present (right folded backwards, left turned laterally), hind legs folded forward under body; gastroliths in situ; minimum measured length 2.23 m (2.63 m reconstructed from head length 375 mm). Palm leaves (doum) and linen fragments associated; objects incl. egg shell remains recovered from body cavity.",
  "Figs 3, 5-8, 18-19", "2.23 m (minimum measured); 2.63 m reconstructed", "head length 375 mm"),
 ("crocodile #4", "C", "PARTIAL", "NO", spp,
  "Most complete skeleton; soft tissue visible at nostrils, eye sockets, fenestrae; scale colour preserved on snout; 23 of 37 caudal vertebrae; 116 scutes; multiple healed pathologies. Palm leaves and rope associated. Bones of 'crocodile #2' (headless) re-assigned to #4.",
  "Figs 9-12, 18", "3.50 m reconstructed", "head length 500 mm"),
 ("crocodile #11", "C", "PARTIAL", "NO", spp + " (largest; lowest skull ratio 1.86)",
  "Skull and lower jaws intact, almost no skin; skeleton quite complete except tail end; 59 scutes (+83 loose scutes possibly from #11); pathologies (possible osteomyelitis of left pubis, healed fibula fracture). Linen fragments and rope associated.",
  "Figs 9, 11, 13", "3.53 m reconstructed (paper also gives 3.54 m)", "head length 505 mm"),
 ("crocodile #1", "F", "PARTIAL", "NO", spp,
  "Bone only, no skin or soft tissue; skeleton far from complete (no ribs or chevrons, few foot bones); 75 scutes.",
  "Figs 9, 11", "2.83 m reconstructed", "head length 405 mm"),
 ("crocodile #7", "F", "PARTIAL", "NO", spp,
  "Skull broken and incomplete, lower jaws complete; postcranial skeleton far from complete; 9 scutes.",
  "Figs 11, 14", "c. 2.3 m reconstructed", "lower jaw length 410 mm"),
 ("crocodile #10", "D", "PARTIAL", "NO", spp,
  "Largest isolated head; skin remains on lower jaws and skull (dorsal), nostrils preserved, soft tissue over supratemporal fenestrae; occipital condyle and angulars damaged (detachment of head).",
  "Figs 15-16", "3.33 m reconstructed", "head length 475 mm"),
 ("crocodile #3", "D", "PARTIAL", "NO", spp,
  "Isolated head; lower jaws detached but intact; soft tissue preserved at nostrils and right eyelid; hind skull damaged.",
  "Fig 15", "2.84 m reconstructed", "head length 405 mm"),
 ("crocodile #6", "F", "PARTIAL", "NO", spp,
  "Isolated skull only, lower jaws absent; no traces of skin; all teeth missing.",
  "Fig 15", "2.73 m reconstructed", "head length 390 mm"),
 ("crocodile #8", "D", "PARTIAL", "NO", spp,
  "Almost intact skull and lower jaws with skin over large parts; chop marks (right squamosum, right angular) from decapitation of desiccated animal; proatlas attached.",
  "Figs 15, 17", "2.69 m reconstructed", "head length 385 mm"),
 ("crocodile #9", "F", "PARTIAL", "NO", spp + " (smallest; ratio 2.26)",
  "Smallest individual; fully preserved but slightly weathered skull, no skin; occipital condyle broken off.",
  "Fig 15", "1.85 m reconstructed", "head length 264 mm"),
]
for num, cl, wp, wrap, sp, desc, figs, L, oth in items:
    r = dict(base)
    r.update(inventory_number="UNKNOWN", other_numbers="Excavation individual no. " + num,
             object_title_original="Crocodile " + num.split()[-1], object_title_english="Crocodile " + num.split()[-1],
             classification=cl,
             classification_basis="peer-reviewed description and published photos (" + figs + ")" + ("; skeletal/skull remains without soft tissue, included because published as part of a crocodile-mummy deposit" if cl == "F" else ""),
             species_if_given=sp, length=L, other_dimensions=oth, description=desc, whole_or_partial=wp, wrapping_present=wrap,
             image_urls=URL + " (" + figs + ")", image_count="see " + figs,
             notes="Excavation number used in De Cupere et al. 2023; no museum inventory number published. Assemblage: 10 individuals (5 bodies, 5 heads), no resin/bitumen, linen almost entirely lost to insects." + (" SKELETAL: bone only, may fall outside corpus definition." if cl == "F" else ""))
    print(json.dumps(r, ensure_ascii=False))
