# =============================================================================
#  fig01_overview.py — Figure 1: how a TA asset is typed, routed and placed on
#                      the TIL ladder (four panels)
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
Input : data/derived/til_68.csv   (written by build_inputs.py)
Output: figures/Figure_01_overview.png and .pdf

  a  the nine routes: applications for which each route names a destination
  b  applications at each TIL level (exclusive), by call
  c  the destination each primary DDSS class is bound for
  d  share of each class for which each route fires, and its mean concordance

Usage
  python fig01_overview.py --data ../data/derived/til_68.csv --out ../figures
"""

import argparse                                     # command-line arguments
import os                                           # file paths

import matplotlib                                   # plotting root package
matplotlib.use('Agg')                               # render to files
import matplotlib.pyplot as plt                     # the plotting interface
import numpy as np                                  # arrays
import pandas as pd                                 # tabular data
from matplotlib.colors import LinearSegmentedColormap  # the single green ramp

INK, MUTED, FAINT, RULE, BG = '#12263a', '#6b7c8c', '#9aa8b4', '#dbe2e8', '#ffffff'  # text and surfaces
GREENS = LinearSegmentedColormap.from_list('til_greens', [  # one sequential ramp, light to dark
    '#f1f8f3', '#d9efde', '#a9d7b4', '#71be84', '#41a05f', '#237c46', '#103f24'])  # colours (continued)
DEST_COL = {'SDL': '#103f24', 'EPOS': '#1f7346', 'EIDA': '#2f8a55', 'CREW': '#3e9a61',  # RI endpoints: greens
            'EFEHR': '#41a05f', 'EMSO': '#71be84', 'ECCSEL': '#a9d7b4', 'ChEESE': '#c6e6cf',  # colours (continued)
            'Zenodo': '#c9cfd4'}                    # a repository: grey, not an RI
CLASSES = ['Data', 'Data product', 'Software', 'Service', 'unclassified']  # DDSS rows, fixed order
ROUTES = [('R1', 'Declared installation'), ('R2', 'Declared infrastructure'),  # route codes and names
          ('R3', 'Declared strategy'), ('R4', 'Asset location'), ('R5', 'Metadata citation'),  # list continues
          ('R6', 'Delivered asset'), ('R7', 'Expected asset'), ('R8', 'Host lineage'),  # list continues
          ('R9', 'Work-package lineage')]            # list continues
LEVELS = ['TIL 0\nNot recorded', 'TIL 1\nImplementation', 'TIL 2\nAccess',  # column labels of panel b
          'TIL 3\nContent', 'TIL 4\nIntegration']    # level labels (continued)

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'text.color': INK,  # defaults
                     'axes.edgecolor': RULE, 'axes.labelcolor': MUTED,  # plot defaults (continued)
                     'xtick.color': MUTED, 'ytick.color': INK})  # plot defaults (continued)


def panel_title(ax, letter, text):                  # "a   The nine routes"
    """Left-aligned bold panel title."""
    ax.set_title(f'{letter}   {text}', loc='left', fontsize=10.5, weight='bold', pad=14)  # draw it


def quiet(ax, keep_bottom=True):                    # recessive axes
    """Hide the frame except, optionally, the baseline."""
    for s in ('top', 'right', 'left') + (() if keep_bottom else ('bottom',)):  # sides to hide
        ax.spines[s].set_visible(False)             # hide
    ax.tick_params(axis='y', length=0)               # no tick marks on the category axis


def main():                                          # entry point: arguments, computation, drawing
    ap = argparse.ArgumentParser(description='Figure 1 — overview.')  # the parser
    ap.add_argument('--data', required=True)         # til_68.csv
    ap.add_argument('--out', required=True)          # output folder
    a = ap.parse_args()                              # read the arguments
    os.makedirs(a.out, exist_ok=True)                # make the output folder
    d = pd.read_csv(a.data).fillna('')               # one row per executed application
    n = len(d)                                       # 68
    fires = {c: int((d[c].astype(str).str.strip() != '').sum()) for c, _ in ROUTES}  # applications per route

    fig = plt.figure(figsize=(14, 10.2), facecolor=BG)  # the canvas
    gs = fig.add_gridspec(2, 2, left=0.17, right=0.91, top=0.9, bottom=0.1,  # 2 x 2 grid
                          wspace=0.42, hspace=0.42)  # spacing between panels
    fig.suptitle('How a TA asset is typed, routed, and placed on the TIL ladder',  # figure title
                 fontsize=12.5, weight='bold', y=0.965)  # style: size, colour, alignment

    # ---- a: the nine routes ------------------------------------------------------
    ax = fig.add_subplot(gs[0, 0])                   # top-left panel
    order = sorted(ROUTES, key=lambda r: fires[r[0]])  # shortest bar at the bottom
    vals = [fires[c] for c, _ in order]              # the counts in that order
    ax.barh(range(len(order)), vals, height=0.68,    # horizontal bars
            color=[GREENS(0.35 + 0.6 * v / max(vals)) for v in vals])  # darker = more
    ax.set_yticks(range(len(order)), [f'{c}  {nm}' for c, nm in order])  # route labels
    for i, v in enumerate(vals):                     # a value on every bar
        inside = v > 0.55 * max(vals)                # long bars carry it inside
        ax.text(v - 1 if inside else v + 1, i, str(v), va='center',  # the count
                ha='right' if inside else 'left', weight='bold',  # style: size, colour, alignment
                color='white' if inside else INK)    # style: size, colour, alignment
        ax.text(n * 1.22, i, f'{round(100 * v / n)}%', va='center', color=MUTED)  # share of n
    ax.set_xlim(0, n * 1.3)                          # room for the shares
    ax.set_xlabel(f'applications naming a destination   ·   n = {n}')  # axis label
    quiet(ax)                                        # recessive frame
    ax.grid(axis='x', color=RULE, lw=0.6); ax.set_axisbelow(True)  # light grid behind bars
    panel_title(ax, 'a', 'The nine routes')          # panel title

    # ---- b: applications at each level, by call ----------------------------------
    ax = fig.add_subplot(gs[0, 1])                   # top-right panel
    m = pd.crosstab(d.Call, d.TIL).reindex(columns=range(5), fill_value=0)  # call x level
    v = m.values                                     # as an array
    ax.imshow(v, cmap=GREENS, vmin=0, vmax=max(1, v.max()), aspect='auto')  # heatmap
    for i in range(v.shape[0]):                      # each call
        for j in range(5):                           # each level
            if v[i, j]:                              # print non-zero cells only
                ax.text(j, i, str(v[i, j]), ha='center', va='center', weight='bold',  # the count
                        color='white' if v[i, j] > 0.55 * v.max() else INK)  # style: size, colour, alignment
    for j in range(5):                               # column totals above the grid
        ax.text(j, -0.75, str(int(v[:, j].sum())), ha='center', va='center', weight='bold')  # at(L)
    ax.text(-0.85, -0.75, 'n', ha='center', va='center', color=MUTED)  # label for the totals row
    ax.set_xticks(range(5), LEVELS, fontsize=7.6, color=MUTED)  # level names
    ax.set_yticks(range(len(m)), [f'{c}   {int(r.sum())}' for c, r in zip(m.index, v)])  # call and size
    ax.set_xticks(np.arange(-0.5, 5), minor=True)    # cell edges
    ax.set_yticks(np.arange(-0.5, len(m)), minor=True)  # cell edges
    ax.grid(which='minor', color='white', lw=2.5); ax.tick_params(which='both', length=0)  # white gutters
    for s in ax.spines.values():                     # no frame
        s.set_visible(False)                         # hide
    ax.set_ylim(len(m) - 0.5, -1.1)                  # room for the totals row
    panel_title(ax, 'b', 'Applications sitting at each level  ·  exclusive at(L)')  # title

    # ---- c: destinations per DDSS class -----------------------------------------
    ax = fig.add_subplot(gs[1, 0])                   # bottom-left panel
    dests = [x for x in DEST_COL if x in set(d.destination)]  # destinations present, fixed order
    classes = [c for c in CLASSES if c in set(d.DDSS)]  # classes present, fixed order
    for i, c in enumerate(classes):                  # one stacked bar per class
        sub = d[d.DDSS == c]                         # applications of that class
        left = 0                                     # running start of the next segment
        for dd in dests:                             # one segment per destination
            k = int((sub.destination == dd).sum())   # applications bound there
            if k:                                    # draw non-empty segments only
                ax.barh(i, k, left=left, color=DEST_COL[dd], height=0.62,  # the segment
                        edgecolor='white', lw=0.6)   # white gap between segments
                if k >= 4:                           # label only segments wide enough
                    ax.text(left + k / 2, i, str(k), ha='center', va='center', weight='bold',  # style: size, colour, alignment
                            color='white' if dd in ('SDL', 'EPOS', 'EIDA', 'CREW', 'EFEHR') else INK)  # style: size, colour, alignment
                left += k                            # advance
        kinds = sub.destination[sub.destination != ''].nunique()  # distinct destinations
        ax.text(len(sub) + 1.2, i, f'{len(sub)}  ·  {kinds} of {len(dests)}',  # size and reach
                va='center', color=MUTED)            # style: size, colour, alignment
    ax.set_yticks(range(len(classes)), classes); ax.invert_yaxis()  # class labels, top-down
    ax.set_xlim(0, max(d.DDSS.value_counts()) * 1.3)  # room for the annotation
    ax.set_xlabel('applications')                    # axis label
    quiet(ax)                                        # recessive frame
    ax.grid(axis='x', color=RULE, lw=0.6); ax.set_axisbelow(True)  # light grid
    panel_title(ax, 'c', 'The highway  ·  destinations the asset type allows')  # title

    # ---- d: routes firing per class ---------------------------------------------
    ax = fig.add_subplot(gs[1, 1])                   # bottom-right panel
    pct = np.array([[100 * (d[d.DDSS == c][r].astype(str).str.strip() != '').mean()  # % firing
                     for r, _ in ROUTES] for c in classes])  # class x route
    ax.imshow(pct, cmap=GREENS, vmin=0, vmax=100, aspect='auto')  # heatmap 0-100 %
    for i in range(pct.shape[0]):                    # each class
        for j in range(pct.shape[1]):                # each route
            p = pct[i, j]                            # the share
            ax.text(j, i, f'{p:.0f}' if p > 0 else '·', ha='center', va='center',  # value or dot
                    color='white' if p > 60 else (INK if p > 0 else FAINT), fontsize=8.8)  # style: size, colour, alignment
        mc = d[d.DDSS == classes[i]].concordance.mean()  # mean routes agreeing
        ax.text(9.1, i, f'{mc:.1f}/9', va='center', weight='bold', color='#237c46')  # printed right
    ax.text(9.35, -0.9, 'mean\nagree', ha='center', va='center', color='#237c46', fontsize=8.5)  # its header
    ax.set_xticks(range(9), [r for r, _ in ROUTES])  # route codes
    ax.set_yticks(range(len(classes)), classes)      # class labels
    ax.set_xticks(np.arange(-0.5, 9), minor=True)    # cell edges
    ax.set_yticks(np.arange(-0.5, len(classes)), minor=True)  # cell edges
    ax.grid(which='minor', color='white', lw=2.5); ax.tick_params(which='both', length=0)  # gutters
    for s in ax.spines.values():                     # no frame
        s.set_visible(False)                         # hide
    ax.set_xlim(-0.5, 8.5)                           # exactly nine columns
    panel_title(ax, 'd', 'The main road  ·  routes firing per class (%)')  # title

    # ---- one legend, one source line --------------------------------------------
    handles = [plt.Rectangle((0, 0), 1, 1, color=DEST_COL[x]) for x in dests]  # swatches
    fig.legend(handles, dests, loc='lower center', ncol=len(dests), frameon=False,  # one row
               bbox_to_anchor=(0.56, 0.015), fontsize=9)  # legend position below the panel
    fig.text(0.02, 0.005, f'Source: TA_Individual_Applications, ILM of 29 September 2026; '  # provenance
             f'the {n} TA projects the project office confirms as executed.',  # text continues
             fontsize=7, color=FAINT, style='italic')  # style: size, colour, alignment
    for ext in ('png', 'pdf'):                       # both formats
        fig.savefig(os.path.join(a.out, f'Figure_01_overview.{ext}'), dpi=200, facecolor=BG)  # write
    plt.close(fig)                                   # free memory
    print(f'  Figure_01_overview.png / .pdf  ({n} applications)')  # report


if __name__ == '__main__':                           # run as a script
    main()                                           # draw the figure
