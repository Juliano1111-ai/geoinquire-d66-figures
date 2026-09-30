# Geo-INQUIRE D6.6 — Figure source code and calculations

**Supporting material for Geo-INQUIRE Deliverable D6.6, *Mechanisms for integration of TNA
assets to VA*.** D6.6 belongs to Work Package 6, Task 6.5, and was prepared at the
University of Bergen. Geo-INQUIRE is funded under Horizon Europe grant agreement
No. 101058518.

## Context

The Grant Agreement asks D6.6 for *"a description of the mechanisms by which the TNA
assets will be integrated into the existing RI portfolio of assets"*, structured by the
Data, Data product, Software and Services (DDSS) framework. D6.5 listed the assets that
Trans-National Access (TA) produced. D6.6 explains how those assets reach the research
infrastructures: through which Virtual Access (VA) installation, under what conditions,
and on what evidence.

D6.6 answers from the project's own records rather than from a survey.

* **Population.** The primary record is the sheet `TA_Individual_Applications` of the
  Implementation Level Matrix (ILM), version of 29 September 2026. The sheet has 75 rows
  across Calls 1–4. The Project Office confirmed on 16 September 2026 that five
  applications were cancelled and two rows duplicate a combined offer. That leaves
  68 executed applications. These corrections are applied through a register, and the
  ILM itself is never edited.
* **Four instruments.** Each of the 68 applications is placed on:
  * **DDSS**: what the asset is;
  * **Routes**: which VA installation and RI portfolio it is bound for, and how strongly
    the record supports that;
  * **TIL**: how far it has progressed (Implementation, Access, Content, Integration);
  * **Mechanism families M1–M5**: what the receiving infrastructure would have to do.
* **TA reports.** The 86 report files written by the TA hosts (WP4, WP5, WP8) are read
  beside the ILM as a second, independent witness (D6.6 Section 3.4, Figure 6). They
  confirm or add evidence and never change a TIL position.

The code is published so that the Project Office, the WP6 partners and reviewers can
regenerate every figure and number in D6.6. This works on the version of the ILM used
in the deliverable and on any later version.

## Figures

| Figure | Script | Section of D6.6 | What it shows |
|---|---|---|---|
| 1 | `src/fig01_overview.py` | 2.3 | How the 68 executed applications are typed (DDSS), routed and placed on the TIL ladder |
| 2 | — | 3.1 | A hand-drawn schematic; there is no script |
| 3 | `src/fig03_roadmap.py` | 3.1 | The road map: DDSS highways narrowing at the four TIL milestones |
| 4 | `src/fig04_til4.py` | 3.3 | The 31 applications at TIL 4: node, portfolio, DDSS, graded mechanism codes, report chip |
| 5 | `src/fig05_below_til4.py` | 3.3 | The 37 applications below TIL 4, grouped by the control required next |
| 6 | `src/fig06_two_witnesses.py` | 3.4 | The ILM and the TA reports read together: (a) item by item, (b) the TIL ladder, (c) the 15 applications the reports would move |

## What the code calculates

The rules below are the ones stated in D6.6 (Table 1 for TIL, Table 2 for the routes,
Table 4 for the mechanism families). ILM attributes are named, never given by column
letter.

1. **Population** (`ilm.py`, `data/registers/pmo_status.csv`). Rows listed as cancelled or
   duplicate are removed before anything else is computed, so they cast no vote in the
   lineage routes.
2. **TIL gates** (`ilm.py`). TIL is cumulative: an application sits at the level just
   below its first unmet gate.
   * Implementation: *Project Stage* has reached "Visit/access exhausted" or beyond.
   * Access: *Number of units used* > 0; or, where that count is blank, Implementation is
     met and *End of the Visit/Access* shows the period is over at the snapshot date
     (`--asof`).
   * Content: both *Metadata of the outcome* and *Level of access* carry a real
     statement. "Not yet available" or "to be determined" does not count.
   * Integration: a destination is declared in *Associated VA*, *Associated RI* or
     *Expected strategy of integration*.
3. **Routes R1–R9** (`ilm.py`).
   * R1–R3 read the three declaring attributes.
   * R4–R7 read *Actual link to asset produced*, *Metadata of the outcome*,
     *Delivered assets as outcomes* and *Expected assets as outcomes*.
   * R8 and R9 infer a destination by leave-one-out co-occurrence within the same TA
     host and the same work package.
   * The winning destination is the one with most votes. Ties go first to a declared
     destination over an inferred one, then alphabetically. Concordance is the number
     of routes that agree.
4. **DDSS** (`ilm.py`, `data/registers/ddss_register.csv`).
   * The primary class comes from lexicon scoring of *Short description of the
     activity*, *Expected assets as outcomes* and *Delivered assets as outcomes*.
   * The multi-label package, the VA node and the RI portfolio used for the mechanism
     families are read from the register of the published figures.
5. **Mechanism families** (`mechanism.py`).
   * Data or Data product gives M1, or M2 when there is catalogue evidence. Software
     gives M3; Service gives M4.
   * M5 requires a repository leg (Zenodo) **and** a separate exposure leg. A repository
     leg alone is reported as *Repository-only*, and missing DDSS evidence as *Unknown*.
   * Every code carries the grade of the route that supports it: declared (R1–R3),
     direct (R4–R7) or lineage (R8/R9). An M5 whose exposure leg rests on lineage is
     provisional.
6. **TA report evidence** (`extract_report_text.py`, `reports.py`,
   `data/registers/report_map.csv`, `report_deposits.csv`).
   * Each report is linked to its ILM application by the Project ID it prints.
   * Six items are read: access documented, access ended, output identifier, reuse
     terms, destination named, and repository deposit.
   * A deposit counts only when reading the report confirms it is the project's own.
   * The *report-supported TIL* is the level an application would reach if the ILM
     recorded what its report documents. It is shown for transparency and is not
     canonical.
7. **Figure inputs** (`build_inputs.py`). All of the above is combined into the tables in
   `data/derived/`, which the figure scripts read.

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

`data/raw/` is not redistributed, because the ILM carries personal data (PI gender,
affiliations, contact e-mails) and the TA reports name individuals.

The registers and derived tables identify each application by its Project ID, acronym,
TA host institution and report file name. Report file names are kept exactly as the
hosts submitted them, so that the pipeline can find each file. Two of them contain a
surname.

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
