# =============================================================================
#  ilm.py — read TA_Individual_Applications and compute TIL, the nine routes
#           and the primary DDSS class for every executed application
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
The ILM is the canonical record. Nothing here edits it. Rows the project office
lists as cancelled or duplicated (data/registers/pmo_status.csv) are removed before
any route is computed, so they cast no vote in the two lineage routes.

TIL is cumulative: an application sits at the level below its first unmet gate.
  1 Implementation  Project Stage has reached "Visit/access exhausted" or beyond
  2 Access          Number of units used > 0, or the access period is over
  3 Content         Metadata of the outcome AND Level of access carry a statement
  4 Integration     a destination is declared in Associated VA, Associated RI or
                    Expected strategy of integration
"""

import re                                           # regular expressions
from collections import Counter                     # vote tallies for the routes

import pandas as pd                                 # tabular data

# ---- where each attribute sits on the sheet (used only to locate it) --------
ATTR = {'Project ID': 1, 'Project acronym': 4,       # identity
        'TA host': 5, 'Project Stage': 7,            # host and stage
        'End of the Visit/Access': 11,               # end of access
        'Number of units used': 15,                  # units used
        'Short description of the activity': 16,     # activity text
        'Expected assets as outcomes': 17,           # expected assets
        'Delivered assets as outcomes': 18,          # delivered assets
        'Metadata of the outcome': 19,               # output description
        'Level of access': 20,                       # reuse terms
        'Associated WP': 21, 'Associated VA': 22,    # work package, VA installation
        'Associated RI': 23,                         # research infrastructure
        'Expected strategy of integration': 24,      # integration strategy
        'Actual link to asset produced': 25}         # link to the asset

# ---- Project Stage as an ordered vocabulary ---------------------------------
STAGE_ORDER = {'pi contacted': 1,                    # scheduling, not access
               'project details negotiated': 2,      # scheduling, not access
               'time window for the visit/access fixed': 3,  # scheduling, not access
               'visit/access exhausted': 4,          # the access has taken place
               'data/products accessible': 5,        # outputs available
               'ta reported to pmo by host manager': 6,  # host has reported
               'project fully reported': 7}          # fully reported
ACCESS_TAKEN_PLACE = 4                               # Implementation is met from rank 4
DISMISSED = 'project dismissed'                      # a stage that never qualifies

DENIAL = re.compile(r'^(not yet|to be determin|tbd|n/?a|none|-|\.)\s*', re.I)  # text that says "nothing yet"
DATE_IN_PROSE = re.compile(r'(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{2,4})')     # d/m/y written in prose
COMPLETION = re.compile(r'(?i)conclud|complet|exhaust|finish|ended|closed')  # words that say it is over

# ---- destinations and the RI portfolio each belongs to ----------------------
DESTINATIONS = [('SDL', r'(?i)\bSDL\b|simulation data lake|sdl\.hpc\.cineca|10\.82554'),  # Simulation Data Lake
                ('Zenodo', r'(?i)zenodo|10\.5281'),                               # open repository
                ('EIDA', r'(?i)\bEIDA\b|orfeus|fdsnws|seedlink'),                 # waveform federation
                ('CREW', r'(?i)\bCREW\b'),                                        # EPOS CREW
                ('ECCSEL', r'(?i)\bECCSEL\b'),                                    # ECCSEL ERIC
                ('ChEESE', r'(?i)\bChEESE\b'),                                    # ChEESE CoE
                ('EMSO', r'(?i)\bEMSO\b'),                                        # EMSO ERIC
                ('EFEHR', r'(?i)\bEFEHR\b'),                                      # EFEHR
                ('ARISE', r'(?i)\bARISE\b'),                                      # ARISE
                ('EPOS', r'(?i)\bEPOS\b')]                                        # EPOS ERIC
ROUTES = [('R1', 'Declared installation', 'Associated VA'),                       # declaration route
          ('R2', 'Declared infrastructure', 'Associated RI'),                     # declaration route
          ('R3', 'Declared strategy', 'Expected strategy of integration'),        # declaration route
          ('R4', 'Asset location', 'Actual link to asset produced'),              # direct route
          ('R5', 'Metadata citation', 'Metadata of the outcome'),                 # direct route
          ('R6', 'Delivered asset', 'Delivered assets as outcomes'),              # direct route
          ('R7', 'Expected asset', 'Expected assets as outcomes'),                # direct route
          ('R8', 'Host lineage', 'TA host'),                                      # lineage route
          ('R9', 'Work-package lineage', 'Associated WP')]                        # lineage route
ROUTE_CODES = [r[0] for r in ROUTES]                 # 'R1' .. 'R9'

# ---- primary DDSS class by lexicon (used by Figures 1 and 3) ----------------
DDSS_LEXICON = {                                     # terms that denote each class
    'Data': ['dataset', 'data set', 'raw data', 'recording', 'waveform', 'time series',  # lexicon terms (continued)
             'timeseries', 'measurement', 'rinex', 'observation', 'log data',  # lexicon terms (continued)
             'acquisition', 'sampling', 'borehole data', 'seismogram'],  # lexicon terms (continued)
    'Data product': ['model', 'simulation', 'synthetic', 'map', 'hazard', 'scenario',  # lexicon terms (continued)
                     'inversion', 'catalogue', 'catalog', 'assessment', 'benchmark',  # lexicon terms (continued)
                     'tomograph', 'velocity model', 'ground motion', 'forecast',  # lexicon terms (continued)
                     'processed', 'derived'],        # lexicon terms (continued)
    'Software': ['software', 'code', 'workflow', 'pipeline', 'script', 'notebook',  # lexicon terms (continued)
                 'algorithm', 'toolbox', 'plugin', 'library', 'solver', 'routine',  # lexicon terms (continued)
                 'github', 'open-source', 'open source'],  # lexicon terms (continued)
    'Service': ['service', 'portal', '\\bapi\\b', 'web service', 'webservice', 'node',  # lexicon terms (continued)
                'streaming', 'real-time', 'real time', 'monitoring network',  # lexicon terms (continued)
                'observatory', 'station network', 'platform', 'dashboard',  # lexicon terms (continued)
                'interface', 'repository service']}  # lexicon terms (continued)
DDSS_TIEBREAK = ['Service', 'Software', 'Data product', 'Data']  # most demanding class wins a tie


def is_stated(value):                                # does a cell carry a real statement?
    """True when a cell holds a statement rather than silence or a denial."""
    s = str(value or '').strip()                     # the cell as text
    return bool(s) and s.lower() != 'nan' and not DENIAL.match(s)  # non-empty and not "tbd"


def access_period_over(value, asof):                 # read End of the Visit/Access
    """Return True when End of the Visit/Access shows that the period has ended."""
    s = str(value or '').strip()                     # the cell as text
    if not s or s.lower() == 'nan':                  # nothing recorded
        return False                                 # cannot be shown to be over
    ts = pd.to_datetime(value, errors='coerce', dayfirst=True)  # a real date cell?
    if pd.notna(ts):                                 # yes
        return bool(ts < asof)                       # over if before the snapshot date
    dates = []                                       # dates written inside prose
    for dd, mm, yy in DATE_IN_PROSE.findall(s):      # every d/m/y in the text
        year = int(yy) + 2000 if len(yy) == 2 else int(yy)  # two-digit years are 20xx
        try:                                         # an impossible date is skipped
            dates.append(pd.Timestamp(year=year, month=int(mm), day=int(dd)))  # keep it
        except ValueError:                           # e.g. 31/02
            pass                                     # ignore it
    if dates:                                        # at least one date in prose
        return bool(max(dates) < asof)               # the latest one decides
    return bool(COMPLETION.search(s))                # otherwise explicit completion wording


def destinations_in(text):                           # which destinations does a text name?
    """Every destination named in a piece of text, as a set."""
    s = str(text or '')                              # the text
    return {name for name, pattern in DESTINATIONS if re.search(pattern, s)}  # all matches


def classify_ddss(text):                             # primary DDSS class of an asset text
    """The class with most lexicon hits; ties go to the more demanding class."""
    t = ' ' + str(text or '').lower() + ' '          # padded lower-case text
    hits = {c: sum(1 for term in terms if re.search(term, t))  # hits per class
            for c, terms in DDSS_LEXICON.items()}    # for all four classes
    best = max(hits.values())                        # the highest count
    if best == 0:                                    # no lexicon term at all
        return 'unclassified'                        # an absence of evidence
    return next(c for c in DDSS_TIEBREAK if hits[c] == best)  # first class at the maximum


def winner(tally, declared=frozenset()):           # a deterministic majority
    """
    The destination with most votes. Ties are broken by (1) a destination declared in
    R1-R3 over one only inferred, then (2) alphabetical order. Counter.most_common
    breaks ties by insertion order, which follows set iteration order and therefore
    changes with PYTHONHASHSEED; that made the result vary between runs.
    """
    return min(tally, key=lambda k: (-tally[k], k not in declared, k))  # most votes, declared, A-Z


def read_sheet(path):                                # load the ILM sheet
    """The TA_Individual_Applications sheet, one row per application (header on row 4)."""
    d = pd.read_excel(path, sheet_name='TA_Individual_Applications', header=3)  # header is row 4
    ids = d.iloc[:, ATTR['Project ID']].astype(str).str.strip()  # Project ID as text
    d = d[ids.str.match(r'^C\d')].copy()             # keep application rows (C1..C4)
    d.index = d.iloc[:, ATTR['Project ID']].astype(str).str.strip()  # index by Project ID
    return d                                         # 75 rows in the September 2026 version


def compute(path, asof, exclude=()):                 # the whole ladder and routes
    """One row per executed application: gates, TIL, routes, concordance, DDSS."""
    raw = read_sheet(path)                           # the sheet
    raw = raw[~raw.index.isin(set(exclude))]         # drop cancelled and duplicate rows first
    col = lambda name: raw.iloc[:, ATTR[name]]       # an attribute by name
    asof = pd.Timestamp(asof).normalize()            # the pinned snapshot date
    d = pd.DataFrame(index=raw.index)                # the result, indexed by Project ID
    d['Project ID'] = raw.index                      # identity
    d['Call'] = raw.index.str.extract(r'^(C\d)', expand=False)  # C1..C4
    d['Host'] = col('TA host').astype(str).str.strip()          # host installation
    d['WP'] = col('Associated WP').astype(str).str.strip()      # work package

    # ---- gate 1: Implementation ------------------------------------------------
    stage = col('Project Stage').fillna('').astype(str).str.strip()  # stage text
    d['Project Stage'] = stage                       # kept for the tables
    rank = stage.str.lower().map(STAGE_ORDER).fillna(0).astype(int)  # stage rank
    d['g1'] = (rank >= ACCESS_TAKEN_PLACE) & ~stage.str.lower().eq(DISMISSED)  # access has taken place

    # ---- gate 2: Access --------------------------------------------------------
    units = pd.to_numeric(col('Number of units used'), errors='coerce')  # a number, or NaN
    over = col('End of the Visit/Access').map(lambda v: access_period_over(v, asof))  # period over?
    d['units_recorded'] = units.fillna(0) > 0        # a positive unit count
    d['g2'] = d.units_recorded | (d.g1 & over)       # units, or Implementation and period over

    # ---- gate 3: Content -------------------------------------------------------
    d['output_described'] = col('Metadata of the outcome').map(is_stated)  # output described
    d['reuse_terms_stated'] = col('Level of access').map(is_stated)        # reuse terms stated
    d['g3'] = d.output_described & d.reuse_terms_stated                    # both required

    # ---- the nine routes -------------------------------------------------------
    for code, _, attribute in ROUTES[:7]:            # R1-R7 read one attribute each
        d[code] = col(attribute).map(destinations_in)  # destinations named there
    declared = [d.at[i, 'R1'] | d.at[i, 'R2'] | d.at[i, 'R3'] for i in d.index]  # R1-R3 union
    d['_declared'] = declared                        # kept for the lineage routes
    for code, group in (('R8', d.Host), ('R9', d.WP)):  # the two lineage routes
        votes = []                                   # one result per application
        for i in d.index:                            # leave-one-out co-occurrence
            tally = Counter()                        # destinations declared by the others
            for j in d.index:                        # every other application
                if j != i and group[j] == group[i]:  # sharing the same host / WP
                    tally.update(d.at[j, '_declared'])  # adds its declared destinations
            votes.append({winner(tally)} if tally else set())  # the commonest one, ties broken deterministically
        d[code] = votes                              # store the route
    tallies = [Counter() for _ in d.index]           # all nine routes per application
    for k, i in enumerate(d.index):                  # each application
        for code in ROUTE_CODES:                     # each route
            tallies[k].update(d.at[i, code])         # adds its destinations
    d['destination'] = [winner(t, dec) if t else '' for t, dec in zip(tallies, d['_declared'])]  # winning destination
    d['concordance'] = [t[w] if t else 0 for t, w in zip(tallies, d['destination'])]  # routes agreeing on it

    # ---- gate 4: Integration and the level -------------------------------------
    d['g4'] = d['_declared'].map(len) > 0            # any declared destination
    d['declared_destination'] = d['_declared'].map(lambda s: '; '.join(sorted(s)))  # as text
    d['TIL'] = 0                                     # start everyone at 0
    for level, gate in enumerate(('g1', 'g2', 'g3', 'g4'), start=1):  # gates in order
        ok = d[[f'g{k}' for k in range(1, level + 1)]].all(axis=1)    # all gates up to this one
        d.loc[ok, 'TIL'] = level                     # raise the level where they hold

    # ---- primary DDSS (destination attributes excluded on purpose) ------------
    text = (col('Expected assets as outcomes').fillna('').astype(str) + ' ' +   # expected
            col('Delivered assets as outcomes').fillna('').astype(str) + ' ' +  # delivered
            col('Short description of the activity').fillna('').astype(str))   # activity
    d['DDSS'] = text.map(classify_ddss)              # one class per application

    for code in ROUTE_CODES:                         # sets to text for the CSV
        d[code] = d[code].map(lambda s: '; '.join(sorted(s)))  # "EPOS; SDL"
    return d.drop(columns=['_declared']).reset_index(drop=True)  # one clean table
