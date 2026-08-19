#!/usr/bin/env python3
"""Build the GitHub Pages demo site for the trip-planner skill.

    python3 scripts/build_site.py [--out _site] [--no-download]

Assembles a static directory that serves every showcase theme as a real,
openable page:

    _site/index.html                      the gallery
    _site/examples/<trip>/<page>.html      the eight rendered deliverables
    _site/examples/<trip>/*.geo.json       the plan each page was built from
    _site/examples/<trip>/*.art.json       the art direction each page was built from
    _site/examples/morocco-2026/portal/    nine mp4 clips (downloaded release asset)
    _site/showcase/*.webp                  gallery cover images
    _site/.nojekyll  _site/404.html

Everything the pages need is either inlined in the page itself or copied here,
so the site is fully static. Only the portal footage comes off the network, and
`--no-download` skips it for local dry runs.

Web-optimised copies (the repo pages themselves are untouched):
    every page's data-URI pictures/fonts are written out once to
    _site/assets/<sha1>.<ext> (shared across pages, cacheable) and the page
    references them by relative URL, so a 2.6 MB single-file page becomes a
    ~150 KB document that paints at once while the pictures stream in; images
    past the first few get loading="lazy". A small shim appended to each page
    re-inlines everything as data URIs the first time an export button
    ([data-x-for] / [data-x-page]) is clicked, so the offline PNG export engine
    (which rasterises through <svg><foreignObject> and therefore cannot fetch
    external resources) keeps working exactly as on the original page.
    `--keep-inline` disables the whole step (pages copied verbatim). The
    site copies are for viewing online; a page saved from the site and opened
    from file:// exports without pictures (fetch is blocked there) — the
    single-file originals live in examples/ in the repo.

Runs from anywhere: the repo root is resolved from this file's location.
Python 3.9+, standard library only.
"""

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE_URL = "https://skywain.github.io/trip-planner-skill/"
REPO_URL = "https://github.com/skywain/trip-planner-skill"

PORTAL_ZIP_URL = (
    "https://github.com/skywain/trip-planner-skill/releases/download/"
    "demo-assets-v1/morocco-portal-clips.zip"
)
PORTAL_ZIP_BYTES = 16396582
PORTAL_CLIPS = [
    "ma01-dive.mp4",
    "ma01-ma02-link.mp4",
    "ma02-dive.mp4",
    "ma02-ma03-link.mp4",
    "ma03-dive.mp4",
    "ma03-ma04-link.mp4",
    "ma04-dive.mp4",
    "ma04-ma05-link.mp4",
    "ma05-dive.mp4",
]
PORTAL_DEST = os.path.join("examples", "morocco-2026", "portal")

