"""Extract \\guide, \\dodont, \\pagebudget and SAMPLE blocks from the AAT template into GUIDANCE.md.

Usage: python -I tools/extract_guidance.py TEMPLATE.tex GUIDANCE.md
"""
import re
import sys
from pathlib import Path


def brace_arg(s, i):
    """Return (content, end_index) of the {...} group starting at s[i] == '{'."""
    assert s[i] == "{"
    depth = 0
    for j in range(i, len(s)):
        c = s[j]
        if c == "\\":
            continue
        if c == "{" and s[j - 1] != "\\":
            depth += 1
        elif c == "}" and s[j - 1] != "\\":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
    raise ValueError("unbalanced braces at %d" % i)


def skip_ws(s, i):
    while i < len(s) and s[i] in " \t\r\n":
        i += 1
    return i


def clean(t):
    """Light LaTeX-to-text for guide prose (kept readable, not exhaustive)."""
    t = re.sub(r"(?m)^\s*%.*$", "", t)
    t = t.replace("~", " ").replace("\\%", "%").replace("\\&", "&").replace("\\_", "_")
    t = t.replace("``", '"').replace("''", '"').replace("---", "--").replace("\\ ", " ")
    t = re.sub(r"\\(?:textbf|emph|textit|texttt)\{([^{}]*)\}", r"\1", t)
    t = re.sub(r"\\ref\{([^{}]*)\}", r"[ref:\1]", t)
    t = re.sub(r"\\cite\{([^{}]*)\}", r"[cite:\1]", t)
    t = re.sub(r"\\textbackslash\s*", "\\\\", t)
    t = re.sub(r"[ \t]*\n[ \t]*", " ", t)
    return re.sub(r" {2,}", " ", t).strip()


def items(t):
    parts = [clean(p) for p in re.split(r"\\item\b", t)]
    return [p for p in parts if p]


def main(src, dst):
    s = Path(src).read_text(encoding="utf-8")
    body = s[s.index("\\begin{document}"):]
    pat = re.compile(r"\\(chapter\*?|section\*?|subsection\*?|guide|dodont|pagebudget)\{|\\begin\{(sample|thebibliography)\}|\\appendix\b")
    out = ["# GUIDANCE: what the AAT template expects, chapter by chapter",
           "",
           "Extracted by `tools/extract_guidance.py` from the official BMSCE AAT `Report_Template.tex`.",
           "Guide = \"What to write here\" box; Do / Don't = the two-column box; SAMPLE = the template's",
           "illustrative SolarScreen text (fictional; NEVER copy its numbers or wording into our report).",
           "Section titles below are the exact titles the template expects. The template's instructions page",
           "(length 30 to 50 pages for Ch.1 to Ch.10, formal tone, honesty, IEEE citations, every figure/table",
           "numbered, captioned and referenced before it appears, architecture diagram in TikZ, no format",
           "changes) is summarised at the end.",
           ""]
    i = 0
    in_appendix = False
    while True:
        m = pat.search(body, i)
        if not m:
            break
        kind = m.group(1) or m.group(2) or "appendix"
        if kind == "appendix":
            in_appendix = True
            out += ["", "---", "", "# APPENDICES", ""]
            i = m.end()
            continue
        if kind in ("sample", "thebibliography"):
            end_tag = "\\end{%s}" % kind
            k = body.index(end_tag, m.end())
            raw = body[m.end():k].strip("\n")
            if kind == "sample":
                out += ["**SAMPLE (illustrative only, do not copy):**", "", "```latex", raw, "```", ""]
            else:
                out += ["**Template reference list (replaced by BibTeX; use only keys in paper/references.bib):**",
                        "", "```latex", raw, "```", ""]
            i = k + len(end_tag)
            continue
        a, j = brace_arg(body, m.end() - 1)
        if kind.startswith("chapter"):
            if kind == "chapter*":
                out += ["", "---", "", "## (front matter) %s" % clean(a), ""]
            else:
                out += ["", "---", "", "## %s%s" % ("Appendix: " if in_appendix else "Chapter: ", clean(a)), ""]
        elif kind.startswith("section"):
            out += ["### %s" % clean(a), ""]
        elif kind.startswith("subsection"):
            out += ["#### %s" % clean(a), ""]
        elif kind == "pagebudget":
            out += ["*Expected length: %s pages*" % clean(a), ""]
        elif kind == "guide":
            out += ["**Guide:** " + clean(a), ""]
        elif kind == "dodont":
            j = skip_ws(body, j)
            b, j = brace_arg(body, j)
            out += ["**Do:**"] + ["- " + x for x in items(a)] + ["", "**Don't:**"] + ["- " + x for x in items(b)] + [""]
        i = j
    head = s[:s.index("\\begin{document}")]
    instr_start = body.find("INSTRUCTIONS PAGE")
    instr_end = body.find("TITLE PAGE")
    out += ["", "---", "", "# Template instructions page (verbatim LaTeX)", "", "```latex",
            body[instr_start:instr_end].strip(), "```", ""]
    Path(dst).write_text("\n".join(out) + "\n", encoding="utf-8")
    print("wrote", dst, "lines", len(out), "preamble chars", len(head))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
