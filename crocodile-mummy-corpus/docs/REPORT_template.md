# REPORT — Global Corpus of Ancient Egyptian Crocodile Mummies (round 1, partial)

**Status: partial corpus, not saturated.** The survey stopped early because the budget ran
out. See `NEXT_STEPS.md` for what remains. `scripts/stats.py` generates every number below
from the master CSVs. Evidence rules are in `work/AGENT_PROTOCOL.md`: no wiki sources,
nothing inferred, UNKNOWN where no source says otherwise.

## A. Holding institutions

- CONFIRMED: **{{N_INST_CONFIRMED}}** institutions in {{N_COUNTRIES_CONFIRMED}} countries.
- PROBABLE: **{{N_INST_PROBABLE}}**.
- UNVERIFIED: {{N_INST_UNVERIFIED}}.
- Checked without confirmation: {{N_NOCONF}} (`searched_no_confirmation.csv`).
- Logged queries: {{N_QUERIES}}. Open leads: {{N_LEADS_OPEN}} (`work/leads_status.csv`).

{{TABLE:region}}

By country:

{{TABLE:country}}

CONFIRMED institutions:

{{TABLE:confirmed_list}}

## B. Objects

- Object rows: {{N_OBJ}}. CONFIRMED **{{N_OBJ_CONFIRMED}}**, PROBABLE {{N_OBJ_PROBABLE}},
  UNVERIFIED {{N_OBJ_UNVERIFIED}}.
- **Minimum number of individually identified objects: {{N_OBJ_CONFIRMED}}** (CONFIRMED
  rows).
- Sum of `minimum_confirmed_objects`: **{{SUM_MIN_CONFIRMED}}**. For each institution
  this is the larger of two numbers: its CONFIRMED object rows, or a count stated by an
  official or scholarly source. In {{N_INST_STATED_EXCEEDS_ROWS}} institutions the stated
  count is higher than the rows.
- One row is one inventory entry. Some entries cover several individuals (for example a
  bundle of hatchlings, or a lot of reptiles); see `notes`.

{{TABLE:classification}}

- Rows with online images: {{N_OBJ_IMG}}. Of these, {{N_OBJ_IMG_CONFIRMED}} are CONFIRMED
  and {{N_OBJ_IMG_AB}} are class A/B.
- Rows with images under an open licence (public domain, CC0, CC BY, CC BY-SA):
  {{N_OBJ_OPEN_IMG}}.
- Parts observable in images. **The systematic image audit has not been done.** YES/NO is
  recorded only where an agent looked at the image; every other value is UNKNOWN.

| Part | YES | NO | UNKNOWN |
|---|---|---|---|
| Head | {{N_HEAD_YES}} | {{N_HEAD_NO}} | {{N_HEAD_UNKNOWN}} |
| Back (dorsal) | {{N_DORSAL_YES}} | {{N_DORSAL_NO}} | {{N_DORSAL_UNKNOWN}} |
| Tail | {{N_TAIL_YES}} | {{N_TAIL_NO}} | {{N_TAIL_UNKNOWN}} |

## C. Digital access

These lists cover CONFIRMED and PROBABLE institutions only. Institutions whose API or
IIIF status is UNKNOWN are left out.

API available ({{N_INST_API}}). The label says whether this is the institution's own API/JSON endpoint or only an aggregator's (Europeana, museum-digital, DigitaltMuseum, K-samsök, GBIF, DigitalNZ, Japan Search, Slovakiana, POP/Joconde). Endpoints are in `x_api_url`.
{{TABLE:api}}

IIIF available ({{N_INST_IIIF}}):
{{TABLE:iiif}}

Institutions with at least one object image under an open licence ({{N_INST_OPEN}}):
{{TABLE:open}}

## D. Literature

`bibliography.csv` has {{N_BIB}} works; the `access` column records whether the full text
was read. For the core literature and the works still unread, see
`work/agents/literature/summary.md` and `NEXT_STEPS.md` §1.

## E. Unresolved

PROBABLE institutions:

{{TABLE:probable}}

UNVERIFIED institutions:

{{TABLE:unverified}}

Institutions with no online database, or whose database was blocked, where a local enquiry
is needed:

{{TABLE:no_online_db}}

## F. Collections most useful for the wrapping study (head / back / tail / bands / colour / textile)

Ranked by the number of CONFIRMED class A/B objects with online images:

{{TABLE:useful}}

## Query languages (search_log)

{{TABLE:languages}}
