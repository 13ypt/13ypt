#!/usr/bin/env python3
"""Emit object records (JSONL) for crocodile entries of Gaillard & Daressy 1905 (CG, Cairo).
Values transcribed from the archive.org scan lafaunemomifie00gail (OCR checked against page images).
Usage: python3 cairo_cg1905.py | python3 crocodile-mummy-corpus/scripts/rec.py egypt objects
"""
import json
SRC = "https://archive.org/details/lafaunemomifie00gail"
BIB = "Gaillard & Daressy 1905, La faune momifiée de l'antique Égypte (CG), "
KO_DATE = "Graeco-Roman (catalogue p. 66: Kom Ombo crocodiles 'datent de l'époque gréco-romaine')"
SP = "Crocodilus niloticus (as identified in 1905 catalogue)"
base = dict(museum="Egyptian Museum, Cairo", city="Cairo", country="EG",
            source_of_identification="Gaillard & Daressy 1905 CG catalogue entry (full-text scan read)",
            evidence_type="OFFICIAL_CATALOGUE", confidence="PROBABLE", image_license="public domain scan (archive.org NOT_IN_COPYRIGHT)",
            online_record_url=SRC)
recs = []
def add(**kw):
    r = dict(base); r.update(kw); recs.append(r)

add(inventory_number="CG 29578", object_title_original="Tête de crocodile. — Momie hors de son enveloppe.",
    object_title_english="Crocodile head, mummy removed from its wrapping", classification="D",
    classification_basis="catalogue description + pl. XXXII (not viewed): head separated at first cervical vertebrae, skin preserved, debris of cloth adhering to bitumen",
    species_if_given=SP, provenance="Kôm-Ombo", date_period=KO_DATE, length="0.61 m", width="0.23 m",
    description="Head of a large individual, separated from the body at the first cervical vertebrae, covered with its integument; 'plusieurs débris d'étoffe adhérant par places au bitume'. Conservation: bonne; two teeth missing left lower jaw.",
    whole_or_partial="PARTIAL", wrapping_present="PARTIAL", bibliography=BIB+"pp. 66-67, pl. XXXII",
    notes="Page images checked (p. 66: L 0.61 m, larg. 0.23 m, Kôm-Ombo, pl. XXXII). Discrepancy in the 1905 print: p. 84 (entry 29628) refers to 'une tête momifiée d'Esneh, cataloguée au Musée du Caire sous le n° 29578', whereas the entry itself gives Kôm-Ombo.")
eggs = [("CG 29579","0.08 m","diam. 0.05 m","Shell white, slightly rough, traces of bitumen used at mummification. Conservation bonne."),
        ("CG 29580","0.07 m","diam. 0.05 m","Shell complete, contains powdery debris from decomposition of egg or embryo."),
        ("CG 29581","0.08 m","diam. 0.05 m","Similar to preceding."),
        ("CG 29582","0.08 m","diam. 0.05 m","No description; conservation bonne."),
        ("CG 29583","0.08 m","diam. 0.05 m","No description; conservation bonne."),
        ("CG 29584","0.12 m","width 0.08 m","Two crocodile eggs joined by a mass of bitumen with bone fragments and a cattle tooth."),
        ("CG 29585","0.10 m","width 0.08 m","Two crocodile eggs held in bitumen amid various debris; one egg broken.")]
for inv, L, oth, d in eggs:
    t = "Œufs de crocodile." if inv in ("CG 29584","CG 29585") else "Œuf de crocodile."
    add(inventory_number=inv, object_title_original=t, object_title_english="Crocodile egg(s)", classification="F",
        classification_basis="catalogue description only (egg with bitumen traces; no wrapping described)",
        provenance="Kôm-Ombo", date_period=KO_DATE, length=L, other_dimensions=oth, description=d,
        whole_or_partial="UNKNOWN", wrapping_present="NO", bibliography=BIB+"pp. 68-69",
        notes="EGG. Bitumen from mummification mentioned (29579) / eggs embedded in bitumen (29584-29585); not described as wrapped.")
big = [("CG 29628","5.20 m","Large Crocodilus niloticus; limbs extended backwards against trunk/tail base; after natron, abundantly coated with bitumen then wrapped in one or more broad linen bands of which only fragments remain on skin and scutes. Conservation bonne.","pp. 84-85"),
       ("CG 29629","4.65 m","Slightly smaller than 29628, mummified the same way; limbs extended back against body; shreds of linen adhering to bitumen. Conservation bonne.","p. 85"),
       ("CG 29630","4.55 m","Same aspect/size as 29629; limbs along body; bitumen stains and linen fragments on head and trunk. Strong wound near orbital region made before mummification (bitumen lines the fracture). Conservation passable.","p. 85")]
