# =============================================================================
#  build_inputs.py — build every table the figures read, from the ILM, the TA
#                    report text and the five registers
#
#  Geo-INQUIRE (Horizon Europe grant agreement No. 101058518)
#  WP6 Task 6.5 · Deliverable D6.6 "Mechanisms for integration of TNA assets to VA"
#
#  Copyright (c) 2026 University of Bergen, Department of Earth Science.
#  Author: Heriniaina Juliano Dani Ramanantsoa <heriniaina.j.ramanantsoa@uib.no>
#  ORCID:  https://orcid.org/0000-0003-0831-2802
#  Cite as: Ramanantsoa, H. J. D. (2026). Geo-INQUIRE D6.6 figures and their
#           inputs: integration of Trans-National Access assets into Virtual
#           Access (version 1.5). University of Bergen. See CITATION.cff.
#
#  SPDX-FileCopyrightText: 2026 University of Bergen
#  SPDX-License-Identifier: LicenseRef-GeoINQUIRE-Pending
#  Licence to be confirmed by the consortium (EUPL-1.2 proposed for code,
#  CC-BY-4.0 for figures). See LICENSE.md.
# =============================================================================
"""
Writes to data/derived/:
  til_68.csv                     TIL, routes and primary DDSS      -> Figures 1 and 3
  Figure_04_TIL4_input.csv       the 31 applications at TIL 4      -> Figure 4
  Figure_05_below_TIL4_input.csv the 37 applications below TIL 4   -> Figure 5
  two_witness.csv                ILM vs TA report, item by item    -> Figure 6
  executed_68.csv                everything above, one row per project

Usage
  python build_inputs.py --ilm data/raw/<ILM>.xlsx --txt data/raw/report_text \
                         --registers data/registers --asof 2026-09-29 --out data/derived
"""

import argparse                                     # command-line arguments
import os                                           # file paths

import pandas as pd                                 # tabular data

import ilm                                          # the canonical computation
import mechanism                                    # the M-code rules
import reports                                      # the TA report evidence

GLYPH = {'DECLARED': '●', 'DIRECT': '◐', 'LINEAGE': '○'}  # printed grade marks
GATE_NAME = {1: 'Implementation', 2: 'Access', 3: 'Content', 4: 'Integration'}  # level names


def read_registers(folder):                         # the five registers
    """Every register as a string table (blanks as '')."""
    rd = lambda n: pd.read_csv(os.path.join(folder, n), dtype=str).fillna('')  # one CSV
    return {k: rd(f'{k}.csv') for k in ('pmo_status', 'report_map', 'ddss_register',  # all five
                                       'report_deposits', 'evidence_overrides')}  # register names (continued)


def report_supported_til(r):                        # level with the report as reference
    """Level reached if each unmet ILM gate were filled from the report (not canonical)."""
    has = bool(r['Report on file'])                  # is there a report?
    g1 = r['g1'] or (has and r['Report: access documented'])        # access took place
    g2 = r['g2'] or (has and r['Report: access period ended'])      # access completed
    g3 = r['g3'] or (has and (r['output_described'] or r['Report: output identified'])  # output described
                     and (r['reuse_terms_stated'] or r['Report: reuse terms stated']))  # and reuse terms
    g4 = r['g4'] or (has and r['Report: RI destination named'])     # destination named
    level = 0                                        # start at 0
    for ok in (g1, g2, g3, g4):                      # gates in order
        if not ok:                                   # first unmet gate
            break                                    # stops the climb
        level += 1                                   # otherwise go up one
    return level                                     # 0..4


def report_chip(r):                                 # label of the report chip on a card
    """The TA-report chip label for Figures 4 and 5."""
    if not r['Report on file']:                      # no report found
        return 'NO REPORT ON FILE'                   # dashed chip
    if r['TIL'] == 4:                                # the TIL 4 cohort
        return 'REPORT ✓ + DOI' if r['Report: output identified'] else 'REPORT ✓'  # on file
    if r['Report-supported TIL'] > r['TIL']:         # the report holds missing gates
        return f"REPORT → TIL {r['Report-supported TIL']}"  # e.g. REPORT → TIL 4
    return 'REPORT: SAME LEVEL'                      # the report adds no gate


