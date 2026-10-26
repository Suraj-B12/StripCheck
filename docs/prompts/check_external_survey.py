"""Check external literature-survey outputs against the brief's format and prepare them for citation verification.

Usage: python docs/prompts/check_external_survey.py ["research_notes/External survey"]
Reads every *.md in the folder (not starting with "_"), writes _intake/INTAKE_REPORT.md, one _intake/<file>.bib per input,
and _intake/new_sources.json (sources not already in our verified bibliography) for the verification stage.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "research_notes/External survey")
OURS = ROOT / "research_notes" / "StripCheck literature survey"
OUT = SRC / "_intake"

SECTIONS = ["1. Summary", "2. Sources", "3. Answers to the key questions", "4. What this means for StripCheck",
            "5. Gaps in the literature", "6. Related-work paragraph", "7. Thesis table rows", "8. Corrections to the brief",
            "9. BibTeX", "10. Search log", "11. Self-check"]
REQUIRED = ["type", "authors", "title", "venue", "year", "doi", "url", "accessed", "peer_reviewed", "access_level", "finding", "relevance"]
KEY_RE = re.compile(r"^[a-z][a-z0-9]*\d{4}[a-z0-9]*$")
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
norm = lambda t: re.sub(r"[^a-z0-9]", "", (t or "").lower())


def our_index():
    keys, dois, titles = set(), set(), set()
    for bib in OURS.glob("*.bib"):
        text = bib.read_text(encoding="utf-8", errors="replace")
        keys |= set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", text))
        dois |= {d.lower() for d in re.findall(r"doi\s*=\s*\{([^}]+)\}", text, re.I)}
        titles |= {norm(t) for t in re.findall(r"\btitle\s*=\s*\{(.+?)\},?\s*\n", text, re.I)}
    return keys, dois, titles


def merge_parts(text):
    """Join multi-part answers: drop repeated header blocks of later parts."""
    parts = re.split(r"(?m)^# THEME ", text)
    if len(parts) <= 2:
        return text
    head = "# THEME " + parts[1]
    rest = ["\n".join(l for l in p.splitlines()[1:] if not re.match(r"^(model|browsing|date|part|sources_count):", l)) for p in parts[2:]]
    return head + "\n" + "\n".join(rest)


def check(path, ours):
    raw = path.read_text(encoding="utf-8", errors="replace").replace("== CONTINUED IN PART 2 ==", "")
    text = merge_parts(raw)
    issues, warn = [], []
    m = re.search(r"(?m)^# THEME (T\d+) · (\w+)", text)
    theme = m.group(2) if m else "unknown"
    if not m:
        issues.append("missing '# THEME Txx · key' first line")
    header = dict(re.findall(r"(?m)^(model|browsing|date|sources_count):\s*(.+)$", text))
    for f in ("model", "browsing", "date"):
        if f not in header:
            issues.append(f"header field '{f}' missing")
    pos = [text.find(f"## {s}") for s in SECTIONS]
    for s, p in zip(SECTIONS, pos):
        if p < 0:
            issues.append(f"section '## {s}' missing")
    if all(p >= 0 for p in pos) and pos != sorted(pos):
        issues.append("sections are out of order")
    src_text = text[pos[1]:pos[2]] if pos[1] >= 0 and pos[2] > pos[1] else ""
    sources = {}
    for blk in re.split(r"(?m)^### \[", src_text)[1:]:
        key = blk.split("]", 1)[0].strip()
        fields = dict(re.findall(r"(?m)^([a-z_]+):\s*(.*)$", blk))
        sources[key] = fields
        miss = [f for f in REQUIRED if not fields.get(f, "").strip()]
        if miss:
            issues.append(f"[{key}] missing fields: {', '.join(miss)}")
        if not KEY_RE.match(key):
            issues.append(f"[{key}] key does not follow surnameYEARword")
        doi = fields.get("doi", "").strip()
        if doi and doi.lower() != "none" and not DOI_RE.match(doi):
            issues.append(f"[{key}] malformed DOI '{doi}'")
        if not fields.get("url", "").startswith("http") and (not doi or doi.lower() == "none"):
            issues.append(f"[{key}] has neither a DOI nor an http(s) URL")
        if fields.get("access_level", "").strip() == "memory":
            warn.append(f"[{key}] from memory (unverified by the model)")
    if not sources:
        issues.append("no source blocks found in section 2")
    if header.get("sources_count", "").strip().isdigit() and int(header["sources_count"]) != len(sources):
        warn.append(f"sources_count says {header['sources_count']} but {len(sources)} blocks found")
    bib = re.search(r"```bibtex\s*\n(.*?)```", text, re.S)
    bib_text = bib.group(1) if bib else ""
    bib_keys = re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib_text)
    if not bib:
        issues.append("no ```bibtex block in section 9")
    for k in set(sources) - set(bib_keys):
        issues.append(f"[{k}] has no BibTeX entry")
    for k in set(bib_keys) - set(sources):
        issues.append(f"BibTeX entry '{k}' has no source block")
    cited = set(re.findall(r"\[([a-z][a-z0-9]*\d{4}[a-z0-9]*)\]", text)) | set(re.findall(r"\\cite\{([^}]+)\}", text))
    cited = {c.strip() for group in cited for c in group.split(",")}
    for k in sorted(cited - set(sources)):
        issues.append(f"cited key '{k}' has no source block")
    keys, dois, titles = ours
    new, dup = [], []
    for k, f in sources.items():
        if k in keys or f.get("doi", "").lower() in dois or norm(f.get("title")) in titles:
            dup.append(k)
        else:
            new.append(dict(key=k, theme=theme, file=path.name, **{x: f.get(x, "") for x in REQUIRED + ["evidence", "note"]}))
    return theme, header, issues, warn, sources, bib_text, new, dup


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ours = our_index()
    files = sorted(p for p in SRC.glob("*.md") if not p.name.startswith("_"))
    shown = SRC.relative_to(ROOT) if SRC.is_relative_to(ROOT) else SRC
    report = ["# Intake report for external literature-survey files", "", f"Folder: `{shown}` | files: {len(files)}", ""]
    all_new = []
    for p in files:
        theme, header, issues, warn, sources, bib_text, new, dup = check(p, ours)
        (OUT / (p.stem + ".bib")).write_text(f"% external, unverified: {p.name}\n" + bib_text, encoding="utf-8")
        all_new += new
        verdict = "PASS" if not issues else f"FIX {len(issues)} issue(s)"
        report += [f"## {p.name}", f"- theme: {theme} | model: {header.get('model', '?')} | browsing: {header.get('browsing', '?')} | date: {header.get('date', '?')}",
                   f"- sources: {len(sources)} | already ours: {len(dup)} | new: {len(new)} | format: **{verdict}**"]
        report += [f"  - issue: {i}" for i in issues] + [f"  - warning: {w}" for w in warn] + [""]
    (OUT / "new_sources.json").write_text(json.dumps(all_new, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "INTAKE_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
    print(f"\n{len(all_new)} new sources written to {OUT / 'new_sources.json'} for citation verification")


if __name__ == "__main__":
    main()
