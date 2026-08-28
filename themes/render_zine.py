#!/usr/bin/env python3
"""Zine collage renderer — gathered-scenes zine (拼贴 zine).

Identity (the four axes, distinct from every sibling theme):
  * organising principle — paper poster planes: each chapter is one large
    flat colour field (cobalt / tomato / mustard / cream / ink, sampled from
    mock-zine.png), glued to the next with a torn-paper edge (seeded jagged
    clip-path x 3 layers: cast shadow, white fibre core, colour sheet);
  * interaction — one vertical scroll; big printed numerals 01–NN are the
    chapter index (thin red hand-drawn ring marks the current one);
  * type voice — structured sans; chapter titles set vertical (vertical-rl)
    with a riso misregistration shadow; everything small is letterspaced;
  * shape language — torn paper, flat colour, hairline rules, small squares.
    No cards, no rounded corners, no capsules.

Every section carries real imagery (owner round-2 note): riso posters as
torn prints — one poster-grade chapter anchor for every scenery day — Kodak
prints re-treated the zine way — white paper mat + crop marks + riso offset
shadow + mono/duotone CSS filters + halftone dots on rectangular prints —
plus gouache cut-outs as stickers and paper props (boarding pass / luggage
tag / ticket) in the colophon. The single-line ink drawings stay and mix
with the prints, the way the mock's ridge line grows out of the El Capitan
photo. All decoration (crop marks, barcode, rubber stamp, halftone) is
hand-written CSS/SVG. WHICH picture goes on WHICH day is the trip's choice
and lives in art.json; the treatments are the theme's.

PNG export (theme_common.export_js): every chapter is a module (#dN —
band + poster + timeline as one sheet), the colophon is one, and the whole
zine exports via the 生成长图 plate docked in the contents page. Buttons are
solid riso plates — red sheet over a blue offset plate, square corners —
half-inked at rest, pulled into register on hover. Icons are inlined at
build time (no sprite) so <use> refs cannot go blank inside the capture.

Usage: python3 render_zine.py <plan.geo.json> [--art <file>|none] [--assets DIR ...] -o out.html

ART CONTRACT (what this renderer reads from the trip's art.json — schema in
ART-SCHEMA.md — and how it degrades when a field is missing; the renderer
never carries a place, a date or a picture name of its own):

  common (themes.zine.cover.* overrides cover.* per key)
    cover.zh          the cover <h1> (2 big vertical glyphs) and the "<zh> ZINE"
                      issue name on every page number and in the colophon
                      → cover.kick, then "拼贴"
    cover.en          English name of the issue: cover eyebrow "<kick> · <en>
                      ZINE · <year>" and the cover edge line "<en> · N DAYS ·
                      <kick_en>"                        → "COLLAGE"
    cover.credit      poem source under the cover dates, small letterspaced
                      ("「万人如海一身藏」—— 苏轼")   → not emitted
    cover.kick        <title> prefix ("<kick> <year> · Zine 拼贴版"), eyebrow
                      prefix, export filename prefix (en page: cover.kick_en
                      wins in <title>/filenames — title_kick) → omitted from each
    cover.kick_en     CAPS trip word on the cover edge line and inside the
                      行前须知 rubber stamp ("READ BEFORE DEPARTURE · <kick_en> ·")
                      → omitted
    days[d].theme     4-char chapter title (vertical, rail, contents, export
                      label)                          → the plan's city
    brief_titles      {plan.brief key: title} for the 行前须知 blocks, over
                      theme_common.BRIEF_TITLES      → shared defaults;
                                                        unknown keys print raw
  themes.zine
    cover.photo       {stem, caption, alt, tear_seed} the torn cover print;
                      caption = letterspaced CAPS side line; alt defaults to
                      caption; tear_seed seeds the torn bottom edge (default
                      "cover-<stem>")                  → no cover print
    toc_strip         [{stem, rot}] small gouache cut-outs (sm variant) lined
                      up above the contents           → no strip
    props             {legs|hotels|checklist: {stem, rot}} paper prop floated
                      in that colophon section        → none
    days[d].poster    {stem, caption, alt, side?} the poster-grade torn print
                      anchoring the chapter. side pl|pr; missing → posters
                      alternate pl / pr down the book (kit rhythm) → none
    days[d].photo     {stem, caption, alt, treat?, rot, side?} one Kodak print
                      on the fibre mat; treat "mono" = B&W + red offset shadow;
                      side default pr — but on a POSTER day the print always
                      takes the poster's opposite side, clears it, and is
                      emitted after the timeline (see pola_figure) → none
    days[d].pair      {prints:[{stem, alt, rot, treat?} x2], caption, rot}
                      big + small overlapping prints as one figure; treat on
                      a print = img class ("duo-blue" = blue duotone); side
                      rule as photo; wins over photo when both are given;
                      either file missing → nothing  → none
    days[d].sticker   {stem, size?, side?, rot} gouache cut-out pasted near
                      the line drawing; size md (default) | sm; side sl|sr
                      (default sl)                     → none
    days[d].band      {stem, caption, alt, tear_seed} full-bleed torn band
                      photo closing the chapter (tear_seed default
                      "band-<stem>")                   → none
    days[d].lineart   name of a KIT sketch (below) or {"svg": "<inner svg
                      markup>"} in the same voice (640x190 viewBox, stroked
                      currentColor)                    → no drawing

  KIT (the theme's own — art picks by name, never supplies markup):
    colour bands      ink / blue / yellow / red cycle down the book so two
                      adjacent chapters never share a band
    print treatments  mono (figure), duo-blue (img)
    line-art sketches flight (dashed arc + plane) · skyline · stadium ·
                      flats (road + sun) · peaks (ridge over a lake) · bridge
                      · ridge (granite ridge) · surf (waves + palm) · volcano
                      · sunrise
    decorations       torn edges, rail chips, halftone screen, crop marks,
                      barcode issue strip, rubber stamp, riso export plates
"""
import argparse
import datetime
import pathlib
import random
import re
import urllib.parse

from theme_common import (Art, LUCIDE, T, add_art_arg, asset_count, brief_titles,
                          data_uri, day_embed_url, esc, et, export_js, export_prefix, ic,
                          init_lang, lang, load_art, load_plan, short_dates, theme_name, title_head,
                          title_kick)

HERE = pathlib.Path(__file__).parent
THEME = "zine"
ART = Art()        # replaced in main() with the trip's art.json

# ------------------------------------------------------------------ i18n --
# The zine's own voice: cover fallback word, rail / contents wording, chip
# tags, the rubber-stamp word, tooltips, ledger heads, colophon footer.
# Shared UI words (tags, section names, save buttons, walk / rain / late-cut
# …) come from theme_common.T(). zh values are the page's historical bytes —
# never edit one without rebuilding the US baseline. The chapter kicker's
# weekday stays the zine's own CAPS English (FRI) in every language.
L = {
    "zh": {
        "cover_fallback": "拼贴", "page_title": "Zine 拼贴版",
        "rail_aria": "章节索引", "rail_day": "第{i}天 · {theme}",
        "rail_app": "附录 · 版权页", "rail_app_glyph": "附",
        "toc_app_title": "版权页 · 索引", "toc_app_sub": "航段 · 住宿 · 预算 · 清单 · 须知",
        "tag_swap": "可换", "nav_to": "导航到 {what}",
        "day_route": "整日路线", "hop_aria": "第{n}跳导航",
        "map_ph": "地图需联网加载 —— 离线时请用下方逐跳链接",
        "mapfold": "路线地图 · 逐跳导航",
        "note": "注", "travel_day": "旅途日",
        "tip_day": "把这一天存成图片,可发朋友圈",
        "tip_page_aria": "把整本 zine 生成一张长图",
        "tip_page": "把整本 zine 存成一张长图,可发朋友圈",
        "tip_appendix": "把附录存成图片,可发朋友圈",
        "backup": "备选",
        "th_item": "项目", "th_pp": "每人", "th_total": "总计", "th_note": "注", "total": "合计",
        "stamp_word": "行前须知",
        "stamp_toc": "目录", "cue": "翻开目录",
        "h_toc": "目 录", "h_app": "附 录",
        "sec_legs": "航段速览", "sec_checklist": "行前清单",
        "fx": "汇率",
        "footer": "日出日落:sunrise-sunset.org · 照片与设计稿由 AI 生成,仅作示意 ·\n      价格以预订渠道实时为准",
    },
    "en": {
        "cover_fallback": "COLLAGE", "page_title": "Zine",
        "rail_aria": "Chapter index", "rail_day": "Day {i} · {theme}",
        "rail_app": "Appendix · colophon", "rail_app_glyph": "AP",
        "toc_app_title": "Colophon · index", "toc_app_sub": "Flights · Stays · Budget · Checklist · Notes",
        "tag_swap": "swap", "nav_to": "Navigate to {what}",
        "day_route": "Full-day route", "hop_aria": "Hop {n} navigation",
        "map_ph": "The map needs internet — offline, use the hop links below",
        "mapfold": "Route map · hop-by-hop",
        "note": "Note", "travel_day": "Travel day",
        "tip_day": "Save this day as an image to share",
        "tip_page_aria": "Render the whole zine as one long image",
        "tip_page": "Save the whole zine as one long image to share",
        "tip_appendix": "Save the appendix as an image to share",
        "backup": "Backup",
        "th_item": "Item", "th_pp": "Per person", "th_total": "Total", "th_note": "Note", "total": "Total",
        "stamp_word": "NOTES",
        "stamp_toc": "TOC", "cue": "OPEN CONTENTS",
        "h_toc": "Contents", "h_app": "Appendix",
        "sec_legs": "Flights & legs", "sec_checklist": "Checklist",
        "fx": "FX",
        "footer": "Sunrise/sunset: sunrise-sunset.org · Photos and layouts are AI-generated, for illustration only ·\n      Prices are live at the booking channel",
    },
}


def t(k):
    return L.get(lang(), L["zh"]).get(k, L["zh"][k])

# PNG-export clones are rendered inside an <img src="data:image/svg+xml">
# document where <use href="#i-x"> cannot reach a sprite that lives outside
# the captured module — every icon would silently vanish from the shared
# picture. So the built page carries no sprite at all: this build-time pass
# swaps each ic()/et() <use> reference for the lucide path body itself.
_USE_RE = re.compile(
    r'<svg class="([^"]*)" aria-hidden="true"><use href="#i-([\w-]+)"/></svg>')


