# =============================================================================
#  extract_report_text.py — convert every TA report (PDF, DOCX, ODT) to plain
#                           text, one .txt file per report
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
Input : the report folder with one sub-folder per work package (WP4, WP5, WP8)
Output: <out>/<WP>_<file name>.txt  (spaces replaced by underscores)

Tools: pdftotext (poppler) for PDF, pandoc for DOCX, LibreOffice for ODT. A file
without an extension is sniffed: a ZIP container is treated as DOCX (the ELITS-SEA
report is such a file). A file that yields no text is still written, empty, so
the count of inputs and outputs always matches.

Usage
  python extract_report_text.py --reports "data/raw/All TA Reports-6" --out data/raw/report_text
"""

import argparse                                     # command-line arguments
import os                                           # file paths
import shutil                                       # temporary folder clean-up
import subprocess                                   # the external converters
import tempfile                                     # a scratch folder for LibreOffice
import zipfile                                      # sniffing extension-less files

WPS = ('WP4', 'WP5', 'WP8')                         # the work-package folders


def kind_of(path):                                  # which converter a file needs
    """'pdf', 'docx', 'odt' or '' for anything else."""
    ext = os.path.splitext(path)[1].lower().lstrip('.')  # the extension
    if ext in ('pdf', 'docx', 'odt'):                # a known report format
        return ext                                   # use it
    if not ext and zipfile.is_zipfile(path):         # no extension but a ZIP container
        with zipfile.ZipFile(path) as z:             # look inside
            return 'docx' if 'word/document.xml' in z.namelist() else ''  # a Word document?
    return ''                                        # not a report


def to_text(path, kind):                            # run the converter
    """The plain text of one report."""
    if kind == 'pdf':                                # PDF: keep the layout so labels stay on their lines
        return subprocess.run(['pdftotext', '-layout', path, '-'],  # write to stdout
                              capture_output=True, text=True).stdout  # the text
    if kind == 'docx':                               # Word: pandoc to plain text
        return subprocess.run(['pandoc', '-f', 'docx', '-t', 'plain', path],  # explicit input format
                              capture_output=True, text=True).stdout  # the text
    tmp = tempfile.mkdtemp()                         # ODT: LibreOffice writes a file
    subprocess.run(['soffice', '--headless', '--convert-to', 'txt:Text', '--outdir', tmp, path],  # convert
                   capture_output=True)              # quietly
    out = [f for f in os.listdir(tmp) if f.endswith('.txt')]  # the file it wrote
    text = open(os.path.join(tmp, out[0]), errors='ignore').read() if out else ''  # its content
    shutil.rmtree(tmp)                               # clean up
    return text                                      # the text


def main():                                          # entry point: arguments, computation, drawing
    ap = argparse.ArgumentParser(description='Extract text from the TA reports.')  # the parser
    ap.add_argument('--reports', required=True)      # the report folder
    ap.add_argument('--out', required=True)          # where to write the .txt files
    a = ap.parse_args()                              # read the arguments
    os.makedirs(a.out, exist_ok=True)                # make the output folder
    n = 0                                            # files converted
    for wp in WPS:                                   # each work package
        folder = os.path.join(a.reports, wp)         # its folder
        for fn in sorted(os.listdir(folder)):        # each file, in a stable order
            path = os.path.join(folder, fn)          # its path
            kind = kind_of(path)                     # its format
            if fn.startswith('.') or not kind:       # hidden files and non-reports
                continue                             # skip
            text = to_text(path, kind)               # convert
            name = (wp + '_' + fn).replace(' ', '_') + '.txt'  # the name the registers expect
            with open(os.path.join(a.out, name), 'w') as fh:  # write it
                fh.write(text)                       # even when empty
            n += 1                                   # count it
    print(f'  {n} report files -> {a.out}')          # report


if __name__ == '__main__':                           # run as a script
    main()                                           # convert everything