# One entry per card, in gallery order. `page` doubles as the repo-relative
# source path and the site-relative href — the site mirrors the repo layout.
THEMES = [
    {
        "slug": "illustrated",
        "name": "Illustrated",
        "zh": "插画版",
        "page": "examples/japan-2026/japan-illustrated.html",
        "cover": "showcase/illustrated-cover.webp",
        "trip": "Japan · 8 days · en",
        "blurb": "A painted picture-book on paper: the cover is the menu, each day "
                 "a tinted riso plate with a ghost numeral, and the whole scroll "
                 "exports as one long image.",
        "plan": "examples/japan-2026/japan.geo.json",
        "art": "examples/japan-2026/japan.art.json",
    },
    {
        "slug": "clay",
        "name": "Clay",
        "zh": "黏土版",
        "page": "examples/china-2026/china-clay.html",
        "cover": "showcase/clay-cover.webp",
        "trip": "China · 8 days · en",
        "blurb": "One continuous claymation landscape scrolled end to end, a "
                 "modelled road threading the milestone stones from one day to "
                 "the next.",
        "plan": "examples/china-2026/china.geo.json",
        "art": "examples/china-2026/china.art.json",
    },
    {
        "slug": "noir",
        "name": "Noir",
        "zh": "夜航版",
        "page": "examples/mexico-2026/mexico-noir.html",
        "cover": "showcase/noir-cover.webp",
        "trip": "Mexico · 10 days · en",
        "blurb": "One night-negative tracking shot: full-bleed frames that "
                 "cross-fade as you scroll, monospace body, days dissolving into "
                 "each other.",
        "plan": "examples/mexico-2026/mexico.geo.json",
        "art": "examples/mexico-2026/mexico.art.json",
    },
    {
        "slug": "glass",
        "name": "Glass",
        "zh": "玻璃版",
        "page": "examples/morocco-2026/morocco-glass.html",
        "cover": "showcase/glass-cover.webp",
        "trip": "Morocco · 10 days · en",
        "blurb": "Liquid-glass panes floating over a fixed world of cross-fading "
                 "photographs, one pane per world — the itinerary reads like a "
                 "native travel app.",
        "plan": "examples/morocco-2026/morocco.geo.json",
        "art": "examples/morocco-2026/morocco.art.json",
    },
    {
        "slug": "journal",
        "name": "Journal",
        "zh": "手账版",
        "page": "examples/mexico-2026/mexico-journal.html",
        "cover": "showcase/journal-cover.webp",
        "trip": "Mexico · 10 days · en",
        "blurb": "A vintage travel journal on a dark desk: tape, stamps, postmarks "
                 "and polaroids, with a Day of the Dead week planned around the "
                 "crowd.",
        "plan": "examples/mexico-2026/mexico.geo.json",
        "art": "examples/mexico-2026/mexico.art.json",
    },
    {
        "slug": "zine",
        "name": "Zine",
        "zh": "Zine 版",
        "page": "examples/japan-2026/japan-zine.html",
        "cover": "showcase/zine-cover.webp",
        "trip": "Japan · 8 days · en",
        "blurb": "Torn riso-poster collage with giant vertical two-colour glyphs, "
                 "hand-set headlines and film-grain plates, built like a "
                 "photocopied fan zine.",
        "plan": "examples/japan-2026/japan.geo.json",
        "art": "examples/japan-2026/japan.art.json",
    },
    {
        "slug": "splash",
        "name": "Splash",
        "zh": "闪屏版",
        "page": "examples/china-2026/china-splash.html",
        "cover": "showcase/splash-cover.webp",
        "trip": "China · 8 days · en",
        "blurb": "A game splash screen stretched into a scroll: floating "
                 "day-islands under a chained sky, routed so the Wall and the "
                 "Forbidden City both land on weekdays.",
        "plan": "examples/china-2026/china.geo.json",
        "art": "examples/china-2026/china.art.json",
    },
    {
        "slug": "portal",
        "name": "Portal",
        "zh": "穿越版",
        "page": "examples/morocco-2026/morocco-portal.html",
        "cover": "showcase/portal-cover.webp",
        "trip": "Morocco · 10 days · en",
        "blurb": "Scrolling is flying: five 3D worlds in one unbroken take, dive → "
                 "frame-chained link → dive, the day's plan laid over the footage. "
                 "Let go and it holds; scroll back and it flies in reverse.",
        "plan": "examples/morocco-2026/morocco.geo.json",
        "art": "examples/morocco-2026/morocco.art.json",
        "pill": "video · 16 MB · scroll = fly",
        "hint": "Silent — nothing to mute; autoplay may need one tap.",
    },
]

# Three of the eight cards show a theme whose docs/showcase frames were rendered
# from a different trip than the one shipped under examples/. Those pages are not
# committed — each trip's art.json already carries the second theme's block, so
# the renderers rebuild them here from the committed geo + art. That keeps the
# gallery cover and the page behind it the same edition.
RENDERED = [
    {
        "renderer": "themes/render_clay2.py",
        "plan": "examples/china-2026/china.geo.json",
        "out": "examples/china-2026/china-clay.html",
    },
    {
        "renderer": "themes/render_noir2.py",
        "plan": "examples/mexico-2026/mexico.geo.json",
        "out": "examples/mexico-2026/mexico-noir.html",
    },
    {
        "renderer": "themes/render_zine.py",
        "plan": "examples/japan-2026/japan.geo.json",
        "out": "examples/japan-2026/japan-zine.html",
    },
]
RENDERED_OUT = set(r["out"] for r in RENDERED)

# The Chinese-language editions of clay / noir / zine. They ship verbatim under
# examples/ and stay on the site, linked in a row under the grid.
ZH_PAGES = [
    {
        "page": "examples/turkey-2026/turkey-clay.html",
        "label": "turkey-clay.html",
        "theme": "黏土",
        "plan": "examples/turkey-2026/turkey.geo.json",
        "art": "examples/turkey-2026/turkey.art.json",
    },
    {
        "page": "examples/nordic-2026/nordic-noir.html",
        "label": "nordic-noir.html",
        "theme": "夜航",
        "plan": "examples/nordic-2026/nordic.geo.json",
        "art": "examples/nordic-2026/nordic.art.json",
    },
    {
        "page": "examples/vietnam-2026/vietnam-zine.html",
        "label": "vietnam-zine.html",
        "theme": "Zine",
        "plan": "examples/vietnam-2026/vietnam.geo.json",
        "art": "examples/vietnam-2026/vietnam.art.json",
    },
]

# Pages copied straight out of the repo: the five shipped cards plus the three
# Chinese editions. The other three cards are rendered, not copied.
COPIED_PAGES = ([t["page"] for t in THEMES if t["page"] not in RENDERED_OUT]
                + [z["page"] for z in ZH_PAGES])

# Every example folder whose source JSON travels with the pages.
EXAMPLE_JSON = sorted(set(
    [t["plan"] for t in THEMES] + [t["art"] for t in THEMES]
    + [z["plan"] for z in ZH_PAGES] + [z["art"] for z in ZH_PAGES]
))


