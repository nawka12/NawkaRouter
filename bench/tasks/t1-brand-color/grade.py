import json, pathlib, re, sys

run = pathlib.Path(sys.argv[1])
here = pathlib.Path(__file__).parent / "repo"
files = ["index.html", "styles/theme.css", "styles/components/card.css"]
text = {f: (run / f).read_text() if (run / f).exists() else "" for f in files}
low = {f: t.lower() for f, t in text.items()}
allt = "\n".join(low.values())

BRAND = r"(#e11d48|var\(--brand\))"
HOVER = r"(#be123c|var\(--brand-hover\))"


def skeleton(s):
    # strip every color token (hex, rgb(a), var(--brand*)) so we can detect collateral edits
    s = re.sub(r"var\(--brand(-hover)?\)", "#C", s.lower())
    s = re.sub(r"#[0-9a-f]{3,8}\b", "#C", s)
    s = re.sub(r"rgba?\([^)]*\)", "rgb(C)", s)
    return re.sub(r"\s+", " ", s).strip()

checks = {
    "old_hex_gone": "2563eb" not in allt and "1d4ed8" not in allt,
    "theme_vars": re.search(r"--brand:\s*#e11d48", low["styles/theme.css"]) is not None
                  and re.search(r"--brand-hover:\s*#be123c", low["styles/theme.css"]) is not None,
    "card_css": re.search(r"\.card-link\s*\{[^}]*color:\s*" + BRAND, low["styles/components/card.css"]) is not None
                and re.search(r"\.card-link:hover\s*\{[^}]*color:\s*" + HOVER, low["styles/components/card.css"]) is not None,
    # theme-color is an HTML attribute, so it needs the literal; the inline style may use the variable
    "html_inline_and_meta": re.search(r'theme-color"\s+content="#e11d48"', low["index.html"]) is not None
                            and re.search(r"border-bottom:\s*3px solid " + BRAND, low["index.html"]) is not None,
    "rgba_focus_ring": "37, 99, 235" not in allt.replace("37,99,235", "37, 99, 235")
                       and re.search(r"rgba\(\s*225\s*,\s*29\s*,\s*72", allt) is not None,
    "no_collateral": all(skeleton(text[f]) == skeleton((here / f).read_text()) for f in files),
}
print(json.dumps({"passed": sum(checks.values()), "total": len(checks), "checks": checks}))