def inline_icons(html):
    return _USE_RE.sub(
        lambda m: (f'<svg class="{m.group(1)}" viewBox="0 0 24 24" '
                   f'aria-hidden="true">{LUCIDE[m.group(2)]}</svg>'), html)

# The mock's interior pages are CREAM with colour planes as anchors — full
# saturated pages belong to the cover only. Every day body sits on paper;
# the day's colour lives in a torn header band (adjacent bands never repeat:
# the cycle starts on ink and ends on red, so wrapping never repeats either).
BAND = ["ink", "blue", "yellow", "red", "blue", "ink",
        "red", "yellow", "blue", "ink", "red"]
BANDVAR = {"blue": "var(--blue)", "yellow": "var(--yellow)",
           "red": "var(--red)", "ink": "var(--inkf)"}


def band_for(i):
    return BAND[(i - 1) % len(BAND)]


# poster-grade torn prints: one 1024x1536 riso poster anchors a scenery
# chapter (art: days[d].poster); sides alternate pl/pr down the book.
#
# Kodak prints re-treated the zine way (mat + crop marks + riso offset;
# treat "mono" = B&W with a red misregistration shadow; art: days[d].photo,
# or days[d].pair for a big+small two-print cluster). On days that also
# carry a poster the print keeps the OPPOSITE float side plus "clr"
# (clear:both) AND is emitted AFTER the timeline: the timeline rows are
# display:grid boxes (independent formatting contexts), and a grid box
# whose top lands in the poster's bottom-margin sliver gets narrowed
# against BOTH floats at once — Chrome squeezed one row to 46px (one
# character per line). Below the timeline only one float can ever be live,
# so the rows never see two floats.
OPPOSITE = {"pl": "pr", "pr": "pl"}


# ---------------------------------------------------------------- tears ----
def _tear_polys(seed, lo=12.0, hi=58.0, drift=13.0):
    """Three stacked jagged polygons (shadow / fibre / colour sheet)."""
    rnd = random.Random(seed)
    n = rnd.randint(26, 34)
    ys, y = [], rnd.uniform(28, 42)
    for _ in range(n + 1):
        y = max(lo, min(hi, y + rnd.uniform(-drift, drift)))
        ys.append(y)
    pts = [(100.0 * i / n, ys[i]) for i in range(n + 1)]

    def poly(dy):
        seq = ", ".join(f"{x:.1f}% {max(0.0, min(100.0, p + dy)):.1f}%"
                        for x, p in pts)
        return f"polygon(0% 100%, {seq}, 100% 100%)"
    return poly(-20), poly(-9), poly(0)


def tear(seed, bg=None):
    """bg overrides the sheet colour — the band tears over the previous
    chapter's cream, then cream tears back over the band's bottom."""
    s, f, c = _tear_polys(seed)
    extra = f"--bg:{bg};" if bg else ""
    return (f'<div class="tear" aria-hidden="true" '
            f'style="{extra}--t0:{s};--t1:{f};--t2:{c}">'
            '<i class="i0"></i><i class="i1"></i><i class="i2"></i></div>')


def torn_photo_polys(seed):
    """Photo torn along its bottom edge: (img clip, fibre clip)."""
    rnd = random.Random(seed)
    n = rnd.randint(16, 22)
    ys, y = [], rnd.uniform(88, 92)
    for _ in range(n + 1):
        y = max(83.0, min(95.0, y + rnd.uniform(-3.5, 3.5)))
        ys.append(y)
    pts = [(100.0 - 100.0 * i / n, ys[i]) for i in range(n + 1)]

    def poly(dy):
        seq = ", ".join(f"{x:.1f}% {min(100.0, p + dy):.1f}%" for x, p in pts)
        return f"polygon(0% 0%, 100% 0%, {seq})"
    return poly(0), poly(3.2)


def torn_band_polys(seed):
    """Full-bleed band torn along its top edge: (img clip, fibre clip)."""
    rnd = random.Random(seed)
    n = rnd.randint(24, 30)
    ys, y = [], rnd.uniform(8, 14)
    for _ in range(n + 1):
        y = max(3.0, min(18.0, y + rnd.uniform(-3.5, 3.5)))
        ys.append(y)
    pts = [(100.0 * i / n, ys[i]) for i in range(n + 1)]

    def poly(dy):
        seq = ", ".join(f"{x:.1f}% {max(0.0, p + dy):.1f}%" for x, p in pts)
        return f"polygon(0% 100%, {seq}, 100% 100%)"
    return poly(0), poly(-2.6)


def chip_poly(seed):
    """Small torn paper scrap for the rail numerals."""
    rnd = random.Random(seed)
    j = lambda a, b: f"{rnd.uniform(a, b):.0f}%"
    return ("polygon(" + ", ".join([
        f"{j(2, 9)} {j(8, 18)}", f"{j(38, 60)} {j(0, 7)}", f"{j(90, 97)} {j(4, 14)}",
        f"{j(93, 99)} {j(42, 58)}", f"{j(88, 96)} {j(85, 96)}", f"{j(40, 62)} {j(92, 100)}",
        f"{j(3, 11)} {j(86, 96)}", f"{j(0, 6)} {j(40, 60)}"]) + ")")


# ------------------------------------------------------------- textures ----
def noise_uri():
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' width='260' height='260'>"
           "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.8'"
           " numOctaves='2' stitchTiles='stitch'/>"
           "<feColorMatrix type='matrix' values='0 0 0 0 0.09 0 0 0 0 0.07"
           " 0 0 0 0 0.04 0 0 0 0.55 0'/></filter>"
           "<rect width='100%' height='100%' filter='url(#n)'/></svg>")
    return "data:image/svg+xml," + urllib.parse.quote(svg)


def ring_uri(color="%23C22C15"):
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 44'>"
           "<path d='M24 5 C37 2 45 11 43 23 C41 35 31 41 19 39 C8 37 3 27 6 16"
           " C9 8 16 7 24 5' fill='none' stroke='" + color +
           "' stroke-width='2.2' stroke-linecap='round'/></svg>")
    return "data:image/svg+xml," + urllib.parse.quote(svg, safe="%'")


# ------------------------------------------------------------- line art ----
# the theme's single-line ink sketches; art picks one by name (days[d].lineart)
LA = {
    "flight": ('<path d="M14 168 C150 44 420 30 620 138" stroke-dasharray="1 11"/>'
        '<circle cx="14" cy="168" r="3.5"/><circle cx="620" cy="138" r="3.5"/>'
        '<g transform="translate(300,18) scale(2.2)" stroke-width="1.1">'
        '<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5'
        'L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1'
        ' 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/></g>'),
    "skyline": ('<path d="M20 170 V120 h26 v50 M58 170 V88 h24 v82 M94 170 V128 h20 v42"/>'
        '<path d="M128 170 V96 h18 v-18 h16 v18 h18 v74"/>'
        '<path d="M196 170 V60 h12 v-16 h10 v16 h12 v110 M213 26 v18"/>'
        '<path d="M246 170 V110 h26 v60 M284 170 V84 h22 v86 M318 170 V130 h20 v40"/>'
        '<path d="M352 170 V100 h16 v-14 h14 v14 h16 v70 M420 170 V140 h24 v30"/>'
        '<path d="M8 170 H630" stroke-dasharray="1 9"/>'),
    "stadium": ('<ellipse cx="320" cy="104" rx="212" ry="62"/>'
        '<ellipse cx="320" cy="104" rx="128" ry="34"/>'
        '<path d="M240 104 h160 M320 88 v32" stroke-dasharray="2 7"/>'
        '<path d="M534 40 v-26 l26 7 -26 8"/>'),
    "flats": ('<path d="M10 148 H190 l22 -44 h46 l16 44 H420 l18 -30 h38 l14 30 H630"/>'
        '<circle cx="536" cy="62" r="20"/>'
        '<path d="M20 166 H160 M210 166 H400 M450 166 H620" stroke-dasharray="1 8"/>'),
    "peaks": ('<path d="M10 150 L128 56 L176 108 L252 34 L318 122 L396 66 L446 132 L630 132"/>'
        '<path d="M140 76 l-16 22 M156 88 l-20 26 M262 56 l-18 26 M280 74 l-22 30'
        ' M404 84 l-14 20" stroke-width="1.2"/>'
        '<path d="M60 160 H590" stroke-dasharray="1 8" opacity=".7"/>'),
    "bridge": ('<path d="M10 142 H630"/>'
        '<path d="M198 142 V44 M218 142 V44 M198 66 h20 M198 96 h20"/>'
        '<path d="M436 142 V44 M456 142 V44 M436 66 h20 M436 96 h20"/>'
        '<path d="M218 50 C288 118 366 118 436 50"/>'
        '<path d="M10 118 C74 62 140 50 198 48 M456 48 C514 50 580 62 630 116"/>'
        '<path d="M258 88 v54 M327 104 v38 M396 88 v54" stroke-dasharray="2 6"'
        ' stroke-width="1.2"/>'),
    "ridge": ('<path d="M10 150 L148 58 L212 100 L330 28 L432 120 L522 78 L630 142"/>'
        '<path d="M160 78 l-14 20 M176 90 l-18 24 M342 50 l-16 24 M360 68 l-20 28"'
        ' stroke-width="1.2"/>'),
    "surf": ('<path d="M10 150 q22 -16 44 0 t44 0 t44 0 t44 0 t44 0 t44 0 t44 0 t44 0'
        ' t44 0 t44 0 t44 0 t44 0 t44 0 t44 0" stroke-width="1.6"/>'
        '<path d="M60 172 q22 -14 44 0 t44 0 t44 0 t44 0 t44 0 t44 0 t44 0 t44 0'
        ' t44 0 t44 0 t44 0 t44 0" stroke-width="1.2" opacity=".7"/>'
        '<path d="M470 150 q28 -34 76 -30 M508 148 v-56 M508 92 c-16 -14 -34 -16 -44 -10'
        ' M508 92 c4 -18 18 -30 34 -32 M508 92 c18 -8 36 -4 44 6"/>'),
    "volcano": ('<path d="M96 162 L252 54 q18 -13 36 0 L568 162"/>'
         '<path d="M266 44 c-10 -16 8 -24 4 -40" stroke-dasharray="3 6"/>'
         '<path d="M300 46 c-6 -14 8 -20 6 -34" stroke-dasharray="3 6"/>'
         '<path d="M282 62 l10 34 M310 74 l16 40 M254 70 l-8 28" class="lava"/>'
         '<path d="M60 176 H600" stroke-dasharray="1 8" opacity=".7"/>'),
    "sunrise": ('<path d="M110 150 q100 -84 210 -84 q110 0 210 84"/>'
         '<circle cx="320" cy="128" r="26"/>'
         '<path d="M320 84 v-20 M268 96 l-12 -16 M372 96 l12 -16 M240 128 h-24'
         ' M400 128 h24" stroke-width="1.4"/>'
         '<path d="M60 168 H580" stroke-dasharray="1 8"/>'),
}


