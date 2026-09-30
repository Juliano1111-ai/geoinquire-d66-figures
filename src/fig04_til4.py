# =============================================================================
#  fig04_til4.py — Figure 4: the applications at TIL 4, one card each
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
Input : data/derived/Figure_04_TIL4_input.csv   (written by build_inputs.py)
Output: figures/Figure_04_TIL4.png and .pdf

Each card: identity and destination on line 1; on line 2 the TA-report chip, the
DDSS package, the core codes M1-M4 with their evidence grade, and the M5 track.

Usage
  python fig04_til4.py --data ../data/derived/Figure_04_TIL4_input.csv --out ../figures
"""

import argparse                                     # command-line arguments
import os                                           # file paths

import matplotlib.pyplot as plt                     # the plotting interface
import pandas as pd                                 # tabular data

import style as S                                   # shared palette and chips

LAYOUT = dict(                                      # every geometric constant, in page units
    fig_w=17.0, fig_h=15.0,                         # canvas size in inches
    left=0.010, col_w=0.484, col_gap=0.012,         # left margin, column width, gap
    title_y=0.985, subtitle_y=0.958, legend_y=0.934,  # title block
    header_y=0.893, top=0.880,                      # column headings and first card
    card_h=0.0455, card_gap=0.0052,                 # card height and spacing
    id_drop=0.0100, chip_y=0.0075,                  # line 1 below the card top; chip row above its bottom
    chip=dict(gap=0.0042, h=0.0165,                 # chip spacing and height
              report=0.092, ddss=0.098, core=0.132, repo=0.100),  # chip widths
    fs=dict(title=17.5, subtitle=10.5, legend=8.6, header=11.0,  # type sizes
            identity=9.0, dest=8.6, chip=7.6, chip_small=7.2, foot=7.0))  # type sizes (continued)
DDSS_SHORT = {'Data product': 'DP', 'Data': 'D', 'Software': 'SW', 'Service': 'SV'}  # chip abbreviations
EMPTY = {'', 'nan', 'none', '—', '-', 'n.a.', 'na', 'n/a'}  # every spelling of an empty cell


def clean(v, default='—'):                     # a cell ready for printing
    """The cell as text, or `default` when it is empty."""
    s = str(v if v is not None else '').strip()      # the cell as text
    return default if s.lower() in EMPTY else s      # empty -> default


def short_ddss(labels):                             # "Data; Software" -> "D + SW"
    """The DDSS package abbreviated for a chip."""
    parts = [p.strip() for p in str(labels).split(';') if p.strip() and p.strip() != 'nan']  # the labels
    return ' + '.join(DDSS_SHORT.get(p, p) for p in parts) or 'Unknown'  # joined, or Unknown


def graded_codes(row):                              # [(code, grade), ...]
    """Each assigned code with the grade of the evidence behind it."""
    return [(c, row[f'{c} grade']) for c in ('M1', 'M2', 'M3', 'M4', 'M5')  # all five families
            if row[f'{c} grade'] not in ('NONE', '', 'nan')]  # only those assigned


def draw_legend(ax, y):                             # the legend strip under the subtitle
    """Two lines: the evidence glyphs, then the TA-report chip."""
    fs = LAYOUT['fs']['legend']                      # legend type size
    x = LAYOUT['left'] + 0.002                       # start at the left margin
    ax.text(x, y, 'Evidence behind each code:', fontsize=fs, weight='bold', va='center')  # heading
    x += 0.150                                       # first entry
    for grade, gloss, step in (('DECLARED', 'in R1–R3', 0.185),  # declared
                               ('DIRECT', 'in R4–R7, not a declaration', 0.240),  # direct
                               ('LINEAGE', 'R8/R9 inference only', 0.205)):  # lineage
        ax.text(x, y, f'{S.GRADE_GLYPH[grade]} {grade.title()}', fontsize=fs,  # glyph and name
                weight='bold', va='center')          # bold
        ax.text(x + 0.058, y, f'— {gloss}', fontsize=fs - 0.5, color=S.MUTED, va='center')  # gloss
        x += step                                    # next entry
    ax.text(x, y, 'Repository-only', fontsize=fs, weight='bold', color=S.PROVIS, va='center')  # non-family outcome
    ax.text(x + 0.083, y, '— no exposure leg', fontsize=fs - 0.5, color=S.MUTED, va='center')  # its gloss
    y2 = y - 0.017                                   # second legend line
    x = LAYOUT['left'] + 0.002                       # back to the margin
    ax.text(x, y2, 'TA report (reference):', fontsize=fs, weight='bold', va='center')  # heading
    ax.text(x + 0.150, y2, 'REPORT ✓ — report on file;  + DOI — it cites an SDL or '  # meaning
            'own repository DOI;  NO REPORT ON FILE — none found. The report never '  # text continues
            'changes the ILM level.', fontsize=fs - 0.5, color=S.MUTED, va='center')  # text continues


def draw_card(ax, x, y, w, h, number, row):         # one application
    """One card: identity and destination, then the chip row."""
    fs, C = LAYOUT['fs'], LAYOUT['chip']             # type sizes and chip widths
    repo_only = row['Non-family outcome'] == 'Repository-only'  # repository and no exposure leg
    S.card(ax, x, y, w, h, S.PROVIS if repo_only else S.TIL_BLUE)  # card with its spine
    twin = clean(row.get('Twin record folded in'), '')  # a duplicate ILM row folded into this one
    twin = f'  (+ {twin}, same project)' if twin else ''  # shown after the ID
    ax.text(x + 0.013, y + h - LAYOUT['id_drop'],    # line 1, left: identity
            f"{number:02d} · {clean(row['Project acronym'], 'Acronym not recorded')} "  # number and acronym
            f"— {row['Project ID']}{twin}",     # Project ID
            fontsize=fs['identity'], weight='bold', va='top')  # bold identity
    if repo_only:                                    # a repository is not an RI portfolio
        dest, col = 'repository (Zenodo)  —  not an RI portfolio', S.PROVIS  # say so
    else:                                            # node -> portfolio
        dest = (f"{clean(row['VA receiving node(s)'], 'node to confirm')}   →   "  # the node
                f"{clean(row['RI portfolio(s)'], 'portfolio to confirm')}")  # the portfolio
        col = S.TIL_BLUE                             # resolved-destination blue
    ax.text(x + w - 0.013, y + h - LAYOUT['id_drop'], dest, fontsize=fs['dest'],  # line 1, right
            weight='bold', color=col, va='top', ha='right')  # right-aligned
    cy, cx = y + LAYOUT['chip_y'], x + 0.013         # chip row origin
    S.report_chip(ax, cx, cy, C['report'], C['h'], row['Report chip'], size=fs['chip_small'])  # TA report
    cx += C['report'] + C['gap']                     # next chip
    S.chip(ax, cx, cy, C['ddss'], C['h'], 'DDSS: ' + short_ddss(row['DDSS labels']),  # DDSS package
           edge=S.DDSS_GREEN, tcolor=S.DDSS_GREEN, size=fs['chip'])  # green
    cx += C['ddss'] + C['gap']                       # next chip
    grades = graded_codes(row)                       # assigned codes
    if repo_only:                                    # no core code is supported
        S.chip(ax, cx, cy, C['core'], C['h'], 'CORE: none supported', edge=S.FAINT,  # say so
               tcolor=S.FAINT, bold=False, size=fs['chip'])  # quiet
    else:                                            # M1-M4 with glyphs
        S.code_chip(ax, cx, cy, C['core'], C['h'], [g for g in grades if g[0] != 'M5'], size=fs['chip'])  # style: size, colour, alignment
    cx += C['core'] + C['gap']                       # next chip
    if repo_only:                                    # repository-only marker
        S.chip(ax, cx, cy, C['repo'], C['h'], 'REPOSITORY-ONLY', face='#fdf1e8',  # pale orange
               edge=S.PROVIS, tcolor=S.PROVIS, size=fs['chip_small'])  # style: size, colour, alignment
    elif dict(grades).get('M5'):                     # an M5 candidate
        g5 = dict(grades)['M5']                      # its grade
        S.chip(ax, cx, cy, C['repo'], C['h'], f'{S.GRADE_GLYPH[g5]} M5 · DUAL-TRACK',  # dual track
               edge=S.REPO_GREY, tcolor=S.REPO_GREY, size=fs['chip_small'])  # style: size, colour, alignment
    else:                                            # no repository leg
        S.chip(ax, cx, cy, C['repo'], C['h'], 'no repository track', edge=S.RULE,  # quiet
               tcolor=S.FAINT, bold=False, size=fs['chip_small'])  # style: size, colour, alignment


def main():                                          # entry point: arguments, computation, drawing
    ap = argparse.ArgumentParser(description='Figure 4 — applications at TIL 4.')  # the parser
    ap.add_argument('--data', required=True)         # Figure_04_TIL4_input.csv
    ap.add_argument('--out', required=True)          # output folder
    a = ap.parse_args()                              # read the arguments
    os.makedirs(a.out, exist_ok=True)                # make the output folder
    d = pd.read_csv(a.data, dtype=str).fillna('')    # the input, all text
    port = {'EPOS': 0, 'ChEESE + EPOS': 1, 'EFEHR': 2}  # portfolio order
    node = {'SDL': 0, 'EIDA': 1, 'CREW': 2}          # node order
    d['_r'] = d['Non-family outcome'].eq('Repository-only')  # repository-only last
    d['_p'] = d['RI portfolio(s)'].map(port).fillna(9)  # portfolio rank
    d['_n'] = d['VA receiving node(s)'].map(node).fillna(8)  # node rank
    d = d.sort_values(['_r', '_p', '_n', 'Project ID']).reset_index(drop=True)  # reading order
    n, L, fs = len(d), LAYOUT, LAYOUT['fs']          # count and layout

    fig = plt.figure(figsize=(L['fig_w'], L['fig_h']))  # the canvas
    fig.patch.set_facecolor(S.PAGE)                  # page tone
    ax = fig.add_axes([0, 0, 1, 1])                  # one axis covering the page
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')  # page units, no frame
    ax.text(L['left'], L['title_y'], 'Figure 4. Applications at TIL 4: receiving nodes, '  # title
            'RI portfolios and candidate mechanisms', fontsize=fs['title'], weight='bold', va='top')  # text continues
    ax.text(L['left'], L['subtitle_y'], f'All {n} of the 68 executed TA projects that have a '  # subtitle
            'declared destination. A mechanism code is a candidate for assessment with the '  # text continues
            'receiver, not a completed integration.', fontsize=fs['subtitle'], color=S.MUTED, va='top')  # text continues
    draw_legend(ax, L['legend_y'])                   # the legend
    half = (n + 1) // 2                              # cards in the left column
    for k, label in ((0, f'Applications 01–{half}'), (1, f'Applications {half + 1}–{n}')):  # headings
        ax.text(L['left'] + k * (L['col_w'] + L['col_gap']) + 0.004, L['header_y'], label,  # placed
                fontsize=fs['header'], weight='bold', va='bottom')  # style: size, colour, alignment
    for i, row in d.iterrows():                      # every card
        col, k = (0, i) if i < half else (1, i - half)  # column and position in it
        x = L['left'] + col * (L['col_w'] + L['col_gap'])  # card x
        y = L['top'] - (k + 1) * (L['card_h'] + L['card_gap'])  # card y
        draw_card(ax, x, y, L['col_w'], L['card_h'], i + 1, row)  # draw it
    y_foot = L['top'] - half * (L['card_h'] + L['card_gap']) - 0.016  # below the last card
    S.footer(ax, L['left'], 1 - L['left'], y_foot,  # source and copyright
             'Source: TA_Individual_Applications, ILM of 29 September 2026, 68 executed projects '  # text continues
             'confirmed by the project office; TA reports as reference. Canonical ILM unchanged.',  # text continues
             size=fs['foot'])                        # style: size, colour, alignment
    y_min = y_foot - 0.018                           # crop the unused bottom of the canvas
    fig.set_size_inches(L['fig_w'], L['fig_h'] * (1 - y_min))  # shorter canvas
    ax.set_position([0, 0, 1, 1]); ax.set_ylim(y_min, 1)  # same drawing scale
    for ext in ('png', 'pdf'):                       # both formats
        fig.savefig(os.path.join(a.out, f'Figure_04_TIL4.{ext}'), dpi=180, facecolor=S.PAGE)  # write
    plt.close(fig)                                   # free memory
    print(f'  Figure_04_TIL4.png / .pdf  ({n} applications)')  # report


if __name__ == '__main__':                           # run as a script
    main()                                           # draw the figure
