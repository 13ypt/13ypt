# Agent protocol — Global Corpus of Ancient Egyptian Crocodile Mummies

Read this whole file before starting. Every research agent follows it exactly.

## 1. Context and goal

An Egyptologist working on crocodile cults is building an exhaustive, source-traceable
world corpus of ancient Egyptian crocodile mummies in museums, university collections,
natural-history collections and archaeological research institutions. The later goal is
image comparison of the bandaging of head, back (dorsal) and tail. **This round's goal is
discovery and verification of holding institutions and individual objects.** Do not do
wrapping typology.

This is a production survey, not a pilot. Do not stop after an arbitrary number of
institutions. Stop only when your assignment checklist is exhausted **and** further
queries in your languages stop yielding new institutions; write the evidence for that
saturation judgement in `summary.md`.

## 2. Where and how to write

Working directory: `/home/user/13ypt`. Your files live in
`crocodile-mummy-corpus/work/agents/<AGENT_NAME>/` (created automatically).

Write every record with the validator (it rejects bad fields; fix and resend):

```bash
python3 crocodile-mummy-corpus/scripts/rec.py <AGENT_NAME> objects <<'EOF'
{"museum": "British Museum", "city": "London", "country": "GB", "inventory_number": "EA 12345", ...}
EOF
```

Kinds: `institutions`, `objects`, `search_log`, `no_confirmation`, `bibliography`, `leads`.
Open `crocodile-mummy-corpus/scripts/rec.py` once to see the exact fields and allowed
values. **Append as you go** (after each institution), never batch everything at the end.
At the end write `crocodile-mummy-corpus/work/agents/<AGENT_NAME>/summary.md`.

Optional: save small raw API/JSON responses you rely on in `.../<AGENT_NAME>/raw/` and any
script you write for systematic querying in `.../<AGENT_NAME>/scripts/` (so the search is
reproducible). Never save images or large HTML dumps. Do not run git. Do not touch other
agents' folders or files outside your folder (except appending via rec.py).

## 3. Evidence rules (strict)

