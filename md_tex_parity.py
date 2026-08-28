#!/usr/bin/env python3
"""Do PAPER_DRAFT.md and paper.tex still make the same numeric claims?

Both were hand-edited through several revisions. A number corrected in one and
missed in the other is exactly the kind of drift this project has already been
bitten by once (736 vs 739). This compares the multiset of numeric tokens in the
two files and reports anything that appears in one but not the other.

Markup differences are normalised away: LaTeX escapes, thousands separators,
math delimiters, figure captions (LaTeX only), and author-year citations.

KNOWN BENIGN RESIDUE, as of draft v0.6 -- roughly a dozen tokens still show as
one-sided and all of them are typography, not content:

  * year ranges. Markdown writes 2010-2019 with an en dash, LaTeX writes
    2010--2019; the tokenizer splits them differently, so one side reports
    "2010" and the other "-2019".
  * em-dashes against a number, e.g. LaTeX "things---257 TB" tokenizes as -257.
  * cross-references to the *Surya paper's* own section 2.1.2, which the
    section-number stripper removes from one file but not the other.
  * workshop and release years (2009, 2017, 2025) adjacent to citations.

Both candidates that looked substantive were checked by hand and are equal in
both files: "3,672" appears six times in each, and the "-4.5" token traces to
the section range 4.3-4.5. Treat a NEW one-sided token as worth investigating;
treat the list above as noise.

Run:  python md_tex_parity.py
"""
import re
import sys
from collections import Counter

BASE = "."
md = open(f"{BASE}/PAPER_DRAFT.md", encoding="utf-8").read()
tex = open(f"{BASE}/paper.tex", encoding="utf-8").read()

# --- strip the parts that legitimately differ -------------------------------
# LaTeX preamble: package options, font sizes, margins
tex_body = tex.split(r"\begin{document}", 1)[-1]
# Markdown status header: build metadata, not a claim
md_body = md.split("## Abstract", 1)[-1]

# drop LaTeX comments and the bibliography (volume/page numbers are formatted
# differently in the two files by design)
tex_body = re.sub(r"(?<!\\)%.*", "", tex_body)
tex_body = tex_body.split(r"\begin{thebibliography}", 1)[0]
md_body = md_body.split("## References", 1)[0]

# section cross-references: Markdown writes "4.4", LaTeX writes \ref{}. Neither
# is a claim about the data, so strip both forms before comparing.
md_body = re.sub(r"§\s*\d+(?:\.\d+)*(?:\s*[-–—]\s*\d+(?:\.\d+)*)?", " ", md_body)
md_body = re.sub(r"^#+\s*\d+(?:\.\d+)*", " ", md_body, flags=re.M)
md_body = re.sub(r"\bsections?\s+\d+(?:\.\d+)*", " ", md_body, flags=re.I)

# figure and table captions exist only in the LaTeX build; the Markdown carries
# a parenthetical pointer instead. Their numbers restate the body text.
def strip_caption(s):
    out, i = [], 0
    while True:
        m = re.search(r"\\caption\{", s[i:])
        if not m:
            out.append(s[i:])
            return "".join(out)
        start = i + m.start()
        out.append(s[i:start])
        j, depth = i + m.end() - 1, 0
        while j < len(s):
            if s[j] == "{" and s[j - 1] != "\\":
                depth += 1
            elif s[j] == "}" and s[j - 1] != "\\":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        i = j + 1


tex_body = strip_caption(tex_body)

# inline author-year citations: Markdown writes "Barnes et al. (2016)" or
# "(Bloomfield et al. 2012)", LaTeX writes \citet{}/\citep{}. Strip only
# parentheticals that contain BOTH a year and a word -- so "(0.056-0.514)" and
# the per-year data tables survive.
md_body = re.sub(r"\([^)]*\b(?:19|20)\d{2}[a-z]?\b[^)]*\)",
                 lambda m: " " if re.search(r"[A-Za-z]{3}", m.group(0)) else m.group(0),
                 md_body)