for inv, L, d, pg in big:
    add(inventory_number=inv, object_title_original="Crocodile momifié.", object_title_english="Mummified crocodile",
        classification="C", classification_basis="catalogue description: bitumen-coated body, only fragments of linen remain",
        species_if_given=SP, provenance="Kôm-Ombo", date_period=KO_DATE, length=L+" (longueur totale)", description=d,
        whole_or_partial="WHOLE", wrapping_present="PARTIAL", bibliography=BIB+pg,
        possible_duplicate_of="Egyptian Museum Cairo, Gallery 53 'Mummies of the big Nile crocodile' (2 displayed specimens, no inventory numbers online)",
        notes="Length OCR for 29630 garbled; read from page image p. 85 (4 m 55 cent.).")
young = [
 ("CG 29710","Jeune crocodile enveloppé.","0.31 m","0.07 m","A","UNKNOWN","No bitumen; natron-treated young crocodile wrapped in linen, thin palm ribs laid on first wrapping, then second series of ornamental bandages; black and light-yellow bands crossing at right angles forming three longitudinal rows of small rectangles on the back; head in black cloth with eyes as light ellipses with black dot. Outer bands missing along whole tail. Conservation passable.","Maspero, Guide de Boulaq no. 117; Notice de Ghizeh no. 796","UNKNOWN","YES",""),
 ("CG 29711","Jeune crocodile enveloppé.","0.25 m","0.07 m","A","UNKNOWN","Fine black and light-yellow bandages alternating and crossed, three rows of rectangles on upper face; underside and sides covered by broad band holding the ornamental bandages. Tail wrapping torn near end. Pl. XLVIII.","Maspero, Guide de Boulaq no. 1276","UNKNOWN","YES",""),
 ("CG 29712","Jeune crocodile enveloppé.","0.36 m","0.06 m","A","Thèbes (Assassif)","Narrow black and light-yellow bands crossing at right angles forming two longitudinal series of four rectangles; head in black cloth with two large elongated eyes of yellowish cloth with painted black disc. Conservation bonne. Pl. XLVIII.","Mariette, Notice de Boulaq 1864 no. 317; 1876 no. 425; Maspero, Guide de Boulaq no. 1273","UNKNOWN","YES",""),
 ("CG 29713","Jeune crocodile enveloppé.","0.34 m","0.08 m","A","UNKNOWN","Except head, covered by a broad piece of light cloth decorated on the upper face with two obliquely crossed bands; head in black cloth, eyes of white cloth with black spot. Linen torn in several places. Pl. XLVIII.","","UNKNOWN","YES",""),
 ("CG 29714","Jeune crocodile enveloppé.","0.38 m","0.06 m","A","Hawara","Covered with papyrus stems laid longitudinally and bound with them in a broad yellowish-white band without ornamental bandage. Linen wrapping missing on half of the surface.","Journal d'entrée du Musée no. 28373","JE 28373","PARTIAL",""),
 ("CG 29715","Jeune crocodile enveloppé.","0.18 m","0.04 m","A","UNKNOWN","Dimensions of a recently hatched crocodile; covered by a single piece of pink cloth; narrow band around body behind head; eyes of white and black cloth. Conservation bonne.","Maspero, Guide de Boulaq no. 1274","UNKNOWN","YES","Hatchling."),
 ("CG 29716","Série de jeunes crocodiles enveloppés.","0.45 m","0.07 m","B","UNKNOWN","Seven to eight very young crocodiles joined by a mass of bitumen; each held straight by two palm ribs (4-5 mm) tied with thread around snout, ribs and body to tail tip; whole dipped in bitumen and covered by broad coarse linen band, now partly torn.","","UNKNOWN","PARTIAL","Multiple individuals (7-8 hatchlings) in one bundle."),
 ("CG 29717","Jeune crocodile.","0.30 m","0.03 m","C","UNKNOWN","Single young crocodile fixed between two thin palm ribs by threads around jaws, ribs and body to tail tip; entirely covered with bitumen (no linen mentioned). Conservation bonne.","","UNKNOWN","NO",""),
 ("CG 29718","Jeune crocodile enveloppé.","0.36 m","0.04 m","C","UNKNOWN","Covered with thick bitumen layer and a broad piece of linen of which only a few fragments remain at both ends. Conservation mauvaise.","","UNKNOWN","PARTIAL",""),
 ("CG 29719","Jeune crocodile enveloppé.","0.39 m","0.03 m","A","UNKNOWN","Not dipped in bitumen; simply wound with a dark-brown linen band 3 cm wide coated with natron and resinous substances. Wrapping torn near head.","","UNKNOWN","YES",""),
 ("CG 29720","Jeune crocodile enveloppé.","0.28 m","0.04 m","C","UNKNOWN","Thick bitumen layer, then swaddled in yellowish-brown cloth bands c. 3 cm wide; cloth almost totally removed. Conservation mauvaise.","","UNKNOWN","PARTIAL",""),
]
for inv, t, L, W, cl, prov, d, bb, other, wrap, note in young:
    add(inventory_number=inv, other_numbers=other, object_title_original=t,
        object_title_english="Young crocodile (wrapped)" if "envelopp" in t else "Young crocodile",
        classification=cl, classification_basis="catalogue description only" + ("; pl. XLVIII (not viewed)" if inv in ("CG 29711","CG 29712","CG 29713") else ""),
        species_if_given=SP, provenance=prov, date_period="UNKNOWN", length=L, width=W, description=d,
        whole_or_partial="WHOLE" if cl in ("A","C") else "UNKNOWN", wrapping_present=wrap,
        bibliography=BIB+"pp. 118-120" + ("; " + bb if bb else ""),
        notes=(note + " " if note else "") + "Lengths read from page images pp. 118-120 (OCR garbled for several).")