Evidence types (`evidence_type`, several allowed, `;`-separated):
`OFFICIAL_DB` (museum's online collection database), `OFFICIAL_API` (API/JSON),
`IIIF`, `OFFICIAL_CATALOGUE` (museum's printed/PDF catalogue), `OFFICIAL_WEBPAGE`
(page on the institution's own domain: news, blog, exhibition, annual report),
`PEER_REVIEWED`, `MONOGRAPH`, `EXCAVATION_REPORT`, `THESIS`,
`NATIONAL_PORTAL` (Europeana, Deutsche Digitale Bibliothek, museum-digital, POP/Joconde,
DigitaltMuseum, Finna, Collectie Nederland, CulturaItalia, CERES/Hispana, Trove,
DigitalNZ, Japan Search, Artefacts Canada, etc. — portals that republish institutional
records), `SECONDARY` (anything else).

Candidate-only sources — may lead you to a candidate, never sufficient for CONFIRMED:
search-engine snippets, blogs, social media, Pinterest, auction/dealer sites, news and
popular articles, travel/tourism sites, YouTube, Google Arts & Culture alone (max
PROBABLE), personal websites.

**Forbidden entirely:** Wikipedia, Wikidata, Wikimedia Commons and any other wiki. Do not
open them, do not cite them (the researcher explicitly excludes them; the validator
rejects wiki URLs).

Confidence levels:
- `CONFIRMED` — an institutional source (OFFICIAL_*, IIIF, NATIONAL_PORTAL) or a
  scholarly source (PEER_REVIEWED, MONOGRAPH, EXCAVATION_REPORT, THESIS) explicitly
  identifies at least one crocodile mummy / crocodile-containing mummy bundle / mummified
  crocodile part as held by that institution. For scholarly-only evidence the source must
  show the object is (or was, at the time of study) in that collection — e.g. it was
  examined, scanned, sampled there, or is cited with that museum's inventory number.
- `PROBABLE` — reliable (official or scholarly) evidence makes a holding highly likely
  but no individual object can be identified in current records: e.g. 19th/early-20th
  century catalogue or excavation report only (possible later loss/transfer), official
  text that mentions crocodile mummies only generically, Google Arts & Culture-only
  records, destroyed/merged/deaccessioned collections.
- `UNVERIFIED` — only candidate-only sources.

Absolute rules:
1. **Never fabricate.** Only record a URL you actually opened in this session. Only record
   values (inventory number, title, dimensions, provenance, date, species, licence,
   counts) that you read in a source. Otherwise write `UNKNOWN`.
2. **Do not infer** provenance, date, species, inventory number, image licence or number of
   crocodile mummies. "Kom Ombo" style provenance only if the source says so.
3. "The museum holds animal mummies" is **not** evidence of a crocodile mummy.
4. WebFetch summarises pages with a small model, which can hallucinate. Ask it to quote
   inventory numbers, titles, dimensions and provenance **verbatim**, and cross-check key
   values with a second fetch (e.g. `curl` of the JSON/HTML, or the API record) when
   possible. If a page is blocked (403/429), try WebFetch vs curl, an API or a portal; if
   still blocked, log it and record the institution in `leads` or `no_confirmation`
   (`DB_BLOCKED_OR_UNAVAILABLE`) — do not guess.
5. Print-only literature: cite fully (author, year, title, pages/cat. no.). Set
   `bibliography.access` honestly (FULL_TEXT / PARTIAL_TEXT / ABSTRACT / CITATION_ONLY).
   If you only know a citation second-hand, the object can be at most `PROBABLE`.

## 4. What counts as an object

Include ancient Egyptian (or stated-Egyptian) crocodile mummies of any size (adults,
juveniles, hatchlings, embryos), crocodile mummy bundles, mummified crocodile parts
(heads, tails, skulls explicitly described as mummified), and wrapped crocodile eggs.
Also record containers/coffins/masks made for crocodile mummies (class E).
Exclude: statues/amulets/reliefs of Sobek, un-mummified crocodile skeletons or bones not
described as mummified, modern taxidermy, casts/replicas (note replicas in `notes` only
if they could be confused with originals).

`classification` (with `classification_basis` stating what you relied on: photo,
description, CT study, title only…):
- `A` Whole / substantially complete crocodile mummy — head, body and tail largely
  present. For wrapped examples: externally complete crocodile form and no evidence that
  the contents are partial/composite.
- `B` Crocodile mummy bundle with crocodilian remains where the contents are known (CT,
  X-ray, description) to be partial, composite or multiple individuals, or a bundle not
  shaped as one crocodile that contains crocodile remains (e.g. bundle of hatchlings).
- `C` Largely unwrapped crocodile mummy (bandages mostly absent).
- `D` Partial crocodile mummy — only head, tail or another body part.
- `E` Container / coffin / mask only (not a crocodile mummy itself).
- `F` Uncertain — information insufficient (e.g. title "crocodile mummy" with no image or
  description). Also use F for wrapped eggs and for crocodile-shaped bundles shown to
  contain no crocodilian remains (pseudo-mummies) and say so in `notes`
  (`EGG` / `PSEUDO-MUMMY`).
Do not upgrade F to A without a photo or description that supports it.

`whole_or_partial`: WHOLE / PARTIAL / UNKNOWN. `wrapping_present`: YES / NO / PARTIAL /
UNKNOWN. `head_visible`, `dorsal_visible`, `tail_visible`: leave `UNKNOWN` in this round
(a separate image-audit pass will fill them) unless you actually looked at the image.

Record `inventory_number` exactly as the source prints it (including prefixes such as
"EA", "ÄM", "N", "E", "AMM", "Cat."); if none, `UNKNOWN`. Put alternative numbers in
`other_numbers`. If the same object appears in several places (museum DB, Europeana,
Google Arts & Culture, article, IIIF), record it **once**, list all URLs, and put the
other occurrences in `notes`/`bibliography`. If an object without inventory number might
be the same as another record, say so in `possible_duplicate_of` with the reason
(provenance, dimensions, description, photo, publication history).

## 5. Institution records

One `institutions` record per holding institution (CONFIRMED / PROBABLE / UNVERIFIED).
`country` = ISO 3166-1 alpha-2 (GB, FR, DE, IT, EG, US, VA …). `museum` = official
English name if the institution uses one, else the original name; put the original-
language name in `museum_original_name`. Separate museums of one university are separate
institutions. If an official/scholarly source gives a total number of crocodile mummies,
record it in `stated_count` with `stated_count_source`; do **not** create placeholder
object rows for unlisted individuals. `possible_additional_holdings` = what else is
suggested but not verified (with source). Record API/IIIF availability for the
institution (YES/NO/UNKNOWN + URL) and the image licence exactly as stated.

Institutions you checked where no crocodile mummy could be confirmed go to
`no_confirmation` with the `result_category`, what you searched (URLs, DB, query terms)
and limitations (e.g. "only ~5 % of the collection is online").

Candidate institutions you learn about but cannot check (outside your region, blocked,
print source unavailable) go to `leads` — this drives the snowball rounds, so be generous
with leads and precise about their source.

## 6. Search practice

- Log **every** query (web search, DB search, API call) in `search_log`, including
  zero-result ones. `result` = short factual outcome ("0 hits", "4 hits: 2 crocodile
  mummies EA 1, EA 2; 2 Sobek statues", "403 blocked").
- Languages: English, French, German, Italian, Spanish, Dutch, Arabic, plus the local
  language(s) of your region (Swedish, Danish, Norwegian, Finnish, Polish, Czech,
  Hungarian, Russian, Greek, Portuguese, Japanese, …). Core terms: crocodile mummy,
  mummified crocodile, crocodile animal mummy, crocodile mummy bundle, crocodilian mummy,
  momie de crocodile, crocodile momifié, Krokodilmumie, mumifiziertes Krokodil, mummia di
  coccodrillo, momia de cocodrilo, krokodillenmummie / mummie van een krokodil, مومياء
  تمساح / تمساح محنط, and local equivalents. In collection DBs also try single words
  ("crocodile", "Krokodil", "coccodrillo", "Crocodylus", "Sobek"/"Souchos"/"Suchos") —
  many records are titled only "Crocodile" with classification "animal mummy".
- Reverse lookup by place/deity: Sobek, Kom Ombo, Fayum/Fayyum, Tebtunis (Umm el-Breigat),
  Medinet Madi (Narmouthis), Manfalut / Maabda (Samoun) caves, Akoris (Tehna el-Gebel),
  Crocodilopolis / Shedet / Arsinoe (Medinet el-Fayum), Theadelphia, Soknopaiou Nesos,
  Kom Ombo, Gebelein, Esna, Qubbat al-Hawa, Hawara, Tuna el-Gebel, etc.
- Prefer official APIs and structured data. Use `curl` via Bash (an HTTPS proxy is
  configured; `requests` and bs4/lxml are installed) and WebSearch/WebFetch. Be polite to
  servers (≤ 1 request/s, no mass crawling).
- Snowball: bibliographies, catalogue entries, acknowledgements and inventory references
  in the literature you read are sources of new institutions and objects. Record them
  (`bibliography`, `leads`) and, if in your scope, check them in the official DB.

## 7. Final message to the orchestrator

Keep it under 400 words — the data is in the files. Include: counts of institutions by
confidence and of objects written; the most important leads outside your scope; blocked
or inaccessible resources; honest gaps remaining in your assignment; your saturation
evidence.
