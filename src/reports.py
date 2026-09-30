# =============================================================================
#  reports.py — read the TA report corpus and return, for each executed project,
#               the evidence its primary report holds for the four TIL gates
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
The TA reports are the reference witness. Nothing here changes an ILM value: the
evidence is returned beside the ILM columns. Which file belongs to which project is
stated, file by file, in data/registers/report_map.csv; which repository DOIs are
the project's own deposits is stated in data/registers/report_deposits.csv. Both
registers were built by reading the reports.
"""

import os                                           # file paths
import re                                           # regular expressions

import pandas as pd                                 # tabular data

# ---- the labelled fields of the report template -----------------------------
FIELD = {'Project ID': r'Project\s*ID\s*:',                          # identity
         'Principal investigator': r'Principal\s+investigator\s*:',  # PI
         'Project title': r'Project\s+title\s*:',                    # title
         'Project acronym': r'Project\s+acronym\s*:',                # acronym
         'Hosting installation': r'Hosting\s+installation\s*:',      # installation
         'Hosting team': r'Hosting\s+team\s*:',                      # team
         'Period of access': r'Period\s+of\s+access\s*:',            # access period
         'Report of activities': r'Report\s+of\s+activities\s*:',    # activities
         'Project outcomes': r'(?:Target\s+)?Project\s+outcomes?\s*:',  # outcomes
         'Virtual Access': r'Geo-?\s*INQUIRE\s+Virtual\s+Access\s*:?',  # VA block
         'Data/Products': r'Data\s*/\s*Products?\s*:',               # data and products
         'DOI field': r'^\s*DOI\s*:'}                                # DOI line

DOI = re.compile(r'10\.\d{4,9}/[^\s"<>,;)\]]+')     # a DOI anywhere in the text
MONTHS = ('january|february|march|april|may|june|july|august|september|october|'  # month names
          'november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec')         # and abbreviations
DATE_NUM = re.compile(r'(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{2,4})')                  # 12/03/2026
DATE_TXT = re.compile(rf'(?i)\b({MONTHS})\w*\.?\s+(?:\d{{1,2}}(?:st|nd|rd|th)?,?\s+)?(?:of\s+)?(\d{{4}})\b')  # "March 12 2026"
CONCLUDED = re.compile(r'(?i)conclud|complet|exhaust|finish|ended|closed|took place|'  # past-tense wording
                       r'was (?:carried out|performed)|were (?:carried out|performed)')  # continued from the line above
LICENCE = re.compile(r'(?i)cc[\s-]?by|creative commons|open[\s-]access|licen[cs]e')  # reuse terms
RI_ENDPOINTS = {'SDL', 'EPOS', 'EIDA', 'CREW', 'ECCSEL', 'ChEESE', 'EMSO', 'EFEHR', 'ARISE'}  # RI destinations
DEST = [('SDL', r'(?i)\bSDL\b|simulation data lake|sdl\.hpc\.cineca|10\.82554'),  # as ilm.py, except CREW: in report prose
                                                    # lowercase 'crew' means the field team (ETNAGRAV)
        ('Zenodo', r'(?i)zenodo|10\.5281'), ('EIDA', r'(?i)\bEIDA\b|orfeus|fdsnws|seedlink'),  # continued from the line above
        ('CREW', r'\bCREW\b|(?i:epos[\s-]crew|crew\.epos)'), ('ECCSEL', r'(?i)\bECCSEL\b'), ('ChEESE', r'(?i)\bChEESE\b'),  # continued from the line above
        ('EMSO', r'(?i)\bEMSO\b'), ('EFEHR', r'(?i)\bEFEHR\b'), ('ARISE', r'(?i)\bARISE\b'),  # continued from the line above
        ('EPOS', r'(?i)\bEPOS\b')]                   # continued from the line above


def text_name(wp, filename):                        # name of the extracted text file
    """The .txt name written by extract_report_text.py for one report file."""
    return (wp + '_' + filename).replace(' ', '_') + '.txt'  # e.g. WP5_C1-TA2-..._OMG.pdf.txt


def field_text(text, name):                         # one template field
    """Text from a field label up to the next field label; '' when absent."""
    m = re.search(FIELD[name], text, re.M | re.I)   # find the label
    if not m:                                        # the field is absent
        return ''                                    # nothing to return
    start, end = m.end(), len(text)                  # from the label to the end
    for other in FIELD:                              # every other label
        if other != name:                            # but this one
            mm = re.search(FIELD[other], text[start:], re.M | re.I)  # its next occurrence
            if mm:                                   # found after the start
                end = min(end, start + mm.start())   # the field stops there
    return text[start:end].strip()                   # the field's text


def period_of(text):                                 # the access period as written
    """Period of access, or the older 'Date of visit' line."""
    p = field_text(text, 'Period of access')         # the current template
    if p:                                            # present
        return p                                     # use it
    m = re.search(r'(?i)Date of visit\s*:?(.{0,80})', text)  # the older template
    return m.group(1).strip() if m else ''           # or nothing


def access_period_ended(period, body, asof):         # has the access ended?
    """True when a date in the period has passed, or the report says it took place."""
    s = period.strip()                               # the period text
    dates = []                                       # every date found
    for dd, mm, yy in DATE_NUM.findall(s):           # numeric dates
        year = int(yy) + 2000 if len(yy) == 2 else int(yy)  # two-digit years are 20xx
        try:                                         # skip impossible dates
            dates.append(pd.Timestamp(year=year, month=int(mm), day=int(dd)))  # keep
        except ValueError:                           # e.g. 21-30 read as day-month
            pass                                     # ignore
    for mon, yr in DATE_TXT.findall(s):              # "October 2025", "March 12 2026"
        try:                                         # unparseable month names skipped
            dates.append(pd.Timestamp(f'{mon} {yr}') + pd.offsets.MonthEnd(0))  # end of that month
        except Exception:                            # anything odd
            pass                                     # ignore
    if dates:                                        # at least one date
        return max(dates) < pd.Timestamp(asof)       # the latest one decides
    return bool(CONCLUDED.search(body))              # else: past-tense wording in the report


def destinations_in(text):                          # destinations named in a text
    """Every destination named in a piece of report text."""
    return {n for n, p in DEST if re.search(p, str(text or ''))}  # all matches


def evidence(report_map, deposits, txtdir, asof):   # the evidence table
    """One row per project that has a primary report."""
    rows = []                                        # collected rows
    for _, m in report_map[report_map.Role == 'primary'].iterrows():  # one primary report per project
        text = open(os.path.join(txtdir, text_name(m['WP'], m['Report file'])),  # its text
                    errors='ignore').read()          # tolerate stray bytes
        period = period_of(text)                     # the access period
        outcomes = ' '.join(field_text(text, k) for k in  # the output fields
                            ('Project outcomes', 'Data/Products', 'Virtual Access'))  # continued from the line above
        dests = set()                                # destinations named
        for k in ('Virtual Access', 'Data/Products', 'DOI field',  # fields that name them
                  'Project outcomes', 'Report of activities'):  # text continues
            dests |= destinations_in(field_text(text, k))  # add what each names
        sdl = sorted({d.rstrip('.​') for d in DOI.findall(text) if d.startswith('10.82554')})  # SDL DOIs
        own = deposits[(deposits['Project ID'] == m['Project ID']) &  # verified deposits
                       deposits.Verdict.isin(['own deposit', 'shared deposit'])]  # continued from the line above
        rows.append({'Project ID': m['Project ID'],  # identity
                     'Report on file': True,         # a report exists
                     'Report file (primary)': m['Report file'],  # which file
                     'Report files (all versions)': int((report_map['Project ID'] == m['Project ID']).sum()),  # versions
                     'ID printed in report': m['ID printed in report'],  # the ID the host wrote
                     'Report period of access': re.sub(r'\s+', ' ', period)[:120],  # tidy period
                     'Report: access documented': len(text) > 1200,  # a substantive report
                     'Report: access period ended': bool(access_period_ended(period, text, asof)),  # over?
                     'Report: SDL DOI': '; '.join(sdl),             # SDL DOIs cited
                     'Report: own repository deposit': '; '.join(own['Identifier in TA report']),  # own deposits
                     'Report: output identified': bool(sdl) or len(own) > 0,  # an identifier exists
                     'Report: reuse terms stated': bool(LICENCE.search(text)),  # licence wording
                     'Report: destinations named': '; '.join(sorted(dests & (RI_ENDPOINTS | {'Zenodo'}))),  # named
                     'Report: RI destination named': bool(dests & RI_ENDPOINTS),  # an RI endpoint named
                     'Report: output described': len(outcomes.strip()) > 40})  # outcomes written
    return pd.DataFrame(rows)                        # the evidence table
