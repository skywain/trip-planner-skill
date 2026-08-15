#!/usr/bin/env python3
"""Splash-theme renderer — one Brawl-Stars-style splash poster stretched
into a vertical scroll.

Identity (the four axes, distinct from the other six themes):
  * organising principle: a single poster's light-field extended downward as
    a chained per-chapter gradient (stop N end == stop N+1 start) that now
    tells a full day/night colour story (night flight → NYC neon → lilac
    day → stadium night → dusk west → rainbow springs → alpine morning →
    golden fog → canyon teal → pacific blue → lava → sunrise gold → night),
    plus diagonal palette washes + light streaks + soft-focus blobs + a
    seeded heart/triangle/spark particle field (build-time PRNG, never JS
    random) + a wide-viewport side field of same-brush splash clouds /
    rainbow balloon / four-point star / sparks / glow dots parked outside
    the text column, and silhouette strips (a trip's own skyline / sunset
    cut-outs, e.g. a night city under the first two chapters) melted into
    the chapter foot as the farthest scenery layer — opacity-capped and
    budgeted by contrast_report(), parked behind the hill silhouettes;
  * interaction: plain vertical scroll along one glowing ribbon road — an
    SVG gradient-stroked path drawn PER CHAPTER (a page-long path would be
    rasterised at full length; see theme-system §4.4) that parks in the
    3.5% / 96.5% gutters so its bright core mathematically never crosses
    the text bands at any viewport width; chapter seams are bridged by
    hill silhouettes whose two halves are each drawn by their own chapter;
  * type voice: the painted title plate (art: hero.title) + heavy rounded
    system faces (weight 800/900, tracked), brush-feel giant numerals 01-11;
  * shape language: big cut-out silhouettes and confetti shards; rainbow
    arches / sun discs / halos / radial beams behind the floating islands
    (all CSS gradients — zero extra image cost); buttons are skewed solid
    slabs; a trip's painted vehicles (a prop plane with cream speed lines
    on its flight days, a luggage-rack tour bus on its group-tour days…)
    and mascot stickers ride the chapter heads — all inside .scene so they
    can never reach band copy; NO white rounded cards anywhere — body copy
    sits on feather-edged darker patches of the same light-field.

ART CONTRACT (what this renderer reads from the trip's art.json — schema in
ART-SCHEMA.md — and how it degrades when a field is missing; the renderer
never carries a place, a date or a picture name of its own):

  common (themes.splash.cover.* / .end.* override cover.* / end.* per key)
    cover.zh          alt text of the painted title plate, and the TEXT title
                      when the trip has no plate → cover.kick → 「出发!」
    cover.sub         the route line under the poster ("纽约 · 球赛 · 黄石")
                      → the plan's meta.route → line omitted
    cover.en          small-caps English line right under the title plate
                      (.en, cream, tracked) → not written
    cover.credit      allusion / source line under the route: one cream
                      monospace badge (.credit) → not written. Keep the poem
                      citation HERE, not in `sub` (that is what two-lined the
                      China cover: an English sub carrying route + citation).
    brief_titles      (art common) {brief key: display title} overlay on
                      theme_common.BRIEF_TITLES — the 行前须知 card headings
                      ("visa" → 签证 · EVUS); unknown keys print as they are
    cover.kick        <title> prefix ("{kick} {year} · 闪屏版行程") and the
                      export filename prefix (theme_common.export_prefix);
                      en page: cover.kick_en wins when set (title_kick)
                      → "{year} · 闪屏版行程" / "{year}-"
    end.line / .fine  endcap closing line / fine print → not written (the
                      spark glyph stays)
    days[d].theme     4-char day title (h2 + jump aria-label) → plan city
  themes.splash
    hero.title        asset stem of the painted title plate (md variant)
                      → cover.zh as an outlined text title
    hero.art          asset stem of the poster's floating hero island (md)
                      → the figure is dropped (its fx go with it)
    hero.palette / hero.scene / hero.wash   colour of the first chapter (see
                      PALETTE below) → kit mood "night"
    hero.sides        extra side-field kinds for the hero, e.g. ["balloon"]
                      → the seeded kit pool only
    appendix.palette / .scene / .wash / .sides   same for the last chapter
                      → kit mood "homebound"; sides pool only
    vehicles          {name: {stem, ratio, speedlines?}} the trip's painted
                      vehicles (class .veh-<name>; ratio = "w/h" of the
                      cut-out; speedlines adds the cream trails behind a
                      plane). A vehicle whose asset is not found paints
                      nothing wherever it is placed.
    mascots           {name: {stem, ratio}} sticker mascots (.mas-<name>)
    strips            {name: {stem, ratio}} foot silhouettes (.strip-<name>),
                      centred, opacity-capped at STRIP_A
    days[d].palette   kit mood name for the chapter's sky (chained: the
                      chapter starts on the previous chapter's last stop)
    days[d].scene     OR explicit gradient stops ["#hex", …] (verbatim — the
                      author owns the seam) · days[d].wash = wash/streak
                      pastels; missing → DEFAULT_RHYTHM cycles the moods
    days[d].island    asset stem of the day's floating island (sm variant)
                      → none (a CSS medallion takes the slot unless fx says
                      otherwise)
    days[d].fx        scene effect behind the island, one of the kit
                      (halo-cyan · halo-gold · halo-teal · burst · beams-cool
                      · rainbow · "rainbow sm" · sun · moon · dusk · sunrise;
                      "" = nothing) → "" with an island, else a medallion
                      by day-number rhythm (moon / dusk / sunrise)
    days[d].vehicle   {kind, when: pre|post, pos} — kind names a `vehicles`
                      entry, when = behind/in front of the island, pos =
                      inline CSS placement inside .scene → none
    days[d].mascot    {kind, pos} — kind names a `mascots` entry → none
    days[d].strip     name of a `strips` entry → none
    days[d].sides     extra side-field kinds (kit words cloud · spark · dot
                      · shard · heart · star · balloon, or {"stem", "w"} for
                      one of the trip's own cut-outs) → pool only

  PALETTE (kit): MOODS names the theme's twelve sky moods — each is four
  gradient stops + its wash pastels, every stop pre-verified dark enough for
  AA under the band (contrast_report() re-checks the resolved chain at build
  time). Chapters chain: stop 0 of chapter N+1 == stop 3 of chapter N, so
  any mood order still seams cleanly.

  ASSET SIZE VARIANTS (hero.sides / appendix.sides trip cut-outs {"stem","w"} → sm) (theme_common.data_uri; the wrong guess is silent):
    hero.title / hero.art → "md" (<stem>.md.webp, falls back to .cut / plain)
    days[d].island        → "sm"
    vehicles / mascots / strips (registry stems) → "cut" (the cut-out itself)
    kit cut-outs (splash-cloud-* / -star / -balloon) → "cut"
    `ratio` in a registry entry is the CUT-OUT's w/h, not the sheet's.

  TEXT LIMITS (measured 2026-08-15 in headless Chrome at a 1200px viewport
  → 1152px of hero text, and at 390px → 342px; the plate-less text title
  .ht-txt is var(--disp) 900 at clamp(52px,12vw,124px), .06em). One line
  holds at most:
    title (no plate)  ~14 Latin caps / 8 CJK           (1200px, 124px type;
                      re-measured with line-box counts — the .ht pop
                      animation scales to .72 at t=0, which once inflated
                      an earlier estimate to 21/12)
                      ~8 Latin caps / 5 CJK           (390px, 52px type, est.)
                      — "MOON OF QIN" (11) needs a plate on a phone; a painted
                      plate (md, 600px wide) has no text limit, its words
                      are pixels.
    sub / .route      63 Latin / 45 CJK (1200px) · 27 Latin / 18 CJK (390px)
                      — 78-char English subs two-line the phone cover; put
                      the citation in `credit` instead.
    en                92 Latin (1200px) · 34 Latin (390px)  (12px caps)
    credit            79 Latin / 46 CJK (1200px) · 43 Latin / 25 CJK (390px)
                      inside the badge (12px mono; wraps, badge stays ≤600px)
  Everything wraps rather than overflows; only the title's wrap looks wrong.

  KIT (nothing to pick in art): the ribbon road + gutters, hills, seeded
  confetti / washes / blobs, the side-field pool and its cloud / star /
  balloon cut-outs (theme library), rainbow / halo / sun / burst / beam fx,
  the three CSS medallions, big numerals, bands, export badges.

PNG export (share): theme_common.export_js engine, whole page + per-chapter
modules. Wording is the family-wide one — 「保存这一天」/「保存附录」 per
module, 「生成长图」 for the whole scroll. The badges speak the theme's own
shape language — skewed solid slabs, kin of the mapfold/hop chips and of
.tag-pin's hard purple drop, with a painted #3A1272 stroke and a pink halo
so they are legible at rest at an UNCHANGED 12.5px (one per day chapter,
one on the appendix, one fixed whole-page badge). The per-module badges ride
in normal flow at the foot of their own band — the earlier absolute
bottom-right parking put them straight across the glowing ribbon road, which
lives in the 96.5% gutter. extra_css pins .reveal visible and
zeroes the hero's 100svh (vh resolves against the FULL capture height inside
the SVG image document, which would balloon the hero in a whole-page grab).
Icons and confetti particles are <use> references to the page-top sprite;
capture clones are serialised as standalone documents, so the export engine
(theme_common.export_js → spriteFor) copies the referenced <symbol>s into
every capture — this renderer does nothing extra for it. (Until 2026-08-15
nothing did, and every icon/particle exported blank; the other themes had
dodged it by inlining icons at build time.)

Usage: python3 render_splash.py <plan.geo.json> [--art <art.json>|none]
                                [--assets DIR ...] -o <out.html>
Assets (islands, vehicles, mascots, strips) are searched in the plan's
directory, every --assets DIR, then themes/assets/ (theme_common.data_uri).
"""
import argparse
import pathlib
import random
import re

from theme_common import (T, add_art_arg, asset_count, brief_titles,
                          data_uri, day_embed_url, esc, et, export_js, export_prefix,
                          ic, init_lang, lang, load_art, load_plan, short_dates, sprite, title_head,
                          tag_pretty, theme_name)

HERE = pathlib.Path(__file__).parent
THEME = "splash"

# ------------------------------------------------------------- theme voice --
# The poster's own words: cover fallback, badge labels, map-fold chip, jump
# nav, button hints, appendix headings that differ from the shared ones,
# tail plate / footer. Shared UI strings (tags, save buttons, 步行/雨备/晚点剪
# 法, section names) come from theme_common.T(). zh values are byte-identical
# to the pre-i18n page — the US baseline pins them.
L = {
    "zh": {
        "poster_word": "出发!",
        "title_suffix": "闪屏版行程",
        "nav.to": "导航到 ",
        "km": " ≈{} km",
        "note": "注",
        "day_route": "整日路线",
        "hop_n": "第{}跳导航",
        "map_ph": "地图加载中…(需联网;离线请用下方链接)",
        "map_label": "沿途地图 · 逐跳导航 ×{}",
        "save_day.title": "把这一天存成图片,可发朋友圈",
        "save_appx.title": "把附录(航段/住宿/预算/清单)存成图片",
        "save_page.title": "把整卷行程拼成一张长图,几秒钟",
        "backup": "备选",
        "th.item": "项目", "th.cost": "费用", "th.note": "注", "total": "合计",
        "jump.to": "跳到第{}天 · ",
        "jump.appx": "跳到附录",
        "jump.label": "跳到某一天",
        "cue": "下滑查看行程",
        "totop": "回到顶部",
        "legs": "航段速览",
        "checklist": "行前清单",
        "fx": "汇率",
        "foot": "日出日落数据:sunrise-sunset.org · 插画与设计稿由 AI 生成,仅作示意 · 价格以预订渠道实时为准",
    },
    "en": {
        "poster_word": "Let's go!",
        "title_suffix": "Splash itinerary",
        "nav.to": "Navigate to ",
        "km": " ≈{} km",
        "note": "note",
        "day_route": "whole-day route",
        "hop_n": "hop {} directions",
        "map_ph": "Map loading… (needs a connection; offline, use the links below)",
        "map_label": "Maps along the way · hop-by-hop ×{}",
        "save_day.title": "Save this day as an image to share",
        "save_appx.title": "Save the appendix (legs / stays / budget / checklist) as an image",
        "save_page.title": "Stitch the whole scroll into one long image, a few seconds",
        "backup": "backup",
        "th.item": "Item", "th.cost": "Cost", "th.note": "Note", "total": "Total",
        "jump.to": "Jump to day {} · ",
        "jump.appx": "Jump to the appendix",
        "jump.label": "Jump to a day",
        "cue": "Scroll for the itinerary",
        "totop": "Back to top",
        "legs": "Flights & legs",
        "checklist": "Checklist",
        "fx": "FX",
        "foot": "Sun times: sunrise-sunset.org · illustrations and layouts generated by AI, illustrative only · prices: check the booking channel",
    },
}