def lineart(pick):
    """pick = kit sketch name, or {"svg": "<inner markup>"} for the trip's own."""
    if isinstance(pick, dict):
        body = pick.get("svg") or ""
    else:
        body = LA.get(pick or "")
    if not body:
        return ""
    return (f'<svg class="la reveal" viewBox="0 0 640 190" aria-hidden="true" '
            f'fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round">{body}</svg>')


# --------------------------------------------------------------- pieces ----
def weekday(date):
    return datetime.date.fromisoformat(date).strftime("%a").upper()


def dshort(date):
    return date[5:].replace("-", ".")


def torn_figure(stem, caption, sidecls, alt=None):
    uri = data_uri(stem)
    if not uri:
        return ""
    pc, pf = torn_photo_polys(f"photo-{stem}")
    return (f'<figure class="photo {sidecls} reveal" '
            f'style="--pc:{pc};--pf:{pf}">'
            f'<img src="{uri}" alt="{esc(alt or caption)}">'
            f'<i class="ht" aria-hidden="true"></i>'
            f'<figcaption><i class="dot" aria-hidden="true"></i>{esc(caption)}'
            f'</figcaption></figure>')


def pola_figure(ad, side):
    """A Kodak print pasted the zine way: fibre mat, crop marks, offset.
    ad = the day's art dict; side = the float side already decided by the
    poster rule ("pr clr" on a poster day, else art's own / pr)."""
    pair = ad.get("pair") or {}
    prints = [x for x in (pair.get("prints") or []) if x.get("stem")]
    if len(prints) >= 2:
        p1, p2 = prints[0], prints[1]
        u1, u2 = data_uri(p1["stem"]), data_uri(p2["stem"])
        if not (u1 and u2):
            return ""
        c1, c2 = p1.get("treat") or "", p2.get("treat") or ""
        cls1 = f' class="{esc(c1)}"' if c1 else ""
        cls2 = f' class="{esc(c2)}"' if c2 else ""
        return (f'<figure class="pp pg {side} reveal" style="--rot:{pair.get("rot", 0)}deg">'
                f'<span class="pi" style="--prot:{p1.get("rot", 0)}deg">'
                f'<img{cls1} src="{u1}" alt="{esc(p1.get("alt", ""))}"></span>'
                f'<span class="pi pi2" style="--prot:{p2.get("rot", 0)}deg">'
                f'<img{cls2} src="{u2}" alt="{esc(p2.get("alt", ""))}"></span>'
                f'<figcaption><i class="dot" aria-hidden="true"></i>{esc(pair.get("caption", ""))}'
                f'</figcaption></figure>')
    ph = ad.get("photo") or {}
    if not ph.get("stem"):
        return ""
    uri = data_uri(ph["stem"])
    if not uri:
        return ""
    treat = ph.get("treat") or ""
    cls = f" {esc(treat)}" if treat == "mono" else ""          # figure-level treatment
    icls = f' class="{esc(treat)}"' if treat and treat != "mono" else ""   # img-level
    return (f'<figure class="pp {side}{cls} reveal" style="--rot:{ph.get("rot", 0)}deg">'
            f'<span class="pi"><img{icls} src="{uri}" alt="{esc(ph.get("alt", ""))}"></span>'
            f'<figcaption><i class="dot" aria-hidden="true"></i>{esc(ph.get("caption", ""))}'
            f'</figcaption></figure>')


def sticker(ad):
    ent = ad.get("sticker") or {}
    if not ent.get("stem"):
        return ""
    uri = data_uri(ent["stem"], ent.get("size") or "md")
    if not uri:
        return ""
    side = ent.get("side") or "sl"
    return (f'<figure class="stick {esc(side)}" aria-hidden="true" '
            f'style="--rot:{ent.get("rot", 0)}deg"><img src="{uri}" alt=""></figure>')


def prop(ent):
    """Colophon paper prop (boarding pass / luggage tag / ticket): {stem, rot}."""
    ent = ent or {}
    uri = data_uri(ent.get("stem"))
    if not uri:
        return ""
    return (f'<figure class="prop" aria-hidden="true" '
            f'style="--rot:{ent.get("rot", 0)}deg"><img src="{uri}" alt=""></figure>')


def rstamp(kick_en):
    ring = f"READ BEFORE DEPARTURE · {esc(kick_en)} ·" if kick_en else "READ BEFORE DEPARTURE ·"
    return f"""<svg class="rstamp" viewBox="0 0 132 132" aria-hidden="true">
<circle cx="66" cy="66" r="60" fill="none" stroke="currentColor" stroke-width="3.4"/>
<circle cx="66" cy="66" r="43" fill="none" stroke="currentColor" stroke-width="1.6"/>
<path id="stc" d="M66 15 a51 51 0 1 1 -0.1 0" fill="none"/>
<text class="rst"><textPath href="#stc">{ring}</textPath></text>
<text class="rsb" x="66" y="73" text-anchor="middle">{esc(t("stamp_word"))}</text>
</svg>"""


def render_rail(days):
    out = [f'<nav class="rail" aria-label="{esc(t("rail_aria"))}">']
    for i, d in enumerate(days, 1):
        theme = ART.day_theme(d.get("date", ""), d.get("city", ""))
        rot = (i % 3 - 1) * 1.4
        out.append(
            f'<a href="#d{i}" data-for="d{i}" aria-label="{esc(t("rail_day").format(i=i, theme=theme))}"'
            f' style="--chip:{chip_poly(f"chip{i}")};--rot:{rot:.1f}deg">'
            f'<span class="rn">{i:02d}</span></a>')
    out.append(f'<a href="#app" data-for="app" aria-label="{esc(t("rail_app"))}"'
               f' style="--chip:{chip_poly("chipapp")};--rot:-1deg">'
               f'<span class="rn">{esc(t("rail_app_glyph"))}</span></a></nav>')
    return "".join(out)


def render_toc(days):
    rows = []
    for i, d in enumerate(days, 1):
        date = d.get("date", "")
        theme = ART.day_theme(date, d.get("city", ""))
        fly = f' <span class="fly">{ic("plane")}</span>' if d.get("travel_day") else ""
        rows.append(
            f'<a class="ix reveal" href="#d{i}">'
            f'<span class="ixn">{i:02d}</span>'
            f'<span class="ixt">{esc(theme)}{fly}</span>'
            f'<span class="ixr"></span>'
            f'<span class="ixc">{esc(d.get("city", ""))}</span>'
            f'<span class="ixd">{dshort(date)} {weekday(date)}</span></a>')
    rows.append('<a class="ix aux reveal" href="#app">'
                f'<span class="ixn">{esc(t("rail_app_glyph"))}</span><span class="ixt">{esc(t("toc_app_title"))}</span>'
                '<span class="ixr"></span>'
                f'<span class="ixc">{esc(t("toc_app_sub"))}</span>'
                '<span class="ixd">COLOPHON</span></a>')
    return "".join(rows)


def render_timeline(day):
    rows = []
    for r in day.get("timeline", []):
        kind = r.get("kind", "anchor")
        est = '<sup class="est">est</sup>' if r.get("verify") == "est" else ""
        tag = ""
        if r.get("tag"):
            raw = r["tag"]
            if raw.startswith("swap→"):     # free-form swap notes wrap as prose
                tag = (f'<span class="tag">{esc(t("tag_swap"))}</span>'
                       f'<span class="swap">→ {esc(raw[5:])}</span>')
            else:
                tag = f'<span class="tag">{esc(T("tag." + raw, raw))}</span>'
        price = (f'<span class="price">{esc(r["price"])}</span>'
                 if r.get("price") else "")
        nav = ""
        if r.get("link"):
            nav = (f'<a class="go" href="{esc(r["link"])}" target="_blank" '
                   f'rel="noopener" aria-label="{esc(t("nav_to").format(what=r.get("what", "")[:18]))}">'
                   f'{ic("pin")}</a>')
        note = (f'<span class="rnote">{et(r["note"])}</span>'
                if r.get("note") else "")
        rows.append(
            f'<div class="r k-{kind}">'
            f'<span class="t">{esc(r.get("t", ""))}{est}</span>'
            f'<span class="w">{et(r.get("what", ""))} {price}{tag}{nav}{note}</span>'
            f'</div>')
    return f'<div class="tl reveal">{"".join(rows)}</div>'


def render_mapfold(day):
    embed = day_embed_url(day)
    links = []
    if day.get("day_map"):
        links.append(f'<a href="{esc(day["day_map"])}" target="_blank" '
                     f'rel="noopener">{esc(t("day_route"))}</a>')
    for n, u in enumerate(day.get("hop_links", []), 1):
        links.append(f'<a href="{esc(u)}" target="_blank" rel="noopener" '
                     f'aria-label="{esc(t("hop_aria").format(n=n))}">{n}</a>')
    if not (embed or links):
        return ""
    embed_html = (f'<div class="map-embed" data-src="{esc(embed)}">'
                  f'<p class="map-ph">{esc(t("map_ph"))}</p></div>'
                  if embed else "")
    btns = f'<div class="hops">{"".join(links)}</div>' if links else ""
    return (f'<details class="mapfold reveal"><summary>{ic("compass")} '
            f'<span class="ls">{esc(t("mapfold"))}</span>'
            f'{ic("chevron", "chev")}</summary>{embed_html}{btns}</details>')


def fine_items(day):
    items = []
    wk = day.get("walking_km")
    if isinstance(wk, dict):
        items.append(("walk", f"{T('walk')} ≈{wk.get('total', '?')} km", wk.get("how", "")))
    elif wk:
        items.append(("walk", f"{T('walk')} ≈{wk} km", ""))
    if day.get("rain_alt"):
        items.append(("rain", T("rain_alt"), day["rain_alt"]))
    if day.get("late_cut"):
        items.append(("clock", T("late_cut"), day["late_cut"]))
    if day.get("note"):
        items.append(("note", t("note"), day["note"]))
    return items


