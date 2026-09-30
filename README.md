# Geo-INQUIRE D6.6 — figure code and inputs

This repository holds the code and data behind the data figures of Deliverable D6.6,
*Mechanisms for integration of TNA assets to VA*. D6.6 is part of Geo-INQUIRE
(Horizon Europe grant agreement No. 101058518), Work Package 6, Task 6.5, and was
written at the University of Bergen.

The deliverable describes how outputs of Trans-National Access (TA) can be
integrated into existing research-infrastructure (RI) portfolios through Virtual
Access (VA). It uses four instruments:

* **DDSS** — what the asset is: Data, Data product, Software or Service.
* **Routes** — where the asset is going. Nine detection rules are applied to the
  Implementation Level Matrix (ILM).
* **TIL** — how far the asset has progressed along a cumulative ladder:
  Implementation, Access, Content, Integration.
* **Mechanism families M1–M5** — the handoff the receiver would have to perform:
  ingestion, catalogue exposure, software deployment, service federation, or
  preservation plus separate exposure.

Every figure can be regenerated from two raw sources and five registers:

* The **Implementation Level Matrix (ILM)**, sheet `TA_Individual_Applications`,
  version of 29 September 2026. This is the canonical record and is never edited.
* The **TA reports** written by the hosts (86 files, WP4/WP5/WP8). They are read
  beside the ILM as a reference and never substituted for it.

Every source file carries a copyright header, a citation line and a comment on
each line of code.

## Figures

| Figure | Script | Section of D6.6 | What it shows |
|---|---|---|---|
| 1 | `src/fig01_overview.py` | 2.3 | How the 68 executed applications are typed (DDSS), routed and placed on the TIL ladder |
| 2 | — | 3.1 | A hand-drawn schematic; there is no script |
| 3 | `src/fig03_roadmap.py` | 3.1 | The road map: DDSS highways narrowing at the four TIL milestones |
| 4 | `src/fig04_til4.py` | 3.3 | The 31 applications at TIL 4: node, portfolio, DDSS, graded mechanism codes, report chip |
| 5 | `src/fig05_below_til4.py` | 3.3 | The 37 applications below TIL 4, grouped by the control required next |
| 6 | `src/fig06_two_witnesses.py` | 3.4 | The ILM and the TA reports read together: (a) item by item, (b) the TIL ladder, (c) the 15 applications the reports would move |

## Layout

```
src/
  style.py                 palette, fonts and chip primitives (no data, no rules)
  ilm.py                   ILM -> TIL gates, nine routes, primary DDSS
  reports.py               TA report text -> evidence per TIL gate
  mechanism.py             candidate mechanism families M1-M5 with evidence grades
  extract_report_text.py   PDF / DOCX / ODT -> plain text
  build_inputs.py          writes every table in data/derived/
  fig01_overview.py        Figure 1
  fig03_roadmap.py         Figure 3
  fig04_til4.py            Figure 4
  fig05_below_til4.py      Figure 5
  fig06_two_witnesses.py   Figure 6
  run_all.py               runs everything in order
data/
  raw/                     NOT redistributed (see "Data policy"); place the inputs here
  registers/               five hand-built registers, each row justified
  derived/                 the tables the figures read (committed so that figures can be redrawn without raw data)
figures/                   the figures, PNG and PDF
```

## Reproduce

Python 3.10 or later is required.

```bash
pip install -r requirements.txt

# Redraw the figures from the committed derived tables (no raw data needed)
cd src
python fig01_overview.py      --data ../data/derived/til_68.csv                    --out ../figures
python fig03_roadmap.py       --data ../data/derived/til_68.csv                    --out ../figures
python fig04_til4.py          --data ../data/derived/Figure_04_TIL4_input.csv      --out ../figures
python fig05_below_til4.py    --data ../data/derived/Figure_05_below_TIL4_input.csv --out ../figures
python fig06_two_witnesses.py --derived ../data/derived                            --out ../figures

# Rebuild everything from the raw ILM and TA reports (requires data/raw/)
cd ..
python src/run_all.py --ilm "data/raw/GeoINQUIRE-ImplementationLevelMatrix (11).xlsx" \
                      --reports "data/raw/All TA Reports-6" --asof 2026-09-29
```

The pipeline is deterministic. All ties are broken by vote count, then declared over
inferred, then alphabetically, so the outputs do not depend on `PYTHONHASHSEED`.

## Inputs

| File | Built by | Read by |
|---|---|---|
| `data/raw/<ILM>.xlsx` | the project (canonical) | `build_inputs.py` |
| `data/raw/All TA Reports-6/` | the TA hosts | `extract_report_text.py` |
| `data/registers/pmo_status.csv` | project-office statement, 16 Sep 2026 (5 cancelled, 2 duplicate rows) | `build_inputs.py` |
| `data/registers/report_map.csv` | reading each report: file -> Project ID, role | `build_inputs.py` |
| `data/registers/report_deposits.csv` | reading each report: own deposit, third-party citation or intention | `build_inputs.py` |
| `data/registers/ddss_register.csv` | multi-label DDSS, VA node and RI portfolio as published in August 2026 | `build_inputs.py` |
| `data/registers/evidence_overrides.csv` | ILM values not used as evidence, with the reason | `build_inputs.py` |
| `data/derived/til_68.csv` | `build_inputs.py` | Figures 1, 3 |
| `data/derived/Figure_04_TIL4_input.csv` | `build_inputs.py` | Figure 4 |
| `data/derived/Figure_05_below_TIL4_input.csv` | `build_inputs.py` | Figure 5 |
| `data/derived/executed_68.csv`, `two_witness.csv` | `build_inputs.py` | Figure 6 |

## Data policy

`data/raw/` is not redistributed. The ILM carries personal data (PI gender,
affiliations, contact e-mails), and the TA reports name individuals. The registers
and derived tables committed here hold no personal data. They identify each
application by its Project ID and acronym only.

## Known limits

* **DDSS, VA node and RI portfolio.** For each application these are taken from the
  register of the August 2026 figures (`ddss_register.csv`). The lexicon run that
  first produced them is not included.
* **The four M2 assignments.** They rest on the published basis column, because the
  catalogue-evidence field is not released.
* **Report evidence.** It is read by text patterns. Each repository deposit used as
  an M5 leg was checked by reading the report (`report_deposits.csv`).

## How to cite

Please cite the software and the deliverable (see also `CITATION.cff`):

> Ramanantsoa, H. J. D. (2026). *Geo-INQUIRE D6.6 figures and their inputs: integration
> of Trans-National Access assets into Virtual Access* (version 1.5). University of Bergen.

```bibtex
@software{ramanantsoa_2026_d66_figures,
  author  = {Ramanantsoa, Heriniaina Juliano Dani},
  title   = {Geo-INQUIRE D6.6 figures and their inputs: integration of
             Trans-National Access assets into Virtual Access},
  version = {1.5},
  year    = {2026},
  publisher = {University of Bergen},
  note    = {Geo-INQUIRE, Horizon Europe grant agreement No. 101058518, WP6 Task 6.5}
}
```

## Licence

The licence is pending agreement by the Geo-INQUIRE consortium; see `LICENSE.md`.
The proposal is EUPL-1.2 for code and CC-BY-4.0 for figures and tables.

## Acknowledgement

Geo-INQUIRE is funded by the European Union under grant agreement No. 101058518
(HORIZON-INFRA-2021-SERV-01). Views and opinions expressed are those of the authors
only and do not necessarily reflect those of the European Union or the European
Research Executive Agency.
