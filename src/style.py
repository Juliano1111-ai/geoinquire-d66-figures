# =============================================================================
#  style.py — palette, fonts and chip primitives shared by every figure
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
"""Palette and drawing primitives. Reads no data and contains no rules."""

import matplotlib                                   # plotting root package
matplotlib.use('Agg')                               # render to files; no screen needed
import matplotlib.pyplot as plt                     # the plotting interface
from matplotlib.patches import FancyBboxPatch       # rounded rectangles for chips and cards

# ---- text and surfaces ------------------------------------------------------
INK = '#1a2e44'                                     # primary text (near-black)
MUTED = '#63748a'                                   # secondary text
FAINT = '#93a2b3'                                   # source and copyright lines
PAGE = '#f7f9fb'                                    # page background of the card figures
CARD = '#ffffff'                                    # face of an application card
RULE = '#d8e0e8'                                    # hairlines and card borders

# ---- the grey-and-green family and its annotation blues ---------------------
TIL_BLUE = '#2d6ca8'                                # card spine and resolved destinations
ROUTE_BLUE = '#3d7fbf'                              # a destination declared in R1-R3
ROUTE_DIRECT = '#7ea6cf'                            # a destination read from R4-R7 only
ROUTE_LOW = '#9aa8b6'                               # a destination inferred from R8/R9 only
DDSS_GREEN = '#2f7d4f'                              # the DDSS chip
CORE_PURP = '#6a5aa8'                               # the chip listing M1-M4
REPO_GREY = '#8892a4'                               # the M5 repository-track chip
PROVIS = '#c9622e'                                  # provisional M5 and repository-only
REPORT_UP = '#2f7d4f'                               # TA report holds evidence the ILM lacks
REPORT_OK = '#5e8f6f'                               # TA report on file

# ---- evidence grades --------------------------------------------------------
GRADE_GLYPH = {'DECLARED': '●',                # filled circle: named in R1-R3
               'DIRECT': '◐',                  # half circle: named in R4-R7
               'LINEAGE': '○',                 # open circle: R8/R9 inference only
               'NONE': ''}                          # no destination at any grade

# ---- the copyright line printed at the foot of every figure -----------------
COPYRIGHT = ('© 2026 University of Bergen for Geo-INQUIRE Deliverable D6.6. '  # owner and deliverable
             'Licence pending consortium agreement; reuse requires approval.')   # reuse condition

plt.rcParams.update({                               # one set of defaults for every figure
    'font.family': 'DejaVu Sans',                   # a font that carries the grade glyphs
    'text.color': INK,                              # default text colour
    'figure.dpi': 150,                              # screen resolution of the canvas
    'savefig.facecolor': PAGE,                      # saved files keep the page tone
})                                                  # end of the defaults


def chip(ax, x, y, w, h, text, *, face='none', edge=RULE, tcolor=INK,  # position, size, label, colours
         bold=True, size=6.6, lw=0.9, dashed=False):                   # weight, type size, outline
    """Draw one rounded label; every attribute on a card is one chip."""
    ax.add_patch(FancyBboxPatch(                    # the rounded outline
        (x, y), w, h,                               # lower-left corner and size
        boxstyle='round,pad=0.0,rounding_size=' + str(h * 0.45),  # corner radius scales with height
        facecolor=face, edgecolor=edge, linewidth=lw,             # fill and outline
        linestyle=(0, (2.4, 1.8)) if dashed else 'solid',         # dashed marks a provisional state
        zorder=3))                                  # above the card face
    ax.text(x + w / 2, y + h / 2, text,             # the label, centred in the chip
            ha='center', va='center',               # centred both ways
            fontsize=size,                          # type size in points
            weight='bold' if bold else 'normal',    # bold unless the chip is a quiet state
            color=tcolor, zorder=4)                 # label colour, above the outline


def code_chip(ax, x, y, w, h, codes_with_grades, *, size=6.6):  # the M1-M4 chip
    """Draw the core-handoff chip: each code preceded by its evidence glyph."""
    if not codes_with_grades:                       # no core code at all
        chip(ax, x, y, w, h, 'CORE: —', edge=RULE, tcolor=FAINT,  # an em dash, faint
             bold=False, size=size)                 # quiet weight
        return                                      # nothing else to draw
    label = 'CORE: ' + '  '.join(                   # e.g. "CORE: ●M1  ●M3"
        f'{GRADE_GLYPH.get(g, "")}{c}' for c, g in codes_with_grades)  # glyph then code
    chip(ax, x, y, w, h, label, edge=CORE_PURP, tcolor=CORE_PURP, size=size)  # purple outline


def report_chip(ax, x, y, w, h, label, *, size=6.6):  # the TA-report chip
    """Draw the TA-report chip; the report is a reference, it never moves a card."""
    lab = str(label)                                # the label computed in build_inputs.py
    if '→' in lab:                             # "REPORT → TIL n": report holds missing gates
        chip(ax, x, y, w, h, lab, face=REPORT_UP, edge=REPORT_UP,  # filled green
             tcolor='white', size=size)             # white text on the fill
    elif lab.startswith('REPORT ✓'):           # "REPORT ✓" or "REPORT ✓ + DOI"
        chip(ax, x, y, w, h, lab, edge=REPORT_OK, tcolor=REPORT_OK, size=size)  # green outline
    elif lab.startswith('NO REPORT'):               # no TA report found for the project
        chip(ax, x, y, w, h, lab, edge=FAINT, tcolor=FAINT, bold=False,  # faint
             size=size, dashed=True)                # dashed: an absence
    else:                                           # "REPORT: SAME LEVEL"
        chip(ax, x, y, w, h, lab, edge=RULE, tcolor=MUTED, bold=False, size=size)  # neutral


def card(ax, x, y, w, h, spine):                    # the white card behind a row of chips
    """Draw an application card with a coloured spine on its left edge."""
    ax.add_patch(FancyBboxPatch((x, y), w, h,       # the card body
                                boxstyle='round,pad=0.0,rounding_size=0.003',  # slight rounding
                                facecolor=CARD, edgecolor=RULE, lw=1.0, zorder=2))  # white, hairline
    ax.add_patch(FancyBboxPatch((x, y), 0.0038, h,  # the spine, 0.38 % of the page wide
                                boxstyle='square,pad=0',  # square ends
                                facecolor=spine, edgecolor='none', zorder=3))  # spine colour


def footer(ax, x_left, x_right, y, source, size=7.0):  # the two foot lines
    """Print one source line (left) and one copyright line (right)."""
    ax.text(x_left, y, source, fontsize=size, color=FAINT, va='top')  # source, left
    ax.text(x_right, y, COPYRIGHT, fontsize=size, color=FAINT,        # copyright, right
            va='top', ha='right')                   # right-aligned