# --------------------------------------------------------------------------
# the gallery page
# --------------------------------------------------------------------------

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Trip Planner Skill — live demos</title>
<meta name="description" content="Eight themed, offline, self-contained trip pages rendered by the trip-planner Agent Skill. Open one — it is the real deliverable, no server needed.">
<meta property="og:type" content="website">
<meta property="og:title" content="Trip Planner Skill — live demos">
<meta property="og:description" content="Eight themed, offline, self-contained trip pages rendered by the trip-planner Agent Skill. Open one — it is the real deliverable, no server needed.">
<meta property="og:url" content="__SITE__">
<meta property="og:image" content="__SITE__showcase/hero-grid.webp">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="__SITE__showcase/hero-grid.webp">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&display=swap">
<style>
  :root {
    --paper:   #f6f1e7;
    --paper-2: #efe8da;
    --ink:     #221d18;
    --ink-2:   #5b5147;
    --ink-3:   #8a7f72;
    --rule:    #ddd2be;
    --accent:  #0a7b83;
    --accent-d:#075f66;
    --shadow:  0 1px 2px rgba(34,29,24,.06), 0 8px 24px rgba(34,29,24,.10);
    --shadow-h:0 2px 4px rgba(34,29,24,.08), 0 16px 40px rgba(34,29,24,.16);
    --serif: 'Fraunces', 'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, serif;
    --sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    --mono: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace;
  }

  * { box-sizing: border-box; }

  html { -webkit-text-size-adjust: 100%; }

  body {
    margin: 0;
    background: var(--paper);
    color: var(--ink);
    font-family: var(--sans);
    font-size: 16px;
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
  }

  /* a faint warm grain so the paper is not a flat fill */
  body::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    background:
      radial-gradient(1200px 600px at 12% -8%, rgba(255,255,255,.55), transparent 60%),
      radial-gradient(900px 500px at 92% 4%, rgba(214,190,150,.20), transparent 62%);
  }

  .wrap {
    position: relative;
    z-index: 1;
    max-width: 1180px;
    margin: 0 auto;
    padding: 0 24px;
  }

  a { color: var(--accent); }

  /* ---------- masthead ---------- */

  header { padding: 72px 0 40px; }

  .eyebrow {
    font-family: var(--mono);
    font-size: 12px;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: var(--ink-3);
    margin: 0 0 18px;
  }

  h1 {
    font-family: var(--serif);
    font-weight: 700;
    font-size: clamp(38px, 6.4vw, 68px);
    line-height: 1.04;
    letter-spacing: -.018em;
    margin: 0 0 20px;
    max-width: 16ch;
  }

  h1 .live {
    display: block;
    color: var(--accent);
    font-style: italic;
  }

  .pitch {
    font-size: clamp(17px, 1.6vw, 20px);
    line-height: 1.55;
    color: var(--ink-2);
    max-width: 62ch;
    margin: 0 0 12px;
  }

  .langnote {
    font-size: 14.5px;
    color: var(--ink-3);
    max-width: 62ch;
    margin: 0 0 28px;
  }

  .toplinks {
    display: flex;
    flex-wrap: wrap;
    gap: 10px 12px;
    align-items: center;
  }

  .toplink {
    display: inline-block;
    padding: 8px 15px;
    border: 1px solid var(--rule);
    border-radius: 999px;
    background: rgba(255,255,255,.5);
    color: var(--ink-2);
    text-decoration: none;
    font-size: 14px;
    transition: border-color .15s, color .15s, background .15s;
  }

  .toplink:hover { border-color: var(--accent); color: var(--accent-d); background: #fff; }

  .rule {
    height: 1px;
    background: var(--rule);
    margin: 0 0 40px;
  }

  /* ---------- grid ---------- */

  .grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 34px 26px;
    padding-bottom: 8px;
  }

  .card {
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .shot {
    display: block;
    position: relative;
    aspect-ratio: 16 / 9;
    border-radius: 12px;
    overflow: hidden;
    background: var(--paper-2);
    box-shadow: var(--shadow);
    border: 1px solid rgba(34,29,24,.07);
    transition: transform .18s ease, box-shadow .18s ease;
  }

  .shot img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }

  .card:hover .shot { transform: translateY(-3px); box-shadow: var(--shadow-h); }

  .pill {
    position: absolute;
    left: 10px;
    bottom: 10px;
    font-family: var(--mono);
    font-size: 10.5px;
    letter-spacing: .05em;
    padding: 4px 9px;
    border-radius: 999px;
    background: rgba(20,16,12,.72);
    color: #f4ece0;
    backdrop-filter: blur(4px);
  }

  .card h2 {
    font-family: var(--serif);
    font-weight: 700;
    font-size: 21px;
    letter-spacing: -.01em;
    line-height: 1.25;
    margin: 16px 0 3px;
  }

  .card h2 .zh {
    font-weight: 500;
    color: var(--ink-2);
  }

  .trip {
    font-family: var(--mono);
    font-size: 11.5px;
    letter-spacing: .06em;
    text-transform: uppercase;
    color: var(--ink-3);
    margin: 0 0 9px;
  }

  .blurb {
    font-size: 14.5px;
    line-height: 1.55;
    color: var(--ink-2);
    margin: 0 0 12px;
  }

  .hint {
    font-size: 12.5px;
    line-height: 1.5;
    color: var(--ink-3);
    margin: -6px 0 12px;
  }

  .actions { margin-top: auto; }

  .btn {
    display: inline-block;
    padding: 9px 16px;
    border-radius: 8px;
    background: var(--accent);
    color: #fff;
    text-decoration: none;
    font-size: 14px;
    font-weight: 600;
    transition: background .15s, transform .15s;
  }

  .btn:hover { background: var(--accent-d); transform: translateY(-1px); }

  .src {
    display: block;
    margin-top: 9px;
    font-size: 12.5px;
    color: var(--ink-3);
  }

  .src a { color: var(--ink-3); text-decoration-color: var(--rule); }
  .src a:hover { color: var(--accent-d); }

  /* ---------- the Chinese editions ---------- */

  .also {
    margin-top: 42px;
    padding: 15px 20px;
    border: 1px solid var(--rule);
    border-radius: 10px;
    background: rgba(255,255,255,.45);
    font-size: 14px;
    line-height: 1.7;
    color: var(--ink-2);
  }

  .also strong { color: var(--ink); font-weight: 600; }
  .also .sep { color: var(--ink-3); padding: 0 4px; }
  .also a { text-decoration-color: var(--rule); }
  .also code {
    font-family: var(--mono);
    font-size: 12.5px;
  }

  /* ---------- footer ---------- */

  footer {
    margin-top: 64px;
    padding: 28px 0 72px;
    border-top: 1px solid var(--rule);
    display: flex;
    flex-wrap: wrap;
    gap: 10px 24px;
    justify-content: space-between;
    align-items: baseline;
    font-size: 13px;
    color: var(--ink-3);
  }

  footer a { color: var(--ink-2); }

  @media (max-width: 980px) {
    .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 32px 24px; }
    header { padding: 56px 0 32px; }
  }

  @media (max-width: 560px) {
    .wrap { padding: 0 18px; }
    .grid { grid-template-columns: minmax(0, 1fr); gap: 34px; }
    header { padding: 44px 0 28px; }
  }
