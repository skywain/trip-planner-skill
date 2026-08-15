#!/usr/bin/env python3
"""Clay-world renderer v2 — one continuous seamless clay diorama page.

No cards, no frames: the page background is a single multi-stop gradient
(sky → mint → green valley → sand → orange desert → turquoise ocean),
four transparent terrain bands melt the zone transitions, and a winding
SVG clay road is drawn through every day's milestone pebble after layout
(JS measures anchors, builds a smooth cubic path, redraws on resize).
Day info floats on the landscape: clay pebble numerals, embossed floating
titles, figurine props, and organic frosted "mist" blobs for timelines.
3D clay title sticker hangs in the sky. Single file, offline-first.

PNG export (theme_common.export_js): hand-pinched clay-bean buttons — 保存这一天
rides in the row of note pellets at the foot of every mist slab, 保存附录 above
the appendix, and 生成长图 is the apricot pebble parked at the end of the
mini-road nav for the whole continuous world. Every bean sits in normal flow
(nothing is absolutely placed over the page) and rests at full strength: a warm
apricot pellet among the white ones, pressed into the clay on hover.
Capture-only CSS repaints each module's slice of its chapter gradient and pins
the 100svh sky to the frozen viewport height.

ART CONTRACT (art.json, see ART-SCHEMA.md) — everything ABOUT the trip comes
from here; the renderer itself carries no place, date, picture name or zone.
themes.clay.<x> overrides the common <x> for cover / end / days (Art.cover /
Art.end / Art.day). Asset stems resolve through theme_common.data_uri — the
size variant each slot asks for is given in [brackets]; the chain then falls
back to md → cut → full-size:

  cover.kick        short trip word; with the plan's year it makes <title>
                    ("美国行 2026 · 黏土版") and the export filename prefix;
                    on an en page cover.kick_en wins when set (title_kick).
                    Missing → <title> is "<year> · 黏土版" (or just 黏土版).
  themes.clay.cover.title_stem   asset stem of the 3D clay title sticker that
                    hangs in the sky (an image — the words are baked into it)
                    [md]. Missing/absent file → a plain embossed text h1
                    instead, reading cover.zh, else cover.kick, else the
                    theme's 黏土世界.
  cover.zh          the display title: alt text of the sticker image, or the
                    text h1 when there is no sticker.
  cover.en          English line: a small hand-pinched clay tag under the
                    title, letterspaced uppercase. Missing → no tag (and none
                    of its CSS).
  cover.sub         the one-line route under the title ("纽约 → 黄石 → … → 北京").
                    Missing → plan meta.route, else the plan's date span, else
                    no line at all.
  cover.credit      the allusion's source, fine print under the route (no
                    tag, 55 % ink). Missing → nothing.
  end.line          the closing words ("北京,到家了。"): a clay signboard on a
                    stake between the appendix and the footer, at the road's
                    end. Missing → no plate (and none of its CSS). end.date /
                    mark / fine / farewell are not read by clay.
  days[date].theme  the 4-character day title (art.day_theme). Missing → the
                    day's `city` from the plan.
  themes.clay.days[date].figurine   asset stem of the clay figurine parked
                    beside the day head [md]. Missing / file absent → no
                    figurine (the head just starts at the DAY tag).
  themes.clay.zones  [{"from_day": 1|"<ISO date>", "kind": <kind>}, …] — where
                    the terrain changes. Days from `from_day` up to the next
                    zone's start share the terrain; the FIRST zone always
                    begins on day 1 whatever it says; zones that end up with
                    no days are dropped; an unknown kind falls back to the
                    theme's default terrain with one stderr warning. Missing →
                    one zone of the default terrain (kind "city") for the
                    whole trip. The colour ramp is chained by the renderer:
                    each zone starts on the previous zone's ground colour, the
                    first on the sky's foot, the appendix on the last zone's.
      kind ∈ kit (picture-free, geography-neutral, drawn by svg_band()):
                    ridge  snow-capped clay cones      ground #d9d3ea
                    plain  fields, hedgerows, hay bales        #e2e6b4
                    coast  surf breaking on a headland         #a9dbd8
                    forest wooded hills                        #b9d9b0
                    lake   still water with ripples            #c3dff0
                    desert dunes with wind ripples             #efd6ad
           kit (US cut-out bands — Liberty skyline, geyser, saguaro,
                    volcano; only for the trip they were drawn for):
                    city (default) #cfe8c9 · park #e6dcb0 · west #f0c9a0 ·
                    isle #7fc9c6
           "custom": the art hands the band in itself —
                    {"kind": "custom", "band": "<stem>" [band],
                     "to": "#rrggbb", "decor": ["<stem>" [md] |
                     {"stem": …, "pos": "<inline style>"}, …]}
                    `to` is the ground the zone ramps down to (bad/missing →
                    #d8e2d5 + warning); `band` missing/absent file → no strip,
                    just the ramp; bare decor stems take the kit's edge slots
                    in order (L, R, L-low, R-low). The renderer only places
                    them and chains the palette.
  brief_titles      (common) {plan.brief key: title} overlay on
                    theme_common.BRIEF_TITLES for the 行前须知 headings.

Kit (the theme's own, nothing to pick in art): the terrain kinds above (band
strip or SVG terrain + edge furniture + ground colour each), the sky clouds /
balloon / tour bus [md], the pebble palette by day number, left/right
alternation by day number, the winding road + road-nav, the mist slabs, the
export beans, the clay tag / plate shapes for en / credit / end.line.

Usage: python3 render_clay2.py <plan.geo.json> [--art <art.json>|none]
                               [--assets DIR ...] -o <out.html>
Assets are searched in the plan's directory, every --assets DIR, then
themes/assets/ (theme_common.data_uri).
"""
import argparse
import pathlib
import re
import sys

from theme_common import (LUCIDE, T, add_art_arg, asset_count, brief_titles,
                          data_uri, day_embed_url, esc, et, export_js, export_prefix, ic,
                          init_lang, lang, load_art, load_plan, set_icon_base, short_dates, title_head,
                          sprite, tag_pretty, theme_name)

HERE = pathlib.Path(__file__).parent

THEME = "clay"

# ------------------------------------------------------------- theme voice --
# The clay world's own words (cover fallback, mist-slab labels, button hints,
# footer). Shared UI strings (tags, save buttons, section names, 步行/雨备…)
# come from theme_common.T(). zh values are byte-identical to the pre-i18n
# page — the US baselines pin them.
L = {
    "zh": {
        "world": "黏土世界",
        "nav.to": "导航到 ",
        "km": "≈{}km",
        "late": "晚点",
        "note": "注",
        "route_map": "路线地图",
        "map_ph": "地图需联网加载",
        "save_day.title": "把这一天存成图片,可发朋友圈",
        "save_appx.title": "把附录(航段·住宿·预算·清单)存成图片,可发朋友圈",
        "save_page.title": "把整条黏土世界拼成一张长图,可发朋友圈",
        "roadnav": "行程路线导航",
        "day_n.pre": "第 ", "day_n.post": " 天",   # nav stone aria-label
        "legs": "航段速览",
        "checklist": "行前清单",
        "extra": "取舍 & 待复核",
        "unverified": "出票前复核",
        "total": "合计",
        "fx": "汇率",
        "foot": "日出日落:sunrise-sunset.org · 黏土世界由 AI 生成,仅作示意 · 价格以预订渠道实时为准",
    },
    "en": {
        "world": "Clay World",
        "nav.to": "Navigate to ",
        "km": " ≈{} km",
        "late": "if late",
        "note": "note",
        "route_map": "route map",
        "map_ph": "map needs a connection to load",
        "save_day.title": "Save this day as an image to share",
        "save_appx.title": "Save the appendix (legs · stays · budget · checklist) as an image",
        "save_page.title": "Stitch the whole clay world into one long image",
        "roadnav": "Trip route navigation",
        "day_n.pre": "Day ", "day_n.post": "",
        "legs": "Flights & legs",
        "checklist": "Checklist",
        "extra": "Decisions & to verify",
        "unverified": "Verify before booking",
        "total": "Total",
        "fx": "FX",
        "foot": "Sun times: sunrise-sunset.org · clay world generated by AI, illustrative only · prices: check the booking channel",
    },
}


def t(k):
    return L.get(lang(), L["zh"]).get(k, L["zh"][k])


def tag_label(tag):
    """pinned/skippable/opener via theme_common.tag_pretty; a swap→X tag is
    printed as written (the zh baseline pins the raw `swap→` form, and in en
    tag_pretty would print exactly that anyway)."""
    return tag if tag.startswith("swap") else tag_pretty(tag)
PEBBLE = ["#f2b28c", "#a8d8c5", "#f5d97e", "#cdb9ef"]