md_body = re.sub(r"\bet al\.\s*", " ", md_body)
# bare "(2016)" / "(2019a, Paper II)" after a stripped author name
md_body = re.sub(r"\(\s*(?:19|20)\d{2}[a-z]?(?:\s*,[^)]*)?\)", " ", md_body)
# and unparenthesised citation years in running prose, e.g. "Barnes (2016) and
# the Leka/Park series" -> handled above; "Roy 2025" style -> here
md_body = re.sub(r"\b(?:Roy|Barnes|Leka|Park|Bobra|Campi|Camporeale|Nishizuka|"
                 r"Bloomfield|Couvidat|Sande)\b[^.\n]{0,40}?\b(?:19|20)\d{2}[a-z]?\b",
                 " ", md_body)


def normalise(s):
    s = re.sub(r"\\(?:cite[tp]?\*?|ref|label|pageref)\s*(?:\[[^\]]*\])*\{[^}]*\}",
               " ", s)                            # citation keys, cross-refs
    s = s.replace("{,}", "").replace("\\,", "")   # LaTeX thousands / thin space
    s = s.replace("−", "-")          # unicode minus
    s = s.replace("–", "-").replace("—", "-")
    s = re.sub(r"\\[a-zA-Z]+", " ", s)    # LaTeX control sequences
    s = re.sub(r"[{}$~^_&\\]", " ", s)    # LaTeX punctuation
    s = re.sub(r"[|*`#\[\]()]", " ", s)   # Markdown punctuation
    s = s.replace(",", "")                # 1,146 -> 1146
    s = s.replace(" ", " ")
    return s


def numbers(s):
    """Numeric tokens that carry meaning: decimals, integers >= 2 digits."""
    out = Counter()
    for tok in re.findall(r"-?\d+(?:\.\d+)?", normalise(s)):
        v = tok.lstrip("-")
        # skip bare single digits and 2-digit values that are almost always
        # structural (list numbers, section numbers, small counts in prose)
        if "." in v or len(v.split(".")[0]) >= 3:
            out[tok] += 1
    return out


# tokens that are format artefacts rather than claims
IGNORE = {
    "0.75", "1.0", "2.0", "4.0",     # \textwidth fractions, license versions
    "1538", "4357", "4365", "637",   # DOI fragments split by punctuation
    "0004", "2041", "8205", "2014",  # ditto
    "0529", "3847", "1088", "1007", "1029", "1002", "1051",
    "1119", "9780470660713",
}

mn, tn = numbers(md_body), numbers(tex_body)
only_md = {k: v for k, v in (mn - tn).items() if k not in IGNORE}
only_tex = {k: v for k, v in (tn - mn).items() if k not in IGNORE}

print("PAPER_DRAFT.md vs paper.tex — numeric claim parity\n")
print(f"  distinct numeric tokens: md {len(mn)}, tex {len(tn)}")

if only_md:
    print(f"\n  IN MARKDOWN ONLY ({len(only_md)}):")
    for k in sorted(only_md, key=lambda x: -only_md[x]):
        ctx = ""
        m = re.search(r"[^\n]*" + re.escape(k) + r"[^\n]*", md_body)
        if m:
            ctx = m.group(0).strip()[:95]
        print(f"    {k:>12}  x{only_md[k]}   {ctx}")

if only_tex:
    print(f"\n  IN LATEX ONLY ({len(only_tex)}):")
    for k in sorted(only_tex, key=lambda x: -only_tex[x]):
        ctx = ""
        m = re.search(r"[^\n]*" + re.escape(k) + r"[^\n]*", tex_body)
        if m:
            ctx = m.group(0).strip()[:95]
        print(f"    {k:>12}  x{only_tex[k]}   {ctx}")

if not only_md and not only_tex:
    print("\n  No numeric claim appears in one file but not the other.")
    sys.exit(0)

print(f"\n  {len(only_md) + len(only_tex)} one-sided token(s). Compare against the")
print("  KNOWN BENIGN RESIDUE list in this file's docstring; anything not on it")
print("  is a real divergence and must be fixed in one of the two files.")
sys.exit(0)
