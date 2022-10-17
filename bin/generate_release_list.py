from io import StringIO
import sys

from milestones import (escape_latex, write_output, get_latest_pmcs_path,
                        get_local_data_path, load_milestones)

def generate_releases(milestones):
    output = StringIO()
    for ms in sorted([ms for ms in milestones if ms.code.startswith("LDM")],
                     key=lambda x: (x.due, x.code)):
        output.write(f"\\subsection{{{escape_latex(ms.name)}: {escape_latex(ms.code)}}}\n")
        output.write("\\textit{")
        output.write(f"Due: {escape_latex(ms.due.strftime('%Y-%m-%d'))}; ")

        if ms.completed:
            output.write(f"completed {escape_latex(ms.completed.strftime('%Y-%m-%d'))}")
        else:
            output.write("currently incomplete")
        output.write(".}\n")

        predecessors = [prems for prems in milestones
                        if prems.code.startswith("DM-")
                        and prems.code in ms.predecessors]

        if predecessors:
            output.write("\\begin{itemize}\n")
            for prems in sorted(predecessors, key=lambda x: (x.due, x.code)):
                output.write(f"\item{{{escape_latex(prems.code)}: {escape_latex(prems.name)} "
                             f"\\textit{{(Due: {escape_latex(prems.due.strftime('%Y-%m-%d'))}; ")

                if prems.completed:
                    output.write(f"completed {escape_latex(prems.completed.strftime('%Y-%m-%d'))}")
                else:
                    output.write("currently incomplete")

                output.write(")}}\n")
            output.write("\\end{itemize}\n")
        else:
            output.write("""\nNo new functionality is associated with this milestone, which """
                         """represents a refined or improved version of earlier deliveries.\n""")
    return output.getvalue()

if __name__ == "__main__":
    forecast = sys.argv[1]=="forecast"
    milestones = load_milestones(get_latest_pmcs_path(), get_local_data_path())
    write_output("featurelist.tex", generate_releases(milestones))