def render_day(i, day, issue, nposter):
    """issue = the "<zh> ZINE" page-number word; nposter = how many posters
    have been hung before this chapter (drives the pl/pr alternation).
    Returns (html, nposter)."""
    date = day.get("date", "")
    ad = ART.day(date, THEME)
    theme = ART.day_theme(date, day.get("city", ""))
    fine = "".join(
        f'<div class="fi"><span class="fh">{ic(icn)} {esc(t)}</span>'
        f'<p>{et(b) if b else ""}</p></div>'
        for icn, t, b in fine_items(day))
    fine_html = f'<div class="fine reveal">{fine}</div>' if fine else ""
    photo, pside = "", ""
    po = ad.get("poster") or {}
    if po.get("stem"):
        pside = po.get("side") if po.get("side") in OPPOSITE else ("pl" if nposter % 2 == 0 else "pr")
        photo = torn_figure(po["stem"], po.get("caption", ""), pside, po.get("alt"))
        if photo:
            nposter += 1
    if photo:
        side = f"{OPPOSITE[pside]} clr"
    else:
        want = (ad.get("pair") or ad.get("photo") or {}).get("side")
        side = want if want in OPPOSITE else "pr"
    pola = pola_figure(ad, side)
    stick = sticker(ad)
    band = ""
    bd = ad.get("band") or {}
    if bd.get("stem"):
        uri = data_uri(bd["stem"])
        if uri:
            pc, pf = torn_band_polys(bd.get("tear_seed") or f"band-{bd['stem']}")
            cap = bd.get("caption", "")
            band = (f'<figure class="band" style="--pc:{pc};--pf:{pf}">'
                    f'<img src="{uri}" alt="{esc(bd.get("alt") or cap)}">'
                    f'<i class="ht" aria-hidden="true"></i>'
                    f'<figcaption><i class="dot" aria-hidden="true"></i>'
                    f'{esc(cap)}</figcaption></figure>')
    fly = (f'<span class="flyday">{ic("plane")} {esc(t("travel_day"))}</span>'
           if day.get("travel_day") else "")
    # sun --write may say 天亮 or dawn depending on the language it ran in
    sun = (f'<p class="sun">{et(day["sun"].replace("天亮", T("sun.dawn")).replace("dawn", T("sun.dawn")))}</p>'
           if day.get("sun") else "")
    ribbon = (f'<p class="ribbon reveal">{et(day["ribbon"])}</p>'
              if day.get("ribbon") else "")
    xbtn = (f'<button class="xbtn no-export" data-x-for="#d{i}" '
            f'data-x-label="P{i:02d} {esc(theme)}" '
            f'title="{esc(t("tip_day"))}">{esc(T("btn.save_day"))}</button>')
    band_cls = band_for(i)
    return f"""
<section class="chap day f-cream b-{band_cls}" id="d{i}" data-spy>
  {tear(f"tear-day-{date}", BANDVAR[band_cls])}
  <div class="hband">
    <div class="wrap hwrap">
      <header class="dhead reveal">
        <span class="dnum">{i:02d}</span>
        <div class="dmeta">
          <p class="kicker">DAY {i:02d} · {dshort(date)} {weekday(date)} {fly}</p>
          <p class="dcity">{esc(day.get("city", ""))}</p>
          <p class="dlabel">{esc(day.get("label", ""))}</p>
          {sun}
        </div>
      </header>
    </div>
  </div>
  {tear(f"tear-band-{date}", "var(--paper)")}
  <h2 class="vtitle" aria-label="{esc(theme)}"><span>{esc(theme)}</span></h2>
  <div class="wrap">
    {ribbon}
    {photo}
    {pola if not photo else ""}
    {render_timeline(day)}
    {pola if photo else ""}
    {render_mapfold(day)}
    {fine_html}
    {stick}
    {lineart(ad.get("lineart"))}
    <div class="pfoot">
      {xbtn}
      <p class="pageno" aria-hidden="true">P.{i:02d} — {esc(issue)}</p>
    </div>
  </div>
  {band}
</section>""", nposter


# --------------------------------------------------------------- colophon --
def render_legs(legs):
    rows = []
    for l in legs:
        backup = (f'<details class="alt"><summary>{esc(t("backup"))}</summary>'
                  f'<p>{esc(l["backup"])}</p></details>' if l.get("backup") else "")
        note = f'<p class="lnote">{et(l["note"])}</p>' if l.get("note") else ""
        link = (f' <a href="{esc(l["link"])}" target="_blank" rel="noopener">{esc(T("price.check"))}</a>'
                if l.get("link") else "")
        rows.append(
            f'<div class="leg"><span class="lg1"><b>{esc(l.get("date", ""))}</b> '
            f'{esc(l.get("from", ""))} → {esc(l.get("to", ""))}'
            f' <i class="ltype">{esc(l.get("type", ""))}</i></span>'
            f'<span class="lg2">{et(l.get("carrier", ""))} · {esc(l.get("dep", ""))}'
            f'→{esc(l.get("arr", ""))} · {esc(l.get("price", ""))}'
            f' · {esc(l.get("bags", ""))}{link}</span>{note}{backup}</div>')
    return "".join(rows)


def render_hotels(hotels):
    out = []
    for h in hotels:
        opts = "".join(
            f'<li><a href="{esc(o.get("link", "#"))}" target="_blank" rel="noopener">'
            f'{esc(o.get("name", ""))}</a> <span class="mini">{esc(o.get("band", ""))}'
            f'</span></li>' for o in h.get("options", []))
        out.append(
            f'<div class="hotel"><h4>{esc(h.get("base", ""))} · {esc(h.get("area", ""))}'
            f'</h4><p class="mini">{esc(h.get("why", ""))}</p><ul>{opts}</ul></div>')
    return f'<div class="hotels">{"".join(out)}</div>'


def render_budget(budget, total):
    rows = "".join(
        f'<tr><td>{et(b.get("cat", ""))}</td><td>{esc(b.get("per_person", ""))}</td>'
        f'<td>{esc(b.get("total", ""))}</td>'
        f'<td class="mini">{et(b.get("note", ""))}</td></tr>' for b in budget)
    return (f'<table class="budget"><tr><th>{esc(t("th_item"))}</th><th>{esc(t("th_pp"))}</th>'
            f'<th>{esc(t("th_total"))}</th>'
            f'<th>{esc(t("th_note"))}</th></tr>{rows}<tr class="sum"><td>{esc(t("total"))}</td>'
            f'<td colspan="3">{esc(total)}</td></tr></table>')


def render_checklist(items):
    out = []
    for c in items:
        link = (f' <a href="{esc(c["link"])}" target="_blank" rel="noopener">'
                f'{esc(c.get("link_text", T("link")))}</a>' if c.get("link") else "")
        note = f'<p class="mini">{et(c["note"])}</p>' if c.get("note") else ""
        out.append(f'<li><b>{et(c.get("item", ""))}</b> — {esc(c.get("deadline", ""))}'
                   f' · {esc(c.get("price", ""))}{link}{note}</li>')
    return f'<ol class="check">{"".join(out)}</ol>'


def render_brief(brief):
    # section titles from the shared table + art common brief_titles;
    # unknown keys (a trip's own headings) print as they are
    titles = brief_titles(ART)
    return "".join(
        f'<div class="bf"><h4>{esc(titles.get(k, k))}</h4><p>{et(v)}</p></div>'
        for k, v in brief.items())


# cover.credit — the poem's source under the cover dates, in the dates' own
# small letterspaced voice (cream on the blue, muted); appended to the page CSS
# only when the art carries a credit so credit-less builds stay byte-identical.
CREDIT_CSS = """
  .cv-credit { font-size:11px; letter-spacing:.22em; line-height:1.8; color:#D8CFBA;
    text-align:center; text-indent:.22em; max-width:20em; text-wrap:balance; }
  @media (max-width:760px) { .cv-credit { text-align:left; text-indent:0; } }
  @media print { .cv-credit { color:#443E33; } }
"""


