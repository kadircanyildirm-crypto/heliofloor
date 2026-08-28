#!/usr/bin/env python3
"""Structural checks on a .tex file without invoking LaTeX.

Catches the errors that actually bite: unbalanced environments, \\ref with no
\\label, \\cite with no \\bibitem, missing graphics files, stray unescaped
specials, and non-ASCII characters that a pdflatex run would choke on.
"""
import os
import re
import sys
from collections import Counter

path = sys.argv[1]
root = os.path.dirname(os.path.abspath(path))
src = open(path, encoding="utf-8").read()

# strip comments (but not \%)
nocomment = re.sub(r"(?<!\\)%.*", "", src)

problems = []

# ---------------------------------------------------------- environments
stack = []
for m in re.finditer(r"\\(begin|end)\{([^}]+)\}", nocomment):
    kind, name = m.group(1), m.group(2)
    line = nocomment[: m.start()].count("\n") + 1
    if kind == "begin":
        stack.append((name, line))
    else:
        if not stack:
            problems.append(f"line {line}: \\end{{{name}}} with nothing open")
        elif stack[-1][0] != name:
            problems.append(
                f"line {line}: \\end{{{name}}} closes \\begin{{{stack[-1][0]}}} "
                f"opened at line {stack[-1][1]}")
            stack.pop()
        else:
            stack.pop()
for name, line in stack:
    problems.append(f"line {line}: \\begin{{{name}}} never closed")

# ---------------------------------------------------------------- braces
depth, line_no = 0, 1
for i, ch in enumerate(nocomment):
    if ch == "\n":
        line_no += 1
    elif ch == "{" and (i == 0 or nocomment[i - 1] != "\\"):
        depth += 1
    elif ch == "}" and (i == 0 or nocomment[i - 1] != "\\"):
        depth -= 1
        if depth < 0:
            problems.append(f"line {line_no}: unmatched closing brace")
            depth = 0
if depth:
    problems.append(f"{depth} unclosed brace(s) at end of file")

# ------------------------------------------------------------ refs/labels
labels = set(re.findall(r"\\label\{([^}]+)\}", nocomment))
refs = set(re.findall(r"\\(?:page)?ref\{([^}]+)\}", nocomment))
for r in sorted(refs - labels):
    problems.append(f"\\ref{{{r}}} has no matching \\label")
unused = sorted(labels - refs)

# ------------------------------------------------------------ cites/bib
bibitems = set(re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}", nocomment))
cites = set()
for m in re.finditer(r"\\cite[tp]?\*?(?:\[[^\]]*\])*\{([^}]+)\}", nocomment):
    cites.update(k.strip() for k in m.group(1).split(","))
for c in sorted(cites - bibitems):
    problems.append(f"\\cite{{{c}}} has no matching \\bibitem")
uncited = sorted(bibitems - cites)

# ------------------------------------------------------------- graphics
gpaths = re.findall(r"\\graphicspath\{\{([^}]*)\}\}", nocomment)
searchdirs = [root] + [os.path.join(root, g) for g in gpaths]
for g in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", nocomment):
    found = any(
        os.path.exists(os.path.join(d, g + ext))
        for d in searchdirs for ext in ("", ".pdf", ".png", ".jpg", ".eps"))
    if not found:
        problems.append(f"\\includegraphics{{{g}}}: no file found in {searchdirs}")

# ------------------------------------------------------------- non-ASCII
bad = Counter()
for i, ch in enumerate(src):
    if ord(ch) > 127:
        bad[ch] += 1

# ------------------------------------------------------------ table cols
def balanced_group(text, start):
    """Return (contents, index_after) for the {...} group beginning at start."""
    assert text[start] == "{"
    depth, i = 0, start
    while i < len(text):
        if text[i] == "{" and text[i - 1] != "\\":
            depth += 1
        elif text[i] == "}" and text[i - 1] != "\\":
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i + 1
        i += 1
    return text[start + 1:], len(text)


for m in re.finditer(r"\\begin\{tabular\}", nocomment):
    spec, after = balanced_group(nocomment, m.end())
    end = nocomment.find(r"\end{tabular}", after)
    body = nocomment[after:end if end != -1 else len(nocomment)]
    # drop @{...} and p{...} argument groups before counting column letters
    clean = re.sub(r"[@p!]\{(?:[^{}]|\{[^{}]*\})*\}", lambda mm: "p" if mm.group(0)[0] == "p" else "", spec)
    ncol = len(re.findall(r"[lcrp]", clean))
    line = nocomment[: m.start()].count("\n") + 1
    for raw in body.split(r"\\"):
        row = re.sub(r"\\(?:toprule|midrule|bottomrule|cmidrule)(?:\([^)]*\))?"
                     r"(?:\{[^}]*\})?", "", raw)
        row = re.sub(r"\\multicolumn\{(\d+)\}\{[^}]*\}\{[^}]*\}",
                     lambda mm: "&" * (int(mm.group(1)) - 1), row)
        if not row.strip():
            continue
        n = row.count("&") + 1
        if n != ncol:
            problems.append(
                f"line ~{line}: tabular declares {ncol} columns but a row has {n}: "
                f"{row.strip()[:70]!r}")

# ------------------------------------------------------------------ report
print(f"checked: {path}")
print(f"  environments balanced : {'no' if any('begin' in p or 'end' in p for p in problems) else 'yes'}")
print(f"  labels {len(labels)}, refs {len(refs)}, bibitems {len(bibitems)}, cites {len(cites)}")
if unused:
    print(f"  note: labels never referenced: {', '.join(unused)}")
if uncited:
    print(f"  note: bibitems never cited: {', '.join(uncited)}")
if bad:
    print(f"  non-ASCII characters present ({sum(bad.values())} total):")
    for ch, n in bad.most_common():
        print(f"      U+{ord(ch):04X} {ch!r} x{n}")
    print("      -> fine with inputenc utf8 + T1, but check each renders as intended")
print()
if problems:
    print(f"{len(problems)} PROBLEM(S):")
    for p in problems:
        print(f"  * {p}")
    sys.exit(1)
print("No structural problems found.")