# The sky gradient's last stop — where the first terrain zone's ramp begins.
SKY_FOOT = "#dcefe6"
# Terrain kit: what a zone kind looks like. `to` is the ground colour the zone
# ramps down to (the next zone starts there); `band` the transparent terrain
# strip (a cut-out asset, `band` variant) that melts the seam — or `svg`, a
# terrain drawn by svg_band() from pure shapes, no picture needed; `decor`
# the edge furniture (stem, inline style).
# Which kind a stretch of days sits in comes from art (themes.clay.zones).
# The four US kinds ride on generated cut-outs (Liberty in the city band, a
# geyser, saguaros, a volcano) — every other trip picks from the neutral,
# picture-free kinds below or hands its own band in with kind "custom".
_PINES_R = ("clay-pines", "right:2%;top:36%;width:clamp(90px,9vw,150px);rotate:2deg")
_PINES_L = ("clay-pines", "left:1.8%;top:30%;width:clamp(100px,10vw,170px);rotate:-2deg")
TERRAIN = {
    "city": {"band": "strip-mountains", "to": "#cfe8c9", "decor": (
        ("clay-signpost", "left:2.5%;top:1.8%;width:clamp(70px,7vw,110px);rotate:-3deg"),
        _PINES_R)},
    "park": {"band": "strip-geyser", "to": "#e6dcb0", "decor": (_PINES_L,)},
    "west": {"band": "strip-desert", "to": "#f0c9a0", "decor": (
        ("clay-cactus", "right:2.2%;top:26%;width:clamp(80px,8vw,130px);rotate:2deg"),)},
    "isle": {"band": "strip-ocean", "to": "#7fc9c6", "decor": (
        ("clay-palm", "left:2%;top:20%;width:clamp(90px,9vw,150px);rotate:-2deg"),)},
    # ---- neutral kinds: CSS/SVG terrain, geography-free ----
    "ridge":  {"svg": "ridge",  "to": "#d9d3ea", "decor": (_PINES_R,)},   # snow-capped ridge
    "plain":  {"svg": "plain",  "to": "#e2e6b4", "decor": ()},            # fields, hedgerows
    "coast":  {"svg": "coast",  "to": "#a9dbd8", "decor": ()},            # surf on a headland
    "forest": {"svg": "forest", "to": "#b9d9b0", "decor": (_PINES_L,)},   # wooded hills
    "lake":   {"svg": "lake",   "to": "#c3dff0", "decor": ()},            # still water, ripples
    "desert": {"svg": "desert", "to": "#efd6ad", "decor": ()},            # dunes (no cactus)
}
# A zone that names no kind (or an unknown one) gets a NEUTRAL band. Never a
# place-bound one: "city" is the New York skyline + Liberty cut-out and
# leaked onto the China test page (owner 2026-08-15) when it was the default.
DEFAULT_TERRAIN = "ridge"
CUSTOM_TO = "#d8e2d5"          # ground for a custom zone that names no `to`
# where a custom zone's decor stems land when art gives bare stems, by index
CUSTOM_DECOR_POS = (
    "left:2%;top:26%;width:clamp(90px,9vw,150px);rotate:-2deg",
    "right:2.2%;top:30%;width:clamp(90px,9vw,150px);rotate:2deg",
    "left:2.5%;top:62%;width:clamp(80px,8vw,130px);rotate:2deg",
    "right:2%;top:66%;width:clamp(80px,8vw,130px);rotate:-2deg",
)
# the closing "deep water" ground under the appendix
DEEP_TO = "#5fb2b6"
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def img(uri, cls, extra=""):
    """A decorative <img> — or nothing when the asset is missing (never an
    empty src)."""
    return f'<img class="{cls}" src="{uri}" alt=""{extra}>' if uri else ""


def custom_terrain(z):
    """A zones[] entry with kind "custom": the art hands the band in itself
    ({"band": stem, "to": "#hex", "decor": [stem | {"stem","pos"}]}); the
    renderer only places it and chains the colour ramp."""
    to = z.get("to")
    if not (isinstance(to, str) and HEX_RE.match(to)):
        print(f"warning: themes.clay.zones custom zone `to` {to!r} is not #rrggbb "
              f"— using {CUSTOM_TO!r}", file=sys.stderr)
        to = CUSTOM_TO
    decor = []
    for k, d in enumerate(z.get("decor") or []):
        if isinstance(d, str):
            stem, pos = d, CUSTOM_DECOR_POS[k % len(CUSTOM_DECOR_POS)]
        elif isinstance(d, dict) and d.get("stem"):
            stem = d["stem"]
            pos = d.get("pos") or d.get("style") or CUSTOM_DECOR_POS[k % len(CUSTOM_DECOR_POS)]
        else:
            continue
        decor.append((stem, pos))
    band = z.get("band")
    return {"band": band if isinstance(band, str) else "", "to": to.lower(),
            "decor": tuple(decor)}


def resolve_zones(zone_spec, days):
    """themes.clay.zones → [(kind, terrain, [days], start_day_number)], empty
    zones dropped, first zone forced to start at day 1. `terrain` is the kit
    entry for the kind, or the art-supplied one for kind "custom"."""
    n = len(days)
    if not n:
        return []
    by_date = {d.get("date", ""): k for k, d in enumerate(days)}
    starts = []
    for z in zone_spec or []:
        if not isinstance(z, dict):
            continue
        fd = z.get("from_day", 1)
        if isinstance(fd, str) and fd in by_date:
            idx = by_date[fd]
        else:
            try:
                idx = int(fd) - 1
            except (TypeError, ValueError):
                idx = 0
        kind = z.get("kind") or DEFAULT_TERRAIN
        if kind == "custom":
            terr = custom_terrain(z)
        elif kind in TERRAIN:
            terr = TERRAIN[kind]
        else:
            print(f"warning: themes.clay.zones kind {kind!r} is not in the kit "
                  f"{sorted(TERRAIN) + ['custom']} — using {DEFAULT_TERRAIN!r}",
                  file=sys.stderr)
            kind, terr = DEFAULT_TERRAIN, TERRAIN[DEFAULT_TERRAIN]
        starts.append((max(0, min(idx, n)), kind, terr))
    if not starts:
        starts = [(0, DEFAULT_TERRAIN, TERRAIN[DEFAULT_TERRAIN])]
    starts.sort(key=lambda s: s[0])
    starts[0] = (0,) + starts[0][1:]
    out = []
    for k, (idx, kind, terr) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else n
        if end > idx:
            out.append((kind, terr, days[idx:end], idx + 1))
    return out


def lerp_hex(a, b, t):
    """Blend two #rrggbb colours; used to hand each exported day the slice of
    its chapter gradient it actually sits on (a module clone has no .chap
    ancestor, so the capture must repaint the ground itself)."""
    return "#" + "".join(
        f"{round(int(a[i:i + 2], 16) + (int(b[i:i + 2], 16) - int(a[i:i + 2], 16)) * t):02x}"
        for i in (1, 3, 5))


# ---------------------------------------------------------- SVG terrain --
# The neutral kinds are drawn, not photographed: rolling clay shapes in the
# same rounded language as the road (horizontal-tangent cubics between
# points), each layer with a rim of light along its top and a soft shadow
# under the front one; the front layer fades into the previous chapter's
# ground so the seam melts exactly like the cut-out bands do.
BAND_W, BAND_H = 1400, 300


def _ridge_d(pts):
    """Open path through pts with horizontal tangents at every point — the
    road's own smoothing, so hills and peaks share the road's hand."""
    d = f"M{pts[0][0]},{pts[0][1]}"
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        mx = (x0 + x1) / 2
        d += f" C{mx},{y0} {mx},{y1} {x1},{y1}"
    return d


def _hill(pts, fill, rim=".55", shadow=False, extra=""):
    """A closed hill from an open ridge (drops to the band floor), its top
    rim lit, optionally a soft shadow beneath. pts must span x 0…BAND_W."""
    d = _ridge_d(pts)
    closed = f"{d} L{BAND_W},{BAND_H} L0,{BAND_H} Z"
    out = ""
    if shadow:
        out += (f'<path d="{closed}" fill="rgba(74,68,88,.11)" '
                f'transform="translate(0,10)"/>')
    out += f'<path d="{closed}" fill="{fill}"{extra}/>'
    if rim:
        out += (f'<path d="{d}" fill="none" stroke="rgba(255,255,255,{rim})" '
                f'stroke-width="7" stroke-linecap="round"/>')
    return out


def _blob(cx, cy, rx, ry, fill, rim=True):
    """A pinched clay pebble/canopy/foam ball: ellipse + a highlight dot."""
    out = f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}"/>'
    if rim:
        out += (f'<ellipse cx="{cx - rx * .3:.0f}" cy="{cy - ry * .35:.0f}" '
                f'rx="{rx * .32:.0f}" ry="{ry * .26:.0f}" fill="rgba(255,255,255,.55)"/>')
    return out


def _peak(x, y, w, fill, snow=True):
    """One clay cone: rounded summit, sides bowing gently out to the band
    floor, a rim of light up its left flank, an optional snow cap whose
    lower edge is pinched into three lobes."""
    H = BAND_H
    body = (f"M{x - w},{H} C{x - w * .45},{H} {x - w * .22},{y} {x},{y} "
            f"C{x + w * .22},{y} {x + w * .45},{H} {x + w},{H} Z")
    out = f'<path d="{body}" fill="{fill}"/>'
    out += (f'<path d="M{x - w * .82},{H - 12} C{x - w * .5},{H - 60} {x - w * .2},{y + 8} {x},{y}" '
            f'fill="none" stroke="rgba(255,255,255,.55)" stroke-width="7" stroke-linecap="round"/>')
    if snow:
        sh = (H - y) * .34            # cap depth
        sw = w * .30                  # cap half-width at its lower edge
        yb = y + sh
        out += (f'<path d="M{x - sw},{yb} C{x - sw * .55},{y + sh * .3} {x - w * .1},{y} {x},{y} '
                f'C{x + w * .1},{y} {x + sw * .55},{y + sh * .3} {x + sw},{yb} '
                f'C{x + sw * .8},{yb + 14} {x + sw * .55},{yb - 6} {x + sw * .33},{yb + 4} '
                f'C{x + sw * .15},{yb + 16} {x - sw * .15},{yb + 16} {x - sw * .33},{yb + 4} '
                f'C{x - sw * .55},{yb - 6} {x - sw * .8},{yb + 14} {x - sw},{yb} Z" '
                f'fill="#fbf7ff"/>')
    return out


