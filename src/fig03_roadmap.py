# =============================================================================
#  fig03_roadmap.py — Figure 3: the integration mechanism drawn as a road map
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
Output: figures/Figure_03_roadmap.png and .pdf

Highway    = the primary DDSS class; its width is the number of assets still travelling.
Milestone  = a TIL gate; at each one a slip road carries the assets that stop there.
Exposure   = the destination reached by the assets that pass all four gates.
The analogy illustrates the figure only; it is not a definition of TIL.

Usage
  python fig03_roadmap.py --data ../data/derived/til_68.csv --out ../figures
"""

import argparse                                     # command-line arguments
import os                                           # file paths

import matplotlib                                   # plotting root package
matplotlib.use('Agg')                               # render to files
import matplotlib.pyplot as plt                     # the plotting interface
import numpy as np                                  # geometry
import pandas as pd                                 # tabular data
from matplotlib.patches import Circle, FancyBboxPatch  # milestone markers, road caps

INK, MUTED = '#12263a', '#6b7c8c'                   # primary and secondary text
RULE, BG, STOPPED = '#e6ecf0', '#fcfdfd', '#ccd3d9'  # milestone bands, page, stopped traffic
LANE_C = {'Data product': '#1f7346', 'Data': '#3d9c5d', 'Service': '#6fbb84',  # one green per highway
          'Software': '#a3d4b2', 'unclassified': '#c7ced4'}  # colours (continued)
DEST_C = {'SDL': '#0e3a22', 'EPOS': '#1f7346', 'EIDA': '#2f8a55', 'CREW': '#3e9a61', 'EFEHR': '#3d9c5d',  # greens for RI endpoints
          'EMSO': '#6fbb84', 'ECCSEL': '#a3d4b2', 'Zenodo': STOPPED}  # grey: not an RI portfolio
LANE_ORDER = ['Data product', 'Data', 'Service', 'Software', 'unclassified']  # top to bottom
MILESTONES = [(1, 'Implementation', 'has the access\ntaken place?'),  # gate, name, question
              (2, 'Access', 'was the allocation\nused?'),  # list continues
              (3, 'Content', 'is the output described,\nand are its terms stated?'),  # list continues
              (4, 'Integration', 'is a destination\ndeclared?')]  # list continues
SCALE, GAP = 0.056, 0.82                            # vertical units per asset; space between highways
XS = [0.0, 1.66, 3.32, 4.98, 6.64, 8.55]            # start, four milestones, terminus

plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': INK,  # defaults
                     'figure.dpi': 150, 'savefig.facecolor': BG})  # plot defaults (continued)


def smoothstep(t):                                  # an ease with zero slope at both ends
    """3t^2 - 2t^3: roads narrow like roads, not like wedges."""
    return t * t * (3.0 - 2.0 * t)                   # the ease


def road(ax, x0, x1, yc, w0, w1, colour):           # one stretch of highway
    """A band centred on yc narrowing from w0 to w1, with a pale highlight on top."""
    xs = np.linspace(x0, x1, 140)                    # dense x for a smooth edge
    half = (w0 + (w1 - w0) * smoothstep((xs - x0) / (x1 - x0))) / 2.0  # eased half-width
    top, bottom = yc + half, yc - half               # the two edges
    ax.fill_between(xs, bottom, top, facecolor=colour, edgecolor='white', linewidth=0.9, zorder=2)  # road
    ax.fill_between(xs, top - (top - bottom) * 0.20, top, facecolor='white',  # highlight on the top fifth
                    alpha=0.15, linewidth=0, zorder=2.1)  # style: size, colour, alignment


def slip_road(ax, xg, yc, w_road, flow, count):     # the exit at a milestone
    """Grey exit carrying the assets that stop at this gate; its width is their number."""
    if count <= 0:                                   # nobody stops here
        return                                       # nothing to draw
    w = max(flow, 0.050)                             # a floor so one asset still shows
    xs = np.linspace(xg, xg + 0.60, 80)              # 0.60 units long
    t = smoothstep((xs - xg) / 0.60)                 # eased progress
    edge = (yc - w_road / 2) - 0.52 * t              # peels off the road's underside
    taper = w * (1.0 - 0.34 * t)                     # narrows to two thirds as traffic disperses
    ax.fill_between(xs, edge - taper, edge, facecolor=STOPPED, edgecolor='white',  # the exit
                    linewidth=0.7, zorder=1)         # style: size, colour, alignment
    ax.text(xs[-1] + 0.09, edge[-1] - taper[-1] / 2, str(count), fontsize=9.2,  # how many stop
            weight='bold', color=MUTED, va='center', ha='left', zorder=4)  # style: size, colour, alignment


def ribbon(ax, x0, x1, y0t, y0b, y1t, y1b, colour):  # from a highway into a destination
    """A curved band keeping its thickness while it bends."""
    xs = np.linspace(x0, x1, 110)                    # dense x
    t = smoothstep((xs - x0) / (x1 - x0))            # eased progress
    ax.fill_between(xs, y0b + (y1b - y0b) * t, y0t + (y1t - y0t) * t,  # both edges follow the ease
                    facecolor=colour, alpha=0.55, linewidth=0, zorder=1)  # style: size, colour, alignment


def main():                                          # entry point: arguments, computation, drawing
    ap = argparse.ArgumentParser(description='Figure 3 — road map.')  # the parser
    ap.add_argument('--data', required=True)         # til_68.csv
    ap.add_argument('--out', required=True)          # output folder
    a = ap.parse_args()                              # read the arguments
    os.makedirs(a.out, exist_ok=True)                # make the output folder
    d = pd.read_csv(a.data).fillna('')               # one row per executed application
    n = len(d)                                       # 68
    lanes = [c for c in LANE_ORDER if c in set(d.DDSS)]  # highways present
    alive = {c: [int(((d.DDSS == c) & (d.TIL >= L)).sum()) for L in range(5)] for c in lanes}  # still travelling
    stop = {c: [int(((d.DDSS == c) & (d.TIL == L)).sum()) for L in range(5)] for c in lanes}   # stopping at L
    done = d[d.TIL == 4]                             # passed all four gates
    arrivals = pd.crosstab(done.DDSS, done.destination)  # class x destination

    fig, ax = plt.subplots(figsize=(17.4, 11.0))     # the canvas
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)  # page tone
    centres, cursor = {}, 0.0                        # highway centre lines, stacking cursor
    for c in lanes:                                  # stack highways downward, widest first
        h = max(alive[c][0] * SCALE, 0.30)           # the highway's starting width
        cursor -= h / 2 + GAP                        # move to its centre
        centres[c] = cursor                          # store
        cursor -= h / 2                              # move past it
    y_head, y_foot = 0.92, cursor - 1.30             # heading and question baselines

    for i in range(4):                               # milestone bands under the roads
        ax.axvspan(XS[i + 1] - 0.038, XS[i + 1] + 0.038, color=RULE, zorder=0)  # soft band

    for c in lanes:                                  # draw every highway
        yc, colour = centres[c], LANE_C[c]           # centre and colour
        w0 = max(alive[c][0] * SCALE, 0.05)          # starting width
        ax.add_patch(FancyBboxPatch((XS[0] - 0.11, yc - w0 / 2), 0.13, w0,  # rounded start cap
                                    boxstyle='round,pad=0,rounding_size=0.055',  # rounded corners
                                    facecolor=colour, edgecolor='white', lw=0.9, zorder=2))  # style: size, colour, alignment
        for i in range(4):                           # four stretches between gates
            ws = max(alive[c][i] * SCALE, 0.02)      # width entering the stretch
            we = max(alive[c][i + 1] * SCALE, 0.02)  # width leaving it
            road(ax, XS[i], XS[i + 1], yc, ws, we, colour)  # the stretch
            slip_road(ax, XS[i + 1], yc, we, stop[c][i] * SCALE, stop[c][i])  # who stops at the gate
            if ws > 0.17:                            # a count where the road is wide enough
                ax.text(XS[i] + 0.22, yc, str(alive[c][i]), fontsize=10.5, weight='bold',  # still travelling
                        va='center', zorder=5, color='white' if c in ('Data product', 'Data') else INK)  # style: size, colour, alignment
        if max(alive[c][4] * SCALE, 0.02) > 0.17:    # count after the last gate
            ax.text(XS[4] + 0.14, yc, str(alive[c][4]), fontsize=10.5, weight='bold',  # style: size, colour, alignment
                    va='center', zorder=5, color='white' if c in ('Data product', 'Data') else INK)  # style: size, colour, alignment
        ax.text(XS[0] - 0.32, yc + 0.14, c, fontsize=13, weight='bold', ha='right',  # highway name
                va='center', color=colour)           # style: size, colour, alignment
        ax.text(XS[0] - 0.32, yc - 0.18, f'{alive[c][0]} assets', fontsize=9, ha='right',  # its size
                va='center', color=MUTED)            # style: size, colour, alignment

    dests = list(arrivals.sum(axis=0).sort_values(ascending=False).index)  # largest destination first
    pos, filled, y = {}, {}, max(centres.values()) + 0.60  # node positions, fill level, cursor
    for dest in dests:                               # stack the destination nodes
        h = max(int(arrivals[dest].sum()) * SCALE, 0.30)  # node height
        y -= h / 2 + 0.66                            # move to its centre
        pos[dest], filled[dest] = (y, h), 0.0        # store
        y -= h / 2                                   # move past it
    for c in lanes:                                  # ribbons from highways to nodes
        if c not in arrivals.index:                  # nothing of this class arrives
            continue                                 # skip
        top = centres[c] + alive[c][4] * SCALE / 2   # pay out from the top of the road
        for dest in dests:                           # each destination
            v = int(arrivals.loc[c, dest]) if dest in arrivals.columns else 0  # arrivals
            if not v:                                # none
                continue                             # skip
            w = v * SCALE                            # ribbon thickness
            yd, hd = pos[dest]                       # node centre and height
            y1 = yd + hd / 2 - filled[dest]          # where the ribbon lands on the node
            ribbon(ax, XS[4], XS[5] - 0.36, top, top - w, y1, y1 - w, DEST_C.get(dest, STOPPED))  # draw
            filled[dest] += w; top -= w              # advance both cursors
    for dest in dests:                               # the nodes and their labels
        yd, hd = pos[dest]                           # centre and height
        ax.add_patch(FancyBboxPatch((XS[5] - 0.36, yd - hd / 2), 0.36, hd,  # rounded node
                                    boxstyle='round,pad=0,rounding_size=0.07',  # rounded corners
                                    facecolor=DEST_C.get(dest, STOPPED), edgecolor='white', lw=1.3, zorder=3))  # style: size, colour, alignment
        ax.text(XS[5] + 0.12, yd + 0.12, dest, fontsize=13.5, weight='bold', va='center')  # name
        note = ('open repository — not an RI portfolio' if dest == 'Zenodo' else  # what it is
                'an endpoint inside EPOS' if dest in ('SDL', 'EIDA', 'CREW') else 'research infrastructure')  # what the node is
        k = int(arrivals[dest].sum())                # assets arriving at this node
        ax.text(XS[5] + 0.12, yd - 0.20, f"{k} asset{'' if k == 1 else 's'}   \u00b7   {note}",  # count and note
                fontsize=9, va='center', color=MUTED)  # style: size, colour, alignment

    for i, (level, name, question) in enumerate(MILESTONES):  # milestone labels
        x = XS[i + 1]                                # gate position
        ax.add_patch(Circle((x, y_head + 0.32), 0.150, facecolor='white',  # numbered marker
                            edgecolor=INK, lw=1.4, zorder=6))  # style: size, colour, alignment
        ax.text(x, y_head + 0.32, str(level), fontsize=11, weight='bold',  # its number
                ha='center', va='center', zorder=7)  # style: size, colour, alignment
        ax.text(x, y_head + 0.66, name, fontsize=12.5, weight='bold', ha='center', va='bottom')  # its name
        ax.text(x, y_foot + 0.34, question, fontsize=9.2, color=MUTED, ha='center',  # its question
                va='top', linespacing=1.55)          # style: size, colour, alignment
        ax.text(x, y_foot - 0.26, f'{int((d.TIL >= level).sum())} travelling on',  # reached(L)
                fontsize=9.8, weight='bold', ha='center', va='top')  # style: size, colour, alignment
    ax.text(XS[0] - 0.11, y_head + 0.66, 'START', fontsize=12.5, weight='bold', ha='left', va='bottom')  # start
    ax.text(XS[0] - 0.11, y_head + 0.32, f'{n} TA applications', fontsize=9, color=MUTED,  # population
            ha='left', va='center')                  # style: size, colour, alignment
    ax.text(XS[5] - 0.36, y_head + 0.66, 'Exposure', fontsize=12.5, weight='bold',  # terminus
            ha='left', va='bottom')                  # style: size, colour, alignment
    ax.text(XS[5] - 0.36, y_head + 0.32, f'{len(done)} assets with a declared destination',  # TIL 4 count
            fontsize=9, color=MUTED, ha='left', va='center')  # style: size, colour, alignment
    key_y = y_foot - 1.12                            # the key sits below the questions
    xs = np.linspace(XS[0] - 0.06, XS[0] + 0.46, 44)  # a short sample slip road
    t = smoothstep((xs - xs[0]) / (xs[-1] - xs[0]))  # eased
    edge = key_y - 0.17 * t                          # its upper edge
    ax.fill_between(xs, edge - 0.078 * (1.0 - 0.34 * t), edge, facecolor=STOPPED,  # the sample
                    edgecolor='white', linewidth=0.7)  # style: size, colour, alignment
    ax.text(XS[0] + 0.62, key_y - 0.13,              # its meaning
            'a slip road  —  assets that stop at this milestone and travel no further',  # text continues
            fontsize=9.6, color=MUTED, va='center')  # style: size, colour, alignment
    ax.set_xlim(XS[0] - 1.40, XS[5] + 2.05)          # horizontal extent
    ax.set_ylim(key_y - 1.62, y_head + 2.22)         # vertical extent
    ax.axis('off')                                   # no frame
    for ext in ('png', 'pdf'):                       # both formats
        fig.savefig(os.path.join(a.out, f'Figure_03_roadmap.{ext}'), dpi=200,  # write
                    bbox_inches='tight', facecolor=BG)  # style: size, colour, alignment
    plt.close(fig)                                   # free memory
    print(f'  Figure_03_roadmap.png / .pdf  ({n} applications)')  # report


if __name__ == '__main__':                           # run as a script
    main()                                           # draw the figure
