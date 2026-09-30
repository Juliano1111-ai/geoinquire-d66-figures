# =============================================================================
#  fig05_below_til4.py — Figure 5: the applications below TIL 4, grouped by the
#                        control each one needs next
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
Input : data/derived/Figure_05_below_TIL4_input.csv   (written by build_inputs.py)
Output: figures/Figure_05_below_TIL4.png and .pdf

Cards are grouped by ILM level, highest first. The route chip gives the evidence
grade of the destination; the report chip gives the level the application would
reach if the ILM recorded what its TA report documents. The card never moves.

Usage
  python fig05_below_til4.py --data ../data/derived/Figure_05_below_TIL4_input.csv --out ../figures
"""

import argparse                                     # command-line arguments
import os                                           # file paths

import matplotlib.pyplot as plt                     # the plotting interface
import pandas as pd                                 # tabular data

import style as S                                   # shared palette and chips
from fig04_til4 import clean, short_ddss, graded_codes  # the same helpers as Figure 4

LAYOUT = dict(                                      # every geometric constant, in page units
    fig_w=17.0, fig_h=16.5,                         # canvas size in inches
    left=0.010, col_w=0.484, col_gap=0.012,         # left margin, column width, gap
    title_y=0.988, subtitle_y=0.966, legend_y=0.947,  # title block
    top=0.912,                                      # top of the first cohort
    card_h=0.0330, card_gap=0.0038, cohort_gap=0.0230,  # card, spacing, cohort heading room
    id_drop=0.0072, chip_y=0.0045,                  # line 1 below the card top; chip row above its bottom
    chip=dict(gap=0.0040, h=0.0125,                 # chip spacing and height
              route=0.068, ddss=0.088, core=0.112, repo=0.088, report=0.084),  # chip widths
    fs=dict(title=17.5, subtitle=10.5, legend=8.6, header=10.0,  # type sizes
            identity=8.2, dest=7.8, chip=7.0, chip_small=6.6, foot=7.0))  # type sizes (continued)
NEXT = {3: 'record a recognised destination pathway',  # the control each level needs next
        2: 'record outcome metadata and reuse terms',  # list continues
        1: 'record the units used or the end of the access',  # list continues
        0: 'record the Project Stage reached'}       # list continues
ROUTE_CHIP = {'DECLARED': ('● R1–R3 declared', S.ROUTE_BLUE),  # declared destination
              'DIRECT': ('◐ R4–R7 direct', S.ROUTE_DIRECT),    # canonical, not declared
              'LINEAGE': ('○ R8/R9 lineage', S.ROUTE_LOW),         # inferred only
              'NONE': ('no destination', S.FAINT)}                       # nothing at all


def draw_legend(ax, y):                             # the legend strip
    """Two lines: the evidence glyphs, then the TA-report chip."""
    fs = LAYOUT['fs']['legend']                      # legend type size
    x = LAYOUT['left'] + 0.002                       # left margin
    ax.text(x, y, 'Evidence behind each code:', fontsize=fs, weight='bold', va='center')  # heading
    x += 0.150                                       # first entry
    for grade, gloss, step in (('DECLARED', 'in R1–R3', 0.185),  # declared
                               ('DIRECT', 'in R4–R7, not a declaration', 0.240),  # direct
                               ('LINEAGE', 'R8/R9 inference only', 0.205)):  # lineage
        ax.text(x, y, f'{S.GRADE_GLYPH[grade]} {grade.title()}', fontsize=fs, weight='bold', va='center')  # glyph
        ax.text(x + 0.058, y, f'— {gloss}', fontsize=fs - 0.5, color=S.MUTED, va='center')  # gloss
        x += step                                    # next entry
    ax.text(x, y, 'M5 provisional', fontsize=fs, weight='bold', color=S.PROVIS, va='center')  # dashed M5
    ax.text(x + 0.078, y, '— exposure leg from lineage only', fontsize=fs - 0.5,  # its meaning
            color=S.MUTED, va='center')              # style: size, colour, alignment
    y2 = y - 0.014                                   # second line
    x = LAYOUT['left'] + 0.002                       # left margin
    ax.text(x, y2, 'TA report (reference):', fontsize=fs, weight='bold', va='center')  # heading
    ax.text(x + 0.150, y2, 'REPORT → TIL n — the TA report already documents the missing '  # meaning
            'gate(s); the ILM would reach TIL n once updated.  SAME LEVEL — the report adds no '  # text continues
            'gate.  The card stays at its ILM level.', fontsize=fs - 0.5, color=S.MUTED, va='center')  # text continues


def draw_card(ax, x, y, w, h, number, row):         # one application
    """One card: identity and destination, then five chips."""
    fs, C = LAYOUT['fs'], LAYOUT['chip']             # type sizes and chip widths
    grades = graded_codes(row)                       # assigned codes
    provisional = row['M5 leg status'] == 'provisional'  # M5 resting on lineage only
    S.card(ax, x, y, w, h, S.PROVIS if provisional else S.TIL_BLUE)  # card and spine
    twin = clean(row.get('Twin record folded in'), '')  # folded duplicate row
    twin = f'  (+ {twin}, same project)' if twin else ''  # shown after the ID
    ax.text(x + 0.013, y + h - LAYOUT['id_drop'],    # line 1, left
            f"{number:02d} · {clean(row['Project acronym'], 'Acronym not recorded')} "  # number, acronym
            f"— {row['Project ID']}{twin}", fontsize=fs['identity'], weight='bold', va='top')  # ID
    node = clean(row['VA receiving node(s)'], 'node to confirm')  # receiving node
    unresolved = node.lower().startswith(('node to', 'to confirm', 'not specified'))  # an open decision
    ax.text(x + w - 0.013, y + h - LAYOUT['id_drop'],  # line 1, right
            f"{node}   →   {clean(row['RI portfolio(s)'], 'portfolio to confirm')}",  # node -> portfolio
            fontsize=fs['dest'], weight='bold', va='top', ha='right',  # right-aligned
            color=S.MUTED if unresolved else S.TIL_BLUE)  # muted when unresolved
    cy, cx = y + LAYOUT['chip_y'], x + 0.013         # chip row origin
    text, colour = ROUTE_CHIP.get(row['Route evidence grade'], ROUTE_CHIP['NONE'])  # route chip
    S.chip(ax, cx, cy, C['route'], C['h'], text, edge=colour, tcolor=colour, size=fs['chip_small'])  # draw it
    cx += C['route'] + C['gap']                      # next chip
    S.chip(ax, cx, cy, C['ddss'], C['h'], 'DDSS: ' + short_ddss(row['DDSS labels']),  # DDSS package
           edge=S.DDSS_GREEN, tcolor=S.DDSS_GREEN, size=fs['chip'])  # style: size, colour, alignment
    cx += C['ddss'] + C['gap']                       # next chip
    if row['Non-family outcome'] == 'Unknown':       # an absence of evidence
        S.chip(ax, cx, cy, C['core'], C['h'], 'CORE: UNKNOWN', edge=S.FAINT,  # say so
               tcolor=S.FAINT, bold=False, size=fs['chip'])  # style: size, colour, alignment
    else:                                            # M1-M4 with glyphs
        S.code_chip(ax, cx, cy, C['core'], C['h'], [g for g in grades if g[0] != 'M5'], size=fs['chip'])  # style: size, colour, alignment
    cx += C['core'] + C['gap']                       # next chip
    if dict(grades).get('M5'):                       # an M5 candidate
        g5 = dict(grades)['M5']                      # its grade
        S.chip(ax, cx, cy, C['repo'], C['h'],        # dashed when provisional
               'M5 · PROVISIONAL' if provisional else f'{S.GRADE_GLYPH[g5]} M5 · DUAL-TRACK',  # text continues
               edge=S.PROVIS if provisional else S.REPO_GREY,  # outline: orange when provisional
               tcolor=S.PROVIS if provisional else S.REPO_GREY,  # style: size, colour, alignment
               dashed=provisional, size=fs['chip_small'])  # style: size, colour, alignment
    else:                                            # no repository leg
        S.chip(ax, cx, cy, C['repo'], C['h'], 'no repository track', edge=S.RULE,  # the "no repository track" chip
               tcolor=S.FAINT, bold=False, size=fs['chip_small'])  # style: size, colour, alignment
    cx += C['repo'] + C['gap']                       # last chip
    S.report_chip(ax, cx, cy, C['report'], C['h'], row['Report chip'], size=fs['chip_small'])  # TA report


def main():                                          # entry point: arguments, computation, drawing
    ap = argparse.ArgumentParser(description='Figure 5 — applications below TIL 4.')  # the parser
    ap.add_argument('--data', required=True)         # Figure_05_below_TIL4_input.csv
    ap.add_argument('--out', required=True)          # output folder
    a = ap.parse_args()                              # read the arguments
    os.makedirs(a.out, exist_ok=True)                # make the output folder
    d = pd.read_csv(a.data, dtype=str).fillna('')    # the input, all text
    d['TIL'] = d['TIL'].astype(int)                  # the level as a number
    d['Report-supported TIL'] = d['Report-supported TIL'].astype(int)  # the reference level
    d = d.sort_values(['TIL', 'Project ID'], ascending=[False, True]).reset_index(drop=True)  # queue order
    n, L, fs = len(d), LAYOUT, LAYOUT['fs']          # count and layout

    fig = plt.figure(figsize=(L['fig_w'], L['fig_h']))  # the canvas
    fig.patch.set_facecolor(S.PAGE)                  # page tone
    ax = fig.add_axes([0, 0, 1, 1])                  # one axis covering the page
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')  # page units, no frame
    ax.text(L['left'], L['title_y'], 'Figure 5. Applications below TIL 4: the pipeline, '  # title
            'grouped by the control required next', fontsize=fs['title'], weight='bold', va='top')  # text continues
    ax.text(L['left'], L['subtitle_y'], f'The other {n} of the 68 executed TA projects, grouped by '  # subtitle
            'the ILM level. An earlier level is a record still to be completed, not a failure.',  # text continues
            fontsize=fs['subtitle'], color=S.MUTED, va='top')  # style: size, colour, alignment
    draw_legend(ax, L['legend_y'])                   # the legend

    half = (n + 1) // 2                              # cards in the left column
    counter, bottoms, seen = 0, [], set()            # running number, column ends, headed levels
    for col, block in ((0, list(d.index)[:half]), (1, list(d.index)[half:])):  # two columns
        x, y, current = L['left'] + col * (L['col_w'] + L['col_gap']), L['top'], None  # column origin
        for idx in block:                            # each card in the column
            row = d.loc[idx]                         # its data
            if row['TIL'] != current:                # a new cohort starts
                y -= L['cohort_gap']                 # room for the heading
                lvl = row['TIL']                     # the level
                cohort = d[d.TIL == lvl]             # all cards at that level
                ahead = int((cohort['Report-supported TIL'] > lvl).sum())  # reports holding the gap
                cont = ' (continued)' if lvl in seen else ''  # a heading repeated in column 2
                ax.text(x + 0.004, y + 0.007, f'TIL {lvl}{cont} · {len(cohort)} · next: '  # heading
                        f'{NEXT[lvl]} — TA report holds it for {ahead}',  # text continues
                        fontsize=fs['header'], weight='bold', va='bottom')  # style: size, colour, alignment
                current = lvl; seen.add(lvl)         # remember it
            counter += 1                             # card number
            y -= L['card_h']                         # card position
            draw_card(ax, x, y, L['col_w'], L['card_h'], counter, row)  # draw it
            y -= L['card_gap']                       # spacing
        bottoms.append(y)                            # where the column ended
    y_foot = min(bottoms) - 0.016                    # below the longer column
    S.footer(ax, L['left'], 1 - L['left'], y_foot,  # source and copyright
             'Source: TA_Individual_Applications, ILM of 29 September 2026, 68 executed projects '  # text continues
             'confirmed by the project office; TA reports as reference. Canonical ILM unchanged.',  # text continues
             size=fs['foot'])                        # style: size, colour, alignment
    y_min = y_foot - 0.018                           # crop the unused bottom
    fig.set_size_inches(L['fig_w'], L['fig_h'] * (1 - y_min))  # shorter canvas
    ax.set_position([0, 0, 1, 1]); ax.set_ylim(y_min, 1)  # same drawing scale
    for ext in ('png', 'pdf'):                       # both formats
        fig.savefig(os.path.join(a.out, f'Figure_05_below_TIL4.{ext}'), dpi=180, facecolor=S.PAGE)  # write
    plt.close(fig)                                   # free memory
    print(f'  Figure_05_below_TIL4.png / .pdf  ({n} applications)')  # report


if __name__ == '__main__':                           # run as a script
    main()                                           # draw the figure
