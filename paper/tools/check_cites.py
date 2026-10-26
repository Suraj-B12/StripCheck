"""List citation keys used in paper/sections/*.tex that are missing from paper/references.bib.

Usage: python paper/tools/check_cites.py
"""
import pathlib, re

PAPER = pathlib.Path(__file__).resolve().parents[1]
bib = (PAPER / "references.bib").read_text(encoding="utf-8")
have = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib))
total, missing = set(), {}
for tex in sorted((PAPER / "sections").glob("*.tex")):
    text = tex.read_text(encoding="utf-8")
    keys = {k.strip() for group in re.findall(r"\\cite\{([^}]+)\}", text) for k in group.split(",")}
    total |= keys
    gone = sorted(keys - have)
    if gone:
        missing[tex.name] = gone
    placeholders = len(re.findall(r"\\citeneeded\{", text))
    print(f"{tex.name}: {len(keys)} keys cited, {len(gone)} missing, {placeholders} placeholders")
print(f"total distinct keys cited: {len(total)}; bibliography entries: {len(have)}")
for name, keys in missing.items():
    print(f"MISSING in {name}: {', '.join(keys)}")
