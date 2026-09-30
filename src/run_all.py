# =============================================================================
#  run_all.py — rebuild every input table and every figure, in order
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
Usage (from the repository root)
  python src/run_all.py --ilm "data/raw/GeoINQUIRE-ImplementationLevelMatrix (11).xlsx" \
                        --reports "data/raw/All TA Reports-6" --asof 2026-09-29
Add --skip-extract when data/raw/report_text already holds the extracted text.
"""

import argparse                                     # command-line arguments
import os                                           # file paths
import subprocess                                   # run each step as its own process
import sys                                          # the current Python interpreter

HERE = os.path.dirname(os.path.abspath(__file__))   # the src folder
ROOT = os.path.dirname(HERE)                        # the repository root


def step(script, *args):                            # run one script
    """Run src/<script> with the given arguments; stop on the first failure."""
    print(f'> {script}')                             # say what runs
    subprocess.run([sys.executable, os.path.join(HERE, script), *args], check=True, cwd=HERE)  # run it


def main():                                          # entry point: arguments, computation, drawing
    ap = argparse.ArgumentParser(description='Rebuild all inputs and figures.')  # the parser
    ap.add_argument('--ilm', required=True)          # the ILM workbook
    ap.add_argument('--reports', default=os.path.join(ROOT, 'data', 'raw', 'All TA Reports-6'))  # report folder
    ap.add_argument('--asof', default='2026-09-29')  # the snapshot date
    ap.add_argument('--skip-extract', action='store_true')  # reuse extracted text
    a = ap.parse_args()                              # read the arguments
    raw = os.path.join(ROOT, 'data', 'raw')          # raw inputs (not redistributed)
    reg = os.path.join(ROOT, 'data', 'registers')    # registers (committed)
    der = os.path.join(ROOT, 'data', 'derived')      # derived tables (committed)
    fig = os.path.join(ROOT, 'figures')              # figures (committed)
    txt = os.path.join(raw, 'report_text')           # extracted report text
    ilm = os.path.abspath(a.ilm)                     # the ILM, absolute
    if not a.skip_extract:                           # step 0: report text
        step('extract_report_text.py', '--reports', os.path.abspath(a.reports), '--out', txt)  # step 0: extract the report text
    step('build_inputs.py', '--ilm', ilm, '--txt', txt, '--registers', reg,  # step 1: every input table
         '--asof', a.asof, '--out', der)             # arguments continue
    step('fig01_overview.py', '--data', os.path.join(der, 'til_68.csv'), '--out', fig)  # Figure 1
    step('fig03_roadmap.py', '--data', os.path.join(der, 'til_68.csv'), '--out', fig)   # Figure 3
    step('fig04_til4.py', '--data', os.path.join(der, 'Figure_04_TIL4_input.csv'), '--out', fig)  # Figure 4
    step('fig05_below_til4.py', '--data', os.path.join(der, 'Figure_05_below_TIL4_input.csv'), '--out', fig)  # Figure 5
    step('fig06_two_witnesses.py', '--derived', der, '--out', fig)  # Figure 6
    print('done')                                    # finished


if __name__ == '__main__':                           # run as a script
    main()                                           # rebuild everything