def main():                                          # entry point: arguments, computation, drawing
    ap = argparse.ArgumentParser(description='Build the figure inputs.')  # the parser
    ap.add_argument('--ilm', required=True)          # the ILM workbook
    ap.add_argument('--txt', required=True)          # folder of extracted report text
    ap.add_argument('--registers', required=True)    # folder of the five registers
    ap.add_argument('--asof', required=True)         # snapshot date, YYYY-MM-DD
    ap.add_argument('--out', required=True)          # output folder
    a = ap.parse_args()                              # read the arguments
    os.makedirs(a.out, exist_ok=True)                # make sure the output folder exists

    reg = read_registers(a.registers)                # the registers
    d = ilm.compute(a.ilm, a.asof, reg['pmo_status']['Project ID'])  # the 68 executed projects
    d.to_csv(os.path.join(a.out, 'til_68.csv'), index=False)  # input of Figures 1 and 3

    raw = ilm.read_sheet(a.ilm)                      # the raw sheet, for free-text attributes
    ev = reports.evidence(reg['report_map'], reg['report_deposits'], a.txt, a.asof)  # report evidence
    t = d.merge(ev, on='Project ID', how='left')     # ILM and report side by side
    for c in ev.columns:                             # fill projects without a report
        if ev[c].dtype == bool:                      # the yes/no evidence flags
            t[c] = t[c].eq(True)                     # absent report = False, no dtype warning
    t = t.fillna('')                                 # remaining blanks as ''

    dd = reg['ddss_register'].set_index('Project ID')  # DDSS package, node, portfolio
    t['DDSS labels'] = t['Project ID'].map(dd['DDSS labels'])  # multi-label DDSS
    t['VA receiving node(s)'] = t['Project ID'].map(dd['VA receiving node(s)'])  # node
    t['RI portfolio(s)'] = t['Project ID'].map(dd['RI portfolio(s)'])  # portfolio
    acr = raw.iloc[:, ilm.ATTR['Project acronym']].fillna('').astype(str).str.strip()  # ILM acronym
    t['Project acronym'] = [a_ if a_.lower() not in ('', 'nan', 'n.a.') else dd.loc[p, 'Project acronym (figure)']  # fallback
                            for p, a_ in zip(t['Project ID'], acr.loc[t['Project ID']])]  # per row
    pmo = reg['pmo_status']                          # the PMO register
    twin = {r['Retained record']: r['Project ID'] for _, r in pmo.iterrows() if r['Retained record']}  # folded rows
    t['Twin record folded in'] = t['Project ID'].map(twin).fillna('')  # shown on the card

    over = reg['evidence_overrides']                 # ILM values not used as evidence
    blocked = set(over.loc[over.Attribute == 'Actual link to asset produced', 'Project ID'])  # R4 blocked
    codes, outcome, repo_src = [], [], []            # results per row
    for _, r in t.iterrows():                        # each executed application
        catalogue = ' '.join(str(raw.loc[r['Project ID']].iloc[k]) for k in (19, 22, 23, 24, 25))  # text M2 reads
        routes = {c: r[c] for c in ('R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9')}  # the routes
        canon_repo = any('Zenodo' in str(routes[c]) for c in ('R1', 'R2', 'R3', 'R5', 'R6', 'R7')  # ILM Zenodo
                         ) or ('Zenodo' in str(routes['R4']) and r['Project ID'] not in blocked)  # R4 unless blocked
        report_repo = 'zenodo' in str(r['Report: own repository deposit']).lower()  # verified report deposit
        c, o = mechanism.assign(routes, r['DDSS labels'], catalogue,  # the rules
                                repository_from_report=report_repo and not canon_repo,  # report as fallback
                                use_lineage=(r['TIL'] < 4),  # lineage not read at TIL 4
                                blocked_routes=('R4',) if r['Project ID'] in blocked else (),  # override
                                m2_published=bool(dd.loc[r['Project ID'], 'M2 basis (published)']))  # published M2
        codes.append(c); outcome.append(o)           # keep codes and outcome
        repo_src.append('canonical (ILM)' if canon_repo else  # where the repository leg comes from
                        'secondary (TA report deposit)' if report_repo else 'none')  # source of the repository leg
    for code in ('M1', 'M2', 'M3', 'M4', 'M5'):      # one grade column per family
        t[f'{code} grade'] = [c.get(code, 'NONE') for c in codes]  # grade or NONE
    t['Codes'] = [' '.join(GLYPH[g] + k for k, g in sorted(c.items())) for c in codes]  # printable
    t['Non-family outcome'] = outcome                # Unknown / Repository-only / ''
    t['M5 leg status'] = ['provisional' if c.get('M5') == 'LINEAGE' else  # lineage exposure leg
                          'established' if 'M5' in c else 'not applicable' for c in codes]  # M5 status per row
    t['Repository leg source'] = repo_src            # canonical / secondary / none
    t['Route evidence grade'] = [mechanism.best_grade(mechanism.grades(r), repository=False)  # grade of the destination
                                 for _, r in t.iterrows()]  # one value per row
    t['Report-supported TIL'] = t.apply(report_supported_til, axis=1)  # reference level
    t['Report chip'] = t.apply(report_chip, axis=1)  # chip label

    link = raw.iloc[:, ilm.ATTR['Actual link to asset produced']].fillna('').astype(str)  # ILM link text
    t['ILM identifier'] = t['Project ID'].map(link.str.contains(r'10\.\d{4}|http'))  # a DOI or URL
    t['ILM repository'] = [any('Zenodo' in str(r[c]) for c in ('R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7'))  # Zenodo in ILM
                           for _, r in t.iterrows()] # one value per row
    t['ILM units recorded'] = t['units_recorded']    # units used: no field in the report template

    t.to_csv(os.path.join(a.out, 'executed_68.csv'), index=False)  # everything
    t[t.TIL == 4].to_csv(os.path.join(a.out, 'Figure_04_TIL4_input.csv'), index=False)  # Figure 4
    t[t.TIL < 4].to_csv(os.path.join(a.out, 'Figure_05_below_TIL4_input.csv'), index=False)  # Figure 5

    items = [('Access took place', 'g1', 'Report: access documented'),              # gate 1
             ('Access completed', 'g2', 'Report: access period ended'),             # gate 2
             ('Output identifier (DOI or URL)', 'ILM identifier', 'Report: output identified'),  # identifier
             ('Reuse terms stated', 'reuse_terms_stated', 'Report: reuse terms stated'),  # gate 3 part
             ('RI destination named', 'g4', 'Report: RI destination named'),        # gate 4
             ('Repository deposit', 'ILM repository', 'Report: own repository deposit'),  # M5 leg
             ('Units used recorded', 'ILM units recorded', None)]                   # ILM only
    rows = []                                        # long table: project x item
    for _, r in t.iterrows():                        # each project
        for label, ilm_col, rep_col in items:        # each evidence item
            i = bool(r[ilm_col])                     # the ILM holds it
            p = bool(r[rep_col]) if rep_col else False  # the report holds it
            rows.append({'Project ID': r['Project ID'], 'Item': label,  # identity
                         'ILM': i, 'Report': p,      # both witnesses
                         'Report has no field': rep_col is None})  # structural absence
    pd.DataFrame(rows).to_csv(os.path.join(a.out, 'two_witness.csv'), index=False)  # input of Figure 6
    print(f'  {len(t)} executed: {int((t.TIL == 4).sum())} at TIL 4, '  # a one-line summary
          f'{int((t.TIL < 4).sum())} below; {int(t["Report on file"].sum())} with a TA report')  # summary text


if __name__ == '__main__':                           # run as a script
    main()                                           # build everything