</style>
</head>
<body>
<div class="wrap">

<header>
  <p class="eyebrow">Trip Planner Skill · demo site</p>
  <h1>Eight themes.<span class="live">One real page each.</span></h1>
  <p class="pitch">Eight themed, offline, self-contained pages rendered by the trip-planner
  skill — open one, it is the real deliverable, ~1.5&nbsp;MB, no server.</p>
  <p class="langnote">Pages are written in whichever language the trip was planned in. The
  eight below are English; three Chinese editions are linked under the grid. Site copies are web-optimised (pictures load separately, exports still work); the single-file originals are in the repo’s <code>examples/</code>.</p>
  <nav class="toplinks">
    <a class="toplink" href="__REPO__">The repo on GitHub&nbsp;↗</a>
    <a class="toplink" href="__REPO__#showcase">README · Showcase&nbsp;↗</a>
    <a class="toplink" href="__REPO__/blob/main/SKILL.md">SKILL.md&nbsp;↗</a>
  </nav>
</header>

<div class="rule"></div>

<main class="grid">
"""

FOOT = """</main>

<p class="also"><strong>Also in Chinese 中文版</strong>__ZHROW__</p>

<footer>
  <span>Pictures generated with gpt-image-2 · Caveat (OFL) · Lucide (ISC) · MIT · © 2026 skywain</span>
  <span><a href="__REPO__">Back to GitHub&nbsp;↗</a></span>
</footer>

</div>
</body>
</html>
"""


def esc(text):
    """Minimal HTML escaping for attribute and text content."""
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def render_card(theme):
    pill = ""
    if theme.get("pill"):
        pill = '\n      <span class="pill">%s</span>' % esc(theme["pill"])

    hint = ""
    if theme.get("hint"):
        hint = '\n    <p class="hint">%s</p>' % esc(theme["hint"])

    alt = "%s theme cover — %s" % (theme["name"], theme["trip"])

    return """  <article class="card">
    <a class="shot" href="{page}">
      <img src="{cover}" alt="{alt}" loading="lazy" width="640" height="360">{pill}
    </a>
    <h2>{name} <span class="zh">· {zh}</span></h2>
    <p class="trip">{trip}</p>
    <p class="blurb">{blurb}</p>{hint}
    <div class="actions">
      <a class="btn" href="{page}">Open the page ↗</a>
      <span class="src"><a href="{plan}">plan</a> + <a href="{art}">art JSON</a></span>
    </div>
  </article>