def t(k):
    return L.get(lang(), L["zh"]).get(k, L["zh"][k])


def sun_text(day):
    """The plan's sun line; sun --write emits 天亮 (zh) or dawn (en) — show it
    in the page language either way."""
    return et(re.sub(r"^(天亮|dawn)\b", T("sun.dawn"), day.get("sun", "") or ""))

# ---------------------------------------------------------------- palette ---
# Sky moods — the theme's colour vocabulary. Each mood = four gradient stops
# (the chapter paints linear-gradient(180deg, *stops)) + the pastel palette
# its washes / streaks / blobs / dots are picked from (alpha caps below keep
# that stack inside the contrast budget no matter which pastel is drawn).
# Chapters CHAIN: chapter i+1 starts on chapter i's last stop, so every seam
# matches exactly while the sky inside a chapter is free to swing hue. Every
# stop is kept dark enough that even the LIGHTEST field point under the worst
# wash+streak stack still passes AA behind the band — contrast_report()
# re-verifies the resolved chain numerically at build time. art.json picks a
# mood per chapter by name (days[d].palette) or gives its own stops.
MOODS = {
    "night":      (["#2A0E5C", "#38146E", "#4B1D8E", "#5B28A6"],  # deep purple night sky
                   ["#FFD9F6", "#9BE8FF", "#FFE9A8"]),
    "neon":       (["#5B28A6", "#7434BE", "#64319E", "#7B3FC8"],  # city neon night
                   ["#FF9DE0", "#79E6FF"]),
    "lilac":      (["#7B3FC8", "#9553D6", "#A75CC2", "#8C55D4"],  # pink morning → lilac noon
                   ["#FFD9F6", "#FFE9A8"]),
    "floodlight": (["#8C55D4", "#5B3EBC", "#3D35A8", "#4A2FA8"],  # indigo stadium night
                   ["#79E6FF", "#B8C0FF"]),
    "dusk":       (["#4A2FA8", "#7C3CB4", "#9C4693", "#A64896"],  # rose dusk, chasing the sun
                   ["#FFC9A0", "#FF9DE0"]),
    "rainbow":    (["#A64896", "#B84A62", "#A85630", "#7A4AB6"],  # warm rose → amber
                   ["#FF8A8A", "#FFE9A8", "#9BFFC8", "#79E6FF", "#E0B0FF"]),
    "alpine":     (["#7A4AB6", "#4A55C0", "#2F68A8", "#4156B4"],  # cold blue-teal mountain morning
                   ["#9BE8FF", "#D8FFF6"]),
    "goldfog":    (["#4156B4", "#7A4E9C", "#A85A38", "#8C4470"],  # golden fog light
                   ["#FFD9A0", "#FFB0C8"]),
    "canyon":     (["#8C4470", "#4E62A0", "#2F7E72", "#3A6B8E"],  # waterfall teal-green
                   ["#A0FFD8", "#9BE8FF"]),
    "ocean":      (["#3A6B8E", "#2F62B8", "#4A58C0", "#7A44A8"],  # pacific blue
                   ["#79E6FF", "#FFFFFF"]),
    "lava":       (["#7A44A8", "#A03A64", "#B84C2C", "#8A3A78"],  # lava orange-red
                   ["#FFB86C", "#FF8A8A"]),
    "sunrise":    (["#8A3A78", "#A44E4A", "#A86428", "#7A3AA0"],  # golden sunrise
                   ["#FFE9A8", "#FFD9A0", "#FF9DE0"]),
    "homebound":  (["#7A3AA0", "#58208C", "#3A1668", "#251043"],  # night flight home
                   ["#C8B8FF", "#79E6FF"]),
}
HERO_MOOD, APPX_MOOD = "night", "homebound"
# day-number rhythm used when a day names no mood: a generic day/night loop
DEFAULT_RHYTHM = ("lilac", "dusk", "neon", "alpine", "goldfog", "canyon",
                  "ocean", "rainbow", "lava", "sunrise", "floodlight")


def _mood_of(spec, fallback):
    """(stops, wash) a chapter asks for: explicit `scene`/`wash` lists win,
    then a kit mood by `palette` name (unknown names fall back), then the
    given fallback mood name."""
    spec = spec or {}
    stops, wash = MOODS.get(spec.get("palette") or "", MOODS[fallback])
    if isinstance(spec.get("scene"), list) and len(spec["scene"]) >= 2:
        stops = [str(c) for c in spec["scene"]]
    if isinstance(spec.get("wash"), list) and spec["wash"]:
        wash = [str(c) for c in spec["wash"]]
    return stops, wash


def resolve_chain(specs):
    """specs = [hero, day1 … dayN, appendix] chapter dicts (from art). Returns
    (SCENES, PALS): per-chapter stop lists chained at the seams (a chapter
    that names a mood starts on the previous chapter's last stop; explicit
    `scene` stops are taken verbatim) and per-chapter pastel palettes."""
    scenes, pals = [], []
    for ci, spec in enumerate(specs):
        if ci == 0:
            fb = HERO_MOOD
        elif ci == len(specs) - 1:
            fb = APPX_MOOD
        else:
            fb = DEFAULT_RHYTHM[(ci - 1) % len(DEFAULT_RHYTHM)]
        stops, wash = _mood_of(spec, fb)
        if ci and not (isinstance((spec or {}).get("scene"), list)):
            stops = [scenes[-1][-1]] + list(stops[1:])
        scenes.append(list(stops))
        pals.append(list(wash))
    return scenes, pals

WHITE = (255, 255, 255)
CREAM = (255, 239, 201)     # #FFEFC9 — times, accents
PALE = (234, 220, 255)      # #EADCFF — secondary copy
DEEP = (42, 16, 80)         # #2A1050 — ink for light chips / buttons
GOLD = (255, 201, 60)       # #FFC93C — pinned badge
BAND = (30, 10, 60)         # band smudge colour
BAND_A = 0.50
STREAK_A = 0.14             # max alpha of one palette streak
WASH_A = 0.09               # max alpha of one broad palette wash
BLOB_A = 0.10               # max alpha of one soft-focus blob

# Per-day scenery (which island / fx / vehicle / mascot / strip / side extras
# a chapter carries) comes from art.json — see the ART CONTRACT above. The
# kit below is what art picks FROM.
MEDALLIONS = ("moon", "dusk", "sunrise")   # CSS-only heads for island-less days
STRIP_A = 0.32  # strip opacity cap — contrast_report() budgets it under the band

KIND_ICON = {"anchor": ("flag", "ki-anchor"), "hop": ("arrow", "ki-hop"),
             "meal": ("meal", "ki-meal"), "free": ("moon", "ki-free")}

GUT_L, GUT_R = 3.5, 96.5     # road parking gutters (% of chapter width)


def grad(stops):
    n = len(stops) - 1
    return ("linear-gradient(180deg," +
            ",".join(f"{c} {i * 100 // n}%" for i, c in enumerate(stops)) + ")")


def _rgb(hx):
    r, g, b = _hex(hx)
    return f"{r},{g},{b}"


# ------------------------------------------------------------- decorations --
def road_svg(d):
    """One chapter's stretch of the ribbon road. Glow = stacked wide strokes
    (no CSS blur on paths — theme-system §4.4)."""
    layers = "".join(
        f'<path class="{c}" d="{d}" vector-effect="non-scaling-stroke"/>'
        for c in ("r-glow", "r-mid", "r-core", "r-sheen"))
    return (f'<svg class="road" viewBox="0 0 100 100" preserveAspectRatio="none" '
            f'aria-hidden="true">{layers}</svg>')


def day_road(entry, park):
    # The S-bend must finish inside the chapter HEAD zone: chapter height is
    # dominated by the text band, so any bend that ends deeper than ~6% would
    # sweep its bright core under band copy and locally break AA (measured:
    # the first build bent to 27% and crossed the DAY overline). 6% of the
    # tallest chapter ≈ 190px, still above where band text starts.
    return road_svg(f"M {entry} 0 C {entry} 2, {park} 3.2, {park} 6 L {park} 100")


def deco(ci, pal, n_pt=16):
    """Seeded per-chapter decoration layer: 2 broad diagonal palette washes +
    4 brush streaks in the head zone (2-32%), 2 soft-focus blobs lower down
    (42-86%), and the confetti field. A wash and a streak may overlap each
    other but never a blob; contrast_report() budgets the full wash+streak
    stack under the band. `pal` = the chapter's pastel palette."""
    # seed = the theme's frozen kit constant (any change re-rolls every
    # page ever built with it), stepped per chapter
    rnd = random.Random(20260925 + ci * 7919)
    bits = []
    for _ in range(2):          # washes: the poster's big paint-in-the-sky
        bits.append(
            '<i class="stk" style="left:{:.1f}%;top:{:.1f}%;width:{:.1f}%;'
            'height:{:.0f}px;--c:{};--a:{:.2f};--r:{:.0f}deg"></i>'.format(
                rnd.uniform(-18, 50), rnd.uniform(2, 15), rnd.uniform(55, 96),
                rnd.uniform(120, 260), _rgb(rnd.choice(pal)),
                rnd.uniform(.05, WASH_A), rnd.uniform(-26, -15)))
    for _ in range(4):          # streaks: tighter bright brush lines
        bits.append(
            '<i class="stk" style="left:{:.1f}%;top:{:.1f}%;width:{:.1f}%;'
            'height:{:.0f}px;--c:{};--a:{:.2f};--r:{:.0f}deg"></i>'.format(
                rnd.uniform(-6, 68), rnd.uniform(3, 30), rnd.uniform(26, 50),
                rnd.uniform(10, 24), _rgb(rnd.choice(pal)),
                rnd.uniform(.08, STREAK_A), rnd.uniform(-30, -17)))
    for _ in range(2):          # soft-focus colour blobs
        s = rnd.uniform(180, 360)
        bits.append(
            '<i class="blob" style="left:{:.1f}%;top:{:.1f}%;width:{:.0f}px;'
            'height:{:.0f}px;--c:{};--a:{:.2f}"></i>'.format(
                rnd.uniform(0, 78), rnd.uniform(42, 86), s, s * rnd.uniform(.6, 1),
                _rgb(rnd.choice(pal + ["#FFBEF0"])), rnd.uniform(.06, BLOB_A)))
    shapes = ["heart"] * 9 + ["tri"] * 8 + ["spark"] * 4
    colors = ["#FF8AD6", "#FFE9A8", "#79E6FF", "#FFFFFF", "#F25CC1", "#9BFFC8"]
    for _ in range(n_pt):
        sz = rnd.uniform(9, 22)
        left, top = rnd.uniform(2, 93), rnd.uniform(3, 94)
        # hero only: keep the confetti out of the first screen's right corner,
        # where the fixed 生成长图 badge parks at every viewport height
        # (badge top lands at 42-89% of the 1510px hero for 700-1350px tall
        # viewports). Measured: one triangle sat under the badge at 1280x1000.
        if ci == 0 and left > 82 and 38 < top < 92:
            left -= 26
        bits.append(
            '<svg class="pt" style="left:{:.1f}%;top:{:.1f}%;width:{:.0f}px;'
            'height:{:.0f}px;color:{};--o:{:.2f};--r:{:.0f}deg;'
            'animation-duration:{:.1f}s;animation-delay:{:.1f}s">'
            '<use href="#p-{}"/></svg>'.format(
                left, top, sz, sz,
                rnd.choice(colors), rnd.uniform(.35, .8), rnd.uniform(-40, 40),
                rnd.uniform(3.2, 7.0), rnd.uniform(0, 6), rnd.choice(shapes)))
    return f'<div class="deco" aria-hidden="true">{"".join(bits)}</div>'


