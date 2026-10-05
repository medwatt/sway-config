#!/usr/bin/python3

import sys
import subprocess
import pathlib
import tempfile


def latex_document(latex):
    return (
        r"""
        \documentclass[10pt]{minimal}
        \usepackage[utf8]{inputenc}
        \usepackage[T1]{fontenc}
        \usepackage{textcomp}
        \usepackage{amsmath, amssymb}
        \usepackage{xcolor}
        \usepackage{sansmathfonts}  % For Beamer-like sans serif math fonts

        \begin{document}
        \pagestyle{empty}
    """
        + latex
        + r"\end{document}"
    )


def main(latex):
    m = tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".tex")
    m.write(latex_document(latex))
    m.close()

    working_directory = tempfile.gettempdir()
    subprocess.run(
        ["latex", "-output-directory=" + working_directory, m.name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    dvi_file = m.name.replace(".tex", ".dvi")
    svg_file = m.name.replace(".tex", ".svg")
    subprocess.run(
        [
            "dvisvgm",
            "--no-fonts",
            "--scale=1.3",
            dvi_file,
            "-o",
            svg_file,
        ],  # Adjust the scale factor
        cwd=working_directory,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    with open(svg_file, "r") as svg:
        subprocess.run(["wl-copy", "--type", "image/x-inkscape-svg"], stdin=svg)


if __name__ == "__main__":
    latex = pathlib.Path(sys.argv[1]).read_text()
    main(latex)