def _trees(xs, base_y, canopy, trunk="#b8926e", r=22):
    out = ""
    for k, x in enumerate(xs):
        rr = r + (k % 3) * 4
        out += (f'<rect x="{x - 4}" y="{base_y - rr}" width="8" height="{rr + 8}" '
                f'rx="3" fill="{trunk}"/>')
        out += _blob(x, base_y - rr - 6, rr, rr * .92, canopy[k % len(canopy)])
    return out


def svg_band(name, c_from, c_to, uid):
    """The neutral kit's terrain strip for kind `name`, sized like the cut-out
    bands (BAND_W×BAND_H, scales with width). Colours: the kind's own palette
    behind, the front hill fading from a blend of the two grounds into
    `c_from` — the previous chapter's floor — so the seam is invisible."""
    front_top = lerp_hex(c_from, c_to, .45)
    gid = f"bg{uid}"
    W, H = BAND_W, BAND_H
    body = ""
    if name == "ridge":
        # two rows of snow-capped cones, tall ones behind, foothills in front
        for x, y, w in ((90, 95, 190), (330, 40, 230), (600, 120, 200), (830, 30, 250),
                        (1080, 100, 210), (1330, 60, 220)):
            body += _peak(x, y, w, "#cbc0e6")
        for x, y, w in ((-30, 190, 170), (210, 150, 180), (460, 175, 190), (720, 140, 200),
                        (960, 185, 190), (1220, 160, 200), (1430, 200, 160)):
            body += _peak(x, y, w, "#b6a9dc")
        front = [(0, 300), (200, 268), (420, 292), (700, 262), (1000, 290), (1250, 268), (1400, 300)]
    elif name == "plain":
        back = [(0, 240), (240, 190), (520, 225), (800, 180), (1100, 220), (1400, 195)]
        mid = [(0, 300), (280, 235), (620, 268), (940, 228), (1400, 262)]
        body += _hill(back, "#cfe0a4", rim=".55")
        # a copse on the far hill, hedgerow bushes hugging the near one
        body += _trees((330, 700, 1230), 212, ("#98bd7a", "#7fb98a"), r=16)
        body += _hill(mid, "#bcd48f", rim=".5")
        for x, y in ((120, 279), (300, 250), (470, 265), (640, 275), (800, 262),
                     (960, 246), (1130, 258), (1300, 270)):
            body += _blob(x, y - 8, 20, 15, "#98bd7a")
        # hay bales
        for x, y in ((220, 262), (560, 268), (1050, 250)):
            body += _blob(x, y, 14, 12, "#e8d28a")
        front = [(0, 300), (350, 284), (720, 296), (1080, 282), (1400, 296)]
    elif name == "coast":
        head = [(0, 300), (140, 200), (330, 240), (520, 300), (1400, 300)]
        body += _hill(head, "#bfd6b3", rim=".5")
        sea = [(0, 300), (200, 300), (400, 258), (560, 270), (720, 254), (880, 268),
               (1040, 252), (1200, 266), (1400, 250)]
        body += _hill(sea, "#8fd0cf", rim=".7", shadow=True)
        for x, y in ((400, 258), (720, 254), (1040, 252), (1400, 250), (560, 270), (880, 268)):
            body += _blob(x - 40, y + 4, 34, 11, "rgba(255,255,255,.7)", rim=False)
        front = [(0, 300), (300, 300), (600, 288), (900, 300), (1160, 286), (1400, 300)]
    elif name == "forest":
        back = [(0, 250), (220, 150), (480, 220), (760, 130), (1040, 210), (1300, 150), (1400, 200)]
        mid = [(0, 300), (260, 235), (560, 265), (860, 220), (1160, 262), (1400, 240)]
        body += _hill(back, "#a9d1a5", rim=".55")
        body += _trees((60, 200, 330, 470, 610, 760, 900, 1050, 1200, 1340), 245,
                       ("#7fb98a", "#5f9e77", "#8fc394"), r=20)
        body += _hill(mid, "#8fbf90", rim=".5")
        body += _trees((140, 400, 700, 980, 1260), 268, ("#5f9e77", "#7fb98a"), r=16)
        front = [(0, 300), (300, 286), (700, 298), (1050, 284), (1400, 296)]
    elif name == "lake":
        back = [(0, 260), (200, 170), (420, 230), (680, 150), (940, 225), (1200, 165), (1400, 240)]
        body += _hill(back, "#c9d5ea", rim=".55")
        water = [(0, 300), (160, 300), (300, 250), (700, 244), (1100, 250), (1260, 300), (1400, 300)]
        body += _hill(water, "#a9cff0", rim=".65", shadow=True)
        for cx, cy, rx in ((520, 268, 90), (860, 276, 70), (700, 288, 40)):
            body += (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="5" fill="none" '
                     f'stroke="rgba(255,255,255,.7)" stroke-width="4"/>')
        front = [(0, 300), (260, 292), (500, 300), (1000, 300), (1250, 290), (1400, 300)]
    elif name == "desert":
        back = [(0, 250), (300, 190), (600, 235), (900, 175), (1200, 230), (1400, 200)]
        mid = [(0, 300), (250, 245), (520, 275), (820, 232), (1100, 270), (1400, 240)]
        body += _hill(back, "#f3e0bd", rim=".65")
        body += _hill(mid, "#e8cd9c", rim=".6")
        # wind ripples on the mid dune
        for x, y in ((360, 262), (700, 252), (1000, 256), (1250, 250)):
            body += (f'<path d="M{x - 40},{y} q20,-8 40,0 q20,8 40,0" fill="none" '
                     f'stroke="rgba(255,255,255,.55)" stroke-width="3" stroke-linecap="round"/>')
        front = [(0, 300), (350, 280), (700, 296), (1050, 278), (1400, 294)]
    else:
        return ""
    body += _hill(front, f"url(#{gid})", rim=".45", shadow=True)
    return (f'<svg class="band band-svg" viewBox="0 0 {W} {H}" aria-hidden="true">'
            f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{front_top}"/>'
            f'<stop offset="1" stop-color="{c_from}"/></linearGradient></defs>'
            f'{body}</svg>')



def tl_row(r):
    kind = r.get("kind", "anchor")
    est = '<sup>est</sup>' if r.get("verify") == "est" else ""
    tag = r.get("tag", "")
    chip = (f'<span class="tag{" hot" if tag == "pinned" else ""}">'
            f'{esc(tag_label(tag))}</span>' if tag else "")
    price = f' <span class="dim">{esc(r["price"])}</span>' if r.get("price") else ""
    nav = (f' <a class="rownav" href="{esc(r["link"])}" target="_blank" rel="noopener"'
           f' aria-label="{esc(t("nav.to"))}{esc(r.get("what", ""))[:18]}">{ic("pin")}</a>'
           if r.get("link") else "")
    return (f'<div class="row k-{kind}"><span class="t">{esc(r.get("t",""))}{est}</span>'
            f'<span class="w">{et(r.get("what",""))}{price}{chip}{nav}</span></div>')


def note_pills(day):
    out = []
    wk = day.get("walking_km")
    if isinstance(wk, dict):
        out.append(("walk", T("walk") + t("km").format(wk.get('total', '?')), wk.get("how", "")))
    elif wk:
        out.append(("walk", T("walk") + t("km").format(wk), ""))
    for key, icn, label in (("rain_alt", "rain", T("rain_alt")), ("late_cut", "clock", t("late")),
                            ("note", "note", t("note"))):
        if day.get(key):
            out.append((icn, label, day[key]))
    return "".join(
        (f'<details class="npill"><summary>{ic(icn)} {esc(lab)}</summary>'
         f'<p>{et(body)}</p></details>') if body else
        f'<span class="npill solo">{ic(icn)} {esc(lab)}</span>'
        for icn, lab, body in out)


def render_day(i, day, art):
    date = day.get("date", "")
    fig = data_uri(art.day(date, THEME).get("figurine", ""))
    side = "L" if i % 2 else "R"
    art_html = f'<img class="figurine" src="{fig}" alt="">' if fig else ""
    # the sun tool writes 天亮 (zh) or dawn (en) — show it in the page language
    sun = et(re.sub(r"^(天亮|dawn)\b", T("sun.dawn"), day.get("sun", "") or ""))
    embed = day_embed_url(day)
    embed_html = (f'<details class="mapfold"><summary class="npill">{ic("compass")}'
                  f' {esc(t("route_map"))}</summary><div class="map-embed" data-src="{esc(embed)}">'
                  f'<p class="map-ph">{esc(t("map_ph"))}</p></div></details>' if embed else "")
    tl = "".join(tl_row(r) for r in day.get("timeline", []))
    pebble_color = PEBBLE[i % 4]
    return f"""
<section class="day side{side}" id="d{i}" data-road-anchor>
  <div class="stone" style="--pb:{pebble_color}">{i:02d}</div>
  <header class="float-head reveal">
    {art_html}
    <div>
      <h2><span class="daytag">DAY {i} · {date[5:].replace("-", ".")} · {esc(day.get("city",""))}</span>
        <span class="h-theme">{esc(art.day_theme(date, day.get("city", "")))}</span></h2>
      <p class="lbl">{esc(day.get("label",""))}</p>
      {f'<p class="sun">{sun}</p>' if sun else ""}
    </div>
  </header>
  <div class="mist reveal">
    {tl}
    <div class="pills">{note_pills(day)}<button class="xbtn no-export"
      data-x-for="#d{i}" data-x-label="DAY{i:02d}"
      title="{esc(t("save_day.title"))}">{esc(T("btn.save_day"))}</button>{embed_html}</div>
  </div>
</section>"""


