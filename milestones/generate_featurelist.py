import argparse
import csv
import sys
import time

from collections import namedtuple
from contextlib import contextmanager
from datetime import datetime
from io import StringIO
from textwrap import dedent

BOM = "\ufeff"
EXCEL_DATEFMT = "%m/%d/%Y %I:%M:%S %p"
Milestone = namedtuple('Milestone',
                       ['code', 'name', 'description', 'due', 'predecessors'])
#                       ['code', 'name', 'short_name', 'test_spec',
#                        'description', 'comments', 'date', 'predecessors'])

def get_milestones(pmcs, dscr):
    """
    """
    milestones = []
    pmcs_reader = csv.DictReader(pmcs)
    dscr_reader = csv.DictReader(dscr)
    descriptions = {
        d['Milestone ID']: d['Description'] for d in dscr_reader
    }

    for ms in pmcs_reader:
        code = ms['task_code']
        if code == "Activity ID":
            continue

        name = ms['task_name'].strip(".")
        description = None
        if code in descriptions:
            dscr = descriptions[code].strip(".")
            if dscr != name:
                description = dscr

        due = (datetime.strptime(ms['end_date'], EXCEL_DATEFMT) if ms['end_date']
               else datetime.strptime(ms['start_date'], EXCEL_DATEFMT))

        pred = ms['pred_list'].split(', ')

        milestones.append(
            Milestone(code, name, description, due, pred)
        )
    return milestones

def escape_latex(text):
    return text.strip().replace("%", "\%").replace("#", "\#").replace("&", "\&").replace("Test report: ", "")

def generate_release_list(milestones, release_prefix="LDM-503-", include_prefix="DM-"):
    output = StringIO()
    for ms in sorted(milestones, key=lambda x: x.due):
        if ms.code.startswith(release_prefix):
            output.write("\\subsection{{{}: {}}}\n".format(
                escape_latex(ms.code),
                escape_latex(ms.name),
            ))

            output.write("\\textit{{Due: {}.}}\n".format(
                escape_latex(ms.due.strftime("%Y-%m-%d"))
            ))

            predecessors = [prems for prems in milestones
                            if prems.code in ms.predecessors]
            if predecessors:
                output.write("\\begin{itemize}\n")
                for prems in sorted(predecessors, key=lambda x: x.due):
                    output.write("\item{{{}: {} (\\textit{{Due: {}}})}}\n".format(
                        escape_latex(prems.code),
                        escape_latex(prems.name),
                        escape_latex(ms.due.strftime("%Y-%m-%d"))
                    ))
                output.write("\\end{itemize}\n\n")

    return output.getvalue()


@contextmanager
def open_without_bom(filename):
    """
    Open the file, discarding the first character if it is a UTF-8 BOM (\ufeff).
    """
    with open(filename) as f:
        bom = f.read(1)
        if bom != BOM:
            f.seek(0)
        yield f

def parse_args():
    parser = argparse.ArgumentParser(description="Prepare DM release summaries")
    parser.add_argument('pmcs', help="Milestone listing extracted from PMCS.")
    parser.add_argument('dscr', help="Mapping of milestone ID to description.")
    parser.add_argument('outp', help="Path to output file.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    with open_without_bom(args.pmcs) as pmcs, open_without_bom(args.dscr) as dscr:
        milestones = get_milestones(pmcs, dscr)
    with open(args.outp, "w") as f:
        f.write(generate_release_list(milestones))