coffins = [
 ("CG 29813","Cercueil de crocodile. — Sycomore.","E","L 0.365 m; H 0.08 m","Elongated wooden block with roughly carved crocodile on top; base hollowed laterally (0.21 m long) to receive the mummy of a small crocodile, 'dont il ne reste que quelques linges'; closing board missing; stucco fallen.","UNKNOWN","","Contains only some linen remains of the mummy."),
 ("CG 29814","Cercueil de crocodile. — Sycomore.","E","L 0.28 m; W 0.08 m; H 0.076 m","Rectangular block with vaguely carved crocodile; side board closes cavity (0.18 m) in which only a linen pad remains that wedged a young crocodile mummy.","UNKNOWN","",""),
 ("CG 29815","Cercueil de crocodile. — Cèdre.","E","L 0.158 m; W 0.065 m; H 0.11 m","Coffin of young crocodile; carved crocodile on top gilded; cavity closed by board 0.128 x 0.065 m; X mark in black at head end. 'La momie n'existe plus.' Pl. LXVI.","Thèbes, Assassif","JE 26485","Mummy no longer present."),
 ("CG 29816","Crocodile sculpté. — Sycomore.","E","L 0.345 m","Carved crocodile meant to be pegged onto a box containing a crocodile mummy; scales indicated; hole on head for a crown; stucco fallen.","UNKNOWN","","Lid figure only."),
 ("CG 29816 bis","Cercueil de crocodile. — Toile stuquée.","F","L 0.265 m","'Momie de jeune crocodile enfermée dans une gaine en toile recouverte de plâtre'; flat top, tail turned slightly left, limbs not indicated; head painted white, rest green; closure complete, sheath cannot be opened.","UNKNOWN","","Young crocodile mummy inside a closed plastered-linen sheath; contents not verified, hence F."),
]
for inv, t, cl, dims, d, prov, other, note in coffins:
    add(inventory_number=inv, other_numbers=other, object_title_original=t,
        object_title_english="Crocodile coffin" if "Cercueil" in t else "Carved crocodile (coffin lid figure)",
        classification=cl, classification_basis="catalogue description only" + ("; pl. LXVI (not viewed)" if inv=="CG 29815" else ""),
        provenance=prov, date_period="UNKNOWN", other_dimensions=dims, description=d,
        whole_or_partial="UNKNOWN", wrapping_present="UNKNOWN" if cl=="F" else "NO",
        bibliography=BIB+"pp. 152-153" + ("; Journal d'entrée no. 26485" if inv=="CG 29815" else ""),
        notes=note)
for r in recs:
    print(json.dumps(r, ensure_ascii=False))