def _wavepath(rnd, lo, hi, close_y):
    """Smooth rolling ridge across the 0-100 viewBox (flat tangents at every
    crest, so no kinks), closed to close_y beyond the box = the solid edge."""
    pts, x = [], -4.0
    while x < 116:
        pts.append((x, rnd.uniform(lo, hi)))
        x += rnd.uniform(20, 34)
    d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        dx = (x1 - x0) * .48
        d += f" C {x0 + dx:.1f} {y0:.1f},{x1 - dx:.1f} {y1:.1f},{x1:.1f} {y1:.1f}"
    d += f" L {pts[-1][0]:.1f} {close_y} L -4 {close_y} Z"
    return d


def hill(ci, edge):
    """One chapter's half of a seam-crossing hill silhouette. Both halves are
    SOLID at the shared edge, so the dark ridge reads as one range running
    across the chapter boundary no matter how the crests differ. Drawn per
    chapter — a single page-long shape would be painted over by the next
    chapter's background (theme-system §4.3), and these short fills stay far
    from every compositor limit."""
    rnd = random.Random(5150 + ci * 61 + (7 if edge == "t" else 0))
    if edge == "b":     # crest-up piece at the chapter's foot
        back = _wavepath(rnd, 16, 46, 108)
        front = _wavepath(rnd, 44, 72, 108)
    else:               # hanging piece at the chapter's head
        back = _wavepath(rnd, 52, 84, -8)
        front = _wavepath(rnd, 24, 50, -8)
    return (f'<svg class="hill h-{edge}" viewBox="0 0 100 100" '
            'preserveAspectRatio="none" aria-hidden="true">'
            f'<path fill="rgba(21,9,46,.16)" d="{back}"/>'
            f'<path fill="rgba(23,8,44,.30)" d="{front}"/></svg>')


def sides(ci, pal, n=5, extra=()):
    """Wide-viewport side field: floating splash clouds (same-brush wishlist
    set — the borrowed clay clouds went home to the clay theme) / rainbow
    balloon / four-point star / sparks / glow dots / confetti shards parked
    OUTSIDE the 768px text column
    via calc(50% ± offset) anchoring — on phones they land off-canvas and the
    chapter's own confetti carries the sides, so no media query is needed.
    Depth = size × opacity pairing (big and solid floats near, small and
    faint sits far). Image kinds are CSS background classes, so each cut-out
    is base64-embedded exactly once no matter how often it appears.
    `extra` = kinds art asks for on top of the seeded pool (kit words, or
    {"stem", "w"} for one of the trip's own cut-outs — drawn as an <img>,
    skipped when the asset is missing)."""
    rnd = random.Random(994009 + ci * 65537)
    pool = ["cloud", "cloud", "spark", "dot", "shard", "heart", "star"]
    kinds = list(extra)
    while len(kinds) < n + len(extra):
        kinds.append(rnd.choice(pool))
    bits = []
    slot = 79.0 / len(kinds)   # stratified: one vertical band per item, jitter inside
    for j, kind in enumerate(kinds):
        anchor = "right" if (j + ci) % 2 == 0 else "left"
        off = rnd.uniform(398, 580)
        top = 5 + slot * (j + rnd.uniform(0.15, 0.85))
        # The hero's first-screen RIGHT corner is the page's tool corner (the
        # fixed 生成长图 badge sits at bottom:16px, and the back-to-top button
        # beside it). "left" anchoring parks an item to the right of the text
        # column, so one landing in the 30-88% band of the 1510px hero drifts
        # straight under the badge on a normal viewport — measured: cloud j=3
        # at 53.9% covered its left third at 1280x900. Send that band to the
        # other side; the items above and below it stay, so the field keeps
        # both flanks.
        if ci == 0 and anchor == "left" and 30 < top < 88:
            anchor = "right"
        pos = (f"{anchor}:calc(50% + {off:.0f}px);top:{top:.1f}%")
        anim = f"--dur:{rnd.uniform(6.5, 12):.1f}s;--del:{rnd.uniform(0, 5):.1f}s"
        near = rnd.random() > 0.45
        if isinstance(kind, dict):  # a trip's own cut-out (art: {"stem","w"})
            uri = data_uri(str(kind.get("stem", "")), "sm")
            if uri:
                w = float(kind.get("w") or rnd.uniform(110, 170))
                bits.append(f'<img class="side" src="{uri}" alt="" style="{pos};'
                            f'width:{w:.0f}px;height:auto;opacity:.92;{anim}">')
        elif kind == "cloud":
            cls = rnd.choice(("sc-a", "sc-b", "sc-c", "sc-d"))
            w = rnd.uniform(120, 190) if near else rnd.uniform(70, 110)
            op = rnd.uniform(.72, .95) if near else rnd.uniform(.45, .6)
            bits.append(f'<i class="side {cls}" style="{pos};width:{w:.0f}px;'
                        f'opacity:{op:.2f};{anim}"></i>')
        elif kind == "balloon":
            bits.append(f'<i class="side sc-bal" style="{pos};'
                        f'width:{rnd.uniform(96, 132):.0f}px;opacity:.94;'
                        f'{anim};--dy:-18px"></i>')
        elif kind == "dot":
            s = rnd.uniform(90, 190)
            bits.append(f'<i class="side dot" style="{pos};width:{s:.0f}px;'
                        f'height:{s:.0f}px;--c:{_rgb(rnd.choice(pal))};'
                        f'--a:{rnd.uniform(.14, .26):.2f};{anim}"></i>')
        elif kind == "shard":
            bits.append(f'<i class="side shard" style="{pos};'
                        f'width:{rnd.uniform(9, 15):.0f}px;'
                        f'height:{rnd.uniform(20, 30):.0f}px;'
                        f'--sc:{rnd.choice(pal)};--o:{rnd.uniform(.5, .75):.2f};'
                        f'--rr:{rnd.uniform(-40, 40):.0f}deg"></i>')
        elif kind == "star":  # wishlist four-point star, the spark pool's big kin
            s = rnd.uniform(26, 46)
            bits.append(f'<i class="side st-star" style="{pos};width:{s:.0f}px;'
                        f'opacity:{rnd.uniform(.55, .9):.2f};{anim}"></i>')
        else:  # spark / heart glyph (an unknown kit word draws a spark)
            glyph = kind if kind in ("spark", "heart") else "spark"
            s = rnd.uniform(22, 42)
            bits.append(f'<svg class="side pt2" style="{pos};width:{s:.0f}px;'
                        f'height:{s:.0f}px;color:{rnd.choice(colors_side)};'
                        f'opacity:{rnd.uniform(.55, .9):.2f};{anim}">'
                        f'<use href="#p-{glyph}"/></svg>')
    return f'<div class="sides" aria-hidden="true">{"".join(bits)}</div>'


colors_side = ["#FFE9A8", "#FF8AD6", "#79E6FF", "#FFFFFF"]


def head_fx(fx):
    """The scene effect living behind a day's floating island — or, for the
    three island-less days, a full CSS medallion in the empty flex slot."""
    if not fx:
        return ""
    if fx == "moon":
        stars = "".join(
            f'<svg class="ms" style="left:{x}%;top:{y}%;width:{s}px;height:{s}px">'
            f'<use href="#p-spark"/></svg>'
            for x, y, s in ((10, 20, 18), (74, 8, 24), (62, 64, 14), (20, 56, 12)))
        return ('<div class="medal m-moon" aria-hidden="true">'
                f'<i class="halo"></i><i class="disc"></i>{stars}</div>')
    if fx == "dusk":
        bars = "".join(f'<i class="dbar" style="left:{l}%;top:{t}%;width:{w}%"></i>'
                       for l, t, w in ((2, 56, 66), (20, 68, 76), (8, 80, 58)))
        return ('<div class="medal m-dusk" aria-hidden="true">'
                f'<i class="dsun"></i>{bars}</div>')
    if fx == "sunrise":
        return ('<div class="medal m-rise" aria-hidden="true"><i class="fxb gold"></i>'
                '<i class="rsun"></i><i class="ring"></i></div>')
    if fx == "burst":
        return '<i class="fx fx-burst" aria-hidden="true"></i>'
    if fx == "beams-cool":
        return '<i class="fx fxb cool" aria-hidden="true"></i>'
    if fx == "sun":
        return ('<i class="fx fx-sun" aria-hidden="true"></i>'
                '<i class="fx fxb gold slow" aria-hidden="true"></i>')
    if fx.startswith("rainbow"):
        sm = " sm" if "sm" in fx else ""
        return f'<i class="fx fx-rainbow{sm}" aria-hidden="true"></i>'
    if fx.startswith("halo-"):
        col = {"halo-cyan": "158,232,255", "halo-gold": "255,217,160",
               "halo-teal": "160,255,216"}[fx]
        return f'<i class="fx fx-halo" style="--c:{col}" aria-hidden="true"></i>'
    return ""


def vehicle(spec, when, vdefs):
    """A trip's painted vehicle on a chapter head (art: days[d].vehicle =
    {kind, when, pos}; kinds are defined in themes.splash.vehicles — e.g. a
    prop plane crossing the flight days, nose left = westbound, cream speed
    lines trailing right; a luggage-rack tour bus on the group-tour days).
    Drawn INSIDE .scene so they can never overlap band copy; `when` picks
    whether the sprite paints behind ("pre") or in front of ("post") the
    island/medallion via DOM order (all of them sit at the same z level).
    `vdefs` = the resolved vehicle kinds (only those whose asset exists)."""
    if not isinstance(spec, dict) or spec.get("when", "post") != when:
        return ""
    kind = str(spec.get("kind", ""))
    if kind not in vdefs:
        return ""
    style = str(spec.get("pos", ""))
    lines = ('<i class="vln"></i><i class="vln v2"></i>'
             if vdefs[kind].get("speedlines") else "")
    return f'<i class="veh veh-{kind}" style="{style}" aria-hidden="true">{lines}</i>'


def mascot(spec, mdefs):
    """A day's mascot sticker at the scene edge (art: days[d].mascot =
    {kind, pos}; kinds defined in themes.splash.mascots)."""
    if not isinstance(spec, dict):
        return ""
    kind = str(spec.get("kind", ""))
    if kind not in mdefs:
        return ""
    style = str(spec.get("pos", ""))
    return f'<i class="mas mas-{kind}" style="{style}" aria-hidden="true"></i>'


def shape_defs():
    return ('<svg style="display:none" aria-hidden="true"><defs>'
            '<symbol id="p-heart" viewBox="0 0 24 24"><path fill="currentColor" '
            'd="M12 21C5.4 16.4 2 12.4 2 8.7 2 5.9 4.2 3.6 7 3.6c1.8 0 3.5 1 '
            '4.6 2.6a5.6 5.6 0 0 1 4.6-2.6c2.8 0 5 2.3 5 5.1 0 3.7-3.4 7.7-9.2 '
            '12.3z"/></symbol>'
            '<symbol id="p-tri" viewBox="0 0 24 24"><path fill="currentColor" '
            'd="M12 3.5 21.5 20.5H2.5Z"/></symbol>'
            '<symbol id="p-spark" viewBox="0 0 24 24"><path fill="currentColor" '
            'd="M12 2l2 8 8 2-8 2-2 8-2-8-8-2 8-2z"/></symbol>'
            '</defs></svg>')


