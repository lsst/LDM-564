#!/usr/bin/env python

import csv
import sys
from collections import OrderedDict

def sanitize_tex(string):
    return string.replace("&", "\&").replace("%", "\%").replace("#", "\#")

def parse_milestones(ms_input):
    descriptions, prereqs = {}, {}
    with open(ms_input, "r") as f:
        reader = csv.DictReader(f)
        for ms in reader:
            descriptions[ms['Milestone ID']] = sanitize_tex(ms['Description'])
            if ms['Milestone ID'].startswith('LDM'):
                prereqs[ms['Milestone ID']] = [ms.strip()
                                               for ms in ms['Prerequisites'].split(',')
                                               if not ms.startswith("LDM")]
    return descriptions, prereqs

if __name__ == "__main__":
    ms_input = sys.argv[1]
    tex_output = sys.argv[2]

    descriptions, prereqs = parse_milestones(ms_input)

    with open(tex_output, 'w') as f:
        f.write("%% AUTOMATICALLY GENERATED\n")
        f.write("%% Do not edit.\n")
        for ldm, prs in prereqs.items():
            if not prs:
                continue
            f.write('\subsection{\\textbf{%s}: %s \label{%s}}\n' % (ldm, descriptions[ldm], ldm))
            f.write('\\begin{itemize}\n')
            for pr in prs:
                f.write('\item{%s (%s)}\n' % (descriptions[pr], pr))
            f.write('\end{itemize}\n')
