# =============================================================================
#  fig06_two_witnesses.py — Figure 6: what the ILM and the TA reports establish
#                           together that neither establishes alone
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
Inputs: data/derived/executed_68.csv, data/derived/two_witness.csv   (build_inputs.py)
Output: figures/Figure_06_two_witnesses.png and .pdf

  a  for seven kinds of evidence, how many of the 68 projects have it in the ILM,
     in the TA report, in both, or in neither
  b  the TIL ladder from the ILM alone, and with the report as reference (not canonical)
  c  the projects whose report documents a gate the ILM has not recorded

Usage
  python fig06_two_witnesses.py --derived ../data/derived --out ../figures
"""

import argparse                                     # command-line arguments
import os                                           # file paths

import matplotlib                                   # plotting root package
matplotlib.use('Agg')                               # render to files
import matplotlib.pyplot as plt                     # the plotting interface
import pandas as pd                                 # tabular data
from matplotlib.patches import Patch               # legend swatches

INK, MUTED, FAINT, RULE, BG = '#12263a', '#6b7c8c', '#9aa8b4', '#dbe2e8', '#ffffff'  # text and surfaces
BOTH, ILM_ONLY = '#1f7346', '#7cc493'               # dark green: both; mid green: ILM only
REP_FACE, REP_EDGE = '#e4f2e8', '#2f7d4f'           # report only: pale green, hatched
NEITHER = '#e3e7eb'                                 # neither record: grey
ORDER = ['Access took place', 'Access completed', 'Output identifier (DOI or URL)',  # panel a rows
         'Reuse terms stated', 'RI destination named', 'Repository deposit', 'Units used recorded']  # evidence items (continued)
GATE_WORD = {1: 'stage', 2: 'access period', 3: 'output + terms', 4: 'destination'}  # what a report filled

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'text.color': INK,  # defaults
                     'axes.edgecolor': RULE, 'axes.labelcolor': MUTED,  # plot defaults (continued)
                     'xtick.color': MUTED, 'ytick.color': INK, 'hatch.linewidth': 0.6})  # plot defaults (continued)


def panel_title(ax, letter, text):                  # "a   What each record holds"
    """Left-aligned bold panel title."""
    ax.set_title(f'{letter}   {text}', loc='left', fontsize=11, weight='bold', pad=12)  # draw it


def filled_gates(r):                                # which gates the report supplies
    """Gates the ILM has not met but the report documents, up to the reference level."""
    b = lambda c: str(r[c]) == 'True'                # a stored flag as a boolean
    rep = {1: b('Report: access documented'),        # report: the access took place
           2: b('Report: access period ended'),      # report: the period is over
           3: (b('output_described') or b('Report: output identified')) and  # output described or identified
              (b('reuse_terms_stated') or b('Report: reuse terms stated')),  # and reuse terms, from either
           4: b('Report: RI destination named')}     # report: an RI destination
    names = [GATE_WORD[k] for k in range(1, int(r['Report-supported TIL']) + 1)  # gates up to the reference level
             if not b(f'g{k}') and rep[k]]           # unmet in the ILM, documented in the report
    return ' \u00b7 '.join(names)                    # e.g. "stage · access period"


def main():                                          # entry point: arguments, computation, drawing
    ap = argparse.ArgumentParser(description='Figure 6 — two witnesses.')  # the parser
    ap.add_argument('--derived', required=True)      # data/derived
    ap.add_argument('--out', required=True)          # output folder
    a = ap.parse_args()                              # read the arguments
    os.makedirs(a.out, exist_ok=True)                # make the output folder
    t = pd.read_csv(os.path.join(a.derived, 'executed_68.csv')).fillna('')  # one row per project
    w = pd.read_csv(os.path.join(a.derived, 'two_witness.csv'))  # project x evidence item
    n = len(t)                                       # 68

    fig = plt.figure(figsize=(16.5, 11.6), facecolor=BG)  # the canvas
    gs = fig.add_gridspec(2, 2, left=0.13, right=0.975, top=0.875, bottom=0.085,  # a and b on top, c below
                          wspace=0.34, hspace=0.52, width_ratios=[1.15, 1],  # panel a a little wider
                          height_ratios=[1, 1.25])   # c holds 15 rows
    fig.text(0.012, 0.975, 'Figure 6. Two witnesses: what the ILM and the TA reports establish together',  # title
             fontsize=16, weight='bold', va='top')   # style: size, colour, alignment
    fig.text(0.012, 0.945, f'The {n} executed TA projects. The ILM stays the canonical record; the TA '  # subtitle
             'report is read beside it and never replaces it.', fontsize=10.5, color=MUTED, va='top')  # text continues

    # ---- a: what each record holds -----------------------------------------------
    ax = fig.add_subplot(gs[0, 0])                   # top-left panel
    for i, item in enumerate(ORDER):                 # one bar per evidence item
        s = w[w.Item == item]                        # its 68 rows
        nofield = bool(s['Report has no field'].iloc[0])  # the report template has no such field
        seg = [('both', int((s.ILM & s.Report).sum()), dict(color=BOTH)),  # in both records
               ('ilm', int((s.ILM & ~s.Report).sum()), dict(color=ILM_ONLY)),  # ILM only
               ('rep', int((~s.ILM & s.Report).sum()), dict(color=REP_FACE, hatch='////',  # report only
                                                            edgecolor=REP_EDGE)),  # style: size, colour, alignment
               ('none', int((~s.ILM & ~s.Report).sum()), dict(color=NEITHER))]  # neither
        left = 0                                     # running start
        for key, k, style in seg:                    # each segment
            if not k:                                # empty
                continue                             # skip
            ax.barh(i, k, left=left, height=0.64, linewidth=0.8 if key == 'rep' else 0,  # the segment
                    **({'edgecolor': 'white'} | style))  # style: size, colour, alignment
            if k >= 3:                               # a count where there is room
                ax.text(left + k / 2, i, str(k), ha='center', va='center', fontsize=9, weight='bold',  # style: size, colour, alignment
                        color='white' if key == 'both' else INK)  # style: size, colour, alignment
            left += k                                # advance
        union = int((s.ILM | s.Report).sum())        # held by at least one record
        gain = union - int(s.ILM.sum())              # added by the report
        note = ('no field in the report template' if nofield else  # structural absence
                f'{union} of {n} together' + (f'  (+{gain} from reports)' if gain else ''))  # combined coverage
        ax.text(n + 1.2, i, note, va='center', fontsize=8.8,  # printed right of the bar
                color=MUTED, weight='normal' if nofield else 'bold')  # style: size, colour, alignment
    ax.set_yticks(range(len(ORDER)), ORDER); ax.invert_yaxis()  # item labels, top-down
    ax.set_xlim(0, n * 1.62); ax.set_xticks(range(0, n + 1, 10))  # room for the notes
    ax.set_xlabel(f'executed TA projects (n = {n})')  # axis label
    for sp in ('top', 'right', 'left'):              # recessive frame
        ax.spines[sp].set_visible(False)             # hide
    ax.tick_params(axis='y', length=0)               # no tick marks on categories
    ax.legend(handles=[Patch(color=BOTH, label='in both'),  # legend: four states
                       Patch(color=ILM_ONLY, label='ILM only'),  # legend entry
                       Patch(facecolor=REP_FACE, edgecolor=REP_EDGE, hatch='////', label='TA report only'),  # legend entry
                       Patch(color=NEITHER, label='in neither')],  # legend entry
              loc='lower center', bbox_to_anchor=(0.36, -0.24), ncol=4, frameon=False, fontsize=8.8)  # legend position below the panel
    panel_title(ax, 'a', 'What each record holds, item by item')  # title

    # ---- b: the ladder, ILM alone and with the report ----------------------------
    ax = fig.add_subplot(gs[0, 1])                   # top-right panel
    names = ['Implementation', 'Access', 'Content', 'Integration']  # the four gates
    ilm_r = [int((t.TIL >= L).sum()) for L in range(1, 5)]  # reached(L), ILM alone
    rep_r = [int((t['Report-supported TIL'] >= L).sum()) for L in range(1, 5)]  # with the report
    for i, (x0, x1) in enumerate(zip(ilm_r, rep_r)):  # one row per gate
        ax.plot([0, n], [i, i], color=RULE, lw=0.8, zorder=0)  # a light track 0..68
        if x1 > x0:                                  # the report adds projects
            ax.annotate('', xy=(x1 - 0.8, i), xytext=(x0 + 0.8, i),  # an arrow from ILM to combined
                        arrowprops=dict(arrowstyle='->', color=BOTH, lw=1.4, linestyle=(0, (3, 2))))  # dashed arrow style
        ax.scatter([x0], [i], s=150, color=BOTH, zorder=3)  # ILM alone: filled
        ax.scatter([x1], [i], s=150, facecolor='white', edgecolor=BOTH, linewidth=2, zorder=3)  # with report: hollow
        ax.text(x0 - 1.4, i + 0.26, str(x0), ha='right', va='center', fontsize=10, weight='bold')  # ILM value
        if x1 != x0:                                 # print the second value only when it differs
            ax.text(x1 + 1.4, i + 0.26, f'{x1}  (+{x1 - x0})', ha='left', va='center',  # combined value
                    fontsize=10, weight='bold', color=BOTH)  # style: size, colour, alignment
    ax.set_yticks(range(4), [f'TIL {k + 1}  {nm}' for k, nm in enumerate(names)])  # gate labels
    ax.invert_yaxis(); ax.set_xlim(0, n + 12); ax.set_ylim(3.6, -0.6)  # top-down, room for labels
    ax.set_xlabel(f'projects that have reached the level (n = {n})')  # axis label
    for sp in ('top', 'right', 'left'):              # recessive frame
        ax.spines[sp].set_visible(False)             # hide
    ax.tick_params(axis='y', length=0)               # no tick marks
    ax.legend(handles=[plt.Line2D([], [], marker='o', ls='', color=BOTH, ms=10, label='ILM alone (canonical)'),  # legend
                       plt.Line2D([], [], marker='o', ls='', mfc='white', mec=BOTH, mew=2, ms=10,  # legend entry
                                  label='ILM with the TA report as reference (not canonical)')],  # legend entry
              loc='lower center', bbox_to_anchor=(0.45, -0.30), ncol=1, frameon=False, fontsize=8.8)  # legend position below the panel
    panel_title(ax, 'b', 'The TIL ladder, reached(L)')  # title

    # ---- c: the projects whose report holds a missing gate -----------------------
    ax = fig.add_subplot(gs[1, :])                   # bottom panel, full width
    up = t[t['Report-supported TIL'] > t.TIL].copy() # the projects the report moves
    up = up.sort_values(['TIL', 'Report-supported TIL', 'Project acronym'],  # grouped by ILM level
                        ascending=[True, False, True]).reset_index(drop=True)  # sort order
    for i, r in up.iterrows():                       # one row per project
        x0, x1 = int(r.TIL), int(r['Report-supported TIL'])  # ILM level and reference level
        ax.plot([0, 4], [i, i], color=RULE, lw=0.6, zorder=0)  # a light track 0..4
        ax.annotate('', xy=(x1 - 0.09, i), xytext=(x0 + 0.09, i),  # the move
                    arrowprops=dict(arrowstyle='->', color=BOTH, lw=1.2, linestyle=(0, (3, 2))))  # dashed arrow style
        ax.scatter([x0], [i], s=70, color=BOTH, zorder=3)  # ILM level
        ax.scatter([x1], [i], s=70, facecolor='white', edgecolor=BOTH, linewidth=1.6, zorder=3)  # with report
        ax.text(4.2, i, filled_gates(r), va='center', fontsize=8.6, color=MUTED)  # what the report filled
    ax.set_yticks(range(len(up)), [f"{r['Project acronym']}  " for _, r in up.iterrows()], fontsize=8.6)  # names
    ax.invert_yaxis()                                # first row on top
    ax.set_xticks(range(5), [f'TIL {k}' for k in range(5)]); ax.set_xlim(-0.2, 6.2)  # levels, room for notes
    ax.set_xlabel('filled dot: ILM level  \u00b7  hollow dot: level with the report as reference  '  # reading key
                  '\u00b7  right: gates the ILM has not met that the report documents')  # text continues
    for sp in ('top', 'right', 'left'):              # recessive frame
        ax.spines[sp].set_visible(False)             # hide
    ax.tick_params(axis='y', length=0)               # no tick marks
    panel_title(ax, 'c', f'{len(up)} of {int((t.TIL < 4).sum())} projects below TIL 4: '  # title with counts
                         'the report documents what the ILM has not recorded')  # text continues

    fig.text(0.012, 0.018, 'Source: TA_Individual_Applications, ILM of 29 September 2026; 86 TA report '  # provenance
             'files (WP4, WP5, WP8). Levels with the report as reference (panels b and c) '  # text continues
             'are not canonical.', fontsize=7.2, color=FAINT, style='italic')  # text continues
    fig.text(0.988, 0.018, '© 2026 University of Bergen for Geo-INQUIRE Deliverable D6.6.',  # copyright
             fontsize=7.2, color=FAINT, ha='right')  # style: size, colour, alignment
    for ext in ('png', 'pdf'):                       # both formats
        fig.savefig(os.path.join(a.out, f'Figure_06_two_witnesses.{ext}'), dpi=200, facecolor=BG)  # write
    plt.close(fig)                                   # free memory
    print(f'  Figure_06_two_witnesses.png / .pdf  ({n} projects, {len(up)} moved by reports)')  # report


if __name__ == '__main__':                           # run as a script
    main()                                           # draw the figure