""".format(
        page=esc(theme["page"]),
        cover=esc(theme["cover"]),
        alt=esc(alt),
        pill=pill,
        name=esc(theme["name"]),
        zh=esc(theme["zh"]),
        trip=esc(theme["trip"]),
        blurb=esc(theme["blurb"]),
        hint=hint,
        plan=esc(theme["plan"]),
        art=esc(theme["art"]),
    )


def render_zh_row():
    """The one-line pointer to the three Chinese editions, under the grid."""
    bits = []
    for zh in ZH_PAGES:
        bits.append(
            '<span class="sep">·</span> <a href="%s"><code>%s</code></a> (%s)'
            % (esc(zh["page"]), esc(zh["label"]), esc(zh["theme"]))
        )
    return " " + " ".join(bits)


def render_index():
    parts = [HEAD]
    for theme in THEMES:
        parts.append(render_card(theme))
    parts.append(FOOT)
    html = "".join(parts)
    return (html.replace("__ZHROW__", render_zh_row())
                .replace("__SITE__", SITE_URL)
                .replace("__REPO__", REPO_URL))


NOT_FOUND = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Not found — Trip Planner Skill</title>
<style>
  body { margin: 0; min-height: 100vh; display: flex; align-items: center;
         justify-content: center; background: #f6f1e7; color: #221d18;
         font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         text-align: center; padding: 24px; }
  h1 { font-family: 'Iowan Old Style', 'Palatino Linotype', Georgia, serif;
       font-size: 44px; margin: 0 0 10px; }
  p { color: #5b5147; margin: 0 0 22px; }
  a { color: #0a7b83; }
</style>
</head>
<body>
<div>
  <h1>404</h1>
  <p>That page is not on this trip.</p>
  <p><a href="/trip-planner-skill/">Back to the eight demos</a></p>
</div>
</body>
</html>
"""


# --------------------------------------------------------------------------
# building
# --------------------------------------------------------------------------

def copy_file(src, out_root, rel_dest, written):
    """Copy repo file `src` to `out_root/rel_dest`, recording the size."""
    dest = os.path.join(out_root, rel_dest)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(src, dest)
    written.append((rel_dest, os.path.getsize(dest)))


def write_text(out_root, rel_dest, text, written):
    dest = os.path.join(out_root, rel_dest)
    os.makedirs(os.path.dirname(dest) or out_root, exist_ok=True)
    with open(dest, "w", encoding="utf-8") as handle:
        handle.write(text)
    written.append((rel_dest, os.path.getsize(dest)))


