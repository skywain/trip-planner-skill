#!/usr/bin/env python3
"""Static QC for a built theme page.

Encodes the defect classes two rounds of design audits kept finding, so the
next theme gets caught by a script instead of by a reviewer:

  1. offline contract   — no external requests may be needed to READ the page
  2. no-JS survival     — hidden-until-revealed content must un-hide without JS
  3. print              — light-on-dark chips must be re-inked, dark themes must
                          reset their tokens, decorations must be hidden
  4. focus              — a :focus-visible rule must exist
  5. link hygiene       — icon-only links need names; target=_blank needs rel
  6. asset sanity       — no loading=lazy on data: URIs, no oversized inlines
  7. inline-style url() — url("…") nested inside a double-quoted style
                          attribute truncates the attribute; every such
                          decoration silently dies (browser computes url("")).
                          Browser-level acceptance must ALSO spot-check that no
                          styled element computes background-image: url("") —
                          that is the runtime symptom of this same class.

Usage: python3 themes/qc.py trips/<trip>/*.html
Exit code is the number of FAILs (0 = clean).
"""
import pathlib
import re
import sys

# hosts a page may legitimately reach out to, and only after the user acts
ALLOWED_HOSTS = ("maps.google.com", "www.google.com/maps", "sunrise-sunset.org")


def check(path):
    s = pathlib.Path(path).read_text()
    style = s[s.index("<style>"):s.index("</style>")] if "<style>" in s else ""
    print_block = ""
    i = style.find("@media print")
    if i >= 0:                       # brace-match instead of guessing indentation:
        j = style.find("{", i)       # a one-line print block is still a print block
        depth, k = 0, j
        while k < len(style):
            if style[k] == "{":
                depth += 1
            elif style[k] == "}":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        print_block = style[j:k]
    fails, warns = [], []

    # 1. offline contract -------------------------------------------------
    eager = re.findall(r'(?:src|href)="(https?://[^"]+)"', s)
    outside = [u for u in eager if not any(h in u for h in ALLOWED_HOSTS)]
    # iframes injected on demand are fine; those live in data-src
    hard = [u for u in outside if 'rel="noopener"' not in s or "<link" in s]
    if any(u for u in outside if u.startswith("http") and "<link" in s):
        fails.append(f"external stylesheet/font: {outside[:2]}")
    if re.search(r'<link[^>]+href="https?://', s):
        fails.append("external <link>")
    if re.search(r'<script[^>]+src="https?://', s):
        fails.append("external <script>")

    # 2. no-JS survival ---------------------------------------------------
    if ".reveal" in style or ".lay" in style:
        hidden = re.findall(r"([.#][\w\-. ]*?)\{[^}]*opacity:0[^}]*\}", style)
        for sel in hidden:
            sel = sel.strip()
            if sel.startswith(".js ") or sel.startswith("html.js"):
                continue                        # correctly gated
            if "reveal" in sel or ("lay" in sel and "data-i" not in sel):
                # is there an un-gated escape hatch?
                if not re.search(r"\.js \.reveal|html\.js \.reveal|"
                                 r'lay\[data-i="0"\][^}]*opacity:1', style):
                    fails.append(f"opacity:0 with no no-JS escape: {sel}")

    # 3. print ------------------------------------------------------------
    if print_block:
        # any rule that paints light text on a dark fill must be neutralised
        light_on_dark = re.findall(r"\{[^}]*background:\s*(?:var\(--(?:hot-ink|amber|rule-hard)\)|#111|#14161A|#0a0a0a)[^}]*color:\s*(?:#f|#e|var\(--paper\)|white)[^}]*\}", style, re.I)
        if light_on_dark and not re.search(r"print-color-adjust:\s*exact|background:\s*(?:none|transparent)\s*!important", print_block):
            fails.append(f"{len(light_on_dark)} light-on-dark fills, print block neither re-inks nor forces colour")
        if re.search(r"--dim:#[0-9a-f]{6}", style, re.I):
            dark_theme = re.search(r"--bg:#0[0-9a-f]", style, re.I)
            if dark_theme and "--dim:" not in print_block:
                fails.append("dark theme does not reset --dim for print")
    else:
        warns.append("no @media print block")

    # 4. focus ------------------------------------------------------------
    if ":focus-visible" not in style:
        fails.append("no :focus-visible rule")

    # 5. link hygiene -----------------------------------------------------
    blank = re.findall(r"<a\b[^>]*target=\"_blank\"[^>]*>", s)
    no_rel = [a for a in blank if "noopener" not in a]
    if no_rel:
        fails.append(f"{len(no_rel)}/{len(blank)} target=_blank without rel=noopener")
    icon_only = re.findall(r'<a\b(?![^>]*aria-label)[^>]*>\s*<svg[^>]*aria-hidden="true"[^>]*>'
                           r'\s*<use[^>]*/>\s*</svg>\s*</a>', s)
    if icon_only:
        fails.append(f"{len(icon_only)} icon-only links with no accessible name")

    # 6. asset sanity -----------------------------------------------------
    lazy_data = re.findall(r'<img[^>]+loading="lazy"[^>]+src="data:', s)
    lazy_data += re.findall(r'<img[^>]+src="data:[^"]{200,}"[^>]+loading="lazy"', s)
    if lazy_data:
        fails.append(f"{len(lazy_data)} data: URIs marked loading=lazy (no-op, hides breakage)")
    if not re.search(r"<h1[ >]", s):
        fails.append("no <h1>")

    # 7. inline-style url() quoting ---------------------------------------
    # style="…url("data:…  — the attribute ends at the second quote, the
    # browser resolves url("") and the decoration dies silently (this killed
    # all 25 journal stamps once). %-encode the URI and write url() unquoted.
    bad_url = re.findall(r'style="[^"]*url\("', s)
    if bad_url:
        fails.append(f'{len(bad_url)} inline style with url(" nested in a '
                     'double-quoted attribute (attribute truncates, image dies)')

    size = pathlib.Path(path).stat().st_size
    name = pathlib.Path(path).name
    status = "FAIL" if fails else ("warn" if warns else "PASS")
    print(f"{status:4s} {name:<26s} {size//1024:>5d}KB")
    for f in fails:
        print(f"       ✗ {f}")
    for w in warns:
        print(f"       · {w}")
    return len(fails)


if __name__ == "__main__":
    # Pass the pages to check explicitly (the shared library has no default
    # deliverables of its own): python3 themes/qc.py trips/x/*.html
    targets = [a for a in sys.argv[1:] if a not in ("-h", "--help")]
    if len(targets) != len(sys.argv[1:]):
        print(__doc__.strip()); sys.exit(0)
    if not targets:
        sys.exit("usage: qc.py <page.html> [more.html ...]")
    sys.exit(sum(check(t) for t in targets))
