#!/usr/bin/env python3
"""Markdown -> styled HTML -> PDF, using headless Chrome for the last step.

Written for PAPER_TR.md, which needs a readable A4 document rather than a web
page: proper margins, page numbers, tables that do not split across pages, and a
serif face for the body text.

No third-party Python packages: the Markdown subset used by these manuscripts
(headings, bold, italic, inline code, tables, block quotes, rules, ordered and
unordered lists) is handled here directly, so the text is reproduced exactly as
written with nothing reflowed or dropped.

Usage:
    python md2pdf.py PAPER_TR.md
    python md2pdf.py PAPER_TR.md --out custom_name.pdf
"""
import html
import os
import re
import subprocess
import sys

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]

CSS = """
@page { size: A4; margin: 22mm 20mm 22mm 20mm; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  /* Cambria ships with Windows and is designed for print; Times is the
     conventional fallback for a journal article. */
  font-family: "Cambria", "Times New Roman", "Georgia", serif;
  font-size: 10.5pt; line-height: 1.55; color: #14181f; margin: 0;
  hyphens: auto; -webkit-hyphens: auto;
}
h1 {
  font-size: 19pt; line-height: 1.28; margin: 0 0 6pt 0; font-weight: 700;
  letter-spacing: -0.2pt; text-align: center;
}
/* title block: author, affiliation, contact, date, keywords */
.byline {
  text-align: center; margin: 0 0 3pt 0; font-size: 11.5pt; font-weight: 700;
}
.affil {
  text-align: center; margin: 0 0 2pt 0; font-size: 9.5pt; color: #3d4756;
}
.datestamp {
  text-align: center; margin: 8pt 0 14pt 0; font-size: 9.5pt; color: #3d4756;
}
.keywords {
  margin: 0 auto 16pt auto; max-width: 86%; font-size: 9.2pt; color: #2a3340;
  padding: 6pt 10pt; background: #f6f8fa; border: 0.5px solid #dde1e7;
  border-radius: 2px; text-align: left; line-height: 1.45;
}
.titlerule { border: none; border-top: 1.5px solid #14181f; margin: 0 0 14pt 0; }
h2 {
  font-size: 14pt; margin: 22pt 0 7pt 0; padding-bottom: 3pt;
  border-bottom: 1.2px solid #c9ced6; font-weight: 700;
  break-after: avoid; page-break-after: avoid;
}
h3 {
  font-size: 11.5pt; margin: 15pt 0 5pt 0; font-weight: 700; color: #2a3340;
  break-after: avoid; page-break-after: avoid;
}
p { margin: 0 0 8pt 0; text-align: justify; }
strong { font-weight: 700; color: #000; }
em { font-style: italic; }
code {
  font-family: "Consolas", "DejaVu Sans Mono", monospace; font-size: 9pt;
  background: #f1f3f6; padding: 0.5pt 3pt; border-radius: 2px;
  border: 0.5px solid #dde1e7;
}
hr { border: none; border-top: 1px solid #c9ced6; margin: 16pt 0; }
blockquote {
  margin: 9pt 0 11pt 0; padding: 7pt 12pt; background: #f6f8fa;
  border-left: 2.5px solid #8b96a5; font-size: 9.8pt; line-height: 1.5;
  break-inside: avoid; page-break-inside: avoid;
}
blockquote p { margin: 0 0 5pt 0; text-align: left; }
blockquote p:last-child { margin-bottom: 0; }
table {
  border-collapse: collapse; width: 100%; margin: 10pt 0 13pt 0;
  font-size: 9pt; break-inside: avoid; page-break-inside: avoid;
}
th {
  background: #eceff3; text-align: left; font-weight: 700;
  padding: 4pt 6pt; border: 0.5px solid #b8bfc9; font-size: 8.8pt;
}
td { padding: 3.5pt 6pt; border: 0.5px solid #ccd2da; vertical-align: top; }
tr:nth-child(even) td { background: #fafbfc; }
ul, ol { margin: 0 0 9pt 0; padding-left: 20pt; }
li { margin-bottom: 4pt; text-align: justify; }
.subtitle {
  font-size: 12.5pt; color: #3d4756; font-weight: 400; font-style: italic;
  margin: 0 0 14pt 0; line-height: 1.35;
}
"""