def appendix(p, total_budget, titles):
    legs = "".join(
        f'<div class="row k-hop"><span class="t">{esc(l.get("date",""))[5:]}</span>'
        f'<span class="w">{esc(l.get("from",""))}→{esc(l.get("to",""))} '
        f'{et(l.get("carrier",""))} {esc(l.get("dep",""))}-{esc(l.get("arr",""))}'
        f' <span class="dim">{esc(l.get("price",""))} · {esc(l.get("bags",""))}</span></span></div>'
        for l in p.get("legs", []))
    hotels = "".join(
        f'<details class="sub"><summary>{esc(h.get("base",""))} · {esc(h.get("area",""))}</summary>'
        f'<p class="dim">{esc(h.get("why",""))}</p><ul>' + "".join(
            f'<li><a href="{esc(o.get("link","#"))}" target="_blank" rel="noopener">{esc(o.get("name",""))}</a>'
            f' <span class="dim">{esc(o.get("band",""))}</span></li>'
            for o in h.get("options", [])) + "</ul></details>"
        for h in p.get("hotels", []))
    budget = "".join(
        f'<div class="row"><span class="t">{esc(b.get("cat",""))}</span>'
        f'<span class="w">{esc(b.get("per_person",""))}'
        f' <span class="dim">{esc(b.get("note",""))}</span></span></div>'
        for b in p.get("budget", []))
    checklist = "".join(
        f'<div class="row"><span class="t">{i:02d}</span><span class="w"><label>'
        f'<input type="checkbox"> {et(c.get("item",""))}</label>'
        f' <span class="dim">{esc(c.get("deadline",""))} · {esc(c.get("price",""))}</span>'
        + (f' <a href="{esc(c["link"])}" target="_blank" rel="noopener">{esc(c.get("link_text", T("link")))}</a>'
           if c.get("link") else "") + "</span></div>"
        for i, c in enumerate(p.get("checklist", []), 1))
    brief = "".join(
        f'<details class="sub"><summary>{esc(titles.get(k, k))}</summary><p class="dim">{et(v)}</p></details>'
        for k, v in p.get("brief", {}).items())
    decisions = "".join(f"<li>{et(u)}</li>" for u in p.get("decisions", []))
    unverified = "".join(f"<li>{et(u)}</li>" for u in p.get("unverified", []))
    blocks = (
        ("legs", "plane", t("legs"), legs),
        ("hotels", "hotel", T("sec.hotels"), hotels),
        ("budget", "wallet", T("sec.budget"),
         budget + f'<p class="total">{esc(t("total"))} {esc(total_budget)}</p>'),
        ("checklist", "checklist", t("checklist"), checklist),
        ("brief", "book", T("sec.brief"), brief),
        ("extra", "brain", t("extra"),
         f'<details class="sub"><summary>{esc(T("sec.decisions"))}</summary><ol class="dim">{decisions}</ol></details>'
         f'<details class="sub"><summary>{ic("alert","warn")} {esc(t("unverified"))}</summary>'
         f'<ul class="dim warn">{unverified}</ul></details>'),
    )
    return "".join(
        f'<section class="appx" id="{aid}"><div class="mist reveal">'
        f'<h2>{ic(icn)} {esc(title)}</h2>{body}</div></section>'
        for aid, icn, title, body in blocks)


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
    year = (meta.get("dates", "") or "")[:4]
    year = year if year.isdigit() else ""

    # cover words — the trip's, all optional
    kick = art.cover(THEME, "kick")
    cover_zh = art.cover(THEME, "zh")
    page_title = " · ".join(x for x in (title_head(art, THEME, year), theme_name(THEME)) if x)
    title_img = data_uri(art.cover(THEME, "title_stem"))
    if title_img:
        title_html = f'<img class="title" src="{title_img}" alt="{esc(cover_zh)}">'
        title_css = ""
    else:
        title_html = esc(cover_zh or kick or t("world"))
        title_css = ("  .sky h1 { line-height:1.15; font-size:clamp(40px,8vw,84px); "
                     "font-weight:900; letter-spacing:.1em; text-align:center; "
                     "padding:0 20px; text-shadow:0 2px 0 rgba(255,255,255,.7), "
                     "0 16px 26px rgba(74,68,88,.22); }\n")
    dates = short_dates(meta.get("dates", "")).replace(" → ", "—")
    sub = art.cover(THEME, "sub") or meta.get("route", "") or dates
    # Latin subtitles want tighter tracking than the .3em CJK setting (a
    # letter-spaced English sentence reads as scattered — owner feedback on the
    # China page); mark them so the CSS can adjust without touching zh pages.
    _latin = bool(sub) and sum(1 for c in sub if ord(c) < 0x2E80) / max(1, len(sub)) > 0.7
    sub_html = (f'<p class="sub{" latin" if _latin else ""}">{esc(sub)}</p>' if sub else "")
    # optional cover slots — hand-pinched little tags under the title; each
    # is emitted (markup AND its CSS) only when the art gives it
    cover_en = art.cover(THEME, "en")
    cover_credit = art.cover(THEME, "credit")
    en_html = f'\n  <p class="en">{esc(cover_en)}</p>' if cover_en else ""
    credit_html = f'\n  <p class="credit">{esc(cover_credit)}</p>' if cover_credit else ""
    extra_css = ""
    if cover_en or cover_credit:
        extra_css += "  .sky .en, .sky .credit { position:relative; z-index:1; }\n"
    if _latin:
        extra_css += ("  .sky .sub.latin { letter-spacing:.06em; font-weight:700; "
                      "font-size:clamp(13px,1.7vw,15px); opacity:.72; "
                      "font-family:'Nunito','Quicksand','Varela Round','Arial Rounded MT Bold',"
                      "'Avenir Next Rounded',system-ui,sans-serif; }\n")
    if cover_en:
        extra_css += (
            "  /* the English line: a small clay tag pinched under the title */\n"
            "  .sky .en { margin-top:16px; font-size:11px; font-weight:800; "
            "letter-spacing:.28em; text-transform:uppercase; color:var(--ink); "
            "background:rgba(255,253,246,.85); padding:6px 16px 6px 20px; rotate:-2deg;\n"
            "    border-radius:46% 54% 52% 48% / 58% 52% 48% 42%;\n"
            "    box-shadow:inset 2px 3px 5px rgba(255,255,255,.95), "
            "inset -2px -3px 5px rgba(74,68,88,.10), 0 6px 12px rgba(74,68,88,.14); }\n"
            "  .sky .en + .sub { margin-top:14px; }\n")
    if cover_credit:
        extra_css += (
            "  /* the source of the allusion: fine print, no tag, quiet */\n"
            "  .sky .credit { margin-top:12px; font-size:11px; letter-spacing:.06em; "
            "color:var(--ink); opacity:.55; text-align:center; max-width:36em; "
            "padding:0 20px; line-height:1.7; }\n")
    # the closing "home" plate: a clay signboard on a stake, after the appendix
    end_line = art.end(THEME, "line")
    end_html = (f'\n<div class="homeplate reveal"><p class="plate">{esc(end_line)}</p></div>'
                if end_line else "")
    if end_line:
        extra_css += (
            "  /* 到家: a hand-cut clay signboard on a stake at the end of the road */\n"
            "  .homeplate { position:relative; z-index:1; max-width:880px; margin:0 auto 34px;\n"
            "    padding:0 clamp(16px,4vw,40px); text-align:center; }\n"
            "  .homeplate .plate { display:inline-block; max-width:34em; padding:16px 30px;\n"
            "    font-size:15px; font-weight:800; letter-spacing:.06em; line-height:1.6;\n"
            "    color:var(--ink); background:rgba(255,253,247,.93); rotate:-1.5deg;\n"
            "    border-radius:28px 36px 30px 38px / 36px 28px 38px 30px;\n"
            "    box-shadow:inset 4px 6px 10px rgba(255,255,255,.95),\n"
            "      inset -4px -6px 12px rgba(74,68,88,.10), 0 16px 26px rgba(74,68,88,.18);\n"
            "    text-shadow:0 1px 0 rgba(255,255,255,.7); }\n"
            "  .homeplate::after { content:\"\"; display:block; width:14px; height:38px;\n"
            "    margin:-4px auto 0; background:#c9905f; border-radius:5px 5px 9px 9px;\n"
            "    box-shadow:inset 2px 0 3px rgba(255,255,255,.45), 0 8px 12px rgba(74,68,88,.22); }\n")

    # sky furniture and the tour bus are the theme's own props
    bus = data_uri("clay-bus-solo")
    deco = {k: data_uri(k) for k in
            ("clay-cloud-a", "clay-cloud-b", "clay-cloud-c", "clay-balloon")}
    # the nav is drawn by JS from the same path; keep real anchors underneath
    # it so the page still navigates with JS off
    dots = "".join(f'<a href="#d{i}" data-spy="d{i}" class="rn-fallback">{i}</a>'
                   for i in range(1, len(days) + 1))

    # chapter = terrain band + the days that live in that terrain.
    # --from of each chapter == --to of the previous one, so the whole page is
    # one unbroken colour ramp and every band sits on matching ground.
    # Which days share a terrain comes from art; the ramp chaining is ours.
    zones = resolve_zones(art.theme(THEME).get("zones"), days)
    assembled = ""
    # a module capture clones one .day with no .chap ancestor, so each exported
    # day gets its slice of the chapter gradient repainted by the capture-only
    # CSS (.__xbody> scoping keeps these rules away from the whole-page clone,
    # where the real .chap gradients and road layers must stay untouched)
    xbg = []
    c_to = SKY_FOOT
    svg_bands = False
    for kind, terr, zdays, start_i in zones:
        c_from, c_to = c_to, terr["to"]
        # landscape furniture for this terrain, parked at the page edges
        decor = "".join(img(data_uri(stem), "deco", f' style="{style}"')
                        for stem, style in terr["decor"])
        if terr.get("svg"):
            band = svg_band(terr["svg"], c_from, c_to, start_i)
            svg_bands = svg_bands or bool(band)
        else:
            band = img(data_uri(terr["band"], "band"), "band", ' aria-hidden="true"')
        inner = "".join(render_day(start_i + j, d, art) for j, d in enumerate(zdays))
        n = len(zdays) or 1
        for j in range(len(zdays)):
            pad = ";padding-top:34px" if j == 0 else ""   # mirrors .chap>.day:first-of-type
            xbg.append(f".__xbody>#d{start_i + j}{{background:linear-gradient(180deg,"
                       f"{lerp_hex(c_from, c_to, j / n)},"
                       f"{lerp_hex(c_from, c_to, (j + 1) / n)}){pad}}}")
        assembled += (
            f'<div class="chap z-{kind}" style="--from:{c_from};--to:{c_to}">'
            f'{band}{decor}{inner}</div>')
    deep_from = c_to   # the appendix's deep water starts on the last ground
    if svg_bands:
        # an inline SVG has no intrinsic height: give the drawn bands the
        # cut-out strips' proportions so they scale with the page like an <img>
        extra_css += (f"  .band-svg {{ aspect-ratio:{BAND_W}/{BAND_H}; height:auto; "
                      "overflow:visible; }\n")

    html_out = f"""<!doctype html>
<html lang="{T("html_lang")}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(page_title)}</title>
<style>
  :root {{
    --ink:#4A4458; --dim:#575066; --hot:#FF8B7B; --hot-ink:#C43D28;
    --road:#f0e2c4; --road-edge:#dcc9a2;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  html {{ background:#6fbdbd; }}
  body {{ color:var(--ink);
    font-family:"PingFang SC","Hiragino Sans GB","Arial Rounded MT Bold",system-ui,sans-serif;
    background:transparent; overflow-x:clip; }}
  /* every chapter paints its own slice; --from/--to are chained so the seams
     between chapters are the same colour — the page reads as one landscape */
  .chap {{ position:relative; z-index:1; padding:0 0 40px;
    background:linear-gradient(180deg, var(--from) 0%, var(--to) 100%); }}
  a {{ color:inherit; }}
  .dim {{ font-size:.85em; color:var(--dim); }}
  sup {{ font-size:8px; color:var(--dim); }}
  .row .t sup {{ margin-left:1px; vertical-align:top; line-height:1.1; }}
  .ic {{ width:1em; height:1em; fill:none; stroke:currentColor; stroke-width:2;
    stroke-linecap:round; stroke-linejoin:round; vertical-align:-0.12em; }}
  .ic.warn {{ color:var(--hot-ink); }}
  :focus-visible {{ outline:3px solid var(--hot-ink); outline-offset:3px; border-radius:6px; }}
  .dots a:focus-visible {{ outline-offset:2px; }}

  #world {{ position:relative; }}
  /* each chapter/sky paints its own gradient, then its own slice of the road
     (viewBox is a window onto the ONE world-coordinate path → auto-clipped),
     then the content on top */
  svg.road-layer {{ position:absolute; inset:0; width:100%; height:100%; z-index:0;
    pointer-events:none; }}

  /* ---------- sky / hero ---------- */
  .sky {{ position:relative; min-height:100svh; display:flex; flex-direction:column;
    align-items:center; justify-content:center; z-index:1;
    background:linear-gradient(180deg, #fbe3e0 0%, #f3e6df 42%, #dcefe6 100%); }}
  .sky h1, .sky .sub {{ position:relative; z-index:1; }}
  .sky h1 {{ margin:0; line-height:0; }}
  .sky .title {{ width:min(420px,72vw); filter:drop-shadow(0 14px 18px rgba(74,68,88,.2)); }}
  .sky .sub {{ margin-top:18px; font-size:clamp(12px,1.6vw,14px); letter-spacing:.3em;
    color:var(--ink); opacity:.65; font-weight:600; }}
{title_css}{extra_css}  /* clouds are clay now too (same sheet as the props), drifting slowly */
  .cloud {{ position:absolute; pointer-events:none;
    filter:drop-shadow(0 16px 20px rgba(74,68,88,.14)); }}
  .c1 {{ width:clamp(150px,19vw,250px); top:11%; left:8%;
    animation:drift 10s ease-in-out infinite alternate; }}
  .c2 {{ width:clamp(100px,13vw,180px); top:23%; right:7%;
    animation:drift 12s ease-in-out infinite alternate -4s; }}
  .c3 {{ width:clamp(70px,9vw,120px); bottom:19%; left:19%; opacity:.92;
    animation:drift 14s ease-in-out infinite alternate -7s; }}
  @keyframes drift {{ to {{ transform:translateX(28px); }} }}
  /* landscape furniture: absolutely placed at the page edges, never over text
     (hidden once the viewport gets too narrow to have edges) */
  .deco {{ position:absolute; pointer-events:none; z-index:1;
    filter:drop-shadow(0 16px 16px rgba(74,68,88,.22)); }}
  .balloon {{ width:clamp(66px,8vw,110px); top:7%; right:15%;
    animation:bob2 7s ease-in-out infinite alternate; }}
  @keyframes bob2 {{ to {{ transform:translateY(-16px); }} }}
  @media (max-width:1280px) {{ .chap .deco {{ display:none; }} }}
  .bus {{ position:absolute; z-index:2; width:clamp(90px,12vw,150px);
    filter:drop-shadow(6px 10px 10px rgba(74,68,88,.25)); }}

  /* ---------- bands / zones ---------- */
  .band {{ display:block; width:100%; height:auto; position:relative; z-index:2;
    pointer-events:none; margin:-6% 0 -1%; }}
  /* the first band opens the world right at the fold — no half-mountain peeking
     into the hero, and nothing overlaps the bus parked above it */
  .chap:first-of-type > .band {{ margin-top:0; }}
  .chap > .day:first-of-type {{ padding-top:34px; }}

  /* ---------- day sections ---------- */
  /* bottom spacing lives in padding (not margin) so a module capture, which
     measures scrollHeight, keeps room for the mist's resting shadow */
  .day {{ position:relative; z-index:1; max-width:1140px; margin:0 auto 26px;
    padding:0 clamp(16px,4vw,40px) 34px; display:grid;
    grid-template-columns:minmax(0,5fr) minmax(0,6fr); gap:24px; }}
  .day.sideR {{ grid-template-columns:minmax(0,6fr) minmax(0,5fr); }}
  .day.sideR .float-head {{ order:2; }}
  .day.sideR .mist {{ order:1; }}
  .stone {{ position:absolute; top:6px; width:58px; height:50px; z-index:2;
    display:flex; align-items:center; justify-content:center;
    font-family:ui-monospace,Menlo,monospace; font-weight:800; font-size:17px;
    color:rgba(74,68,88,.75);
    background:var(--pb); border-radius:46% 54% 52% 48% / 58% 52% 48% 42%;
    box-shadow:inset 3px 5px 8px rgba(255,255,255,.65),
      inset -3px -5px 8px rgba(74,68,88,.14), 0 10px 16px rgba(74,68,88,.22); }}
  .sideL .stone {{ left:clamp(4px,3vw,30px); }}
  .sideR .stone {{ right:clamp(4px,3vw,30px); }}

  .float-head {{ display:flex; gap:18px; align-items:flex-start; padding-top:26px; }}
  .figurine {{ flex:0 0 auto; max-width:clamp(110px,14vw,170px); max-height:190px;
    filter:drop-shadow(0 14px 14px rgba(74,68,88,.28)); rotate:-2deg; }}
  .sideR .figurine {{ rotate:2deg; }}
  .float-head h2 .h-theme {{ display:block; }}
  .daytag {{ display:inline-block; font-size:11px; font-weight:800; letter-spacing:.12em;
    background:rgba(255,253,246,.8); border-radius:999px; padding:4px 13px;
    box-shadow:0 6px 12px rgba(74,68,88,.12); }}
  .float-head h2 {{ font-size:clamp(30px,4vw,44px); font-weight:900; letter-spacing:.06em;
    margin:10px 0 6px; color:var(--ink);
    text-shadow:0 2px 0 rgba(255,255,255,.65), 0 10px 20px rgba(74,68,88,.22); }}
  .lbl {{ font-size:13px; font-weight:600; color:var(--ink); opacity:.72; max-width:26em;
    text-shadow:0 1px 0 rgba(255,255,255,.5); }}
  .sun {{ font-size:11.5px; color:var(--ink); opacity:.6; margin-top:5px; }}

  /* a slab of clay pressed onto the land: hand-squeezed corners (same family
     as the milestone stones), lit top-left, resting shadow below */
  .mist {{ position:relative; padding:30px 34px 26px;
    background:rgba(255,253,247,.93);
    border-radius:38px 52px 42px 56px / 50px 40px 54px 44px;
    box-shadow:inset 5px 7px 12px rgba(255,255,255,.95),
      inset -5px -8px 14px rgba(74,68,88,.10),
      0 22px 34px rgba(74,68,88,.16); }}

  .row {{ display:flex; gap:11px; padding:6px 2px; font-size:13px; line-height:1.7;
    border-bottom:1px dashed rgba(74,68,88,.1); }}
  .row:last-of-type {{ border-bottom:none; }}
  /* hand-squeezed like the milestone stones — not the family's 999px capsule */
  .row .t {{ flex:0 0 96px; text-align:center; font-size:11px; font-weight:800;
    font-family:ui-monospace,Menlo,monospace; background:rgba(255,255,255,.88);
    border-radius:46% 54% 52% 48% / 58% 52% 48% 42%; padding:5px 6px;
    align-self:flex-start; margin-top:1px;
    box-shadow:inset 1px 2px 4px rgba(255,255,255,.95),
      inset -1px -2px 4px rgba(74,68,88,.10), 0 3px 6px rgba(74,68,88,.10);
    white-space:nowrap; }}
  .k-anchor .t {{ background:var(--hot-ink); color:#fff; }}
  .k-meal .t {{ background:#f7e7c8; }}
  .k-hop .w, .k-free .w {{ color:var(--dim); font-size:12.5px; }}
  .w {{ min-width:0; overflow-wrap:anywhere; }}
  .tag {{ font-size:10px; font-weight:800; background:rgba(255,255,255,.9);
    border-radius:999px; padding:1px 8px; margin-left:5px; white-space:nowrap;
    box-shadow:0 2px 5px rgba(74,68,88,.1); }}
  .tag.hot {{ background:var(--hot-ink); color:#fff; }}
  .rownav {{ display:inline-flex; align-items:center; justify-content:center;
    min-width:44px; min-height:44px; margin:-13px -8px -13px 0; color:#3f6e67;
    vertical-align:middle; }}

  .pills {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:12px; }}
  .npill {{ font-size:11.5px; font-weight:700; }}
  .npill summary, .npill.solo {{ list-style:none; cursor:pointer; display:inline-flex;
    align-items:center; gap:6px; background:rgba(255,255,255,.85); border-radius:999px;
    padding:6px 14px; box-shadow:inset 0 1px 3px rgba(255,255,255,.9),
      0 4px 8px rgba(74,68,88,.1); }}
  .npill summary::-webkit-details-marker {{ display:none; }}
  .npill p {{ background:rgba(255,255,255,.85); border-radius:18px; padding:10px 14px;
    margin-top:6px; font-size:12px; font-weight:400; line-height:1.7; }}
  .mapfold {{ flex-basis:100%; font-size:11.5px; font-weight:700; }}
  .mapfold summary {{ list-style:none; cursor:pointer; display:inline-flex; gap:6px;
    align-items:center; background:rgba(255,255,255,.85); border-radius:999px;
    padding:6px 14px; box-shadow:0 4px 8px rgba(74,68,88,.1); }}
  .mapfold summary::-webkit-details-marker {{ display:none; }}
  .map-embed {{ margin-top:10px; border-radius:22px; overflow:hidden; }}
  .map-embed iframe {{ display:block; width:100%; height:300px; border:0; }}
  .map-ph {{ padding:16px; font-size:12px; color:var(--dim); text-align:center;
    background:rgba(255,255,255,.6); }}

  /* ---------- dots nav ---------- */
  /* the navigation IS the road: a 1/12-scale copy of the same world path,
     with the stones as the hit targets. No other theme can do this. */
  .roadnav {{ position:fixed; top:14px; left:50%; translate:-50% 0; z-index:50;
    width:min(430px, calc(100vw - 28px)); height:62px; padding:7px 86px 7px 12px;
    background:rgba(255,253,246,.74); backdrop-filter:blur(10px);
    border-radius:28px 34px 30px 36px / 34px 28px 36px 30px;
    box-shadow:0 10px 24px rgba(74,68,88,.16); }}
  .roadnav svg {{ display:block; width:100%; height:100%; overflow:visible; }}
  .roadnav .rn-stone {{ cursor:pointer; }}
  .roadnav .rn-stone circle {{ transition:r .2s ease, fill .2s ease; }}
  .roadnav .rn-stone:focus-visible {{ outline:3px solid var(--hot-ink);
    outline-offset:2px; border-radius:50%; }}
  .rn-num {{ font:800 8.5px ui-monospace,Menlo,monospace; fill:rgba(74,68,88,.78);
    text-anchor:middle; dominant-baseline:central; pointer-events:none;
    transition:fill .2s ease; }}
  .rn-bus {{ pointer-events:none; transition:transform .55s cubic-bezier(.45,1.4,.4,1);
    filter:drop-shadow(0 3px 3px rgba(74,68,88,.32)); }}
  /* no-JS / print fallback: the plain numbered anchors */
  .rn-fallback {{ display:inline-flex; align-items:center; justify-content:center;
    min-width:30px; min-height:30px; font-size:12px; font-weight:800;
    text-decoration:none; color:var(--ink); }}
  .js .roadnav .rn-fallback {{ display:none; }}

  /* ---------- export beans ---------- */
  /* share-to-PNG chips speak the theme's shape language: little hand-pinched
     clay pellets (same squeeze as the milestone stones). The day bean rides in
     the row of note pellets at the foot of its mist slab — in flow, so it can
     never land on top of anything — and it rests at FULL strength: one warm
     apricot pellet among the white ones is impossible to miss while still
     smaller and quieter than every heading on the page. Hover presses it into
     the clay (the lighting flips, the resting shadow collapses). */
  .xbtn {{ position:relative; margin-left:auto; align-self:center;
    border:0; cursor:pointer; font-family:inherit; font-size:11px; font-weight:800;
    letter-spacing:.1em; color:#453F52; padding:8px 15px; background:#f3ce62;
    rotate:-2deg; border-radius:44% 56% 48% 52% / 62% 48% 52% 38%;
    box-shadow:inset 2px 3px 5px rgba(255,255,255,.85),
      inset -2px -3px 6px rgba(150,110,26,.30), 0 8px 14px rgba(74,68,88,.22);
    transition:rotate .2s ease, translate .2s ease, box-shadow .2s ease; }}
  /* the thumb print: where the finger pressed, the clay stayed shiny */
  .xbtn::before {{ content:""; position:absolute; left:13%; top:15%;
    width:32%; height:30%; border-radius:50%; pointer-events:none;
    background:radial-gradient(closest-side, rgba(255,255,255,.72), rgba(255,255,255,0)); }}
  .xbtn:hover, .xbtn:focus-visible {{ rotate:1deg; translate:0 2px;
    background:#eec552;
    box-shadow:inset 3px 4px 7px rgba(150,110,26,.36),
      inset -2px -3px 5px rgba(255,255,255,.55), 0 3px 6px rgba(74,68,88,.16); }}
  .sideR .xbtn {{ rotate:2deg; }}
  .sideR .xbtn:hover, .sideR .xbtn:focus-visible {{ rotate:-1deg; }}
  #appendix {{ position:relative; padding:6px 0 30px; }}
  .xrow {{ position:relative; z-index:1; max-width:880px; margin:0 auto 4px;
    padding:0 clamp(16px,4vw,40px); display:flex; justify-content:flex-end; }}
  /* the whole-page bean lives at the end of the mini road, an apricot pebble */
  .x-page {{ position:absolute; top:50%; right:8px; translate:0 -50%; margin:0;
    width:70px; height:36px; padding:0; letter-spacing:.02em; background:#f4b183;
    rotate:3deg; border-radius:46% 54% 40% 60% / 56% 44% 58% 42%; }}
  .x-page::before {{ left:16%; top:14%; width:30%; height:32%; }}
  .x-page:hover, .x-page:focus-visible {{ rotate:-3deg; background:#efa872;
    translate:0 calc(-50% + 2px); }}

  /* ---------- appendix ---------- */
  .appx {{ position:relative; z-index:1; max-width:880px; margin:0 auto 40px;
    padding:0 clamp(16px,4vw,40px); }}
  .appx h2 {{ font-size:18px; font-weight:900; letter-spacing:.06em; margin-bottom:10px; }}
  .appx .row .t {{ flex-basis:100px; white-space:normal; }}
  .total {{ margin-top:12px; background:var(--hot-ink); color:#fff; font-weight:800;
    font-size:13.5px; border-radius:999px; padding:9px 18px; display:inline-block;
    box-shadow:0 8px 16px rgba(196,61,40,.3); }}
  details.sub {{ margin-top:8px; font-size:13px; }}
  details.sub summary {{ cursor:pointer; font-weight:800; list-style:none;
    background:rgba(255,255,255,.75); border-radius:16px; padding:8px 14px;
    box-shadow:0 3px 8px rgba(74,68,88,.08); }}
  details.sub summary::-webkit-details-marker {{ display:none; }}
  details.sub p, details.sub ul, details.sub ol {{ padding:8px 12px 4px 18px;
    line-height:1.85; }}
  ul.warn li {{ margin-top:5px; }}
  input[type=checkbox] {{ accent-color:var(--hot); margin-right:4px; }}

  footer {{ position:relative; z-index:1; text-align:center; font-size:11px;
    color:rgba(255,255,255,.85); padding:10px 16px 46px; line-height:2;
    text-shadow:0 1px 3px rgba(0,60,60,.3); }}

  .js .reveal {{ opacity:0; transform:translateY(24px);
    transition:opacity .7s ease, transform .7s ease; }}
  .reveal.in {{ opacity:1; transform:none; }}
  section[id] {{ scroll-margin-top:60px; }}
  @media (prefers-reduced-motion:reduce) {{
    .reveal {{ opacity:1; transform:none; transition:none; }}
    .rn-bus, .deco, .cloud {{ transition:none; animation:none; }}
    html {{ scroll-behavior:auto; }}
  }}

  @media (max-width:860px) {{
    .day, .day.sideR {{ grid-template-columns:1fr; gap:12px; }}
    .day.sideR .float-head {{ order:1; }}
    .day.sideR .mist {{ order:2; }}
    .stone {{ top:-8px; }}
    .tag {{ white-space:normal; }}
    .row .t {{ flex-basis:88px; }}
    .appx .row .t {{ flex-basis:80px; }}
    .float-head {{ padding-top:34px; }}
    .figurine {{ max-width:96px; }}
    .sky {{ min-height:100svh; }}   /* hero owns the whole first screen on phones too */
    /* the roadnav ends in the 生成长图 pebble, which reaches further right than
       the old 存 one — drop the balloon below the nav so nothing sits under it */
    .balloon {{ top:14%; }}
    .band {{ margin:-14px 0 -4px; }}
  }}
  @media print {{
    body {{ background:#fff; }}
    svg.road-layer, .roadnav svg, .mapfold, .cloud, .bus, .deco,
    .xbtn, .xrow {{ display:none; }}
    .mist {{ background:#fff; box-shadow:none; }}
    .k-anchor .t, .tag.hot, .total {{ -webkit-print-color-adjust:exact;
      print-color-adjust:exact; }}
    footer {{ color:#123033; text-shadow:none; }}
    .chap, html {{ background:#fff; }}
    .band {{ display:none; }}
    .reveal {{ opacity:1; transform:none; }}
    .day {{ break-inside:avoid-page; }}
  }}
</style>
</head>
<body>
<nav class="roadnav" id="roadnav" aria-label="{esc(t("roadnav"))}">{dots}<button
  class="xbtn x-page no-export" data-x-page
  title="{esc(t("save_page.title"))}">{esc(T("btn.save_page"))}</button></nav>

<div id="world">
<header class="sky" id="top" data-road-start>
  {img(deco["clay-cloud-a"], "cloud c1")}
  {img(deco["clay-cloud-b"], "cloud c2")}
  {img(deco["clay-cloud-c"], "cloud c3")}
  {img(deco["clay-balloon"], "deco balloon")}
  <h1 class="claytitle">{title_html}</h1>{en_html}
  {sub_html}{credit_html}
  {img(bus, "bus", ' style="bottom:9%; left:9%;"')}
</header>

{assembled}

<div class="chap z-deep" style="--from:{deep_from};--to:{DEEP_TO}">
<div id="appendix">
<div class="xrow no-export"><button class="xbtn x-appx" data-x-for="#appendix"
  data-x-label="{esc(T("label.appendix"))}"
  title="{esc(t("save_appx.title"))}">{esc(T("btn.save_appendix"))}</button></div>
{appendix(p, meta.get("budget_total", ""), brief_titles(art))}
</div>{end_html}
<footer data-road-end>
  {esc(meta.get("party",""))} · {esc(t("fx"))} {esc(meta.get("fx",""))}<br>
  {esc(t("foot"))}
</footer>
</div>
</div>

<script>
(function () {{
  document.documentElement.classList.add('js');
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* the export clone cannot resolve 100svh (in an SVG image document the
     viewport is the whole 16k-px capture), so the live viewport height is
     frozen into a var on #world; the capture-only CSS pins .sky to it */
  var worldEl = document.getElementById('world');
  var setVh = function () {{
    worldEl.style.setProperty('--vh', innerHeight + 'px');
  }};
  setVh(); addEventListener('resize', setVh);

  /* ---- winding clay road: one world path, sliced into every layer ---- */
  var NS = 'http://www.w3.org/2000/svg';
  function drawRoad() {{
    var world = document.getElementById('world');
    var W = world.clientWidth;
    var wr = world.getBoundingClientRect();
    var absY = function (el, frac) {{
      var r = el.getBoundingClientRect();
      return r.top - wr.top + r.height * (frac || 0);
    }};
    var pts = [];
    var sky = document.querySelector('.sky');
    pts.push([W * 0.30, absY(sky, 0.86)]);
    document.querySelectorAll('[data-road-anchor]').forEach(function (s) {{
      var stone = s.querySelector('.stone');
      if (!stone) return;
      var r = stone.getBoundingClientRect();
      pts.push([r.left - wr.left + r.width / 2, r.top - wr.top + r.height / 2]);
    }});
    var foot = document.querySelector('footer');
    pts.push([W * 0.5, absY(foot) + 20]);

    // each layer only carries the road segments inside its own window —
    // a single world-length path in every svg makes the raster bounds huge
    // (12k+ px), which kills compositors. World coords stay; content shrinks.
    function segD(top, bottom) {{
      var m = 90, out = '', open = false;
      for (var i = 1; i < pts.length; i++) {{
        var p0 = pts[i - 1], p1 = pts[i];
        var lo = Math.min(p0[1], p1[1]), hi = Math.max(p0[1], p1[1]);
        if (hi < top - m || lo > bottom + m) {{ open = false; continue; }}
        var my = (p0[1] + p1[1]) / 2;
        if (!open) {{ out += 'M' + p0[0] + ',' + p0[1]; open = true; }}
        out += ' C' + p0[0] + ',' + my + ' ' + p1[0] + ',' + my
             + ' ' + p1[0] + ',' + p1[1];
      }}
      return out;
    }}

    drawNav(pts, W);
    var roadW = innerWidth < 860 ? 30 : 44;
    // [width, colour, dash, dy, opacity] — a clay coil pressed onto the land:
    // stacked soft shadows (cheap fake blur — a real filter blows the GPU),
    // dark under-edge, rim, road fill, top bevel light, white dashes.
    var strokes = [[roadW + 18, 'rgba(74,68,88,.06)', 0, 8, 1],
                   [roadW + 10, 'rgba(74,68,88,.09)', 0, 8, 1],
                   [roadW + 4, 'rgba(74,68,88,.11)', 0, 7, 1],
                   [roadW + 9, '#d2bb8e', 0, 2.5, 1],
                   [roadW + 8, '#dcc9a2', 0, 0, 1],
                   [roadW, '#f0e2c4', 0, 0, 1],
                   [roadW * .44, '#fbf3dd', 0, -roadW * .17, .9],
                   [3.5, 'rgba(255,255,255,.95)', '16 22', 0, 1]];
    document.querySelectorAll('.sky, .chap').forEach(function (layer) {{
      var svg = layer.querySelector('svg.road-layer');
      if (!svg) {{
        svg = document.createElementNS(NS, 'svg');
        svg.setAttribute('class', 'road-layer');
        svg.setAttribute('aria-hidden', 'true');
        svg.setAttribute('preserveAspectRatio', 'none');
        layer.insertBefore(svg, layer.firstChild);
      }}
      var top = absY(layer);
      svg.setAttribute('viewBox', '0 ' + top + ' ' + W + ' ' + layer.offsetHeight);
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      var dSeg = segD(top, top + layer.offsetHeight);
      if (!dSeg) return;
      strokes.forEach(function (st) {{
        var path = document.createElementNS(NS, 'path');
        path.setAttribute('d', dSeg);
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke', st[1]);
        path.setAttribute('stroke-width', st[0]);
        path.setAttribute('stroke-linecap', 'round');
        if (st[2]) path.setAttribute('stroke-dasharray', st[2]);
        if (st[3]) path.setAttribute('transform', 'translate(0,' + st[3] + ')');
        if (st[4] !== 1) path.setAttribute('opacity', st[4]);
        svg.appendChild(path);
      }});
    }});
  }}
  var rt;
  var redraw = function (ms) {{ clearTimeout(rt); rt = setTimeout(drawRoad, ms || 120); }};
  // a ResizeObserver on the world catches viewport changes AND <details> toggles
  if (window.ResizeObserver) {{
    new ResizeObserver(function () {{ redraw(); }}).observe(document.getElementById('world'));
  }} else {{
    addEventListener('resize', function () {{ redraw(180); }});
  }}
  // toggle does not bubble — listen in the capture phase
  document.addEventListener('toggle', function (e) {{
    if (e.target.tagName === 'DETAILS') redraw(60);
  }}, true);
  addEventListener('load', function () {{ redraw(0); }});
  try {{ drawRoad(); }} catch (e) {{ /* decoration only */ }}

  /* ---- the road, again, as the navigation ---- */
  var nav = document.getElementById('roadnav');
  var navSvg = null, navStones = [], navPts = [], navBus = null, navIdx = 0;
  function setActive(idx) {{
    navIdx = idx;
    navStones.forEach(function (s, n) {{
      s[0].setAttribute('r', n === idx ? '9.5' : '8');
      s[0].setAttribute('fill', n === idx ? '#C43D28' : '#f2b28c');
      s[1].setAttribute('fill', n === idx ? '#fff' : 'rgba(74,68,88,.78)');
    }});
    // the little bus drives the mini road to wherever you are reading
    if (navBus && navPts[idx]) {{
      navBus.style.transform = 'translate(' + (navPts[idx][0] - 15) + 'px,'
        + (navPts[idx][1] - 24) + 'px)';
    }}
  }}
  function drawNav(pts, W) {{
    if (!nav || pts.length < 3) return;
    if (!navSvg) {{
      navSvg = document.createElementNS(NS, 'svg');
      nav.insertBefore(navSvg, nav.firstChild);
    }}
    // viewBox aspect mirrors the rendered box → uniform scale, round stones,
    // upright numbers (preserveAspectRatio:none would squash the digits)
    var box = navSvg.getBoundingClientRect();
    var NW = 300, NH = box.width ? Math.round(300 * box.height / box.width) : 48;
    navSvg.setAttribute('viewBox', '0 0 ' + NW + ' ' + NH);
    while (navSvg.firstChild) navSvg.removeChild(navSvg.firstChild);
    // x = progress through the trip, y = the road's own left/right swing:
    // the same journey, read sideways
    var mid = pts.slice(1, -1);
    var n = mid.length, P = mid.map(function (pt, i) {{
      return [16 + (NW - 32) * (n < 2 ? 0.5 : i / (n - 1)),
              NH / 2 + 2.5 + (pt[0] / W - 0.5) * NH * 0.5];
    }});
    navPts = P;
    var d2 = 'M' + P[0][0] + ',' + P[0][1];
    for (var i = 1; i < P.length; i++) {{
      var a = P[i - 1], b = P[i], mx = (a[0] + b[0]) / 2;
      d2 += ' C' + mx + ',' + a[1] + ' ' + mx + ',' + b[1] + ' ' + b[0] + ',' + b[1];
    }}
    // same extrusion recipe as the big road, one octave down
    [[11, '#d2bb8e', 1.5], [10, '#dcc9a2', 0], [7, '#f0e2c4', 0]].forEach(function (st) {{
      var path = document.createElementNS(NS, 'path');
      path.setAttribute('d', d2); path.setAttribute('fill', 'none');
      path.setAttribute('stroke', st[1]); path.setAttribute('stroke-width', st[0]);
      path.setAttribute('stroke-linecap', 'round');
      if (st[2]) path.setAttribute('transform', 'translate(0,' + st[2] + ')');
      navSvg.appendChild(path);
    }});
    navStones = [];
    P.forEach(function (pt, i) {{
      var a = document.createElementNS(NS, 'a');
      a.setAttribute('href', '#d' + (i + 1));
      a.setAttribute('class', 'rn-stone');
      a.setAttribute('aria-label', '{t("day_n.pre")}' + (i + 1) + '{t("day_n.post")}');
      var hit = document.createElementNS(NS, 'circle');
      hit.setAttribute('cx', pt[0]); hit.setAttribute('cy', pt[1]);
      hit.setAttribute('r', '13'); hit.setAttribute('fill', 'transparent');
      var c = document.createElementNS(NS, 'circle');
      c.setAttribute('cx', pt[0]); c.setAttribute('cy', pt[1]);
      c.setAttribute('r', '8'); c.setAttribute('fill', '#f2b28c');
      c.setAttribute('stroke', 'rgba(74,68,88,.3)'); c.setAttribute('stroke-width', '1.4');
      var t = document.createElementNS(NS, 'text');
      t.setAttribute('x', pt[0]); t.setAttribute('y', pt[1]);
      t.setAttribute('class', 'rn-num');
      t.textContent = i + 1;
      a.appendChild(hit); a.appendChild(c); a.appendChild(t); navSvg.appendChild(a);
      navStones.push([c, t]);
    }});
    navBus = document.createElementNS(NS, 'image');
    var heroBus = document.querySelector('.bus');
    if (heroBus) navBus.setAttribute('href', heroBus.getAttribute('src'));
    navBus.setAttribute('width', '30'); navBus.setAttribute('height', '20');
    navBus.setAttribute('preserveAspectRatio', 'xMidYMid meet');
    navBus.setAttribute('class', 'rn-bus');
    navSvg.appendChild(navBus);
    setActive(navIdx);
  }}

  /* ---- scrollspy ---- */
  var links = [].slice.call(document.querySelectorAll('.roadnav a[data-spy]'));
  var spy = new IntersectionObserver(function (es) {{
    es.forEach(function (e) {{
      if (!e.isIntersecting) return;
      setActive(parseInt(e.target.id.slice(1), 10) - 1);
      links.forEach(function (l) {{
        l.classList.toggle('active', l.getAttribute('data-spy') === e.target.id);
      }});
    }});
  }}, {{ rootMargin: '-30% 0px -60% 0px' }});
  links.forEach(function (l) {{
    var t = document.getElementById(l.getAttribute('data-spy'));
    if (t) spy.observe(t);
  }});

  /* ---- reveal ---- */
  if (reduce) {{
    document.querySelectorAll('.reveal').forEach(function (n) {{ n.classList.add('in'); }});
  }} else {{
    var rev = new IntersectionObserver(function (es) {{
      es.forEach(function (e) {{
        if (e.isIntersecting) {{ e.target.classList.add('in'); rev.unobserve(e.target); }}
      }});
    }}, {{ rootMargin: '0px 0px -6% 0px' }});
    document.querySelectorAll('.reveal').forEach(function (n) {{ rev.observe(n); }});
  }}

  /* ---- lazy map embeds ---- */
  document.querySelectorAll('details.mapfold').forEach(function (d) {{
    d.addEventListener('toggle', function () {{
      if (!d.open) return;
      var box = d.querySelector('.map-embed');
      if (!box || box.dataset.done) return;
      box.dataset.done = '1';
      var f = document.createElement('iframe');
      f.src = box.dataset.src;
      f.addEventListener('load', function () {{
        var ph = box.querySelector('.map-ph'); if (ph) ph.remove();
      }});
      box.appendChild(f);
    }});
  }});
}})();
</script>
<script>
EXPORT_JS_PLACEHOLDER
</script>
</body>
</html>"""
    # The lucide sprite would sit outside #world and outside every module
    # clone, so <use href="#i-…"> resolves to nothing inside an export capture
    # and every icon silently vanishes from the PNG (probed 2026-08-14).
    # Expand each reference into its inline path body and ship no sprite.
    html_out = re.sub(
        r'<svg class="([^"]*)" aria-hidden="true"><use href="#i-([a-z]+)"/></svg>',
        lambda m: (f'<svg class="{m.group(1)}" viewBox="0 0 24 24" '
                   f'aria-hidden="true">{LUCIDE[m.group(2)]}</svg>'),
        html_out)
    assert "<use href" not in html_out, "un-expanded sprite reference left behind"

    # PNG-export engine (theme_common). Capture-only CSS in order:
    #   · force every scroll-reveal state visible (module clones are captured
    #     before the IntersectionObserver ever saw them);
    #   · pin .sky to the frozen live viewport height (svh is meaningless
    #     inside the SVG image document — it would balloon to the page height);
    #   · iframes cannot rasterise inside an SVG image, keep the box, blank it;
    #   · per-day chapter-gradient slices + the chapter-first padding mirror,
    #     scoped to .__xbody> so only module clones repaint their ground.
    html_out = html_out.replace("EXPORT_JS_PLACEHOLDER", export_js(
        theme_name(THEME), "#6fbdbd",
        extra_css=(".reveal{opacity:1!important;transform:none!important}"
                   ".__xbody .sky{min-height:0!important;height:var(--vh,900px)!important}"
                   ".__xbody .map-embed iframe{visibility:hidden!important}"
                   # the SVG-image rasteriser drops text-decoration and draws
                   # platform checkboxes; swap in layout-safe lookalikes
                   ".__xbody a:not(.rownav){text-decoration:none!important;"
                   "border-bottom:1.5px solid currentColor}"
                   ".__xbody input[type=checkbox]{appearance:none;"
                   "-webkit-appearance:none;width:13px;height:13px;"
                   "border:1.5px solid rgba(74,68,88,.75);border-radius:4px;"
                   "background:#fff;vertical-align:-2px;margin-right:4px}"
                   + "".join(xbg) +
                   f".__xbody>#appendix{{background:linear-gradient(180deg,{deep_from},#63b5b8)}}"
                   # a captured module is its own picture, not a slice of the
                   # scroll: without margins the stone badge and the figurine
                   # sit flush on the crop edge and the card reads as guillotined
                   ".__xbody>.day{padding:34px 30px 40px!important;"
                   "max-width:none!important;margin:0!important;"
                   "border-radius:26px}"
                   ".__xbody>.day>.stone{top:34px!important}"),
        page_root="#world", file_prefix=export_prefix(art, meta, THEME)))
    out = pathlib.Path(args.out)
    out.write_text(html_out, encoding="utf-8")
    print(f"{out.name}: {out.stat().st_size//1024}KB, days={len(days)}, assets={asset_count()}")


if __name__ == "__main__":
    main()