# ------------------------------------------------------------------ main ---
def main():
    global ART
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("-o", "--out", required=True)
    add_art_arg(ap)
    args = ap.parse_args()
    p = load_plan(args.plan)
    init_lang(args, p)
    ART = load_art(args.plan, args.art, args.assets)

    meta = p.get("meta", {})
    days = p.get("days", [])
    tz = ART.theme(THEME)
    year = (meta.get("dates", "") or "")[:4]
    year = year if year.isdigit() else ""
    # cover words — the trip's, all optional (see ART CONTRACT)
    kick = title_kick(ART, THEME)
    kick_en = ART.cover(THEME, "kick_en")
    cover_zh = ART.cover(THEME, "zh") or kick or t("cover_fallback")
    cover_en = ART.cover(THEME, "en", "COLLAGE")
    cover_credit = ART.cover(THEME, "credit")        # poem source, under the cover dates
    issue = f"{cover_zh} ZINE"                       # "<zh> ZINE" — page numbers, colophon
    page_title = " · ".join(x for x in (title_head(ART, THEME, year), t("page_title")) if x)
    eyebrow = " · ".join(x for x in (kick, f"{cover_en} ZINE", year) if x)
    edge = " · ".join(x for x in (cover_en, f"{len(days)} DAYS", kick_en) if x)
    colo_issue = " · ".join(x for x in (issue, year) if x)

    parts, nposter = [], 0
    for i, d in enumerate(days, 1):
        html, nposter = render_day(i, d, issue, nposter)
        parts.append(html)
    days_html = "".join(parts)
    cp = (ART.cover(THEME).get("photo") or {}) if ART else {}
    cover_uri = data_uri(cp.get("stem"))
    cover_html = ""
    if cover_uri:
        cv_pc, cv_pf = torn_photo_polys(cp.get("tear_seed") or f"cover-{cp['stem']}")
        cv_cap = cp.get("caption", "")
        cover_html = (f'<figure class="cv-photo" style="--pc:{cv_pc};--pf:{cv_pf}">\n'
                      f'    <img src="{cover_uri}" alt="{esc(cp.get("alt") or cv_cap)}">\n'
                      f'    <i class="ht" aria-hidden="true"></i>\n'
                      f'    <figcaption><i class="dot" aria-hidden="true"></i>{esc(cv_cap)}</figcaption>\n'
                      f'  </figure>')
    dates = short_dates(meta.get("dates", "")).replace("-", ".") \
                                              .replace(" → ", " — ")
    decisions = "".join(f"<li>{et(u)}</li>" for u in p.get("decisions", []))
    unverified = "".join(f"<li>{et(u)}</li>" for u in p.get("unverified", []))
    route = esc(meta.get("route", ""))
    ring = ring_uri()

    # contents strip: small gouache cut-outs previewing the trip's legs (art)
    strip_imgs = []
    for ent in tz.get("toc_strip") or []:
        u = data_uri(ent.get("stem"), "sm")
        if u:
            strip_imgs.append(f'<img src="{u}" alt="" style="--rot:{ent.get("rot", 0)}deg">')
    tocstrip = (f'<div class="tocstrip" aria-hidden="true">'
                f'{"".join(strip_imgs)}</div>' if strip_imgs else "")
    props = tz.get("props") or {}
    barnum = " ".join(re.findall(r"\d+", meta.get("dates", "")))
    issue_bar = (f'<p class="issue" aria-hidden="true"><span class="bars"></span>'
                 f'<span class="bnum">{esc(barnum)}</span></p>' if barnum else "")

    css = """
  :root {
    --paper:#F2EAD8; --fiber:#F8F2E2; --ink:#201A13;
    --blue:#2036B1; --yellow:#E3B004; --red:#EB4B32; --inkf:#17120D;
    --num:"DIN Alternate","Avenir Next Condensed","Bahnschrift","Arial Narrow",
      Arial,sans-serif;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  html { scroll-behavior:smooth; }
  body { background:var(--paper); color:var(--ink);
    font-family:"PingFang SC","Hiragino Sans GB","Noto Sans SC","Microsoft YaHei",
      system-ui,sans-serif; font-size:14px; line-height:1.8;
    overflow-wrap:anywhere; }
  body::after { content:""; position:fixed; inset:0; z-index:60;
    pointer-events:none; opacity:.5; mix-blend-mode:multiply;
    background:url("__NOISE__"); }
  .ic { width:1em; height:1em; fill:none; stroke:currentColor; stroke-width:1.9;
    stroke-linecap:round; stroke-linejoin:round; vertical-align:-.125em; }
  a { color:inherit; }
  sup.est { font-family:var(--num); font-size:8.5px; letter-spacing:.14em;
    color:var(--accS); vertical-align:super; margin-left:2px; }
  .mini { font-size:11.5px; color:var(--soft); }
  :focus-visible { outline:3px solid var(--focus,#A6220C); outline-offset:3px; }

  /* colour fields — every chapter re-inks its own text tokens */
  .f-cream  { --bg:var(--paper); --tx:#201A13; --soft:#453E30;
    --accS:#A6220C; --accL:#C22C15; --hair:rgba(32,26,19,.28); --focus:#A6220C; }
  .f-yellow { --bg:var(--yellow); --tx:#201A13; --soft:#3F3826;
    --accS:#7A1A0A; --accL:#A6220C; --hair:rgba(32,26,19,.34); --focus:#7A1A0A; }
  .f-blue   { --bg:var(--blue); --tx:#F6EFDF; --soft:#D8CFBA;
    --accS:#E9BE24; --accL:#E9BE24; --hair:rgba(246,239,223,.34); --focus:#E9BE24; }
  .f-ink    { --bg:var(--inkf); --tx:#F6EFDF; --soft:#CFC5AC;
    --accS:#E9BE24; --accL:#E8442E; --hair:rgba(246,239,223,.28); --focus:#E9BE24; }
  .f-red    { --bg:var(--red); --tx:#16100B; --soft:#16100B;
    --accS:#16100B; --accL:#F6EFDF; --hair:rgba(22,16,11,.4); --focus:#16100B; }

  /* the day's colour lives in ONE torn header band; the body is paper */
  .hband { position:relative; background:var(--bband); color:var(--btx); }
  .hwrap { padding-top:clamp(40px,6vh,64px); padding-bottom:clamp(44px,7vh,78px); }
  .b-blue   { --bband:var(--blue);   --btx:#F6EFDF; --bsoft:#D8CFBA;
    --bnum:#E9BE24; --bacc:#E9BE24; }
  .b-ink    { --bband:var(--inkf);   --btx:#F6EFDF; --bsoft:#CFC5AC;
    --bnum:#E8442E; --bacc:#E9BE24; }
  .b-red    { --bband:var(--red);    --btx:#16100B; --bsoft:#231610;
    --bnum:#F6EFDF; --bacc:#16100B; }
  .b-yellow { --bband:var(--yellow); --btx:#201A13; --bsoft:#3F3826;
    --bnum:#A6220C; --bacc:#7A1A0A; }
  .hband .dnum { color:var(--bnum); border-color:var(--bnum); }
  .hband .kicker { color:var(--bacc); }
  .hband .dcity { color:var(--btx); }
  .hband .dlabel, .hband .sun { color:var(--bsoft); }
  .hband .dhead { margin-bottom:0; }

  .chap { position:relative; display:flow-root;
    background:var(--bg); color:var(--tx); }
  .wrap { max-width:920px; margin:0 auto;
    padding:clamp(40px,7vh,86px) clamp(88px,15vw,170px)
            clamp(64px,10vh,120px) clamp(20px,5vw,64px); }
  section[id], h3[id] { scroll-margin-top:24px; }

  /* ---- torn edges: shadow / fibre core / colour sheet ---- */
  .tear { position:relative; height:64px; margin-top:-64px; z-index:3;
    pointer-events:none; }
  .tear i { position:absolute; inset:0; display:block; }
  .tear .i0 { background:rgba(24,15,7,.20); clip-path:var(--t0); }
  .tear .i1 { background:var(--fiber); clip-path:var(--t1); }
  .tear .i2 { background:var(--bg); clip-path:var(--t2); }

  /* ---- rail: torn paper scraps with printed numerals ---- */
  .rail { position:fixed; left:10px; top:50%; translate:0 -50%; z-index:80;
    display:none; flex-direction:column; gap:2px; }
  .rail a { position:relative; width:48px; height:44px; display:flex;
    align-items:center; justify-content:center; text-decoration:none;
    rotate:var(--rot,0deg); }
  .rail a::before { content:""; position:absolute; inset:3px;
    background:var(--fiber); clip-path:var(--chip);
    box-shadow:0 1px 0 rgba(24,15,7,.25); }
  .rail .rn { position:relative; font-family:var(--num); font-size:12.5px;
    letter-spacing:.1em; color:#201A13; }
  .rail a[aria-current] { rotate:0deg; }
  .rail a[aria-current]::after { content:""; position:absolute; inset:0;
    background:url("__RING__") center/44px 40px no-repeat; }
  .rail a[aria-current] .rn { color:#A6220C; font-weight:700; }
  @media (min-width:1180px) { .rail { display:flex; }
    .cv-edge { left:68px; } }   /* clear the fixed rail (10px+48px wide) */

  .stamp { position:fixed; right:12px; bottom:14px; z-index:80;
    width:46px; height:46px; display:flex; align-items:center;
    justify-content:center; background:#201A13; color:#F6EFDF;
    font-size:11px; letter-spacing:.2em; text-decoration:none;
    writing-mode:vertical-rl; text-indent:.2em;
    clip-path:polygon(6% 4%, 55% 0%, 96% 7%, 100% 52%, 94% 94%, 48% 100%,
      5% 93%, 0% 45%); }
  @media (min-width:1180px) { .stamp { display:none; } }

  /* ---- cover ---- */
  .cv { min-height:96svh; display:flex; flex-direction:column; }
  .cv-photo { position:relative; width:min(58vw,520px);
    margin:0 0 26px calc(-1*clamp(8px,2vw,22px));
    transform:rotate(-1.3deg); z-index:1; }
  .cv-photo::before { content:""; position:absolute; inset:0;
    background:var(--fiber); clip-path:var(--pf); }
  .cv-photo img { position:relative; display:block; width:100%; height:auto;
    clip-path:var(--pc); }
  .cv-photo figcaption, .photo figcaption, .pp figcaption {
    position:absolute; left:-22px; top:8px; writing-mode:vertical-rl;
    font-family:var(--num); font-size:9.5px; letter-spacing:.34em;
    color:var(--tx); white-space:nowrap; }
  .dot { display:inline-block; width:7px; height:7px; background:var(--accL);
    margin-bottom:10px; }
  .cv-side { position:absolute; right:clamp(10px,4vw,72px);
    top:clamp(26px,6vh,72px); display:flex; flex-direction:column;
    align-items:center; gap:18px; z-index:2; }
  .cv h1 { writing-mode:vertical-rl; font-size:clamp(96px,19vw,196px);
    line-height:1; letter-spacing:.16em; font-weight:800; color:#F6EFDF;
    text-shadow:5px 5px 0 rgba(232,68,46,.55); }
  .cv-dates { font-family:var(--num); font-size:clamp(12px,1.6vw,15px);
    letter-spacing:.42em; color:#F6EFDF; text-indent:.42em; }
  .cv-edge { position:absolute; left:10px; top:clamp(28px,7vh,80px);
    writing-mode:vertical-rl; font-family:var(--num); font-size:9px;
    letter-spacing:.5em; color:#D8CFBA; z-index:3;
    text-shadow:0 1px 8px rgba(22,16,11,.7), 0 0 3px rgba(22,16,11,.55); }
  .cv-foot { margin-top:auto; position:relative; z-index:2;
    padding:24px clamp(80px,15vw,170px) 26px clamp(16px,4vw,60px); }
  .cv-eyebrow { font-family:var(--num); font-size:11px; letter-spacing:.4em;
    color:#D8CFBA; margin-bottom:12px; }
  .cv-route { font-size:12px; letter-spacing:.18em; color:#F6EFDF;
    max-width:44em; }
  .cue { display:inline-flex; align-items:center; gap:12px; margin-top:20px;
    min-height:44px; color:#D8CFBA; text-decoration:none; font-size:10.5px;
    letter-spacing:.3em; }
  .cue::after { content:""; width:44px; height:1px; background:#D8CFBA;
    animation:drip 2.2s ease-in-out infinite; }
  @keyframes drip { 50% { transform:translateX(10px); opacity:.5; } }

  /* ---- toc ---- */
  .toc .wrap { padding-right:clamp(20px,5vw,64px); }
  .sechead { display:flex; align-items:center; gap:14px; margin-bottom:26px; }
  .sechead::after { content:""; flex:1; height:1px; background:var(--hair); }
  .sechead .sq { width:9px; height:9px; background:var(--accL); }
  .sechead h2, .sechead h3 { font-size:15px; letter-spacing:.42em;
    font-weight:700; }
  .sechead .en { font-family:var(--num); font-size:10px; letter-spacing:.32em;
    color:var(--soft); }
  .ix { display:grid; align-items:baseline; column-gap:16px;
    grid-template-columns:auto auto minmax(0,1fr) auto auto;
    padding:15px 2px; border-bottom:1px solid var(--hair);
    text-decoration:none; }
  .ix .ixn { font-family:var(--num); font-size:clamp(30px,4.5vw,44px);
    font-weight:700; color:var(--accL); line-height:.9; letter-spacing:.04em; }
  .ix .ixt { font-size:16.5px; font-weight:700; letter-spacing:.14em; }
  .ix .fly .ic { width:13px; height:13px; color:var(--accS); }
  .ix .ixr { height:1px; background:var(--hair); align-self:center; }
  .ix .ixc { font-size:11.5px; color:var(--soft); letter-spacing:.06em; }
  .ix .ixd { font-family:var(--num); font-size:11px; letter-spacing:.18em;
    color:var(--accS); }
  .ix:hover .ixn { color:#7A1A0A; }
  .ix:hover .ixt { text-decoration:underline; text-underline-offset:4px; }
  .toc-note { margin-top:26px; font-size:11.5px; color:var(--soft);
    letter-spacing:.06em; }
  .tocstrip { display:flex; flex-wrap:wrap; justify-content:flex-end;
    align-items:flex-end; gap:16px; margin:-6px 0 16px; }
  .tocstrip img { height:clamp(44px,6vw,64px); width:auto;
    rotate:var(--rot,0deg); filter:drop-shadow(3px 4px 0 rgba(24,15,7,.16)); }

  /* ---- day chapters ---- */
  /* giant type sits on the PAPER below the band, like the mock's 热泉万彩 */
  .vtitle { position:absolute; top:clamp(330px,40vh,430px);
    right:clamp(8px,3.4vw,52px); writing-mode:vertical-rl; z-index:2;
    font-size:clamp(52px,8.4vw,92px); font-weight:800; letter-spacing:.2em;
    line-height:1; color:var(--tx);
    text-shadow:4px 4px 0 rgba(232,68,46,.5); }
  .f-red .vtitle, .f-cream .vtitle, .f-yellow .vtitle {
    text-shadow:4px 4px 0 rgba(32,54,177,.28); }
  .dhead { display:flex; align-items:flex-start; gap:clamp(16px,3vw,30px);
    margin-bottom:26px; }
  .dnum { font-family:var(--num); font-size:clamp(64px,10vw,116px);
    font-weight:700; line-height:.82; color:var(--accL);
    border-bottom:3px solid var(--accL); padding-bottom:10px; }
  .kicker { font-family:var(--num); font-size:11px; letter-spacing:.32em;
    color:var(--accS); margin-bottom:8px; }
  .flyday { margin-left:8px; letter-spacing:.18em; }
  .dcity { font-size:clamp(19px,2.6vw,25px); font-weight:800;
    letter-spacing:.1em; }
  .dlabel { font-size:13px; color:var(--soft); margin-top:6px; max-width:36em; }
  .sun { font-size:11.5px; color:var(--soft); margin-top:6px;
    letter-spacing:.08em; }
  .ribbon { border-top:1px solid var(--hair); border-bottom:1px solid var(--hair);
    padding:10px 0; margin:0 0 26px; font-size:12px; letter-spacing:.1em;
    color:var(--soft); }

  .photo { position:relative; width:min(44%,400px); margin:6px 0 22px 30px;
    float:right; transform:rotate(1.4deg); }
  .photo.pl { float:left; margin:6px 30px 22px 0; transform:rotate(-1.2deg); }
  .photo::before { content:""; position:absolute; inset:0;
    background:var(--fiber); clip-path:var(--pf); }
  .photo img { position:relative; display:block; width:100%; height:auto;
    clip-path:var(--pc); }
  .photo.mono img { filter:grayscale(1) contrast(1.16) brightness(1.17); }

  /* halftone dot screen over rectangular prints — the riso印刷网点 */
  .ht { position:absolute; inset:0; pointer-events:none; clip-path:var(--pc);
    background:radial-gradient(circle at 1.1px 1.1px, rgba(24,15,7,.65) 1px,
      transparent 1.6px) 0 0/4.4px 4.4px; opacity:.13;
    mix-blend-mode:multiply; }

  /* ---- pasted prints: fibre mat + crop marks + riso offset shadow ---- */
  .pp { position:relative; width:min(40%,330px); float:right;
    margin:6px 4px 24px 30px; rotate:var(--rot,1.8deg); }
  .pp.pl { float:left; margin:6px 30px 24px 4px; }
  .pp .pi { position:relative; display:block; background:var(--fiber);
    padding:9px 9px 12px; box-shadow:var(--off,7px 8px 0 rgba(24,15,7,.16));
    rotate:var(--prot,0deg); }
  .pp img { display:block; width:100%; height:auto;
    filter:saturate(.9) contrast(1.06); }
  .pp.mono img { filter:grayscale(1) contrast(1.14) brightness(1.05); }
  .pp.mono { --off:7px 8px 0 rgba(232,68,46,.42); }
  .pp img.duo-blue { filter:grayscale(1) sepia(1) saturate(2.7)
    hue-rotate(192deg) brightness(.95) contrast(1.05); }
  /* on poster days the print clears the poster and takes the other side:
     the two floats never overlap vertically, so no pinched text column */
  .pp.clr { clear:both; }
  .pp.pg .pi2 { width:74%; margin:-30% 0 0 auto; }
  .pp::before, .pp::after { content:""; position:absolute; width:15px;
    height:15px; pointer-events:none; z-index:1; }
  .pp::before { left:-9px; top:-9px; border-left:2px solid var(--accS);
    border-top:2px solid var(--accS); }
  .pp::after { right:-9px; bottom:-9px; border-right:2px solid var(--accS);
    border-bottom:2px solid var(--accS); }

  /* ---- gouache cut-outs pasted as stickers ---- */
  .stick { float:left; width:clamp(120px,15vw,180px); margin:4px 16px 10px 0; }
  .stick.sr { float:right; margin:4px 0 10px 16px; }
  .stick img { display:block; width:100%; height:auto; rotate:var(--rot,0deg);
    filter:drop-shadow(4px 5px 0 rgba(24,15,7,.2)); }

  .tl { border-top:2px solid var(--tx); }
  .r { position:relative; display:grid;
    grid-template-columns:96px minmax(0,1fr); column-gap:16px;
    padding:11px 0 11px 20px; border-bottom:1px solid var(--hair); }
  .r::before { content:""; position:absolute; left:2px; top:19px;
    width:7px; height:7px; background:var(--accL); }
  .k-hop::before { height:2px; top:22px; width:10px; background:var(--soft); }
  .k-meal::before { background:var(--soft); }
  .k-free::before { background:none; border:1.5px solid var(--soft);
    width:6px; height:6px; }
  .t { font-family:var(--num); font-size:12px; letter-spacing:.08em;
    color:var(--accS); font-variant-numeric:tabular-nums; padding-top:2px; }
  .w { min-width:0; font-size:13.5px; }
  .k-hop .w { font-size:12.5px; color:var(--soft); }
  .k-free .w { color:var(--soft); }
  .price { font-family:var(--num); font-size:11px; letter-spacing:.06em;
    color:var(--soft); margin-left:6px; }
  .tag { font-size:11px; letter-spacing:.22em; color:var(--accS);
    font-weight:700; margin-left:8px; }
  .tag::before { content:"/ "; } .tag::after { content:" /"; }
  .swap { font-size:11.5px; color:var(--soft); }
  .rnote { display:block; font-size:11.5px; color:var(--soft); margin-top:3px; }
  .go { display:inline-flex; align-items:center; justify-content:center;
    min-width:44px; min-height:44px; margin:-14px -10px -14px 0;
    color:var(--accS); vertical-align:middle; }
  .go .ic { width:13px; height:13px; }

  .mapfold { margin-top:16px; font-size:12px; color:var(--soft); }
  .mapfold summary { display:flex; align-items:center; gap:12px;
    min-height:44px; cursor:pointer; list-style:none; user-select:none;
    letter-spacing:.2em; border-bottom:1px solid var(--hair); }
  .mapfold summary::-webkit-details-marker { display:none; }
  .mapfold summary::after { content:""; flex:1; height:1px;
    background:var(--hair); }
  .mapfold .chev { transition:transform .25s ease; }
  .mapfold[open] .chev { transform:rotate(180deg); }
  .map-embed { margin-top:12px; border:1px solid var(--hair); }
  .map-embed iframe { display:block; width:100%; height:320px; border:0; }
  .map-ph { padding:22px; text-align:center; letter-spacing:.08em; }
  .hops { padding-top:6px; }
  .hops a { display:inline-flex; align-items:center; justify-content:center;
    min-width:44px; min-height:44px; padding:0 6px;
    font-family:var(--num); letter-spacing:.08em; text-decoration:none;
    color:var(--accS); }
  .hops a::before { content:"["; opacity:.6; margin-right:2px; }
  .hops a::after { content:"]"; opacity:.6; margin-left:2px; }

  .fine { clear:both; display:grid;
    grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));
    gap:16px 34px; margin-top:30px; border-top:1px solid var(--hair);
    padding-top:18px; }
  .fi .fh { font-family:var(--num); font-size:10.5px; letter-spacing:.3em;
    color:var(--accS); display:block; margin-bottom:4px; }
  .fi p { font-size:12px; color:var(--soft); }

  .la { display:block; width:min(100%,560px); height:auto; margin:38px auto 0;
    color:var(--tx); opacity:.8; }
  .la .lava { stroke:var(--accL); }
  .pageno { margin-top:34px; text-align:right; font-family:var(--num);
    font-size:10px; letter-spacing:.3em; color:var(--soft); }

  .band { position:relative; margin-top:20px; }
  .band::before { content:""; position:absolute; inset:0;
    background:var(--fiber); clip-path:var(--pf); }
  .band img { position:relative; display:block; width:100%;
    height:clamp(240px,44vh,420px); object-fit:cover; clip-path:var(--pc); }
  .band figcaption { position:absolute; right:clamp(16px,4vw,60px);
    bottom:16px; font-family:var(--num); font-size:10px; letter-spacing:.34em;
    color:#F6EFDF; text-shadow:0 1px 3px rgba(0,0,0,.65); }
  .band .dot { margin:0 10px 0 0; vertical-align:1px; }

  /* ---- colophon ---- */
  .colo .wrap { padding-right:clamp(20px,5vw,64px); }
  .colo section { margin-bottom:52px; }
  .colo .sechead { margin-top:0; }
  .leg { padding:10px 2px; border-bottom:1px solid var(--hair);
    font-size:12.5px; }
  .lg1 { display:block; letter-spacing:.06em; }
  .lg1 b { font-family:var(--num); letter-spacing:.1em; }
  .ltype { font-style:normal; font-size:10.5px; letter-spacing:.2em;
    color:var(--accS); margin-left:8px; }
  .lg2 { display:block; font-size:11.5px; color:var(--soft); margin-top:2px; }
  .lnote { font-size:11px; color:var(--soft); margin-top:2px; }
  .alt { font-size:11.5px; color:var(--soft); margin-top:4px; }
  .alt summary { cursor:pointer; letter-spacing:.12em; min-height:24px; }
  .alt p { padding:4px 0 2px 14px; }
  .leg a, .check a, .hotel a { color:var(--accS); text-underline-offset:3px; }

  .hotels { display:grid;
    grid-template-columns:repeat(auto-fit,minmax(16rem,1fr)); gap:26px 40px; }
  .hotel h4 { font-size:13.5px; letter-spacing:.08em;
    border-top:2px solid var(--accL); padding-top:10px; }
  .hotel ul { margin:8px 0 0 18px; font-size:12px; }
  .hotel li { margin-top:4px; }

  table.budget { width:100%; border-collapse:collapse; font-size:12px;
    table-layout:fixed; }
  .budget th { font-family:var(--num); font-size:10px; letter-spacing:.24em;
    text-align:left; color:var(--soft);
    border-bottom:2px solid var(--tx); padding:0 12px 8px 0; }
  .budget th:nth-child(1) { width:34%; } .budget th:nth-child(2) { width:27%; }
  .budget th:nth-child(3) { width:11%; }
  .budget td { border-bottom:1px solid var(--hair); padding:9px 12px 9px 0;
    vertical-align:top; line-height:1.65; }
  .budget td:nth-child(2) { color:#7A2A12; font-variant-numeric:tabular-nums; }
  .budget tr.sum td { font-weight:800; border-top:2px solid var(--tx);
    border-bottom:4px double var(--tx); font-size:12.5px; }

  ol.check { margin-left:2px; list-style:none; counter-reset:ck;
    columns:2 22em; column-gap:3.4em; }
  ol.check li { counter-increment:ck; break-inside:avoid; margin-bottom:14px;
    padding-left:38px; position:relative; font-size:12.5px; }
  ol.check li::before { content:counter(ck,decimal-leading-zero);
    position:absolute; left:0; top:1px; font-family:var(--num); font-size:15px;
    font-weight:700; color:var(--accL); }
  .briefs { columns:2 22em; column-gap:3.4em; }
  .bf { break-inside:avoid; margin-bottom:18px; }
  .bf h4 { font-size:12px; letter-spacing:.3em; color:var(--accS);
    border-bottom:1px solid var(--hair); padding-bottom:4px;
    margin-bottom:6px; }
  .bf p { font-size:12px; color:var(--soft); }
  ol.plain { margin-left:20px; font-size:12.5px; }
  ol.plain li { margin-bottom:10px; }
  ul.warn { list-style:none; }
  ul.warn li { padding:8px 0 8px 22px; position:relative; font-size:12px;
    color:var(--soft); border-bottom:1px solid var(--hair); }
  ul.warn li::before { content:""; position:absolute; left:2px; top:16px;
    width:8px; height:8px; background:var(--accL); }
  .colofoot { margin-top:64px; padding-top:22px; text-align:center;
    font-size:10.5px; letter-spacing:.14em; color:var(--soft); line-height:2.3;
    border-top:1px solid var(--hair); position:relative; }
  .colofoot::before, .colofoot::after { content:"✕"; position:absolute;
    top:8px; font-size:9px; opacity:.6; }
  .colofoot::before { left:0; } .colofoot::after { right:0; }

  /* ---- colophon paper props + rubber stamp + issue barcode ---- */
  .prop { float:right; width:clamp(150px,20vw,220px); margin:-4px 0 14px 24px; }
  .prop img { display:block; width:100%; height:auto; rotate:var(--rot,0deg);
    filter:drop-shadow(5px 6px 0 rgba(24,15,7,.16)); }
  .rstamp { float:right; width:clamp(96px,12vw,124px); height:auto;
    margin:-6px 4px 12px 22px; color:var(--accL); rotate:-12deg; opacity:.85;
    mix-blend-mode:multiply; }
  .rstamp .rst { font-family:var(--num); font-size:10.5px;
    letter-spacing:.3em; fill:currentColor; }
  .rstamp .rsb { font-size:19px; font-weight:800; fill:currentColor;
    letter-spacing:.16em; }
  .issue { display:flex; flex-direction:column; align-items:center; gap:5px;
    margin:0 0 16px; }
  .issue .bars { width:150px; height:30px;
    background:repeating-linear-gradient(90deg, #201A13 0 2px,
      transparent 2px 3px, #201A13 3px 6px, transparent 6px 9px,
      #201A13 9px 10px, transparent 10px 13px, #201A13 13px 15px,
      transparent 15px 17px); }
  .issue .bnum { font-family:var(--num); font-size:10px; letter-spacing:.4em;
    color:var(--soft); }

  /* ---- export chips: solid riso plates (red sheet over a blue offset
     plate), square-cornered like every other zine block — no capsule, no
     radius. They print at FULL ink at rest: at half strength nobody found
     them. Hover pulls the misregistered sheets back into register.
     Type size is unchanged (11px) — the flat plate is what carries the
     visibility, and a 100x44 block stays a footer prop next to a 116px
     chapter numeral, not a call to action. ---- */
  .xbtn { display:inline-flex; align-items:center; justify-content:center;
    min-height:44px; padding:0 16px; border:0; border-radius:0;
    background:var(--red); color:#16100B; cursor:pointer;
    font-family:var(--num); font-size:11px; font-weight:700;
    letter-spacing:.24em; text-decoration:none;
    box-shadow:5px 5px 0 var(--blue);
    transition:translate .2s ease, box-shadow .2s ease; }
  .xbtn:hover, .xbtn:focus-visible { translate:3px 3px;
    box-shadow:2px 2px 0 var(--blue); }
  .pfoot { clear:both; display:flex; align-items:center;
    justify-content:flex-end; gap:20px; margin-top:34px; }
  .pfoot .pageno { margin-top:0; }
  .xbtn-appx { position:absolute; top:clamp(40px,7vh,86px);
    right:clamp(20px,5vw,64px); z-index:4; }
  /* whole-issue plate: docked in the CONTENTS page, in flow. It used to
     float fixed at the right edge — which is this zine's vertical-title
     gutter, so it sat on top of 熔岩之心 and friends at half the scroll
     positions (measured: 33.5x46 of overlap). In flow it can never collide,
     and the contents page is the one screen every reader passes through. */
  .tocx { display:flex; align-items:center; gap:16px; flex-wrap:wrap;
    margin-top:30px; }
  .tocx-en { font-family:var(--num); font-size:10px; letter-spacing:.3em;
    color:var(--soft); }
  .xbtn-page { padding:0 20px; background:var(--blue); color:#F6EFDF;
    box-shadow:5px 5px 0 var(--red); }
  .xbtn-page:hover, .xbtn-page:focus-visible { box-shadow:2px 2px 0 var(--red); }

  /* ---- motion ---- */
  .js .reveal { opacity:0; transform:translateY(16px);
    transition:opacity .55s ease, transform .55s ease; }
  .js .reveal.in { opacity:1; transform:none; }
  @media (prefers-reduced-motion:reduce) {
    html { scroll-behavior:auto; }
    .js .reveal { opacity:1; transform:none; transition:none; }
    .cue::after { animation:none; }
    .mapfold .chev { transition:none; }
    .xbtn { transition:none; }
  }

  /* ---- small screens ---- */
  @media (max-width:760px) {
    .wrap { padding-right:clamp(64px,17vw,88px); }
    .vtitle { font-size:clamp(44px,11.5vw,60px); top:288px;
      right:clamp(6px,2.5vw,18px); }
    .cv h1 { font-size:clamp(88px,24vw,120px); }
    .cv-photo { width:74vw; }
    .cv-route { right:clamp(56px,15vw,90px); letter-spacing:.1em; }
    .dhead { gap:14px; }
    .r { grid-template-columns:70px minmax(0,1fr); column-gap:10px;
      padding-left:16px; }
    .t { font-size:10.5px; }
    .photo, .photo.pl { float:none; width:min(86%,400px);
      margin:6px auto 24px; }
    .pp, .pp.pl { float:none; width:min(80%,340px); margin:8px auto 26px; }
    .pp.pg { width:min(88%,360px); }
    .stick, .stick.sr { float:none; margin:4px auto 12px; }
    .prop { width:138px; margin:0 0 10px 14px; }
    .tocstrip { gap:10px; }
    .tocstrip img { height:40px; }
    .cv-edge { display:none; }
    .ix { grid-template-columns:auto minmax(0,1fr) auto; row-gap:2px; }
    .ix .ixr { display:none; }
    .ix .ixc { grid-column:2 / 4; font-size:11px; }
    ol.check, .briefs { columns:1; }
  }

  /* ---- print: re-ink to dark-on-white, drop the collage machinery ---- */
  @media print {
    body::after, .tear, .rail, .stamp, .cue, .la, .mapfold, .pageno,
    .stick, .tocstrip, .rstamp, .issue, .ht, .prop, .cv-edge, .xbtn, .tocx
      { display:none !important; }
    .pp, .pp.pl { float:none; rotate:none; margin:8px auto; }
    .pp .pi { box-shadow:none; rotate:none; }
    .pp img, .photo img { filter:none !important; }
    .chap, .f-cream, .f-yellow, .f-blue, .f-ink, .f-red {
      --bg:#fff; --tx:#1C1712; --soft:#443E33; --accS:#8F1F0B;
      --accL:#8F1F0B; --hair:rgba(0,0,0,.35);
      background:#fff !important; color:#1C1712 !important; }
    .cv { min-height:auto; }
    .cv h1 { color:#1C1712; text-shadow:none; writing-mode:horizontal-tb; }
    .cv-dates, .cv-eyebrow, .cv-route { color:#443E33; position:static; }
    .cv-side { position:static; align-items:flex-start; }
    .cv-photo, .photo { transform:none; }
    .vtitle { position:static; writing-mode:horizontal-tb; text-shadow:none;
      font-size:26px; margin:0 0 8px; padding:8px 0 0; }
    .wrap { padding:18px 0; max-width:none; }
    .js .reveal { opacity:1 !important; transform:none !important; }
    .band img { height:200px; }
    .day { break-inside:avoid-page; }
    .hband { background:#fff !important; }
    .hband .dnum { color:#8F1F0B; border-color:#8F1F0B; }
    .hband .kicker, .hband .dcity, .hband .dlabel, .hband .sun {
      color:#1C1712; }
    .dnum { border-color:#8F1F0B; }
    .tl { border-top-color:#1C1712; }
    a { text-decoration:none; color:inherit; }
  }
"""
    css = css.replace("__NOISE__", noise_uri()).replace("__RING__", ring)
    if cover_credit:                # rule injected only when the line exists
        css += CREDIT_CSS           # (art without a credit → bytes unchanged)
    credit_html = f'\n    <p class="cv-credit">{esc(cover_credit)}</p>' if cover_credit else ""

    html_out = f"""<!doctype html>
<html lang="{T("html_lang")}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(page_title)}</title>
<style>{css}</style>
</head>
<body>
{render_rail(days)}
<a class="stamp" href="#toc">{esc(t("stamp_toc"))}</a>

<div id="zine">
<header class="chap cv f-blue" id="top">
  <p class="cv-edge" aria-hidden="true">{esc(edge)}</p>
  {cover_html}
  <div class="cv-side">
    <h1>{esc(cover_zh)}</h1>
    <p class="cv-dates">{esc(dates)}</p>{credit_html}
  </div>
  <div class="cv-foot">
    <p class="cv-eyebrow">{esc(eyebrow)}</p>
    <p class="cv-route">{route}</p>
    <a class="cue" href="#toc">{esc(t("cue"))}</a>
  </div>
</header>

<section class="chap toc f-cream" id="toc" data-spy>
  {tear("tear-toc")}
  <div class="wrap">
    <div class="sechead"><i class="sq" aria-hidden="true"></i>
      <h2>{esc(t("h_toc"))}</h2><span class="en">CONTENTS · {len(days)} DAYS</span></div>
    {tocstrip}
    {render_toc(days)}
    <p class="toc-note">{esc(meta.get("party", ""))} · {esc(T("sec.budget"))} {esc(meta.get("budget_total", ""))}</p>
    <div class="tocx">
      <a class="xbtn xbtn-page no-export" href="#" data-x-page
        aria-label="{esc(t("tip_page_aria"))}"
        title="{esc(t("tip_page"))}">{esc(T("btn.save_page"))}</a>
      <span class="tocx-en" aria-hidden="true">WHOLE ISSUE · ONE LONG IMAGE</span>
    </div>
  </div>
</section>

<main>
{days_html}

<section class="chap colo f-cream" id="app" data-spy>
  {tear("tear-colophon")}
  <button class="xbtn xbtn-appx no-export" data-x-for="#app" data-x-label="{esc(T("label.appendix"))}"
    title="{esc(t("tip_appendix"))}">{esc(T("btn.save_appendix"))}</button>
  <div class="wrap">
    <div class="sechead"><i class="sq" aria-hidden="true"></i>
      <h2>{esc(t("h_app"))}</h2><span class="en">COLOPHON · INDEX</span></div>

    <section id="legs">
      <div class="sechead"><i class="sq" aria-hidden="true"></i>
        <h3>{esc(t("sec_legs"))}</h3><span class="en">{ic("plane")} FLIGHTS</span></div>
      {prop(props.get("legs"))}
      {render_legs(p.get("legs", []))}
    </section>

    <section id="hotels">
      <div class="sechead"><i class="sq" aria-hidden="true"></i>
        <h3>{esc(T("sec.hotels"))}</h3><span class="en">{ic("hotel")} STAYS</span></div>
      {prop(props.get("hotels"))}
      {render_hotels(p.get("hotels", []))}
    </section>

    <section id="budget">
      <div class="sechead"><i class="sq" aria-hidden="true"></i>
        <h3>{esc(T("sec.budget"))}</h3><span class="en">{ic("wallet")} BUDGET</span></div>
      {render_budget(p.get("budget", []), meta.get("budget_total", ""))}
    </section>

    <section id="checklist">
      <div class="sechead"><i class="sq" aria-hidden="true"></i>
        <h3>{esc(t("sec_checklist"))}</h3><span class="en">{ic("checklist")} CHECKLIST</span></div>
      {prop(props.get("checklist"))}
      {render_checklist(p.get("checklist", []))}
    </section>

    <section id="brief">
      <div class="sechead"><i class="sq" aria-hidden="true"></i>
        <h3>{esc(T("sec.brief"))}</h3><span class="en">{ic("book")} NOTES</span></div>
      {rstamp(kick_en)}
      <div class="briefs">{render_brief(p.get("brief", {}))}</div>
    </section>

    <section id="decisions">
      <div class="sechead"><i class="sq" aria-hidden="true"></i>
        <h3>{esc(T("sec.decisions"))}</h3><span class="en">{ic("brain")} DECISIONS</span></div>
      <ol class="plain">{decisions}</ol>
    </section>

    <section id="unverified">
      <div class="sechead"><i class="sq" aria-hidden="true"></i>
        <h3>{esc(T("sec.unverified"))}</h3><span class="en">{ic("alert")} UNVERIFIED</span></div>
      <ul class="warn">{unverified}</ul>
    </section>

    <footer class="colofoot">
      {issue_bar}
      {esc(p.get("trip", ""))}<br>
      {esc(meta.get("party", ""))} · {esc(t("fx"))} {esc(meta.get("fx", ""))}<br>
      {esc(meta.get("generated", ""))}<br>
      {esc(t("footer"))} · {esc(colo_issue)}
    </footer>
  </div>
</section>
</main>
</div>

<script>
(function () {{
  document.documentElement.classList.add('js');
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  try {{
    var rail = [].slice.call(document.querySelectorAll('.rail a[data-for]'));
    if (rail.length) {{
      var spy = new IntersectionObserver(function (es) {{
        es.forEach(function (e) {{
          if (!e.isIntersecting) return;
          rail.forEach(function (l) {{
            if (l.getAttribute('data-for') === e.target.id)
              l.setAttribute('aria-current', 'true');
            else l.removeAttribute('aria-current');
          }});
        }});
      }}, {{ rootMargin: '-40% 0px -50% 0px' }});
      document.querySelectorAll('[data-spy]').forEach(function (s) {{
        spy.observe(s);
      }});
    }}
  }} catch (err) {{}}

  document.querySelectorAll('details.mapfold').forEach(function (d) {{
    d.addEventListener('toggle', function () {{
      if (!d.open) return;
      var box = d.querySelector('.map-embed');
      if (!box || box.dataset.done) return;
      box.dataset.done = '1';
      var f = document.createElement('iframe');
      f.referrerPolicy = 'no-referrer-when-downgrade';
      f.src = box.dataset.src;
      f.addEventListener('load', function () {{
        var ph = box.querySelector('.map-ph'); if (ph) ph.remove();
      }});
      box.appendChild(f);
    }});
  }});

  var nodes = document.querySelectorAll('.reveal');
  if (reduce || !('IntersectionObserver' in window)) {{
    nodes.forEach(function (n) {{ n.classList.add('in'); }});
  }} else {{
    var rev = new IntersectionObserver(function (es) {{
      es.forEach(function (e) {{
        if (e.isIntersecting) {{ e.target.classList.add('in'); rev.unobserve(e.target); }}
      }});
    }}, {{ rootMargin: '0px 0px -7% 0px' }});
    nodes.forEach(function (n) {{ rev.observe(n); }});
    setTimeout(function () {{   // watchdog: environments that suspend IO
      if (!document.querySelector('.reveal.in'))
        nodes.forEach(function (n) {{ n.classList.add('in'); }});
    }}, 1400);
  }}
}})();
</script>
<script>
EXPORT_JS_PLACEHOLDER
</script>
</body>
</html>"""
    html_out = inline_icons(html_out)
    # export capture overrides: force scroll-reveal states visible, drop the
    # module's own top tear (it is the PREVIOUS chapter's bottom edge and
    # renders 64px above the clone), neutralise the svh cover height (inside
    # the capture 96svh = 96% of the 16000px-tall image), collapse the map
    # fold's online-only innards, and re-lay the fixed paper-grain overlay
    # (body::after never survives the clone) onto the capture wrapper.
    xcss = (
        ".js .reveal{opacity:1!important;transform:none!important}"
        ".__xbody>.chap>.tear:first-child{display:none!important}"
        ".cv{min-height:auto!important}"
        ".mapfold .map-embed,.mapfold .hops{display:none!important}"
        ".__xbody{position:relative}"
        '.__xbody::after{content:"";position:absolute;inset:0;z-index:60;'
        "pointer-events:none;opacity:.5;mix-blend-mode:multiply;"
        'background:url("' + noise_uri() + '")}')
    html_out = html_out.replace("EXPORT_JS_PLACEHOLDER", export_js(
        theme_name(THEME), "#F2EAD8", extra_css=xcss, page_root="#zine",
        file_prefix=export_prefix(ART, meta, THEME)))
    out = pathlib.Path(args.out)
    out.write_text(html_out, encoding="utf-8")
    print(f"{out.name}: {out.stat().st_size // 1024}KB, days={len(days)}, "
          f"assets={asset_count()}")


if __name__ == "__main__":
    main()
