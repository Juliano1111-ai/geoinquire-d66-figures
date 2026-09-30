# =============================================================================
#  mechanism.py — the candidate mechanism families M1-M5, each graded by the
#                 strength of the destination evidence behind it
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
What the receiving infrastructure would have to do:
  M1  Data / Data product   take custody of the content
  M2  Data / Data product   catalogue metadata and a link (content stays put)
  M3  Software              deploy and operate it
  M4  Service               federate with it
  M5  repository preservation PLUS a separate M1-M4 exposure leg (never a DOI alone)
Two outcomes are not families: Repository-only (a repository leg and no exposure
leg) and Unknown (DDSS evidence insufficient).

Every code carries a grade: DECLARED (R1-R3), DIRECT (R4-R7), LINEAGE (R8/R9).
An M5 whose exposure leg is LINEAGE is provisional.
"""

import re                                           # regular expressions

REPOSITORIES = {'Zenodo'}                           # destinations that are repositories
CATALOGUE = re.compile(r'(?i)data\s*catalogue|catalogue\s*registration|metadata\s*harvest|'  # catalogue wording
                       r'metadata\s*integration|metadata\s*inventory|discovery\s*service')  # catalogue wording (continued)
GRADE_ROUTES = (('DECLARED', ('R1', 'R2', 'R3')),    # strongest: a declaration
                ('DIRECT', ('R4', 'R5', 'R6', 'R7')),  # canonical but not a declaration
                ('LINEAGE', ('R8', 'R9')))           # inference from co-occurrence


def _split(cell):                                   # "EPOS; SDL" -> {'EPOS', 'SDL'}
    """A route cell as a set of destination tokens."""
    s = str(cell or '').strip()                      # the cell as text
    if not s or s.lower() in ('nan', '—', '-', 'none'):  # every spelling of empty
        return set()                                 # nothing named
    return {p.strip() for p in re.split(r'[;,]', s) if p.strip()}  # the tokens


def grades(row, use_lineage=True, blocked_routes=()):  # destinations sorted by grade
    """Destinations per grade; routes in `blocked_routes` are not read."""
    out = {}                                         # grade -> set of destinations
    for grade, routes in GRADE_ROUTES:               # in order of strength
        if grade == 'LINEAGE' and not use_lineage:   # at TIL 4 lineage is not read
            out[grade] = set()                       # nothing at this grade
            continue                                 # next grade
        found = set()                                # destinations at this grade
        for r in routes:                             # each route of the grade
            if r not in blocked_routes:              # unless its value is overridden
                found |= _split(row.get(r))          # add what it names
        out[grade] = found                           # store
    return out                                       # e.g. {'DECLARED': {'SDL'}, ...}


def best_grade(g, repository):                       # strongest grade for one leg
    """Strongest grade at which a repository (True) or a non-repository (False) is named."""
    for grade in ('DECLARED', 'DIRECT', 'LINEAGE'):  # strongest first
        pool = g[grade]                              # destinations at that grade
        hit = (pool & REPOSITORIES) if repository else (pool - REPOSITORIES)  # the kind wanted
        if hit:                                      # found
            return grade                             # this is the grade
    return 'NONE'                                    # not named at any grade


def assign(row, ddss_labels, catalogue_text='', repository_from_report=False,  # one application
           use_lineage=True, blocked_routes=(), m2_published=False):  # continued from the line above
    """Candidate codes {code: grade} and the non-family outcome, if any."""
    labels = {p.strip() for p in str(ddss_labels or '').split(';') if p.strip()}  # the DDSS package
    if not labels or labels <= {'Unknown', 'unclassified'}:  # no bounded classification
        return {}, 'Unknown'                         # an absence of evidence
    g = grades(row, use_lineage, blocked_routes)     # destinations by grade
    exposure = best_grade(g, repository=False)       # grade of the exposure leg
    repo = best_grade(g, repository=True)            # grade of the repository leg
    if repo == 'NONE' and repository_from_report:    # no repository in the ILM routes
        repo = 'DIRECT'                              # a verified report deposit counts as canonical-level evidence
    codes = {}                                       # the result
    has_data = bool(labels & {'Data', 'Data product'})  # content to move or point to
    catalogues = bool(CATALOGUE.search(catalogue_text or '')) or m2_published  # catalogue evidence
    if has_data and catalogues and exposure != 'NONE':  # M2 before M1 for the same content
        codes['M2'] = exposure                       # catalogue exposure
    if has_data and 'M2' not in codes and exposure != 'NONE':  # otherwise ingestion
        codes['M1'] = exposure                       # managed ingestion
    if 'Software' in labels and exposure != 'NONE':  # a software component
        codes['M3'] = exposure                       # software deployment
    if 'Service' in labels and exposure != 'NONE':   # a service component
        codes['M4'] = exposure                       # service federation
    if repo != 'NONE':                               # a repository leg exists
        if exposure == 'NONE':                       # and no exposure leg at all
            return {}, 'Repository-only'             # evidence of an absence
        codes['M5'] = exposure                       # preservation plus exposure (LINEAGE = provisional)
    if not codes:                                    # nothing fired
        return {}, 'Unknown'                         # no bounded classification
    return codes, ''                                 # the candidate codes