# --------------------------------------------------------------- inline spans
def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def convert(md):
    lines = md.split("\n")
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # horizontal rule
        if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", stripped):
            out.append("<hr>")
            i += 1
            continue

        # headings
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1
            continue

        # table: a header row followed by a separator row
        if (stripped.startswith("|") and i + 1 < len(lines)
                and re.fullmatch(r"\|[\s:|-]+\|", lines[i + 1].strip())):
            head = split_row(stripped)
            i += 2
            body = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                body.append(split_row(lines[i].strip()))
                i += 1
            out.append("<table><thead><tr>"
                       + "".join(f"<th>{inline(c)}</th>" for c in head)
                       + "</tr></thead><tbody>")
            for row in body:
                row += [""] * (len(head) - len(row))
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>"
                                            for c in row[:len(head)]) + "</tr>")
            out.append("</tbody></table>")
            continue

        # block quote
        if stripped.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            paras, cur = [], []
            for b in buf:
                if b.strip():
                    cur.append(b.strip())
                elif cur:
                    paras.append(" ".join(cur)); cur = []
            if cur:
                paras.append(" ".join(cur))
            out.append("<blockquote>"
                       + "".join(f"<p>{inline(p)}</p>" for p in paras)
                       + "</blockquote>")
            continue

        # lists
        m = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", line)
        if m:
            ordered = bool(re.fullmatch(r"\d+\.", m.group(2)))
            tag = "ol" if ordered else "ul"
            items, cur = [], None
            while i < len(lines):
                mm = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", lines[i])
                if mm:
                    if cur is not None:
                        items.append(" ".join(cur))
                    cur = [mm.group(3).strip()]
                    i += 1
                elif lines[i].strip() and lines[i].startswith((" ", "\t")) and cur is not None:
                    cur.append(lines[i].strip())
                    i += 1
                else:
                    break
            if cur is not None:
                items.append(" ".join(cur))
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items)
                       + f"</{tag}>")
            continue

        # paragraph: gather until a blank line or a block-level marker.
        # A line ending in two spaces is a hard break, as in standard Markdown.
        buf = []
        while i < len(lines):
            cur = lines[i]
            if (not cur.strip()
                    or cur.strip().startswith(("#", ">", "|"))
                    or re.fullmatch(r"-{3,}|\*{3,}|_{3,}", cur.strip())
                    or re.match(r"^\s*([-*+]|\d+\.)\s+", cur)):
                break
            buf.append(cur.rstrip() + ("\x00" if cur.endswith("  ") else ""))
            i += 1
        if buf:
            text = " ".join(x.strip() for x in buf)
            out.append(f"<p>{inline(text).replace(chr(0), '<br>')}</p>")
    return "\n".join(out)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "PAPER_TR.md"
    out_pdf = os.path.abspath(
        sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv
        else os.path.splitext(src)[0] + ".pdf")

    md = open(src, encoding="utf-8").read()
    body = convert(md)

    # the line immediately after the H1 is a subtitle, not a section heading
    body = body.replace("<h3>Ucuz taban", "<p class='subtitle'>Ucuz taban", 1)
    body = body.replace("modelle başa baş gidiyor</h3>", "modelle başa baş gidiyor</p>", 1)

    # --- title block ------------------------------------------------------
    # Style the author, affiliation, contact, date and keywords the way a
    # journal front page does, rather than leaving them as running paragraphs.
    body = re.sub(r"<p><strong>(Kadir Can Y[ıi]ld[ıi]r[ıi]m)</strong>\s*(.*?)</p>",
                  lambda m: (f"<p class='byline'>{m.group(1)}</p>"
                             + "".join(f"<p class='affil'>{part.strip()}</p>"
                                       for part in re.split(r"<br\s*/?>|\n",
                                                            m.group(2)) if part.strip())),
                  body, count=1, flags=re.S)
    body = re.sub(r"<p><strong>(Taslak s[üu]r[üu]m|Draft v)([^<]*)</strong>([^<]*)</p>",
                  r"<p class='datestamp'><strong>\1\2</strong>\3</p>",
                  body, count=1)
    body = re.sub(r"<p>(<strong>(?:Anahtar kelimeler|Keywords):</strong>.*?)</p>",
                  r"<p class='keywords'>\1</p>", body, count=1, flags=re.S)
    # a rule under the title block, before the first section
    body = body.replace("<blockquote>", "<hr class='titlerule'><blockquote>", 1)

    html_path = os.path.abspath(os.path.splitext(src)[0] + ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(f"<!doctype html><html lang='tr'><head><meta charset='utf-8'>"
                f"<title>{html.escape(os.path.basename(src))}</title>"
                f"<style>{CSS}</style></head><body>{body}</body></html>")
    print(f"HTML : {html_path}")

    chrome = next((c for c in CHROME_CANDIDATES if os.path.exists(c)), None)
    if not chrome:
        print("Chrome/Edge bulunamadi. HTML dosyasini tarayicida acip "
              "Ctrl+P -> 'PDF olarak kaydet' ile ciktisini alabilirsin.")
        return 1

    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
           f"--print-to-pdf={out_pdf}", "file:///" + html_path.replace("\\", "/")]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if os.path.exists(out_pdf):
        print(f"PDF  : {out_pdf}  ({os.path.getsize(out_pdf)/1024:.0f} KB)")
        return 0
    print("PDF uretilemedi.")
    print((r.stderr or "")[-800:])
    return 1


if __name__ == "__main__":
    sys.exit(main())