# ------------------------------------------------------------------- days ---
def tag_html(tag):
    if not tag:
        return ""
    # pinned/skippable/opener via theme_common.tag_pretty; a swap→X tag is
    # printed as written (the zh baseline pins the raw `swap→` form, and in en
    # tag_pretty would print exactly that anyway)
    label = tag if tag.startswith("swap") else tag_pretty(tag)
    cls = {"pinned": "tag-pin", "skippable": "tag-skip",
           "opener": "tag-open"}.get(tag, "tag-swap")
    return f'<span class="tag {cls}">{esc(label)}</span>'


def render_timeline(day):
    rows = []
    for r in day.get("timeline", []):
        kind = r.get("kind", "anchor")
        icn, icls = KIND_ICON.get(kind, KIND_ICON["anchor"])
        est = '<sup class="est">est</sup>' if r.get("verify") == "est" else ""
        price = (f' <span class="price">{esc(r["price"])}</span>'
                 if r.get("price") else "")
        nav = (f' <a class="rownav" href="{esc(r["link"])}" target="_blank" '
               f'rel="noopener" aria-label="{esc(t("nav.to"))}{esc(r.get("what", ""))[:18]}">'
               f'{ic("pin")}</a>' if r.get("link") else "")
        rows.append(
            f'<div class="row k-{esc(kind)}">'
            f'<div class="t">{esc(r.get("t", ""))}{est}</div>'
            f'<div class="w">{ic(icn, icls)}{et(r.get("what", ""))}{price}'
            f'{tag_html(r.get("tag", ""))}{nav}</div></div>')
    return "".join(rows)


def day_notes(day):
    notes = []
    wk = day.get("walking_km")
    if isinstance(wk, dict):
        notes.append(("walk", T("walk") + t("km").format(wk.get('total', '?')), wk.get("how", "")))
    if day.get("rain_alt"):
        notes.append(("rain", T("rain_alt"), day["rain_alt"]))
    if day.get("late_cut"):
        notes.append(("clock", T("late_cut"), day["late_cut"]))
    if day.get("note"):
        notes.append(("note", t("note"), day["note"]))
    out = "".join(
        f'<div class="note"><b>{ic(icn)} {esc(t)}</b>'
        + (f" {et(b)}" if b else "") + "</div>"
        for icn, t, b in notes)
    return f'<div class="notes">{out}</div>' if out else ""


def map_fold(day):
    links = []
    if day.get("day_map"):
        links.append(f'<a href="{esc(day["day_map"])}" target="_blank" '
                     f'rel="noopener">{esc(t("day_route"))}</a>')
    for n, u in enumerate(day.get("hop_links", []), 1):
        links.append(f'<a href="{esc(u)}" target="_blank" rel="noopener" '
                     f'aria-label="{esc(t("hop_n").format(n))}">{n}</a>')
    embed = day_embed_url(day)
    if not links and not embed:
        return ""
    embed_html = (f'<div class="map-embed" data-src="{esc(embed)}">'
                  f'<p class="map-ph">{esc(t("map_ph"))}</p>'
                  '</div>' if embed else "")
    btns = f'<div class="hop-btns">{"".join(links)}</div>' if links else ""
    label = t("map_label").format(len(links)) if links else T("sec.map")
    return (f'<details class="mapfold"><summary>{ic("compass")} {esc(label)} '
            f'{ic("chevron", "chev")}</summary>{embed_html}{btns}</details>')


def _side_extras(v):
    """days[d].sides / hero.sides / appendix.sides → tuple of kinds for
    sides(extra=…): kit words as strings, {"stem","w"} dicts for a trip's own
    cut-out; anything else is ignored."""
    if isinstance(v, str):
        v = [v]
    if not isinstance(v, list):
        return ()
    return tuple(k for k in v if (isinstance(k, str) and k)
                 or (isinstance(k, dict) and k.get("stem")))


def render_day(i, day, ART, kit, stops, pal):
    """One day chapter. `ART` = the trip's Art; `kit` = the resolved
    vehicle/mascot/strip registries; `stops`/`pal` = the chapter's colours
    from resolve_chain."""
    date = day.get("date", "")
    art = ART.day(date, THEME)      # days[d] merged with themes.splash.days[d]
    title = ART.day_theme(date, day.get("city", ""))
    entry = GUT_R if i == 1 else (GUT_L if (i - 1) % 2 == 1 else GUT_R)
    park = GUT_L if i % 2 == 1 else GUT_R
    side = "side-l" if i % 2 == 1 else "side-r"

    isle_uri = data_uri(str(art.get("island") or ""), "sm")
    fx = art.get("fx")
    if fx is None:      # nothing chosen: an island stands alone, an empty
        fx = "" if isle_uri else MEDALLIONS[(i - 1) % len(MEDALLIONS)]
    fx = str(fx)        # slot gets a CSS medallion by day-number rhythm
    vpre = vehicle(art.get("vehicle"), "pre", kit["vehicles"])
    vpost = vehicle(art.get("vehicle"), "post", kit["vehicles"])
    mas = mascot(art.get("mascot"), kit["mascots"])
    scene = ""
    if isle_uri:
        scene = (f'<div class="scene">{head_fx(fx)}{vpre}'
                 f'<figure class="isle"><img src="{isle_uri}" '
                 f'alt="" aria-hidden="true"></figure>{vpost}{mas}</div>')
    elif fx:
        scene = f'<div class="scene">{head_fx(fx)}{vpre}{vpost}{mas}</div>'
    strip_kind = str(art.get("strip") or "")
    strip = (f'<i class="strip strip-{strip_kind}" aria-hidden="true"></i>'
             if strip_kind in kit["strips"] else "")

    sun = sun_text(day)
    wk = day.get("walking_km")
    wk_total = wk.get("total") if isinstance(wk, dict) else wk
    meta_bits = []
    if sun:
        meta_bits.append(f"<span>{sun}</span>")
    if wk_total:
        meta_bits.append(f'<span>{ic("walk")} {esc(T("walk") + t("km").format(wk_total))}</span>')
    meta = (f'<p class="meta">{"".join(meta_bits)}</p>' if meta_bits else "")
    rib = (f'<p class="rib1">{et(day["ribbon"])}</p>' if day.get("ribbon") else "")

    extra = _side_extras(art.get("sides"))
    return f"""
<section class="chap" id="d{i}" style="background:{grad(stops)}">
  {deco(i, pal)}
  {strip}
  {hill(i, 't')}{hill(i, 'b')}
  {sides(i, pal, extra=extra)}
  {day_road(entry, park)}
  <div class="chap-head {side}">
    <span class="bignum" aria-hidden="true">{i:02d}</span>
    {scene}
  </div>
  <div class="wrap">
    <article class="band reveal">
      <p class="ov">DAY {i} · {esc(date)} · {esc(day.get("city", ""))}</p>
      <h2 class="dt">{esc(title)}</h2>
      <p class="lbl">{et(day.get("label", ""))}</p>
      {rib}
      {meta}
      <div class="tl">{render_timeline(day)}</div>
      {day_notes(day)}
      {map_fold(day)}
      <div class="xrow no-export"><button type="button" class="xbtn"
        data-x-for="#d{i}" data-x-label="DAY{i:02d}"
        title="{esc(t("save_day.title"))}"><span class="xs" aria-hidden="true">✦</span>{esc(T("btn.save_day"))}</button></div>
    </article>
  </div>
</section>"""


# --------------------------------------------------------------- appendix ---
def render_legs(legs):
    rows = []
    for l in legs:
        backup = (f'<details class="bk"><summary>{esc(t("backup"))}</summary>'
                  f'<p>{et(l["backup"])}</p></details>' if l.get("backup") else "")
        link = (f' <a href="{esc(l["link"])}" target="_blank" rel="noopener">{esc(T("price.check"))}</a>'
                if l.get("link") else "")
        rows.append(
            f'<div class="leg"><b>{esc(l.get("date", ""))}</b> '
            f'{esc(l.get("from", ""))} → {esc(l.get("to", ""))}'
            f'<span class="mini">{esc(l.get("type", ""))} · {et(l.get("carrier", ""))}'
            f' · {esc(l.get("dep", ""))}→{esc(l.get("arr", ""))}'
            f' · {esc(l.get("price", ""))} · {esc(l.get("bags", ""))}{link}</span>'
            f'{backup}</div>')
    return "".join(rows)


def render_hotels(hotels):
    out = []
    for h in hotels:
        opts = "".join(
            f'<li><a href="{esc(o.get("link", "#"))}" target="_blank" '
            f'rel="noopener">{esc(o.get("name", ""))}</a>'
            f' <span class="mini">{esc(o.get("band", ""))}</span></li>'
            for o in h.get("options", []))
        out.append(
            f'<div class="hotel"><h3>{esc(h.get("base", ""))} · {esc(h.get("area", ""))}</h3>'
            f'<p class="mini">{et(h.get("why", ""))}</p><ul>{opts}</ul></div>')
    return "".join(out)


def render_budget(budget, total):
    rows = "".join(
        f'<tr><td>{esc(b.get("cat", ""))}</td><td>{esc(b.get("per_person", ""))}</td>'
        f'<td class="mini">{esc(b.get("note", ""))}</td></tr>' for b in budget)
    return (f'<div class="tbw"><table><tr><th>{esc(t("th.item"))}</th><th>{esc(t("th.cost"))}</th>'
            f'<th>{esc(t("th.note"))}</th></tr>'
            f'{rows}<tr class="total"><td>{esc(t("total"))}</td><td colspan="2">{esc(total)}</td>'
            '</tr></table></div>')


def render_checklist(items):
    out = []
    for c in items:
        link = (f' <a href="{esc(c["link"])}" target="_blank" rel="noopener">'
                f'{esc(c.get("link_text", T("link")))}</a>' if c.get("link") else "")
        note = f'<p class="mini">{et(c["note"])}</p>' if c.get("note") else ""
        out.append(f'<li><b>{et(c.get("item", ""))}</b> — {esc(c.get("deadline", ""))}'
                   f' · {esc(c.get("price", ""))}{link}{note}</li>')
    return '<ol class="check">' + "".join(out) + "</ol>"


def render_brief(brief, titles):
    return "".join(
        f'<div class="brief"><h3>{esc(titles.get(k, k))}</h3><p>{et(v)}</p></div>'
        for k, v in brief.items())