def render_siblings(out_root, written):
    """Render the three English sibling pages straight into the site tree.

    Each renderer picks up `<plan>.art.json` beside its plan and resolves
    pictures from themes/assets/, so no extra flags are needed. A non-zero
    exit fails the build — a half-rendered gallery is worse than no site.
    """
    for job in RENDERED:
        renderer = os.path.join(REPO_ROOT, job["renderer"])
        plan = os.path.join(REPO_ROOT, job["plan"])
        dest = os.path.join(out_root, job["out"])
        os.makedirs(os.path.dirname(dest), exist_ok=True)

        if not os.path.exists(renderer):
            raise SystemExit("ERROR: missing renderer %s" % renderer)

        result = subprocess.run(
            [sys.executable, renderer, plan, "-o", dest],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        output = result.stdout.decode("utf-8", "replace").strip()
        if result.returncode != 0:
            raise SystemExit(
                "ERROR: %s failed (exit %d) building %s\n%s"
                % (job["renderer"], result.returncode, job["out"], output)
            )
        if not os.path.exists(dest):
            raise SystemExit(
                "ERROR: %s exited 0 but wrote no file at %s"
                % (job["renderer"], job["out"])
            )
        written.append((job["out"], os.path.getsize(dest)))
        print("  %s -> %s" % (os.path.basename(job["renderer"]), job["out"]))
        if output:
            print("    %s" % output)


DATA_URI_RE = re.compile(
    r"data:(image|font|application)/([a-z0-9.+\-]+);base64,([A-Za-z0-9+/=]+)")
ASSET_EXT = {"svg+xml": "svg", "jpeg": "jpg", "x-font-ttf": "ttf",
             "x-font-woff": "woff", "font-woff": "woff", "font-woff2": "woff2",
             "octet-stream": "bin"}
LAZY_AFTER = 4          # real <img> tags after this many (document order) get loading="lazy"
IMG_TAG_RE = re.compile(r"<img(?=[\s/>])", re.IGNORECASE)
# text ranges the lazy pass must not touch
SKIP_RANGE_RE = re.compile(
    r"<script\b.*?</script>|<!--.*?-->|<template\b.*?</template>|<noscript\b.*?</noscript>",
    re.DOTALL | re.IGNORECASE)
# a payload must end at a real terminator, else the regex only saw a prefix
PAYLOAD_END = "\"')>, \t\r\n"
# the shim can restore exactly these carriers — anything else fails the build
CARRIER_OK_RE = re.compile(r'(?:src|href|xlink:href)=["\']$|url\(["\']?$')
ASSET_REF_RE = re.compile(r"assets/[0-9a-f]{20}\.[a-z0-9]+")
MODULE_ONLY_MARK = 'PAGE_ROOT = ""'     # export_js: whole-page export disabled

# The shim is appended to every externalised page. It does nothing until an
# export button is clicked; then it fetches each asset (browser cache), turns
# it back into a data URI, swaps it into <img src>, SVG <image href>, inline
# style url() and <style> text, drops loading="lazy", waits for decode/fonts,
# and re-dispatches that one click. After that the page is the same DOM the
# offline engine was written for. Per-asset failures cost that one picture,
# not the export; while it works the button is aria-busy and the cursor is
# 'progress'; extra clicks during the fetch are dropped, not queued.
INLINE_SHIM = """
<script data-site-shim>
(function(){
var U=__URLS__,SEL=__SEL__,M=null,P=null,B=null;
function toData(u){return fetch(u).then(function(r){if(!r.ok)throw new Error(u);return r.blob()})
 .then(function(b){return new Promise(function(ok,no){var fr=new FileReader();fr.onload=function(){ok(fr.result)};fr.onerror=no;fr.readAsDataURL(b)})})}
function rep(t){var n=t;for(var k in M){if(n.indexOf(k)>=0){n=n.split(k).join(M[k])}}return n}
function settle(){var w=[];if(document.fonts&&document.fonts.ready)w.push(document.fonts.ready);
 Array.prototype.forEach.call(document.images,function(i){if(!i.complete){w.push(new Promise(function(ok){i.addEventListener('load',ok,{once:true});i.addEventListener('error',ok,{once:true})}))}});
 return Promise.race([Promise.all(w),new Promise(function(ok){setTimeout(ok,2500)})])}
function inlineAll(){if(P)return P;P=Promise.all(U.map(function(u){return toData(u).then(function(d){return[u,d]},function(){return null})}))
 .then(function(pairs){M={};var miss=0;pairs.forEach(function(p){if(p){M[p[0]]=p[1]}else{miss++}});
 if(miss===U.length&&U.length){P=null;throw new Error('offline')}
 Array.prototype.forEach.call(document.querySelectorAll('img'),function(im){var s=im.getAttribute('src');if(s&&M[s]){im.setAttribute('src',M[s])}im.removeAttribute('loading')});
 Array.prototype.forEach.call(document.querySelectorAll('image'),function(im){var s=im.getAttribute('href')||im.getAttribute('xlink:href');if(s&&M[s]){im.setAttribute('href',M[s])}});
 Array.prototype.forEach.call(document.querySelectorAll('[style]'),function(el){var s=el.getAttribute('style');if(s&&s.indexOf('url(')>=0){var n=rep(s);if(n!==s)el.setAttribute('style',n)}});
 Array.prototype.forEach.call(document.querySelectorAll('style'),function(st){var t=st.textContent||'';var n=rep(t);if(n!==t)st.textContent=n});
 window.__siteMissing=miss;
 return settle().then(function(){window.__siteInlined=true})});return P}
function busy(on){document.documentElement.style.cursor=on?'progress':'';if(B){if(on){B.setAttribute('aria-busy','true')}else{B.removeAttribute('aria-busy')}}}
document.addEventListener('click',function(e){
 if(window.__siteInlined||!e.target||!e.target.closest)return;
 var b=e.target.closest(SEL);if(!b)return;
 e.stopImmediatePropagation();e.preventDefault();
 if(B)return;
 B=b;busy(true);
 inlineAll().then(function(){busy(false);var t=B;B=null;t.click()},function(){busy(false);var t=B;B=null;window.__siteInlined=true;t.click();window.__siteInlined=false});
},true);
window.__siteInline=inlineAll;
})();
</script>
"""


def externalize_page(out_root, rel_page, written, stats):
    """Rewrite one copied page in place: data URIs -> _site/assets/<sha1>.<ext>,
    lazy-load the later <img>s, append the re-inline shim. Returns the number
    of data URIs actually moved out. The repo file is never touched. Fails the
    build (SystemExit) on anything the shim could not restore at export time."""
    path = os.path.join(out_root, rel_page)
    with open(path, "r", encoding="utf-8") as handle:
        html = handle.read()
    original = html
    page_dir = os.path.dirname(rel_page)
    rel_assets = os.path.relpath("assets", page_dir).replace(os.sep, "/")
    assets_dir = os.path.join(out_root, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    urls = []
    moved = [0]

    # tripwire 1: every base64 data URI must sit in a carrier the shim restores
    for m in DATA_URI_RE.finditer(original):
        ctx = original[max(0, m.start() - 12):m.start()]
        if not CARRIER_OK_RE.search(ctx):
            raise SystemExit(
                "ERROR: %s has a data URI in a carrier the re-inline shim cannot "
                "restore (context %r) — extend the shim or build with --keep-inline"
                % (rel_page, ctx))

    def swap(match):
        kind, subtype, b64 = match.groups()
        nxt = match.string[match.end():match.end() + 1]
        if nxt and nxt not in PAYLOAD_END:
            return match.group(0)          # payload continues (wrapped / URL-safe) — leave inline
        try:
            raw = base64.b64decode(b64, validate=True)
        except (ValueError, TypeError):
            return match.group(0)          # not real base64 — leave it alone
        ext = ASSET_EXT.get(subtype, subtype.split("+")[0])
        name = "%s.%s" % (hashlib.sha1(raw).hexdigest()[:20], ext)
        dest = os.path.join(assets_dir, name)
        if not os.path.exists(dest):
            with open(dest, "wb") as out:
                out.write(raw)
            written.append((os.path.join("assets", name), len(raw)))
            stats["new_assets"] += 1
        else:
            stats["shared_hits"] += 1
        url = rel_assets + "/" + name
        if url not in urls:
            urls.append(url)
        moved[0] += 1
        return url

    before = len(html.encode("utf-8"))
    html = DATA_URI_RE.sub(swap, html)
    if moved[0] == 0:
        return 0                             # portal: nothing inline, keep verbatim

    # tripwire 2: no asset reference may have landed inside a <script> (the
    # shim cannot rewrite JS strings) — the shim itself is appended later
    for m in re.finditer(r"<script\b.*?</script>", html, re.DOTALL | re.IGNORECASE):
        if ASSET_REF_RE.search(m.group(0)):
            raise SystemExit(
                "ERROR: %s: an externalised asset is referenced inside a <script> "
                "block; the export shim cannot restore it" % rel_page)

    # lazy-load the pictures past the first few (cover + first day keep
    # priority); <img in scripts / comments / templates / noscript is skipped
    skip = [(m.start(), m.end()) for m in SKIP_RANGE_RE.finditer(html)]
    seen = [0]

    def lazy(match):
        pos = match.start()
        if any(a <= pos < b for a, b in skip):
            return match.group(0)
        tag_end = html.find(">", pos)
        if tag_end != -1 and re.search(r"\sloading=", html[pos:tag_end]):
            return match.group(0)            # already declares its own policy
        seen[0] += 1
        if seen[0] > LAZY_AFTER:
            return '<img loading="lazy"'
        return match.group(0)
    html = IMG_TAG_RE.sub(lazy, html)

    module_only = MODULE_ONLY_MARK in html
    sel = "[data-x-for]" if module_only else "[data-x-for],[data-x-page]"
    shim = (INLINE_SHIM.replace("__URLS__", json.dumps(urls))
                       .replace("__SEL__", json.dumps(sel)))
    if "</body>" in html:
        html = html.replace("</body>", shim + "</body>", 1)
    else:
        html = html + shim
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(html)
    after = len(html.encode("utf-8"))
    for i, row in enumerate(written):
        if row[0] == rel_page:
            written[i] = (rel_page, after)
    stats["bytes_before"] += before
    stats["bytes_after"] += after
    print("  %s: %s -> %s, %d data URIs -> %d assets%s"
          % (rel_page, human(before), human(after), moved[0], len(urls),
             " (module-only export)" if module_only else ""))
    return moved[0]


def download_zip(url, expect_bytes, attempts=3):
    """Fetch the release asset, following redirects. Returns the bytes."""
    last = None
    for attempt in range(1, attempts + 1):
        try:
            print("  fetching %s (attempt %d/%d)" % (url, attempt, attempts))
            request = urllib.request.Request(
                url, headers={"User-Agent": "trip-planner-skill build_site.py"}
            )
            # urlopen follows 3xx redirects for http/https by default.
            with urllib.request.urlopen(request, timeout=120) as response:
                blob = response.read()
            if expect_bytes and len(blob) != expect_bytes:
                raise IOError(
                    "size mismatch: got %d bytes, expected %d"
                    % (len(blob), expect_bytes)
                )
            print("  got %s bytes" % format(len(blob), ","))
            return blob
        except (urllib.error.URLError, IOError, OSError) as exc:
            last = exc
            print("  failed: %s" % exc)
            if attempt < attempts:
                delay = 2 * attempt
                print("  retrying in %ds" % delay)
                time.sleep(delay)
    raise SystemExit(
        "ERROR: could not download the portal footage after %d attempts (%s).\n"
        "       The portal page renders blank without its clips.\n"
        "       Re-run with --no-download only for a local dry run."
        % (attempts, last)
    )


def extract_clips(blob, out_root, written):
    """Unzip the flat clip archive into _site/examples/morocco-2026/portal/."""
    dest_dir = os.path.join(out_root, PORTAL_DEST)
    os.makedirs(dest_dir, exist_ok=True)

    tmp_zip = os.path.join(out_root, ".portal-clips.zip")
    with open(tmp_zip, "wb") as handle:
        handle.write(blob)

    try:
        with zipfile.ZipFile(tmp_zip) as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                name = os.path.basename(info.filename)
                if not name.endswith(".mp4"):
                    continue
                target = os.path.join(dest_dir, name)
                with archive.open(info) as source:
                    with open(target, "wb") as handle:
                        shutil.copyfileobj(source, handle)
                written.append((os.path.join(PORTAL_DEST, name),
                                os.path.getsize(target)))
    finally:
        os.remove(tmp_zip)

    missing = [c for c in PORTAL_CLIPS
               if not os.path.exists(os.path.join(dest_dir, c))]
    if missing:
        raise SystemExit(
            "ERROR: the portal archive is missing %d expected clip(s): %s"
            % (len(missing), ", ".join(missing))
        )


def build(out_root, download=True, externalize=True):
    out_root = os.path.abspath(out_root)
    if os.path.exists(out_root):
        shutil.rmtree(out_root)
    os.makedirs(out_root)

    written = []

    # 1. the gallery
    write_text(out_root, "index.html", render_index(), written)

    # 2. the pages that ship verbatim, same relative paths as in the repo
    print("shipped pages:")
    for rel in COPIED_PAGES:
        src = os.path.join(REPO_ROOT, rel)
        if not os.path.exists(src):
            raise SystemExit("ERROR: missing example page %s" % src)
        copy_file(src, out_root, rel, written)
        print("  %s" % rel)

    # 2b. the three English siblings, rendered from the committed geo + art
    print("rendered pages:")
    render_siblings(out_root, written)

    # 2c. web-optimise every page copy: pictures out to assets/, shim in
    if externalize:
        print("externalising data URIs:")
        stats = {"new_assets": 0, "shared_hits": 0, "bytes_before": 0, "bytes_after": 0}
        pages = list(COPIED_PAGES) + [job["out"] for job in RENDERED]
        for rel in pages:
            externalize_page(out_root, rel, written, stats)
        print("  assets/: %d files written, %d shared references; pages %s -> %s"
              % (stats["new_assets"], stats["shared_hits"],
                 human(stats["bytes_before"]), human(stats["bytes_after"])))
    else:
        print("externalising data URIs: SKIPPED (--keep-inline)")

    # 3. the plan + art sources beside them
    for rel in EXAMPLE_JSON:
        src = os.path.join(REPO_ROOT, rel)
        if not os.path.exists(src):
            raise SystemExit("ERROR: missing example source %s" % src)
        copy_file(src, out_root, rel, written)

    # 4. gallery cover images
    showcase_dir = os.path.join(REPO_ROOT, "docs", "showcase")
    covers = sorted(f for f in os.listdir(showcase_dir) if f.endswith(".webp"))
    if not covers:
        raise SystemExit("ERROR: no webp files in docs/showcase/")
    for name in covers:
        copy_file(os.path.join(showcase_dir, name), out_root,
                  os.path.join("showcase", name), written)
    print("showcase: %d webp" % len(covers))

    # 5. portal footage
    if download:
        print("portal footage:")
        blob = download_zip(PORTAL_ZIP_URL, PORTAL_ZIP_BYTES)
        extract_clips(blob, out_root, written)
        print("  unzipped %d clips into %s/" % (len(PORTAL_CLIPS), PORTAL_DEST))
    else:
        print("portal footage: SKIPPED (--no-download)")
        print("  NOTICE: examples/morocco-2026/morocco-portal.html will render")
        print("          blank without portal/*.mp4. This build is a dry run —")
        print("          do not deploy it.")

    # 6. housekeeping
    write_text(out_root, ".nojekyll", "", written)
    write_text(out_root, "404.html", NOT_FOUND, written)

    return out_root, written


def human(size):
    if size >= 1024 * 1024:
        return "%.2f MB" % (size / 1024.0 / 1024.0)
    if size >= 1024:
        return "%.1f KB" % (size / 1024.0)
    return "%d B" % size


def print_summary(out_root, written):
    written = sorted(written, key=lambda row: row[0])
    width = max([len(row[0]) for row in written] + [20])
    print("")
    print("%-*s  %10s" % (width, "file", "size"))
    print("-" * (width + 12))
    for rel, size in written:
        print("%-*s  %10s" % (width, rel, human(size)))
    print("-" * (width + 12))
    total = sum(row[1] for row in written)
    print("%-*s  %10s" % (width, "%d files" % len(written), human(total)))
    print("")
    print("site: %s" % out_root)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Build the GitHub Pages demo site."
    )
    parser.add_argument("--out", default="_site",
                        help="output directory (default: _site, relative to the repo root)")
    parser.add_argument("--no-download", action="store_true",
                        help="skip the portal footage download (local dry runs only)")
    parser.add_argument("--keep-inline", action="store_true",
                        help="copy the pages verbatim (no data-URI externalisation, no shim)")
    args = parser.parse_args(argv)

    out = args.out
    if not os.path.isabs(out):
        out = os.path.join(REPO_ROOT, out)

    out_root, written = build(out, download=not args.no_download,
                              externalize=not args.keep_inline)
    print_summary(out_root, written)
    return 0


if __name__ == "__main__":
    sys.exit(main())