# ------------------------------------------------------- contrast (build) ---
def _lum(rgb):
    def f(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _mix(bg, fg, a):
    """sRGB-space alpha composite (what browsers do by default)."""
    return tuple(bg[i] * (1 - a) + fg[i] * a for i in range(3))


def _cr(fg, bg):
    la, lb = sorted((_lum(fg), _lum(bg)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def contrast_report(SCENES):
    """Worst-case AA audit over the whole resolved scene chain. The overlay
    model matches the deco() zones: a band can sit under one wash PLUS one
    streak (both taken as pure white — an upper bound over every palette
    pastel) or under one blob; washes/streaks never reach the page foot, so
    the endcap pair uses the foot field. Rainbow / sun / burst fx live
    strictly behind the aria-hidden islands and numerals, never under live
    text. The silhouette strips park at the chapter foot: a streak's tip
    cannot reach that deep (top ≤30% + ≤24px + rotation), but a rotated wash
    tip and a blob can — so the strip pairs stack strip (pure white at
    STRIP_A, an upper bound over the skyline/sunset pixels) + wash + blob
    under the band. The vehicles / mascots live inside the aria-hidden
    chapter heads and never sit under live text."""
    stops = [_hex(c) for chap in SCENES for c in chap]
    fields = stops + [_mix(a, b, .5) for a, b in zip(stops, stops[1:])]
    lightest = max(fields, key=_lum)
    stack = _mix(_mix(lightest, WHITE, STREAK_A), WHITE, WASH_A)
    band_stack = _mix(stack, BAND, BAND_A)
    band_blob = _mix(_mix(lightest, _hex("#FFE9A8"), BLOB_A), BAND, BAND_A)
    strip_stack = _mix(_mix(_mix(_mix(lightest, WHITE, STRIP_A), WHITE, WASH_A),
                            _hex("#FFE9A8"), BLOB_A), BAND, BAND_A)
    hero_light = max((_hex(c) for c in SCENES[0]), key=_lum)
    hero_stack = _mix(_mix(hero_light, WHITE, STREAK_A), WHITE, WASH_A)
    appx_light = max((_hex(c) for c in SCENES[-1]), key=_lum)
    appx_stack = _mix(_mix(appx_light, WHITE, STREAK_A), WHITE, WASH_A)
    foot = _mix(_hex(SCENES[-1][2]), _hex(SCENES[-1][3]), .5)
    foot_blob = _mix(foot, _hex("#FFE9A8"), BLOB_A)
    pairs = [
        ("白正文 vs 色带@最亮场+洗×光带", WHITE, band_stack, 4.5),
        ("奶油时间字 vs 同上", CREAM, band_stack, 4.5),
        ("淡紫辅文 vs 同上", PALE, band_stack, 4.5),
        ("可砍标签 vs 同上", _hex("#FFD7F0"), band_stack, 4.5),
        ("淡紫辅文 vs 色带+柔焦块", PALE, band_blob, 4.5),
        ("白正文 vs 色带@最亮场+剪影条(白上界)+洗+柔焦", WHITE, strip_stack, 4.5),
        ("奶油时间字 vs 色带+剪影条+洗+柔焦", CREAM, strip_stack, 4.5),
        ("淡紫辅文 vs 色带+剪影条+洗+柔焦", PALE, strip_stack, 4.5),
        ("可砍标签 vs 色带+剪影条+洗+柔焦", _hex("#FFD7F0"), strip_stack, 4.5),
        ("hero 白路线字 vs hero 亮场+洗×光带", WHITE, hero_stack, 4.5),
        ("hero 奶油跳转号 vs 同上", CREAM, hero_stack, 4.5),
        ("附录裸标题(大字) vs 附录亮场+洗×光带", WHITE, appx_stack, 3.0),
        ("尾牌白字 vs 页尾场+柔焦", WHITE, foot_blob, 4.5),
        ("尾牌淡紫小字 vs 页尾场+柔焦", PALE, foot_blob, 4.5),
        ("钉死徽章深字 vs 金底", DEEP, GOLD, 4.5),
        ("缎带白字 vs 缎带亮端", WHITE, _hex("#8A2BD0"), 4.5),
        ("按钮奶油字 vs 深紫钮", CREAM, DEEP, 4.5),
        ("页脚淡紫 vs 页尾底", PALE, _hex(SCENES[-1][-1]), 4.5),
    ]
    lines, ok = [], True
    for name, fg, bg, need in sorted(pairs, key=lambda p: _cr(p[1], p[2])):
        r = _cr(fg, bg)
        flag = "PASS" if r >= need else "FAIL"
        ok &= r >= need
        lines.append(f"  {flag} {r:4.2f}:1 (需{need}) {name}")
    return ok, lines


# ------------------------------------------------------------------- page ---
CSS = """
  :root { --cream:#FFEFC9; --pale:#EADCFF; --deep:#2A1050; --gold:#FFC93C;
    --pink:#FF9DE0; --cyan:#7FE8FF;
    --disp:"Yuanti SC","Arial Rounded MT Bold","PingFang SC","Hiragino Sans GB",sans-serif; }
  * { margin:0; padding:0; box-sizing:border-box; }
  html { scroll-behavior:smooth; }
  body { background:#251043; color:#fff; line-height:1.75;
    font-family:"PingFang SC","Hiragino Sans GB","Noto Sans SC",system-ui,sans-serif; }
  img { max-width:100%; height:auto; }
  a { color:var(--cream); }
  [id] { scroll-margin-top:24px; }
  .mini { font-size:12px; color:var(--pale); font-weight:500; }
  .ic { width:1em; height:1em; fill:none; stroke:currentColor; stroke-width:2;
    stroke-linecap:round; stroke-linejoin:round; vertical-align:-.12em; }
  :focus-visible { outline:3px solid var(--gold); outline-offset:3px; }

  /* every chapter is one stretch of the same poster: its own multi-stop
     scene gradient (seams chained in Python), its own stretch of road,
     hills, side field and confetti */
  .chap { position:relative; overflow:hidden; z-index:0; }

  .road { position:absolute; inset:0; width:100%; height:100%; z-index:0;
    pointer-events:none; }
  .road path { fill:none; stroke-linecap:round; }
  .r-glow { stroke:rgba(255,158,224,.16); stroke-width:24px; }
  .r-mid  { stroke:rgba(255,158,224,.30); stroke-width:12px; }
  .r-core { stroke:#FFC9EC; stroke-width:6.5px; opacity:.92; }
  .r-sheen{ stroke:#fff; stroke-width:2px; opacity:.5; }

  .deco { display:contents; }
  .stk { position:absolute; z-index:0; pointer-events:none;
    background:linear-gradient(90deg,transparent,rgba(var(--c,255,217,246),var(--a,.12)),transparent);
    transform:rotate(var(--r,-24deg)); }
  .blob { position:absolute; z-index:0; pointer-events:none; border-radius:50%;
    background:radial-gradient(closest-side,rgba(var(--c,255,190,240),var(--a,.07)),transparent); }
  .pt { position:absolute; z-index:0; pointer-events:none; opacity:var(--o,.6);
    transform:rotate(var(--r,0deg));
    animation:tw var(--d,5s) ease-in-out infinite; }
  .pt use { fill:currentColor; }
  @keyframes tw { 50% { opacity:calc(var(--o,.6)*.3);
    transform:rotate(var(--r,0deg)) scale(.8); } }

  /* seam-crossing hills: each chapter draws its own half; both halves are
     solid at the shared edge, so the ridge continues across the boundary */
  .hill { position:absolute; left:0; width:100%; z-index:0; pointer-events:none; }
  .hill.h-b { bottom:0; height:120px; }
  .hill.h-t { top:0; height:88px; }

  /* wishlist silhouette strips: the poster's farthest scenery layer, parked
     at the chapter foot BEHIND the hills (earlier in DOM, same z). Ends are
     pre-faded in the asset; opacity is capped at __STRIPA__ (= STRIP_A),
     which contrast_report() budgets under the band with a pure-white worst
     case + wash + blob. Centred and ≤100% wide inside the chapter's
     overflow:hidden — no horizontal overflow at any width. */
  .strip { position:absolute; bottom:0; left:50%; transform:translateX(-50%);
    width:min(100%,1560px); z-index:0; pointer-events:none; opacity:__STRIPA__; }
__STRIP_CSS__

  /* wishlist vehicles: plane on the flight-day heads (d4/d9), tour bus on
     the group-tour heads (d5/d6). Positioned inside .scene, so they can
     never reach band copy; tilt/flip use the rotate/scale PROPERTIES so the
     drift keyframe's transform composes with them instead of replacing them. */
  .veh { position:absolute; z-index:0; pointer-events:none; --dy:-9px;
    rotate:var(--vr,0deg); scale:var(--vsx,1) 1;
    filter:drop-shadow(0 12px 16px rgba(30,8,60,.42));
    animation:drift 8.5s ease-in-out infinite; }
__VEH_CSS__
  /* day mascots: nodes2 stickers peeking at the scene edge */
  .mas { position:absolute; z-index:1; pointer-events:none;
    rotate:var(--vr,0deg);
    filter:drop-shadow(0 10px 14px rgba(30,8,60,.4));
    animation:drift 9.5s ease-in-out -3.2s infinite; }
__MAS_CSS__
  .vln { position:absolute; right:-30%; top:36%; width:46%; height:4px;
    border-radius:99px; opacity:.85;
    background:linear-gradient(90deg,rgba(255,239,201,.8),rgba(255,239,201,0)); }
  .vln.v2 { top:54%; right:-22%; width:34%; opacity:.6; }

  /* wide-viewport side field (lands off-canvas on phones by construction) */
  .sides { display:contents; }
  .side { position:absolute; z-index:0; pointer-events:none;
    animation:drift var(--dur,9s) ease-in-out var(--del,0s) infinite; }
  @keyframes drift { 50% { transform:translateY(var(--dy,-12px)); } }
  /* clouds = wishlist splash-cloud-a..d (same brush as the poster; the clay
     clouds went home to the clay theme); star = wishlist splash-star */
  .sc-a { aspect-ratio:443/297; background:url(__CLOUDA__) center/contain no-repeat; }
  .sc-b { aspect-ratio:390/188; background:url(__CLOUDB__) center/contain no-repeat; }
  .sc-c { aspect-ratio:184/154; background:url(__CLOUDC__) center/contain no-repeat; }
  .sc-d { aspect-ratio:107/88; background:url(__CLOUDD__) center/contain no-repeat; }
  .st-star { aspect-ratio:218/246; background:url(__STAR__) center/contain no-repeat; }
  .sc-bal { aspect-ratio:355/436; background:url(__BALLOON__) center/contain no-repeat;
    filter:drop-shadow(0 12px 18px rgba(30,8,60,.35)); }
  .side.dot { border-radius:50%;
    background:radial-gradient(closest-side,rgba(var(--c,255,217,246),var(--a,.2)),transparent); }
  .side.shard { animation:none; background:var(--sc,#FF8AD6); opacity:var(--o,.6);
    transform:rotate(var(--rr,18deg)) skew(-10deg); }
  .pt2 use { fill:currentColor; }

  /* scene fx behind the floating islands: rainbow arches, halos, sun discs,
     paint bursts, radial beams — pure CSS gradients, no blur, no images */
  .scene { position:relative; display:grid; place-items:center; }
  /* base kept at single-class specificity so the geometry of .fxb /
     .fx-rainbow / .fx-sun below can override it by source order */
  .fx { position:absolute; inset:-16%; z-index:-1; pointer-events:none; }
  .fx-burst { background:
      radial-gradient(closest-side at 46% 54%,rgba(255,138,214,.5),rgba(255,138,214,0) 46%),
      radial-gradient(closest-side at 64% 38%,rgba(255,233,168,.42),transparent 44%),
      radial-gradient(closest-side at 34% 34%,rgba(121,230,255,.36),transparent 40%); }
  .fxb { inset:-28%;
    background:repeating-conic-gradient(from 8deg,rgba(255,255,255,.13) 0 7deg,rgba(255,255,255,0) 7deg 24deg);
    -webkit-mask-image:radial-gradient(closest-side,#000 16%,transparent 66%);
    mask-image:radial-gradient(closest-side,#000 16%,transparent 66%);
    animation:spin 80s linear infinite; }
  .fxb.cool { background:repeating-conic-gradient(from 0deg,rgba(158,232,255,.15) 0 8deg,rgba(158,232,255,0) 8deg 26deg); }
  .fxb.gold { background:repeating-conic-gradient(from 4deg,rgba(255,233,168,.17) 0 7deg,rgba(255,233,168,0) 7deg 22deg); }
  .fxb.warm { background:repeating-conic-gradient(from 6deg,rgba(255,217,246,.16) 0 6deg,rgba(255,217,246,0) 6deg 20deg); }
  .fxb.slow { animation-duration:120s; }
  @keyframes spin { to { transform:rotate(1turn); } }
  .fx-rainbow { inset:auto; left:-14%; right:-14%; top:-28%; height:80%;
    background:
      radial-gradient(closest-side at 50% 100%,
        transparent 51%, rgba(255,110,110,.85) 52% 58.5%, rgba(255,180,78,.85) 58.5% 65%,
        rgba(255,228,94,.85) 65% 71.5%, rgba(126,221,142,.82) 71.5% 78%,
        rgba(94,200,255,.82) 78% 84.5%, rgba(197,145,255,.8) 84.5% 90%, transparent 91.5%),
      radial-gradient(closest-side at 50% 100%, rgba(255,255,255,.22) 0 48%, transparent 60%); }
  .fx-rainbow.sm { opacity:.6; top:-18%; height:68%; left:-6%; right:-6%; }
  .fx-halo { inset:-20%;
    background:radial-gradient(closest-side,rgba(var(--c,255,217,160),.35),transparent 70%); }
  .fx-sun { inset:auto; left:4%; right:4%; top:-26%; bottom:24%;
    background:radial-gradient(closest-side at 50% 56%,
      #FFE9A8 0 22%, #FFC93C 36%, rgba(255,150,64,.8) 50%,
      rgba(255,110,80,.3) 65%, transparent 73%); }

  /* medallions: the CSS-only scene for island-less days (moon / dusk /
     sunrise) so no chapter head ever sits half-empty */
  .medal { position:relative; width:clamp(170px,38vw,280px); aspect-ratio:1;
    animation:bob2 9s ease-in-out infinite; }
  .medal > i, .medal > svg { position:absolute; pointer-events:none; }
  .m-moon .halo { inset:-10%;
    background:radial-gradient(closest-side at 60% 38%,rgba(255,246,220,.3),transparent 66%); }
  .m-moon .disc { left:36%; top:10%; width:48%; aspect-ratio:1; border-radius:50%;
    background:
      radial-gradient(circle at 33% 30%,rgba(206,172,138,.5) 0 7%,transparent 8.5%),
      radial-gradient(circle at 62% 60%,rgba(206,172,138,.42) 0 9%,transparent 10.5%),
      radial-gradient(circle at 42% 76%,rgba(206,172,138,.38) 0 5%,transparent 6.5%),
      radial-gradient(circle at 38% 36%,#FFF8E2 0 58%,#F1DCA8 100%);
    box-shadow:0 0 46px rgba(255,239,201,.5); }
  .m-moon .ms { color:#FFE9A8; animation:tw 4.5s ease-in-out infinite; }
  .m-moon .ms use { fill:currentColor; }
  .m-dusk .dsun { left:18%; top:18%; width:64%; aspect-ratio:1; border-radius:50%;
    background:radial-gradient(circle at 50% 42%,#FFE9A8 0 28%,#FFC93C 56%,rgba(255,150,80,.5) 76%,transparent 85%); }
  .m-dusk .dbar { height:8%; border-radius:99px; background:rgba(32,11,64,.55); }
  .m-rise .fxb { inset:-4%; }
  .m-rise .rsun { left:25%; top:32%; width:50%; aspect-ratio:1; border-radius:50%;
    background:radial-gradient(circle at 50% 44%,#FFF3C4 0 32%,#FFC93C 60%,rgba(255,140,90,.55) 78%,transparent 87%);
    box-shadow:0 0 56px rgba(255,201,60,.45); }
  .m-rise .ring { inset:8%; border-radius:50%; border:2px solid rgba(255,233,168,.3); }

  /* ---------- hero: the poster itself ---------- */
  .hero-inner { position:relative; z-index:2; min-height:100vh; min-height:100svh;
    display:flex; flex-direction:column; align-items:center; text-align:center;
    padding:clamp(36px,6vh,72px) 24px 170px; }
  .ht { line-height:0; animation:pop .8s cubic-bezier(.2,1.6,.4,1) both; }
  .ht img { width:min(88vw,600px); filter:drop-shadow(0 14px 30px rgba(30,8,60,.55)); }
  @keyframes pop { from { transform:scale(.72); opacity:0; } }
  .ribbon { position:relative; margin-top:6px; }
  .ribbon i { position:absolute; top:14px; border:13px solid #45157E; z-index:-1; }
  .ribbon i.rl { left:-16px; border-left-color:transparent; }
  .ribbon i.rr { right:-16px; border-right-color:transparent; }
  .ribbon span { display:inline-block; background:linear-gradient(180deg,#8A2BD0,#5B1FA8);
    padding:9px 32px; font-weight:900; font-size:clamp(15px,2.6vw,19px);
    letter-spacing:.24em; text-indent:.24em; color:#fff;
    text-shadow:0 2px 0 rgba(42,16,80,.6); transform:rotate(-2deg);
    box-shadow:0 6px 0 rgba(42,16,80,.35); }
  .hcl { margin-top:clamp(16px,3.5vh,34px); position:relative; z-index:1; }
  .hcl::before { content:""; position:absolute; inset:-10% -16%; z-index:-1;
    background:radial-gradient(closest-side,rgba(255,158,224,.38),rgba(255,158,224,0) 72%),
      radial-gradient(closest-side at 30% 62%,rgba(255,233,168,.22),transparent 70%); }
  .hcl .fxb.warm { inset:-20% -30%; }
  .hcl .fx-burst { inset:-8% -16%; }
  .hcl img { position:relative; width:min(78vw,500px); animation:bob2 8s ease-in-out infinite; }
  @keyframes bob2 { 50% { transform:translateY(-13px) rotate(1.2deg); } }
  .route { margin-top:14px; font-weight:800; font-size:clamp(15px,2.4vw,19px);
    letter-spacing:.32em; text-indent:.32em; color:#fff;
    text-shadow:0 2px 0 rgba(42,16,80,.7); }
  /* cover.en — small caps under the plate, tracked like the jump numerals */
  .en { margin-top:10px; font-size:12px; font-weight:800; letter-spacing:.28em;
    text-indent:.28em; text-transform:uppercase; color:var(--cream);
    text-shadow:0 2px 0 rgba(42,16,80,.6); }
  /* cover.credit — the allusion as a cream mono badge (kin of the export
     slabs: skewed, painted stroke), one notch quieter than the route line */
  .credit { display:inline-block; margin-top:12px; padding:5px 14px;
    font-family:ui-monospace,Menlo,monospace; font-size:12px; line-height:1.6;
    color:var(--cream); background:rgba(42,16,80,.55);
    border:1.5px solid rgba(255,239,201,.55); transform:skew(-6deg);
    box-shadow:3px 3px 0 rgba(42,16,80,.45); max-width:min(88vw,600px); }
  .jump { margin-top:12px; display:flex; flex-wrap:wrap; justify-content:center;
    gap:2px 4px; }
  .jump a { display:inline-flex; align-items:center; justify-content:center;
    min-width:44px; min-height:44px; font-family:var(--disp); font-weight:900;
    font-size:19px; color:var(--cream); text-decoration:none;
    text-shadow:0 2px 0 #3A1272; transform:rotate(-4deg); transition:transform .18s; }
  .jump a:hover { transform:rotate(-4deg) scale(1.24); color:#fff; }
  .jump .apx { font-size:14px; letter-spacing:.1em; }
  .cue { margin-top:auto; padding-top:22px; color:var(--cream);
    display:inline-flex; min-width:44px; min-height:44px; align-items:center;
    justify-content:center; animation:bob 1.9s ease-in-out infinite; }
  @keyframes bob { 50% { transform:translateY(8px); } }

  /* ---------- day chapters ---------- */
  .chap-head { position:relative; z-index:1; display:flex; align-items:center;
    gap:clamp(10px,4vw,40px); padding:clamp(38px,7vh,70px) clamp(18px,7vw,84px) 4px; }
  .chap-head.side-r { flex-direction:row-reverse; }
  .bignum { font-family:var(--disp); font-weight:900; line-height:.9;
    font-size:clamp(92px,17vw,164px); color:var(--cream); letter-spacing:.02em;
    transform:rotate(-5deg); position:relative;
    text-shadow:0 4px 0 #3A1272, 0 8px 0 rgba(42,16,80,.45), 0 0 36px rgba(255,158,224,.4); }
  .bignum::after { content:""; position:absolute; left:8%; bottom:-14px;
    width:72%; height:7px; transform:skew(-30deg);
    background:linear-gradient(90deg,rgba(255,239,201,.9),rgba(255,239,201,0)); }
  .isle { position:relative; }
  .isle img { width:clamp(200px,46vw,330px);
    filter:drop-shadow(0 22px 30px rgba(30,8,60,.5));
    animation:bob2 7s ease-in-out infinite; }

  .wrap { position:relative; z-index:2; max-width:768px; margin-inline:auto;
    padding:0 12px 34px; }
  .wrap.wide { max-width:900px; }

  /* the band: a feather-edged darker patch of the SAME field — no border,
     no radius, no card. Vertical feather in the paint, horizontal feather
     via mask on the ::before so glyphs are never masked (padding > ramp). */
  .band { position:relative; z-index:2; overflow-wrap:anywhere;
    padding:54px clamp(32px,6vw,56px) 50px; }
  .band::before { content:""; position:absolute; inset:0; z-index:-1;
    background:linear-gradient(180deg, rgba(30,10,60,0),
      rgba(30,10,60,.5) 48px, rgba(30,10,60,.5) calc(100% - 48px), rgba(30,10,60,0));
    -webkit-mask-image:linear-gradient(90deg,transparent,#000 26px,#000 calc(100% - 26px),transparent);
    mask-image:linear-gradient(90deg,transparent,#000 26px,#000 calc(100% - 26px),transparent); }

  .ov { font-size:13px; font-weight:800; letter-spacing:.22em; color:var(--cream); }
  h2.dt { font-family:var(--disp); font-weight:900; letter-spacing:.12em;
    font-size:clamp(32px,6.4vw,46px); color:#fff; margin:8px 0 6px;
    text-shadow:0 3px 0 rgba(42,16,80,.65), 0 0 26px rgba(42,16,80,.35); }
  .lbl { color:var(--pale); font-size:14.5px; font-weight:600; }
  .rib1 { color:var(--pale); font-size:12.5px; margin-top:8px; }
  .meta { display:flex; flex-wrap:wrap; gap:6px 18px; margin-top:10px;
    font-size:12.5px; color:var(--pale); font-weight:600; }

  .tl { margin-top:24px; border-top:2px dashed rgba(255,255,255,.28); padding-top:6px; }
  .row { display:grid; grid-template-columns:96px minmax(0,1fr); gap:12px;
    padding:9px 0; border-bottom:1px dotted rgba(255,255,255,.20); min-width:0; }
  .row:last-child { border-bottom:none; }
  .t { color:var(--cream); font-weight:800; font-size:13px; text-align:right;
    font-variant-numeric:tabular-nums; letter-spacing:.02em; padding-top:2px; }
  .w { font-size:14px; min-width:0; overflow-wrap:anywhere; }
  .ki-anchor { color:var(--gold); } .ki-hop { color:var(--cyan); }
  .ki-meal { color:var(--pink); } .ki-free { color:var(--pale); }
  .w .ic { margin-right:7px; width:15px; height:15px; }
  .k-hop .w { color:var(--pale); font-size:13px; }
  .k-hop .t { color:var(--pale); font-weight:700; }
  .k-free .w { color:var(--pale); font-style:italic; }
  .est { font-size:.62em; color:var(--cream); letter-spacing:.06em; margin-left:2px; }
  .price { color:var(--cream); font-size:12px; font-weight:700; }
  .tag { display:inline-block; padding:2px 10px; margin-left:7px;
    transform:skew(-8deg); font-size:11.5px; font-weight:800; letter-spacing:.05em; }
  .tag-pin { background:var(--gold); color:var(--deep);
    box-shadow:2px 2px 0 rgba(42,16,80,.55); }
  .tag-open { background:var(--cyan); color:var(--deep);
    box-shadow:2px 2px 0 rgba(42,16,80,.55); }
  .tag-skip { border:1.5px solid var(--pink); color:#FFD7F0; }
  .tag-swap { border:1.5px solid var(--cyan); color:#CFF4FF; transform:skew(-4deg);
    max-width:100%; }
  .rownav { display:inline-flex; align-items:center; justify-content:center;
    min-width:44px; min-height:44px; margin:-14px -10px -14px -4px;
    color:var(--cream); vertical-align:middle; }
  .rownav .ic { width:15px; height:15px; }

  .notes { margin-top:18px; display:grid; gap:10px; }
  .note { border-left:3px solid var(--pink); padding-left:12px; font-size:12.5px;
    color:var(--pale); }
  .note b { color:#fff; font-size:13px; }
  .note .ic { color:var(--pink); }

  .mapfold { margin-top:24px; }
  .mapfold summary { cursor:pointer; list-style:none; display:inline-flex;
    align-items:center; gap:9px; min-height:44px; padding:6px 20px;
    background:var(--deep); color:var(--cream); font-weight:800;
    letter-spacing:.08em; transform:skew(-6deg);
    border-bottom:3px solid var(--pink); user-select:none; }
  .mapfold summary::-webkit-details-marker { display:none; }
  .mapfold .chev { transition:transform .25s ease; }
  .mapfold[open] summary .chev { transform:rotate(180deg); }
  .map-embed { margin-top:14px; border:2px solid rgba(255,157,224,.45); }
  .map-embed iframe { display:block; width:100%; height:330px; border:0; }
  .map-ph { padding:22px; font-size:12.5px; color:var(--pale); text-align:center; }
  .hop-btns { margin-top:12px; display:flex; flex-wrap:wrap; gap:8px; }
  .hop-btns a { display:inline-flex; align-items:center; justify-content:center;
    min-width:44px; min-height:44px; padding:0 14px; background:rgba(42,16,80,.85);
    color:var(--cream); font-weight:800; text-decoration:none;
    transform:skew(-6deg); border-bottom:2px solid var(--cyan); }

  /* ---------- appendix ---------- */
  h2.sec { font-family:var(--disp); font-weight:900; letter-spacing:.14em;
    font-size:clamp(24px,4.6vw,34px); color:#fff; margin:60px 0 14px;
    padding-left:clamp(20px,5vw,44px);
    text-shadow:0 3px 0 rgba(42,16,80,.6); position:relative; z-index:2; }
  h2.sec .ic { width:24px; height:24px; color:var(--pink); margin-right:6px; }
  .appx .band { padding-top:44px; padding-bottom:42px; }
  .leg { padding:10px 0; border-bottom:1px dotted rgba(255,255,255,.2);
    font-size:13.5px; }
  .leg .mini { display:block; }
  .bk { font-size:12.5px; color:var(--pale); margin-top:4px; }
  .bk summary { cursor:pointer; color:var(--cream); font-weight:700;
    min-height:28px; display:inline-block; }
  .bk p { padding:4px 0 4px 14px; }
  .hotel { border-top:2px solid var(--pink); padding-top:12px; margin-top:20px; }
  .hotel h3 { font-size:15px; font-weight:800; margin-bottom:4px; }
  .hotel ul { margin:8px 0 0 18px; font-size:13px; }
  .hotel li { margin-top:4px; }
  .tbw { overflow-x:auto; }
  table { width:100%; border-collapse:collapse; font-size:13px; }
  th, td { border-bottom:1px solid rgba(255,255,255,.25); padding:10px 18px 10px 0;
    text-align:left; vertical-align:top; line-height:1.65;
    font-variant-numeric:tabular-nums; }
  th:last-child, td:last-child { padding-right:0; }
  th { border-bottom:2px solid var(--pink); font-size:11px; font-weight:800;
    letter-spacing:.18em; color:var(--cream); }
  td:nth-child(2) { color:var(--cream); }
  tr.total td { font-weight:800; font-size:13.5px; color:var(--cream);
    border-top:2px solid var(--pink); border-bottom:4px double var(--pink); }
  ol.check { margin-left:22px; font-size:13.5px; }
  ol.check li { margin-top:10px; line-height:1.7; }
  ol.check li::marker { color:var(--cream); font-weight:900;
    font-family:var(--disp); }
  ol.plain { margin-left:22px; font-size:13.5px; }
  ol.plain li { margin-top:8px; }
  ul.warn { margin-left:22px; font-size:13px; color:var(--pale); }
  ul.warn li { margin-top:6px; line-height:1.7; }
  .brief-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));
    gap:24px 34px; }
  .brief h3 { color:var(--cream); font-size:14px; font-weight:800;
    letter-spacing:.1em; margin-bottom:6px; border-bottom:1.5px solid rgba(255,157,224,.5);
    display:inline-block; padding-bottom:2px; }
  .brief p { font-size:12.5px; line-height:1.8; color:var(--pale); }
  .ic.warn { color:var(--gold); }

  .endcap { text-align:center; margin:76px 0 24px; position:relative; z-index:2; }
  .term { width:46px; height:46px; color:var(--cream);
    filter:drop-shadow(0 0 18px rgba(255,158,224,.9)); }
  .endcap p { font-family:var(--disp); font-weight:900; font-size:20px;
    letter-spacing:.14em; margin-top:10px;
    text-shadow:0 2px 0 rgba(42,16,80,.7); }
  .endcap .fine { font-family:inherit; font-weight:500; font-size:12px;
    color:var(--pale); letter-spacing:.04em; text-shadow:none; margin-top:6px; }
  footer { position:relative; z-index:2; text-align:center; font-size:12px;
    color:var(--pale); padding:8px 16px 46px; line-height:2; }

  /* export badges — the poster's own skewed slab, kin of .tag-pin (skew,
     hard purple drop) and the mapfold chip. Owner note: the old .55-opacity
     ghost was invisible; type size is unchanged, the badge is instead made
     findable with the theme's OWN materials — cream paint plate + a painted
     deep-purple stroke (the same #3A1272 the giant numerals are outlined in)
     + a soft pink halo (微光, same pink as the ribbon road glow). Small prop,
     not a CTA: 12.5px label, ~34px tall, parked at the band's own right edge
     in NORMAL FLOW, so it can never land on the road, a numeral or copy. */
  .xrow { display:flex; justify-content:flex-end; margin-top:26px;
    position:relative; z-index:3; }
  .xrow-appx { margin-top:34px; }
  .xbtn { display:inline-flex; align-items:center; gap:7px; cursor:pointer;
    padding:7px 18px; font-family:inherit; font-size:12.5px; font-weight:800;
    letter-spacing:.14em; color:var(--deep); background:var(--cream);
    border:2px solid #3A1272; transform:skew(-8deg);
    box-shadow:3px 3px 0 rgba(42,16,80,.55), 0 0 20px rgba(255,157,224,.45);
    transition:box-shadow .2s ease, translate .2s ease, background .2s ease; }
  /* label stays skewed with the plate — same as .tag-pin and the mapfold chip */
  .xbtn .xs { color:#B32E8C; font-size:13px; line-height:1;
    text-shadow:0 0 8px rgba(255,157,224,.9); }
  .xbtn:hover, .xbtn:focus-visible { background:#FFF9E8; translate:0 -2px;
    box-shadow:4px 5px 0 rgba(42,16,80,.65), 0 0 32px rgba(255,157,224,.85); }
  /* whole-page badge: same slab, parked next to the back-to-top button so
     the two read as one small tool cluster. It may only FLOAT while the
     right gutter is wide enough to hold it clear of the 768px text column
     (viewport ≥ 768 + 2×(70 + 128) ≈ 1180px); below that it would land on
     band copy, so it drops into normal flow at the foot of the scroll
     instead of being hidden — the affordance survives at every width. */
  .xbtn.xpage { position:fixed; right:70px; bottom:16px; z-index:60;
    height:46px; padding:0 20px; }
  @media (max-width:1180px) {
    /* display:flex (not inline-flex) so margin-inline:auto can centre it */
    .xbtn.xpage { position:static; height:auto; padding:9px 22px;
      display:flex; width:fit-content; margin:26px auto 46px; }
  }
  @media print { .xbtn, .xrow { display:none; } }

  .totop { position:fixed; right:16px; bottom:16px; z-index:60; width:46px;
    height:46px; display:flex; align-items:center; justify-content:center;
    background:var(--deep); color:var(--cream); border:2px solid var(--pink);
    text-decoration:none; transform:rotate(-4deg); font-size:15px; }
  /* JS on: hidden until past the hero so it never sits on the poster; no-JS
     keeps it always visible (it is the only way back up without JS). */
  .js .totop { opacity:0; pointer-events:none; transition:opacity .3s ease; }
  .js .totop.on { opacity:1; pointer-events:auto; }

  .js .reveal { opacity:0; transform:translateY(26px) scale(.985);
    transition:opacity .65s ease, transform .65s ease; }
  .js .reveal.in { opacity:1; transform:none; }

  @media (prefers-reduced-motion:reduce) {
    html { scroll-behavior:auto; }
    * { animation:none !important; transition:none !important; }
    .js .reveal { opacity:1; transform:none; }
  }

  @media (max-width:760px) {
    .row { grid-template-columns:62px minmax(0,1fr); gap:9px; }
    .t { font-size:11.5px; }
    .w { font-size:13.5px; }
    .chap-head { padding-top:30px; }
    .isle img { width:min(46vw,220px); }
    .jump a { font-size:17px; }
    .route { letter-spacing:.18em; text-indent:.18em; }
    .en { letter-spacing:.18em; text-indent:.18em; }
    /* strips scale with the viewport down to 760, then bow out: below that
       the skyline is a <170px sliver mostly hidden behind the hills */
    .strip { display:none; }
  }

  @media print {
    .road, .pt, .stk, .blob, .cue, .jump, .mapfold, .totop, .hcl, .deco,
    .side, .sides, .fx, .fxb, .medal, .hill, .pt2, .strip, .veh, .mas
      { display:none !important; }
    body { background:#fff; }
    .chap { background:#fff !important; overflow:visible; }
    .band::before { display:none; }
    .chap *, footer, a { color:#241043 !important; text-shadow:none !important; }
    .bignum { color:#F3EAFB !important; -webkit-text-stroke:2px #58208C; }
    .bignum::after { background:#D8C6EE; }
    .ht img { filter:none; }
    .ribbon span { background:none; border:2px solid #4A1E8A; box-shadow:none;
      transform:none; print-color-adjust:exact; }
    .ribbon i { display:none; }
    .credit { background:none; border-color:#241043; box-shadow:none; transform:none; }
    .tag-pin, .tag-open { background:none; border:1.5px solid #241043;
      box-shadow:none; }
    .tag-skip, .tag-swap { border-color:#241043; }
    .tl { border-top-color:#999; }
    .row { border-bottom-color:#ccc; break-inside:avoid; }
    .note { border-left-color:#888; }
    th { border-bottom-color:#241043; }
    th, td { border-color:#bbb; }
    tr.total td { border-color:#241043; }
    .hotel { border-top-color:#241043; }
    .brief h3 { border-bottom-color:#241043; }
    .isle img { filter:none; animation:none; }
    .js .reveal { opacity:1; transform:none; }
  }
"""

# kit fallback for a trip with no painted title plate: the word itself, in
# the poster's display face with the numerals' painted outline. Injected into
# the page CSS only when used, so pages with a plate are unchanged.
TITLE_TXT_CSS = """
  .ht.ht-txt { line-height:1.05; font-family:var(--disp); font-weight:900;
    font-size:clamp(52px,12vw,124px); letter-spacing:.06em; color:var(--cream);
    transform:rotate(-3deg); filter:drop-shadow(0 14px 30px rgba(30,8,60,.55));
    text-shadow:0 5px 0 #3A1272, 0 10px 0 rgba(42,16,80,.45), 0 0 40px rgba(255,158,224,.45); }
"""

JS = """
(function () {
  document.documentElement.classList.add('js');
  try {
    var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

    var tt = document.querySelector('.totop');
    var ttSync = function () {
      tt.classList.toggle('on', scrollY > innerHeight * 0.8);
    };
    addEventListener('scroll', ttSync, { passive: true });
    ttSync();

    document.querySelectorAll('details.mapfold').forEach(function (d) {
      d.addEventListener('toggle', function () {
        if (!d.open) return;
        var box = d.querySelector('.map-embed');
        if (!box || box.dataset.done) return;
        box.dataset.done = '1';
        var f = document.createElement('iframe');
        f.referrerPolicy = 'no-referrer-when-downgrade';
        f.src = box.dataset.src;
        f.addEventListener('load', function () {
          var ph = box.querySelector('.map-ph'); if (ph) ph.remove();
        });
        box.appendChild(f);
      });
    });

    if (reduce || !('IntersectionObserver' in window)) {
      document.querySelectorAll('.reveal').forEach(function (n) { n.classList.add('in'); });
    } else {
      var rev = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (e.isIntersecting) { e.target.classList.add('in'); rev.unobserve(e.target); }
        });
      }, { rootMargin: '0px 0px -8% 0px' });
      document.querySelectorAll('.reveal').forEach(function (n) { rev.observe(n); });
    }
  } catch (err) {
    document.querySelectorAll('.reveal').forEach(function (n) { n.classList.add('in'); });
  }
})();
"""


def _registry(block, key):
    """themes.splash.<key> ({name: {stem, ratio, …}}) → the entries whose
    cut-out asset actually resolves, with the data URI attached; a kind that
    has no picture is dropped so nothing ever paints an empty url()."""
    out = {}
    for name, d in (block.get(key) or {}).items():
        if not isinstance(d, dict) or not d.get("stem"):
            continue
        uri = data_uri(str(d["stem"]), "cut")
        if not uri:
            continue
        e = dict(d)
        e["uri"] = uri
        e["ratio"] = str(d.get("ratio") or "1/1")
        out[str(name)] = e
    return out


def kit_css(kit):
    """The per-trip CSS classes: one .veh-<kind> / .mas-<kind> / .strip-<kind>
    per resolved registry entry, in registry order (mascot selectors are
    padded to one column, as the hand-written block was)."""
    veh = "".join(
        f"  .veh-{k} {{ aspect-ratio:{d['ratio']}; background:url({d['uri']}) "
        "center/contain no-repeat; }\n" for k, d in kit["vehicles"].items())
    w = max((len("mas-" + k) for k in kit["mascots"]), default=0)
    mas = "".join(
        f"  .{('mas-' + k).ljust(w)} {{ aspect-ratio:{d['ratio']}; "
        f"background:url({d['uri']}) center/contain no-repeat; }}\n"
        for k, d in kit["mascots"].items())
    strip = "".join(
        f"  .strip-{k} {{ aspect-ratio:{d['ratio']};\n"
        f"    background:url({d['uri']}) center bottom/contain no-repeat; }}\n"
        for k, d in kit["strips"].items())
    return veh, mas, strip


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("-o", "--out", required=True)
    add_art_arg(ap)
    args = ap.parse_args()
    p = load_plan(args.plan)
    init_lang(args, p)
    art = load_art(args.plan, args.art, args.assets)

    meta = p.get("meta", {})
    days = p.get("days", [])
    dates = short_dates(meta.get("dates", "")).replace("-", ".")
    dates = dates.replace(" → ", " – ")
    m = re.search(r"\d{4}", meta.get("dates", "") or "")
    year = m.group(0) if m else ""      # for <title>; the ribbon drops it

    tb = art.theme(THEME)
    hero_spec = tb.get("hero") or {}
    appx_spec = tb.get("appendix") or {}
    kit = {"vehicles": _registry(tb, "vehicles"),
           "mascots": _registry(tb, "mascots"),
           "strips": _registry(tb, "strips")}
    # chapter index: 0 = hero, 1..N = days, N+1 = appendix (the seeded
    # decorations key off this index, so it is the renderer's, not art's)
    chain_specs = ([hero_spec] + [art.day(d.get("date", ""), THEME) for d in days]
                   + [appx_spec])
    SCENES, PALS = resolve_chain(chain_specs)
    n_appx = len(days) + 1

    days_html = "".join(render_day(i + 1, d, art, kit, SCENES[i + 1], PALS[i + 1])
                        for i, d in enumerate(days))
    decisions = "".join(f"<li>{et(u)}</li>" for u in p.get("decisions", []))
    unverified = "".join(f'<li>{ic("alert", "warn")} {et(u)}</li>'
                         for u in p.get("unverified", []))

    jump = "".join(
        f'<a href="#d{i}" aria-label="{esc(t("jump.to").format(i))}'
        f'{esc(art.day_theme(d.get("date", ""), d.get("city", "")))}">'
        f"{i:02d}</a>" for i, d in enumerate(days, 1))
    jump += (f'<a class="apx" href="#legs" aria-label="{esc(t("jump.appx"))}">'
             f'{esc(T("sec.appendix"))}</a>')

    # Hero road launches from the text-free strip BELOW the scroll cue (the
    # hero keeps 170px bottom padding as its runway); the appendix road stays
    # parked in the left gutter for its whole run — a centred path would pass
    # under every appendix band — and simply runs off the poster's foot.
    hero_road = road_svg(f"M 50 87.5 C 50 92.5, {GUT_R} 93.5, {GUT_R} 100")
    appx_road = road_svg("M 3.5 0 L 3.5 96")

    embeds = {  # kit CSS-class embeds (theme library): each cut-out enters
        "__CLOUDA__": "splash-cloud-a", "__CLOUDB__": "splash-cloud-b",  # once
        "__CLOUDC__": "splash-cloud-c", "__CLOUDD__": "splash-cloud-d",
        "__STAR__": "splash-star", "__BALLOON__": "splash-balloon",
    }
    css = CSS.replace("__STRIPA__", f"{STRIP_A}")
    for ph, stem in embeds.items():
        uri = data_uri(stem, "cut")
        assert uri, f"missing asset: {stem}.cut.webp"
        css = css.replace(ph, uri)
    veh_css, mas_css, strip_css = kit_css(kit)
    css = (css.replace("__VEH_CSS__\n", veh_css).replace("__MAS_CSS__\n", mas_css)
              .replace("__STRIP_CSS__\n", strip_css))

    # ---- cover words / pictures (art; every one optional) ----
    kick = art.cover(THEME, "kick")
    zh = art.cover(THEME, "zh")
    page_title = " · ".join(x for x in (title_head(art, THEME, year), t("title_suffix")) if x)
    title_uri = data_uri(str(hero_spec.get("title") or ""), "md")
    title_word = zh or kick or t("poster_word")    # the theme's own neutral poster word
    if title_uri:
        h1 = f'<h1 class="ht"><img src="{title_uri}" alt="{esc(title_word)}"></h1>'
    else:   # no painted plate: the theme sets the word itself (kit CSS,
        css += TITLE_TXT_CSS   # injected only when needed)
        h1 = f'<h1 class="ht ht-txt"><span>{esc(title_word)}</span></h1>'
    hero_uri = data_uri(str(hero_spec.get("art") or ""), "md")
    hcl = (f'<figure class="hcl"><i class="fx fxb warm" aria-hidden="true"></i>'
           f'<i class="fx fx-burst" aria-hidden="true"></i><img src="{hero_uri}" '
           f'alt="" aria-hidden="true"></figure>' if hero_uri else "")
    route = art.cover(THEME, "sub") or meta.get("route", "")
    route_html = f'<p class="route">{esc(route)}</p>' if route else ""
    # en: a small-caps line right under the plate; credit: the allusion in a
    # cream mono badge under the route — both the poster's own words, both
    # optional, both in colours contrast_report() already clears on the hero
    en = art.cover(THEME, "en")
    en_html = f'\n    <p class="en">{esc(en)}</p>' if en else ""
    credit = art.cover(THEME, "credit")
    credit_html = f'\n    <p class="credit">{esc(credit)}</p>' if credit else ""
    end_line = art.end(THEME, "line")
    end_fine = art.end(THEME, "fine")
    endcap = (f'<p>{esc(end_line)}</p>' if end_line else "") + (
        f'\n      <p class="fine">{esc(end_fine)}</p>' if end_fine else "")

    html_out = f"""<!doctype html>
<html lang="{T("html_lang")}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(page_title)}</title>
<style>{css}</style>
</head>
<body>
{sprite()}
{shape_defs()}

<header class="chap hero" id="top" style="background:{grad(SCENES[0])}">
  {deco(0, PALS[0], 24)}
  {hill(0, 'b')}
  {sides(0, PALS[0], 5, _side_extras(hero_spec.get("sides")))}
  {hero_road}
  <div class="hero-inner">
    {h1}{en_html}
    <div class="ribbon"><i class="rl"></i><i class="rr"></i><span>{esc(dates)}</span></div>
    {hcl}
    {route_html}{credit_html}
    <nav class="jump" aria-label="{esc(t("jump.label"))}">{jump}</nav>
    <a class="cue" href="#d1" aria-label="{esc(t("cue"))}"><svg width="20" height="11" viewBox="0 0 22 12" fill="none" aria-hidden="true"><path d="M2 2 L11 10 L20 2" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg></a>
  </div>
</header>

<main>
{days_html}

<section class="chap appx" id="appendix" style="background:{grad(SCENES[n_appx])}">
  {deco(n_appx, PALS[n_appx], 28)}
  {hill(n_appx, 't')}
  {sides(n_appx, PALS[n_appx], 9, _side_extras(appx_spec.get("sides")))}
  {appx_road}
  <div class="wrap wide">
    <h2 class="sec reveal" id="legs">{ic("plane")} {esc(t("legs"))}</h2>
    <div class="band reveal">{render_legs(p.get("legs", []))}</div>
    <h2 class="sec reveal" id="hotels">{ic("hotel")} {esc(T("sec.hotels"))}</h2>
    <div class="band reveal">{render_hotels(p.get("hotels", []))}</div>
    <h2 class="sec reveal" id="budget">{ic("wallet")} {esc(T("sec.budget"))}</h2>
    <div class="band reveal">{render_budget(p.get("budget", []), meta.get("budget_total", ""))}</div>
    <h2 class="sec reveal" id="checklist">{ic("checklist")} {esc(t("checklist"))}</h2>
    <div class="band reveal">{render_checklist(p.get("checklist", []))}</div>
    <h2 class="sec reveal">{ic("book")} {esc(T("sec.brief"))}</h2>
    <div class="band reveal"><div class="brief-grid">{render_brief(p.get("brief", {}), brief_titles(art))}</div></div>
    <h2 class="sec reveal">{ic("brain")} {esc(T("sec.decisions"))}</h2>
    <div class="band reveal"><ol class="plain">{decisions}</ol></div>
    <h2 class="sec reveal">{ic("alert")} {esc(T("sec.unverified"))}</h2>
    <div class="band reveal"><ul class="warn">{unverified}</ul></div>

    <div class="xrow xrow-appx no-export"><button type="button" class="xbtn"
      data-x-for="#appendix" data-x-label="{esc(T("label.appendix"))}"
      title="{esc(t("save_appx.title"))}"><span class="xs" aria-hidden="true">✦</span>{esc(T("btn.save_appendix"))}</button></div>

    <div class="endcap">
      <svg class="term" aria-hidden="true"><use href="#p-spark"/></svg>
      {endcap}
    </div>
    <footer>
      {esc(meta.get("party", ""))} · {esc(t("fx"))} {esc(meta.get("fx", ""))}<br>
      {esc(t("foot"))}
    </footer>
  </div>
</section>
</main>

<button type="button" class="xbtn xpage no-export" data-x-page
  title="{esc(t("save_page.title"))}"><span class="xs" aria-hidden="true">✦</span>{esc(T("btn.save_page"))}</button>
<a class="totop" href="#top" aria-label="{esc(t("totop"))}"><span aria-hidden="true">▲</span></a>

<script>{JS}</script>
<script>
EXPORT_JS_PLACEHOLDER
</script>
</body>
</html>"""

    html_out = html_out.replace("EXPORT_JS_PLACEHOLDER", export_js(
        theme_name(THEME), "#251043",
        # every chapter carries scroll-reveal + a fixed-position back-to-top;
        # inside a capture there is no scrolling, so pin the reveals visible
        # and drop the page furniture that would otherwise float over the card
        extra_css=(".reveal,.js .reveal,.js .reveal.in{opacity:1!important;"
                   "transform:none!important}"
                   ".__xbody .totop{display:none!important}"
                   ".__xbody .map-embed iframe{visibility:hidden!important}"
                   # a chapter is a slice of a continuous scroll: its own
                   # gradient must fill the card instead of leaving the page
                   # backdrop showing through the hills' bleed area
                   ".__xbody>.chap{margin:0!important}"),
        page_root="main", file_prefix=export_prefix(art, meta, THEME)))
    out = pathlib.Path(args.out)
    out.write_text(html_out, encoding="utf-8")
    ok, lines = contrast_report(SCENES)
    print(f"{out.name}: {out.stat().st_size // 1024}KB, days={len(days)}, "
          f"assets={asset_count()}")
    print("contrast (worst first):" + ("" if ok else "  ** FAIL **"))
    for ln in lines:
        print(ln)


if __name__ == "__main__":
    main()
