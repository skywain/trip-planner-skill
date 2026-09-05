#!/usr/bin/env python3
"""Journal-collage theme renderer — 手账拼贴版.

Identity (four axes, per the theme-system manual):
  * organising principle — ONE spread-open vintage travel journal: a single
    continuous sheet of aged rice/kraft paper (CSS gradient chain + noise
    tile), never a grid of floating cards;
  * interaction — vertical scroll; one fountain-pen dashed route meanders
    down the page spine through all 11 days; brass push-pins 01–11 are the
    anchors and the navigation objects;
  * type voice — Kaiti (楷体) handwriting for titles and annotations, a
    typewriter monospace for clock digits, and Caveat (an embedded OFL
    variable webfont, wght 400-700) for the English handwritten asides,
    with the platform cursive stack as fallback;
  * shape language — torn paper edges, washi tape laid at an angle, ticket
    stubs / postage stamps / postmarks / a wax seal; blocks carry ≤1deg of
    rotation so body text stays readable.

Usage: python3 render_journal.py <plan.geo.json> [--art <file>|none] [--assets DIR ...] -o out.html

ART CONTRACT (what this renderer reads from the trip's art.json — schema in
ART-SCHEMA.md — and how it degrades when a field is missing; the renderer
never carries a place, a date or a picture name of its own):

  common (themes.journal.cover.* overrides cover.* per key — the poem title
  is per theme, so zh/sub/credit normally live in the journal block)
    cover.zh          the cover <h1> — the big Kaiti display word. Sized by
                      character count: 2-3 chars = full size, 4 = a notch
                      down, 5-6 = smaller, ≥7 = shrunk to fit one line
                      (container-query clamp; a title never folds).
                      → falls back to cover.kick, then "旅行手账"
    cover.sub         cover copy under the dates ("\\n" = line break) → none
    cover.credit      small allusion/source line under the copy → none
    cover.kick        <title> prefix + export filename prefix ONLY (never
                      the h1); on an en page cover.kick_en wins when set
                      (theme_common.title_kick)        → cover.zh, then "旅行手账"
    cover.postmark_date  the COVER postmark + ghost "first day of issue"
                      (day postmarks always use the day's date) → days[0].date
    end.date          endcap postmark date             → no endcap postmark
    end.mark          CAPS city on the endcap postmark → blank ring
    end.line / .fine  hand-written closing line / fine print → not written
    end.farewell      2nd line of the TRIP COMPLETE chop → "HOMEWARD BOUND"
    days[d].theme     4-char day title                 → the plan's city
    days[d].en        English place line in the head   → omitted
    days[d].mark      CAPS text on the day's postmark  → blank ring
    brief_titles      section titles of the country brief, over the shared
                      theme_common.BRIEF_TITLES      → shared defaults
  themes.journal
    cover.photo       {stem, alt, caption:[zh,en]} cover polaroid → no polaroid
    cover_stamps      [{cls, rot}] postage stamps on the cover (≤3 — the
                      strip shares the corner with the postmark) → postmark only
    stamps            {slot: asset-stem} scans for the 3 stamp SLOTS
                      st-a / st-b (portrait) · st-wide (landscape, wider);
                      the old names st-lib / st-gg / st-bis are permanent
                      ALIASES (art written against them keeps working);
                      a slot with no scan renders nothing wherever it is used
    days[d].photo     polaroid asset stem              → no polaroid
    days[d].caption   [zh, en] under the polaroid      → no figcaption
    days[d].annot     ✎ margin note under the head     → none
    days[d].props     rail collage, list of KIT items  → empty rail
    days[d].photos2   [{stem, en, alt}] extra kodak prints, stacked in the
                      SAME rail column under the day's polaroid, one notch
                      smaller (254 vs 290px), Caveat caption → none
    days[d].doodle    {sketch | svg, note, font, rot} → a generic quip
    days[d].poster    {stem | title, line, alt, rot} in the notes column → none

  PROP KIT (props[].kind — the look is the theme's, the words are the trip's):
    img      {stem, w, rot}            a scanned keepsake (boarding pass, ticket);
                                        w = display width in CSS px, 105-220
                                        is the range that sits well in the rail
    stamp    {cls, rot}                one of the stamp slots above
    vtk      {tone green|brown, lines [name, sub, price, serial], rot}
                                        vintage park-entrance ticket, all CSS
    bagtag   {lines, rot}              luggage tag with monospace text
    seal     {rot}                     the wax seal
    flora    {stem?, w?, rot?}         a pressed flower: no stem = the next one
                                        from the theme's seeded deck; a stem =
                                        that scan (the trip's own pressing —
                                        gets a fl-x* CSS class + data URI like
                                        the deck, w px default 90)
    postcard {stem?, alt, note, rot, stamp:{cls, rot}}
                                        franked postcard — REPLACES the day's prop.
                                        With a stem: that scan; WITHOUT a stem:
                                        a plain linen-textured card (CSS) with
                                        the note hand-written on it, the stamp
                                        slot and the postmark — no picture
    poster   (days[d].poster, not a prop) {stem, alt, line, rot} hangs that
                                        print; {title, line, rot} with NO stem
                                        hangs a CSS kraft-paper vintage poster
                                        frame: title as big Kaiti caps, line
                                        hand-written; tack + fabric tape as ever
  DOODLE SKETCHES (doodle.sketch): skyline · bison · bridge · waves · volcano
    · peaks (ridge + rock pillars) · coral (branch + fish) · palm (palm/fern)
    · train (scenic railway) · cabin (log hut) · ferry (fjord boat)
    · aurora (light bands over pines) — single-line ink drawings, no fills;
    skyline/bison/waves/coral/ferry/aurora also get the curly red arrow.
    doodle.svg {viewBox, d, arrow?} = the trip's OWN single-line drawing in
    the same voice (one <path d>, stroked by the theme, no fill); it wins
    over sketch. No sketch and no svg → the note alone (or, with no note
    either, one of the theme's generic quips).
    note: English short line(s) or "\\n"-broken lines — the box does NOT
    auto-wrap (white-space:nowrap, so CJK never collapses one char per line);
    keep it ≤2 lines and ≤18 chars per line. font: hand | cur.
  Theme-owned, not in art: tapes, washi, pressed-flora deck, stains, the
  page-edge flora rhythm (days 2/5/7/9), the wax seal, luggage tag,
  the AIR MAIL / SUBJECT TO CHANGE / PAID / APPROVED chops, the cover quote,
  the DEPARTED airport chop (from plan legs; type shrinks to fit long names).
"""
import argparse
import base64
import datetime
import pathlib
import random
import re
import urllib.parse

from theme_common import (T, tag_pretty, lang, weekday, theme_name, init_lang,
                          asset_count, brief_titles, data_uri, export_js,
                          export_prefix, day_embed_url, esc, et, ic, load_plan, sprite,
                          Art, load_art, add_art_arg, short_dates, title_kick)

HERE = pathlib.Path(__file__).parent
THEME = "journal"

# ------------------------------------------------------------- theme voice --
# The journal's OWN words (cover fallback, section titles, slip labels, chops'
# tooltips…) per language; everything every theme shares (tags, buttons,
# toasts, 步行/晚点剪法, weekdays) comes from theme_common.T(). zh values are
# the historical literals — the US baseline must stay byte-identical.
L = {
    "zh": {
        "fallback_title": "旅行手账",
        "title_suffix": "手账拼贴版",
        "eyebrow": "一 本 旅 行 手 账",
        "cue": "往下翻",
        "nav_aria": "手账页签",
        "nav_cover": "封", "nav_cover_aria": "回到封面",
        "nav_day_aria": "第{i}天 · {theme}",
        "nav_appx": "附", "nav_appx_aria": "附录:航段住宿预算清单",
        "nav_page_aria": "把整本手账生成一张长图",
        "nav_page_title": "把整本手账存成一张长图,可发朋友圈",
        "save_day_title": "把这一天存成图片,可发朋友圈",
        "save_appx_title": "把附录存成图片,可发朋友圈",
        "travel_day": "移动日",
        "nav_to": "导航到 ",
        "pocket": "路线图袋 · 第 {i} 天",
        "pocket_ph": "地图会在联网展开时贴进这一页;离线请用下面的票根链接。",
        "day_route": "整日路线", "hop_n": "跳 {n}",
        "map_title": "当日路线地图",
        "rain": "下雨就改", "note": "旁注",
        "backup": "备选",
        "th_item": "项目", "th_cost": "费用(每人)", "th_note": "手写旁注", "total": "合计",
        "ddl": "限:",
        "sec_legs": "航段票夹", "sec_hotels": "落脚的地方", "sec_budget": "手写账本",
        "sec_check": "行前清单",
        "seal_legs": "航", "seal_hotels": "宿", "seal_budget": "账", "seal_check": "备",
        "seal_brief": "知", "seal_dec": "断", "seal_unv": "核",
        "legs_sub": "{n}段机票按日期插在这一页 —— 价格是查证当日的,出票前再核。",
        "fx": "汇率",
        "foot_ai": "日出日落数据:sunrise-sunset.org · 照片与贴纸由 AI 生成,仅作手账示意 · 价格以预订渠道实时为准",
    },
    "en": {
        "fallback_title": "Travel Journal",
        "title_suffix": "Journal collage",
        "eyebrow": "A TRAVEL JOURNAL",
        "cue": "turn the page",
        "nav_aria": "journal tabs",
        "nav_cover": "C", "nav_cover_aria": "back to the cover",
        "nav_day_aria": "Day {i} · {theme}",
        "nav_appx": "A", "nav_appx_aria": "appendix: flights, stays, budget, checklist",
        "nav_page_aria": "save the whole journal as one long image",
        "nav_page_title": "Save the whole journal as one long image to share",
        "save_day_title": "Save this day as an image to share",
        "save_appx_title": "Save the appendix as an image to share",
        "travel_day": "travel day",
        "nav_to": "navigate to ",
        "pocket": "Map pocket · Day {i}",
        "pocket_ph": "The map is glued in when this pocket is opened online; offline, use the ticket-stub links below.",
        "day_route": "Full-day route", "hop_n": "Hop {n}",
        "map_title": "Route map for the day",
        "rain": "if it rains", "note": "Note",
        "backup": "Backup",
        "th_item": "Item", "th_cost": "Cost (pp)", "th_note": "Notes", "total": "Total",
        "ddl": "by: ",
        "sec_legs": "Ticket wallet", "sec_hotels": "Where we sleep", "sec_budget": "Handwritten ledger",
        "sec_check": "Pre-trip checklist",
        "seal_legs": "F", "seal_hotels": "S", "seal_budget": "B", "seal_check": "C",
        "seal_brief": "I", "seal_dec": "D", "seal_unv": "V",
        "legs_sub": "{n} flight tickets filed by date on this page — prices are as of the check date; re-check before ticketing.",
        "fx": "FX",
        "foot_ai": "Sun times: sunrise-sunset.org · Photos and stickers are AI-generated, journal illustration only · Prices as live on the booking channel",
    },
}


def t(k):
    return L.get(lang(), L["zh"]).get(k, L["zh"][k])
# every decoration that "randomises" (stain scatter, marginalia pick, washi
# angles) draws from this seeded RNG at BUILD time — the page itself is
# static, so refreshing never re-rolls the mess (Math.random is banned here)
RNG = random.Random(20260925)
ART = Art()        # replaced in main() with the trip's art.json
LEG_BY_DATE = {}   # filled in main(); render_day stamps travel days from it
MON = ["", "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
       "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
NUM_ZH = "零一二三四五六七八九十"

# the three postage-stamp SLOTS of the journal kit (CSS classes; the scans
# they show come from art: themes.journal.stamps). st-wide is the wide one.
# The slots were born as st-lib / st-gg / st-bis (the US trip's Liberty /
# Golden Gate / bison scans); those names stay accepted forever as aliases
# — normalised on the way in, so the HTML/CSS only ever carry the new names.
STAMP_SLOTS = ("st-a", "st-b", "st-wide")
STAMP_ALIAS = {"st-lib": "st-a", "st-gg": "st-b", "st-bis": "st-wide"}


def slot(cls):
    """Canonical stamp-slot name for an art value (alias or new name)."""
    return STAMP_ALIAS.get(cls or "", cls or "")


def stamp_stems():
    """themes.journal.stamps with every key normalised to the new slot names
    (a new-name key wins over an alias pointing at the same slot)."""
    raw = ART.theme(THEME).get("stamps") or {}
    out = {}
    for k, v in raw.items():
        c = slot(k)
        if c in STAMP_SLOTS and (c not in out or k == c):
            out[c] = v
    return out


def stamp_ok(cls):
    """A stamp slot is usable only if art gave it a scan that exists."""
    cls = slot(cls)
    return cls in STAMP_SLOTS and bool(data_uri(stamp_stems().get(cls, "")))


def _rot(v, lo=-4, hi=4):
    """CSS angle text: art's own number verbatim, else a seeded roll."""
    return f"{v}" if v is not None else f"{RNG.uniform(lo, hi):.1f}"


def prop_html(pr):
    """One rail-collage prop from the kit; '' when it cannot be built
    (unknown kind, missing scan) — never a broken image."""
    kind = pr.get("kind", "")
    if kind == "flora":
        return flora_prop(pr)
    if kind == "img":
        uri = data_uri(pr.get("stem", ""))
        if not uri:
            return ""
        w = f";width:{pr['w']}px" if pr.get("w") else ""
        return (f'<img class="prop" src="{uri}" alt="" aria-hidden="true" '
                f'style="--rot:{_rot(pr.get("rot"))}deg{w}">')
    if kind == "stamp":
        cls = slot(pr.get("cls", ""))
        if not stamp_ok(cls):
            return ""
        return (f'<span class="stampd {cls}" aria-hidden="true" '
                f'style="--rot:{_rot(pr.get("rot"))}deg"></span>')
    if kind == "vtk":
        tone = "brown" if pr.get("tone") == "brown" else "green"
        ln = list(pr.get("lines", []))[:4] + [""] * 4
        cells = "".join(f"<{tg}>{esc(t)}</{tg}>"
                        for tg, t in zip(("b", "i", "em", "u"), ln) if t)
        return (f'<span class="vtk vtk-{tone}" aria-hidden="true" '
                f'style="--rot:{_rot(pr.get("rot"))}deg">{cells}</span>')
    if kind == "bagtag":
        txt = "<br>".join(esc(t) for t in pr.get("lines", []))
        return (f'<span class="bagtag" aria-hidden="true" style="--rot:{_rot(pr.get("rot"))}deg">'
                f'<span class="bagtag-txt">{txt}</span></span>')
    if kind == "seal":
        return (f'<span class="sealbg seal-sm" aria-hidden="true" '
                f'style="--rot:{_rot(pr.get("rot"))}deg"></span>')
    return ""

# ---- pressed-flora scatter pool (2 original pressings + 3 wishlist ones) ----
# Every flora placement — day props, page-edge scatter, the cover sprig —
# draws a CSS class (one data URI per stem in the stylesheet, so repeats cost
# no bytes) from ONE seeded shuffled deck, so neighbouring spreads never show
# the same pressing and a rebuild never re-rolls the arrangement.
FL_CLS = {
    "journal-flower-a": "fl-a", "journal-flower-b": "fl-b",
    "journal-flora-daisy": "fl-daisy", "journal-flora-fern": "fl-fern",
    "journal-flora-maple": "fl-maple",
}
FLORA_W = {  # display width per stem (px) — pressings are small keepsakes
    "journal-flower-a": 66, "journal-flower-b": 74,
    "journal-flora-daisy": 74, "journal-flora-fern": 92,
    "journal-flora-maple": 88,
}
_FLORA_DECK = RNG.sample(list(FL_CLS), len(FL_CLS))
_flora_i = [0]


def next_flora():
    s = _FLORA_DECK[_flora_i[0] % len(_FLORA_DECK)]
    _flora_i[0] += 1
    return s


# page-edge flora rhythm by day NUMBER (theme's layout beat, not the trip's);
# the rail-prop pressings are art's call: props=[{"kind":"flora"}]
FLORA_EDGE_DAYS = {2: "R", 5: "L", 7: "R", 9: "L"}  # day index -> page edge


def eflora(side):
    """One pressed flower glued near a page edge (gutter zones only, so body
    text never sits under it; hidden on narrow screens like the clay theme's
    chapter decorations)."""
    stem = next_flora()
    w = FLORA_W[stem] * RNG.uniform(.95, 1.25)
    if side == "L":   # on the pen-route spine, low on the page
        pos = (f"left:{RNG.uniform(-1.4, .2):.1f}%;"
               f"bottom:{RNG.uniform(18, 64):.0f}px")
    else:             # right gutter beside the rail
        pos = (f"right:{RNG.uniform(-1.2, .4):.1f}%;"
               f"top:{RNG.uniform(32, 56):.0f}%")
    return (f'<span class="eflora {FL_CLS[stem]}" aria-hidden="true" '
            f'style="{pos};width:{w:.0f}px;--rot:{RNG.uniform(-26, 26):.1f}deg"></span>')


# the trip's OWN pressings (props[].kind=flora with a stem): each stem gets a
# fl-x<n> class in the stylesheet (data URI + aspect ratio measured from the
# scan), so re-using one pressing on several days costs no extra bytes.
FL_CUSTOM = {}      # stem -> (cls, aspect "w/h") — filled while rendering days


def _img_aspect(uri):
    """'w/h' of a data-URI image (PIL), or a tall default when unreadable."""
    try:
        import io
        from PIL import Image
        w, h = Image.open(io.BytesIO(base64.b64decode(uri.split(",", 1)[1]))).size
        return f"{w}/{h}"
    except Exception:
        return "2/3"


def flora_custom_cls(stem):
    """CSS class for a trip-owned pressing; '' when the scan is missing."""
    if stem in FL_CUSTOM:
        return FL_CUSTOM[stem][0]
    uri = data_uri(stem)
    if not uri:
        return ""
    cls = f"fl-x{len(FL_CUSTOM) + 1}"
    FL_CUSTOM[stem] = (cls, _img_aspect(uri))
    return cls


def flora_custom_css():
    """One rule per trip-owned pressing (call after every day is rendered)."""
    return "".join(
        f'  .{cls} {{ background-image:url("{data_uri(stem)}"); aspect-ratio:{ar}; }}\n'
        for stem, (cls, ar) in FL_CUSTOM.items())


def flora_prop(pr=None):
    """A pressed flower glued into the rail: the next one from the theme's
    seeded deck, or — when art names a stem — the trip's own pressing at
    `w` px (default 90). Deck pressings roll their tilt from the RNG exactly
    as before, so a trip that never names a stem re-renders unchanged."""
    pr = pr or {}
    if pr.get("stem"):
        cls = flora_custom_cls(pr["stem"])
        if not cls:
            return ""
        w = pr.get("w") or 90
        return (f'<span class="prop propfl {cls}" aria-hidden="true" '
                f'style="--rot:{_rot(pr.get("rot"), -7, 7)}deg;width:{w}px"></span>')
    stem = next_flora()
    return (f'<span class="prop propfl {FL_CLS[stem]}" aria-hidden="true" '
            f'style="--rot:{RNG.uniform(-7, 7):.1f}deg;width:{FLORA_W[stem]}px"></span>')


# second photo(s) pinned into the rail of the big sight-seeing days — 70s
# kodak prints in the same white frame + corner-tape system as the polaroids,
# captioned in Caveat handwriting (English-only, like the mock's photo notes).
# Which days / which subjects: art days[d].photos2 (lift them from the timeline).

# margin doodles: single-line ink sketches + a hand note + a curly arrow,
# taped into the notes column of selected days (mock: Chrysler sketch,
# bison "So wild!", waves "Aloha!", smoking volcano). The SKETCHES are the
# theme's kit; which day gets which, and the note, come from art
# days[d].doodle = {sketch, note, font, rot}.
ARROW = ('<svg class="dd-arrow" viewBox="0 0 34 30" aria-hidden="true">'
         '<path d="M4 4 C 18 6 26 12 28 24 M22 20 l6 5 2 -8"/></svg>')
SKETCH = {   # name -> (ink drawing, gets the curly arrow?)
    "skyline": ('<svg viewBox="0 0 44 96" class="dd"><path d="M22 8 v10 M18 18 h8 M16 24 h12 '
                'M14 30 h16 M17 24 q5 -4 10 0 M15 30 q7 -6 14 0 M12 38 h20 M13 38 q9 -8 18 0 '
                'M12 38 v50 M32 38 v50 M12 56 h20 M12 74 h20 M16 88 v-8 M22 88 v-8 M28 88 v-8"/></svg>',
                True),
    "bison": ('<svg viewBox="0 0 96 62" class="dd"><path d="M14 44 q0 -12 12 -14 q4 -12 18 -12 '
              'q16 0 18 12 q12 2 12 10 q0 6 -6 8 l-2 12 h-7 l-1 -8 h-14 l-1 8 h-7 l-2 -12 '
              'q-16 0 -20 -4z M56 20 q4 -6 9 -3 M20 30 q-6 0 -8 5"/></svg>', True),
    "bridge": ('<svg viewBox="0 0 110 56" class="dd"><path d="M6 48 h98 M26 48 V14 M84 48 V14 '
               'M22 20 h8 M80 20 h8 M22 28 h8 M80 28 h8 M2 34 Q26 10 55 26 Q84 42 108 18 '
               'M26 26 v-6 M84 30 v-8"/></svg>', False),
    "waves": ('<svg viewBox="0 0 96 40" class="dd"><path d="M6 26 q8 -14 16 0 q-10 -2 -8 6 '
              'M34 20 q7 -12 14 0 q-9 -1 -7 5 M60 26 q8 -14 16 0 q-10 -2 -8 6"/></svg>', True),
    "volcano": ('<svg viewBox="0 0 84 68" class="dd"><path d="M10 62 L34 18 q4 -6 8 0 L66 62 z '
                'M30 30 h20 M38 18 q-2 -8 4 -12 M42 16 q4 -6 10 -6 M36 8 q-6 -2 -8 2"/></svg>',
                False),
    # ---- neutral additions (2026-08-15): the same one-line ink voice, no
    # place attached, so any trip's mountains / reef / rainforest / railway /
    # hut / boat / night sky can be drawn without borrowing another trip's
    # landmark. viewBoxes stay in the 84-110 x 40-96 family of the originals.
    "peaks": ('<svg viewBox="0 0 110 60" class="dd"><path d="M4 54 L22 22 L32 36 L46 8 '
              'L58 30 L66 22 L76 40 L86 32 L106 54 M40 20 h6 M50 16 l4 5 M28 32 q4 -3 8 0 '
              'M62 54 v-14 q3 -5 6 0 v14 M72 54 v-10 q2 -4 5 0 v10 M81 54 v-8 q2 -3 4 0 v8 '
              'M2 54 h106"/></svg>', False),
    "coral": ('<svg viewBox="0 0 96 62" class="dd"><path d="M30 58 v-14 q-10 -6 -8 -18 '
              'M30 46 q10 -4 12 -14 M22 28 q-6 -6 -2 -12 M42 32 q8 -4 10 -12 M30 44 v-8 '
              'q-4 -6 0 -12 M8 58 h82 M62 20 q9 -9 20 0 q-9 9 -20 0 z M82 20 l7 -6 v12 z '
              'M67 19 h1 M88 9 a2.2 2.2 0 1 0 .1 0 M92 3 a1.4 1.4 0 1 0 .1 0 '
              'M14 58 q4 -8 8 0 M74 58 q4 -8 8 0"/></svg>', True),
    "palm": ('<svg viewBox="0 0 70 96" class="dd"><path d="M36 92 q2 -30 -4 -56 M6 92 h56 '
             'M32 36 q-16 -6 -26 4 q12 -2 22 4 M32 36 q-6 -18 -18 -22 q6 10 12 22 '
             'M32 36 q4 -20 18 -22 q-8 8 -12 22 M32 36 q18 -4 30 8 q-14 -4 -26 0 '
             'M32 36 q-10 6 -12 20 q4 -10 14 -14 M32 36 q12 4 16 18 q-2 -10 -12 -14 '
             'M29 40 a2.6 2.6 0 1 0 .1 0 M35 42 a2.6 2.6 0 1 0 .1 0 M50 92 q4 -8 8 0"/></svg>',
             False),
    "train": ('<svg viewBox="0 0 110 60" class="dd"><path d="M4 50 h102 M4 54 h102 '
              'M14 44 v-18 q0 -4 4 -4 h38 q4 0 4 4 v18 z M20 28 h8 v8 h-8 z M32 28 h8 v8 h-8 z '
              'M44 28 h8 v8 h-8 z M22 50 a4 4 0 1 0 .1 0 M50 50 a4 4 0 1 0 .1 0 '
              'M66 44 v-14 q0 -3 3 -3 h18 l8 8 v9 z M72 32 h8 v6 h-8 z M84 50 a4 4 0 1 0 .1 0 '
              'M76 26 q-3 -6 3 -9 q5 -3 3 -8 M100 46 h6 M100 43 h6"/></svg>', False),
    "cabin": ('<svg viewBox="0 0 96 62" class="dd"><path d="M14 56 v-24 l34 -22 l34 22 v24 z '
              'M8 34 l40 -26 l40 26 M42 56 v-14 h12 v14 M22 40 h10 v8 h-10 z M27 40 v8 '
              'M22 44 h10 M64 40 h10 v8 h-10 z M69 40 v8 M64 44 h10 M66 20 v-9 h6 v13 '
              'M70 9 q-2 -4 2 -6 M2 56 h92 M14 48 h22 M60 48 h22 M14 36 h22 M60 36 h22"/></svg>',
              False),
    "ferry": ('<svg viewBox="0 0 110 56" class="dd"><path d="M8 34 h94 l-10 14 h-76 z '
              'M30 34 v-12 h44 v12 M40 22 v-8 h24 v8 M50 14 v-7 h6 v7 M36 28 h5 M46 28 h5 '
              'M56 28 h5 M66 28 h5 M2 52 q6 -5 12 0 t12 0 M84 52 q6 -5 12 0 t12 0 '
              'M62 6 q6 -3 10 0"/></svg>', True),
    "aurora": ('<svg viewBox="0 0 110 62" class="dd"><path d="M4 28 q20 -22 40 -8 t40 -6 t22 4 '
               'M4 38 q20 -20 40 -6 t40 -6 t22 6 M40 18 v-9 M70 14 v-8 '
               'M14 8 l1 3 l3 1 l-3 1 l-1 3 l-1 -3 l-3 -1 l3 -1 z '
               'M4 58 h102 M20 58 l4 -12 l4 12 M28 58 l3 -8 l3 8 M74 58 l4 -14 l4 14 '
               'M84 58 l3 -9 l3 9"/></svg>', True),
}

_VB_RE = re.compile(r"^\s*-?\d+(\.\d+)?(\s+-?\d+(\.\d+)?){3}\s*$")
_PATH_RE = re.compile(r"^[MmLlHhVvCcSsQqTtAaZz0-9\s.,+\-eE]+$")


def custom_sketch(sv):
    """art doodle.svg = {viewBox, d, arrow?} → the same .dd ink drawing the
    kit's sketches use (one stroked path, theme colour/width, no fill).
    Returns (svg, arrow) or ("", True) when the shape is not usable — the
    values are validated so a typo can never inject markup."""
    if not isinstance(sv, dict):
        return "", True
    vb, d = str(sv.get("viewBox", "")).strip(), str(sv.get("d", "")).strip()
    if not (_VB_RE.match(vb) and d and _PATH_RE.match(d)):
        return "", True
    return (f'<svg viewBox="{vb}" class="dd"><path d="{esc(d)}"/></svg>',
            bool(sv.get("arrow", False)))


def doodle_html(dd):
    """A taped-in margin doodle from art; '' when there is nothing to draw."""
    svg, arrow = SKETCH.get(dd.get("sketch", ""), ("", True))
    if dd.get("svg"):
        c_svg, c_arrow = custom_sketch(dd["svg"])
        if c_svg:
            svg, arrow = c_svg, c_arrow
    note = dd.get("note", "")
    if not (svg or note):
        return ""
    font = "hand" if dd.get("font") == "hand" else "cur"
    note_html = ('<span class="{} dd-note">{}</span>'.format(
        font, "<br>".join(esc(l) for l in note.split("\n"))) if note else "")
    # arrow + note travel as one .dd-tail, so when the row is too narrow for
    # sketch + note the tail drops under the sketch together (arrow still
    # pointing at its note) instead of the note being squeezed word-per-line
    return (f'<div class="doodle" style="--rot:{_rot(dd.get("rot"), -2.5, 2.5)}deg" '
            f'aria-hidden="true">{svg}<span class="dd-tail">{ARROW if arrow else ""}'
            f'{note_html}</span></div>')


# brief section titles: shared table theme_common.BRIEF_TITLES + art common
# brief_titles (e.g. "签证 · EVUS") — see brief_titles(ART) in render_brief
# four washi scans + the three wishlist fabric tapes (floral / ticking /
# gingham) rotate through one counter, so no two neighbouring pieces of tape
# repeat a pattern and the mix re-deals deterministically on every build
TAPES = ["tp-a", "tp-b", "tp-c", "tp-d", "tp-e", "tp-f", "tp-g"]

_uid = [0]


def tape(rot=None, cls=""):
    """A strip of washi/fabric tape; the seven scans rotate through a counter."""
    _uid[0] += 1
    t = TAPES[_uid[0] % len(TAPES)]
    r = rot if rot is not None else (-7 if _uid[0] % 2 else 6)
    return (f'<span class="tape {t} {cls}" aria-hidden="true" '
            f'style="rotate:{r}deg"></span>')


def svg_uri(svg):
    return "data:image/svg+xml," + urllib.parse.quote(svg, safe="")


def route_tile(w, h, amp, stroke):
    """One vertically-tileable meander of the pen route (start/end at centre
    with a vertical tangent so repeat-y joins seamlessly), plus two tiny ink
    sparkles beside the bends — the mock dots its route with little stars."""
    c, a = w / 2, amp
    d = (f"M{c} 0 C {c} {h*.08:.0f} {c+a} {h*.13:.0f} {c+a*.8:.0f} {h*.23:.0f} "
         f"C {c+a*.6:.0f} {h*.33:.0f} {c-a} {h*.37:.0f} {c-a*.7:.0f} {h*.48:.0f} "
         f"C {c-a*.4:.0f} {h*.6:.0f} {c+a} {h*.63:.0f} {c+a*.7:.0f} {h*.75:.0f} "
         f"C {c+a*.45:.0f} {h*.87:.0f} {c} {h*.9:.0f} {c} {h}")

    def spark(x, y, r):
        return (f"<path d='M{x:.1f} {y - r:.1f} L{x + r*.3:.1f} {y - r*.3:.1f} "
                f"L{x + r:.1f} {y:.1f} L{x + r*.3:.1f} {y + r*.3:.1f} "
                f"L{x:.1f} {y + r:.1f} L{x - r*.3:.1f} {y + r*.3:.1f} "
                f"L{x - r:.1f} {y:.1f} L{x - r*.3:.1f} {y - r*.3:.1f} Z' "
                f"fill='#26455f' opacity='.5'/>")

    r = w * .055 + 1.5
    deco = (spark(c + a * .8 + w * .09, h * .21, r)
            + spark(c - a * .7 - w * .09, h * .5, r * .8))
    return svg_uri(
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' "
        f"viewBox='0 0 {w} {h}'><path d='{d}' fill='none' stroke='#26455f' "
        f"stroke-width='{stroke}' stroke-linecap='round' "
        f"stroke-dasharray='9 8' opacity='.72'/>{deco}</svg>")


# parchment tile: fine grain + a warm low-frequency mottle + faint fibre
# streaks, all baked into ONE small SVG tile (rasterised once, repeated —
# never a live full-page filter). stitchTiles keeps the repeat seamless.
NOISE = svg_uri(
    "<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'>"
    "<filter id='m'><feTurbulence type='fractalNoise' baseFrequency='0.013' "
    "numOctaves='3' seed='7' stitchTiles='stitch'/><feColorMatrix type='matrix' values="
    "'0 0 0 0 0.59 0 0 0 0 0.41 0 0 0 0 0.18 0 0 0 0.045 0'/></filter>"
    "<filter id='f'><feTurbulence type='turbulence' baseFrequency='0.012 0.11' "
    "numOctaves='2' seed='11' stitchTiles='stitch'/><feColorMatrix type='matrix' values="
    "'0 0 0 0 0.45 0 0 0 0 0.32 0 0 0 0 0.13 0 0 0 0.03 0'/></filter>"
    "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.8' "
    "numOctaves='2' stitchTiles='stitch'/><feColorMatrix type='matrix' values="
    "'0 0 0 0 0.26 0 0 0 0 0.19 0 0 0 0 0.07 0 0 0 0.055 0'/></filter>"
    "<rect width='240' height='240' filter='url(#m)'/>"
    "<rect width='240' height='240' filter='url(#f)'/>"
    "<rect width='240' height='240' filter='url(#n)'/></svg>")


# torn strip under the sticky tab bar: one small tile repeated-x
TORN_TILE = svg_uri(
    "<svg xmlns='http://www.w3.org/2000/svg' width='72' height='9'>"
    "<path d='M0 0 H72 V2.5 q-5 4.5 -12 1.5 t-13 2.5 t-12 -3 t-11 3.5 t-13 -1.5 "
    "t-11 1 z' fill='#e2d1a9'/></svg>")

# speckle alpha mask: eats ~20% of a chop's ink so it prints unevenly
SPECK = svg_uri(
    "<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'>"
    "<filter id='s'><feTurbulence type='fractalNoise' baseFrequency='.5' "
    "numOctaves='2' seed='9' stitchTiles='stitch'/><feColorMatrix type='matrix' "
    "values='0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 .55 .55 .55 0 .45'/></filter>"
    "<rect width='120' height='120' filter='url(#s)'/></svg>")


# ---------------------------------------------------------------- stains ----
def _wobble(fid, freq, scale, seed):
    """Displacement filter that turns clean geometry into organic blots."""
    return (f"<filter id='{fid}' x='-30%' y='-30%' width='160%' height='160%'>"
            f"<feTurbulence type='fractalNoise' baseFrequency='{freq}' "
            f"numOctaves='2' seed='{seed}' result='n'/>"
            f"<feDisplacementMap in='SourceGraphic' in2='n' scale='{scale}'/></filter>")


def _stain_ring():
    """Coffee-cup ring: displaced ellipse strokes + a few dried droplets."""
    g = _wobble("d", .045, 10, 3)
    return svg_uri(
        "<svg xmlns='http://www.w3.org/2000/svg' width='210' height='200' viewBox='0 0 210 200'>"
        f"{g}<g filter='url(#d)' fill='none' stroke='#6d4a1f'>"
        "<ellipse cx='105' cy='98' rx='84' ry='78' stroke-width='7' opacity='.32'/>"
        "<ellipse cx='105' cy='98' rx='84' ry='78' stroke-width='2.4' opacity='.5' "
        "transform='rotate(9 105 98)'/>"
        "<ellipse cx='101' cy='95' rx='68' ry='64' stroke-width='3' opacity='.18'/></g>"
        "<g fill='#6d4a1f'><circle cx='30' cy='176' r='3.2' opacity='.3'/>"
        "<circle cx='186' cy='44' r='2.4' opacity='.34'/>"
        "<circle cx='168' cy='172' r='4.2' opacity='.26'/>"
        "<circle cx='44' cy='30' r='1.8' opacity='.3'/></g></svg>")


def _stain_ink():
    """Fountain-pen blot in the route's navy ink, with satellite spatter."""
    g = _wobble("d", .07, 26, 9)
    return svg_uri(
        "<svg xmlns='http://www.w3.org/2000/svg' width='190' height='170' viewBox='0 0 190 170'>"
        f"{g}<g filter='url(#d)' fill='#263349'>"
        "<ellipse cx='92' cy='84' rx='40' ry='33' opacity='.5'/>"
        "<ellipse cx='118' cy='104' rx='16' ry='12' opacity='.42'/>"
        "<ellipse cx='64' cy='104' rx='9' ry='7' opacity='.4'/></g>"
        "<g fill='#263349'><circle cx='152' cy='58' r='3' opacity='.42'/>"
        "<circle cx='166' cy='84' r='1.9' opacity='.4'/>"
        "<circle cx='38' cy='48' r='2.4' opacity='.38'/>"
        "<circle cx='24' cy='128' r='1.6' opacity='.4'/>"
        "<path d='M136 44 q10 -8 22 -10' stroke='#263349' stroke-width='1.6' "
        "fill='none' opacity='.35' stroke-linecap='round'/></g></svg>")


def _stain_water():
    """Dried water mark: pale wide rims, soft edge faked with three strokes
    of falling opacity (NO blur filters — manual's compositor rule)."""
    g = _wobble("d", .03, 16, 5)
    return svg_uri(
        "<svg xmlns='http://www.w3.org/2000/svg' width='260' height='240' viewBox='0 0 260 240'>"
        f"{g}<g filter='url(#d)' fill='none' stroke='#8a6a33'>"
        "<ellipse cx='130' cy='118' rx='104' ry='92' stroke-width='16' opacity='.05'/>"
        "<ellipse cx='130' cy='118' rx='108' ry='96' stroke-width='7' opacity='.09'/>"
        "<ellipse cx='130' cy='118' rx='111' ry='99' stroke-width='2.6' opacity='.14'/>"
        "<ellipse cx='124' cy='112' rx='84' ry='74' stroke-width='2' opacity='.07'/></g></svg>")


def _stain_print():
    """Inky fingerprint: dashed concentric ellipses, half wiped."""
    g = _wobble("d", .14, 5, 13)
    rings = "".join(
        f"<ellipse cx='45' cy='56' rx='{8 + i * 5.4:.0f}' ry='{11 + i * 6.6:.0f}' "
        f"stroke-dasharray='{4 + (i % 3)} {3 + (i * 2) % 5}' "
        f"transform='rotate({-14 + i * 3} 45 56)' opacity='{.5 - i * .045:.2f}'/>"
        for i in range(6))
    return svg_uri(
        "<svg xmlns='http://www.w3.org/2000/svg' width='96' height='118' viewBox='0 0 96 118'>"
        f"{g}<g filter='url(#d)' fill='none' stroke='#5c4426' stroke-width='2.1'>"
        f"{rings}</g></svg>")


def _stain_wax():
    """Candle-wax drips: translucent amber blobs with a darker rim and a
    gloss spot — reads waxy without any blur."""
    g = _wobble("d", .09, 7, 21)
    return svg_uri(
        "<svg xmlns='http://www.w3.org/2000/svg' width='150' height='130' viewBox='0 0 150 130'>"
        f"{g}<g filter='url(#d)'>"
        "<ellipse cx='72' cy='62' rx='34' ry='27' fill='#caa14e' opacity='.26'/>"
        "<ellipse cx='72' cy='62' rx='34' ry='27' fill='none' stroke='#a67c26' "
        "stroke-width='2.4' opacity='.22'/>"
        "<ellipse cx='108' cy='92' rx='13' ry='10' fill='#caa14e' opacity='.24'/>"
        "<ellipse cx='108' cy='92' rx='13' ry='10' fill='none' stroke='#a67c26' "
        "stroke-width='1.8' opacity='.2'/>"
        "<ellipse cx='42' cy='96' rx='8' ry='6' fill='#caa14e' opacity='.22'/>"
        "<ellipse cx='62' cy='52' rx='9' ry='6' fill='#fdf6e2' opacity='.3'/></g></svg>")


def _stain_smudge():
    """Graphite thumb-smear: layered soft streaks, no blur."""
    g = _wobble("d", .05, 12, 17)
    return svg_uri(
        "<svg xmlns='http://www.w3.org/2000/svg' width='220' height='90' viewBox='0 0 220 90'>"
        f"{g}<g filter='url(#d)' fill='#4a3b28'>"
        "<rect x='18' y='30' width='184' height='30' rx='15' opacity='.05'/>"
        "<rect x='30' y='36' width='150' height='19' rx='10' opacity='.07'/>"
        "<rect x='46' y='40' width='104' height='11' rx='6' opacity='.08'/></g></svg>")


def _stain_spatter():
    """Loose ink spatter thrown across a corner (seeded, baked)."""
    rng = random.Random(77)
    dots = "".join(
        f"<circle cx='{rng.uniform(8, 152):.0f}' cy='{rng.uniform(8, 132):.0f}' "
        f"r='{rng.uniform(1.1, 3.8):.1f}' fill='{rng.choice(['#263349', '#5c4426'])}' "
        f"opacity='{rng.uniform(.22, .45):.2f}'/>" for _ in range(13))
    return svg_uri(
        "<svg xmlns='http://www.w3.org/2000/svg' width='160' height='140' viewBox='0 0 160 140'>"
        f"{dots}<path d='M28 96 q14 -20 36 -24' stroke='#5c4426' stroke-width='1.4' "
        "fill='none' opacity='.3' stroke-linecap='round'/></svg>")


STN_URIS = {
    "ring": _stain_ring(), "ink": _stain_ink(), "wtr": _stain_water(),
    "fp": _stain_print(), "wax": _stain_wax(), "smg": _stain_smudge(),
    "spat": _stain_spatter(),
}
# base display width per type (scaled per instance)
STN_W = {"ring": 150, "ink": 130, "wtr": 210, "fp": 62, "wax": 110,
         "smg": 150, "spat": 110}
# Three slot families, by what may legally sit beneath body text:
#   SIDE  = left/right gutters (spine & rail edges) — any species, full punch
#   BAND  = top/bottom centre strips — pale species only (water/spatter/wax):
#           their boxes stretch into head/pocket text, dark planes banned
#   FIELD = inside the text column — thin-stroke or light-pigment species only
_SLOT_SIDE = [("left:-1.5%", "top:4%"), ("right:-1%", "top:16%"),
              ("left:1%", "top:58%"), ("right:2%", "bottom:4%"),
              ("left:-2%", "bottom:12%"), ("right:-2.5%", "top:38%")]
_SLOT_BAND = [("left:30%", "top:.4%"), ("right:24%", "bottom:.6%"),
              ("left:52%", "top:1%")]
_SLOT_FIELD = [("left:40%", "top:26%"), ("left:56%", "bottom:20%"),
               ("right:30%", "top:52%"), ("left:34%", "bottom:8%")]
_SIDE_TYPES = ["ring", "ink", "wtr", "spat", "ring", "smg", "ink"]
_BAND_TYPES = ["wtr", "spat", "wax"]
_FIELD_TYPES = ["fp", "wax"]


def _stn(t, x, y, wmul, opa, opb, rot=70):
    w = STN_W[t] * RNG.uniform(*wmul)
    return (f'<span class="stn s-{t}" aria-hidden="true" style="{x};{y};'
            f'width:{w:.0f}px;--rot:{RNG.uniform(-rot, rot):.0f}deg;'
            f'--sx:{RNG.choice([1, 1, -1])};opacity:{RNG.uniform(opa, opb):.2f}"></span>')


def stainfield(n_edge=3, n_field=1, extra=""):
    """A seeded scatter of aged-paper stains for one chapter. Dark heavy
    species live in the side gutters; the strips that reach under text only
    ever get pale species (AA re-checked with these caps, not eyeballed)."""
    out = []
    for k in range(n_edge):
        if RNG.random() < .68:
            t = RNG.choice(_SIDE_TYPES)
            x, y = _SLOT_SIDE[RNG.randrange(len(_SLOT_SIDE))]
        else:
            t = RNG.choice(_BAND_TYPES)
            x, y = _SLOT_BAND[RNG.randrange(len(_SLOT_BAND))]
        out.append(_stn(t, x, y, (.72, 1.35), .55, .9))
    for k in range(n_field):
        t = RNG.choice(_FIELD_TYPES)
        x, y = _SLOT_FIELD[RNG.randrange(len(_SLOT_FIELD))]
        out.append(_stn(t, x, y, (.8, 1.2), .4, .6, rot=40))
    return "".join(out) + extra


# ---------------------------------------------------------------- stamps ----
_INK_GRUNGE = ("<filter id='g' x='-8%' y='-8%' width='116%' height='116%'>"
               "<feTurbulence type='fractalNoise' baseFrequency='{f}' "
               "numOctaves='3' seed='{s}' result='n'/>"
               "<feColorMatrix in='n' type='matrix' "
               "values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1.15 1.15 1.15 0 -0.62' result='a'/>"
               "<feComposite in='SourceGraphic' in2='a' operator='in'/></filter>")


def postmark_uri(city, mon, day, year, ink="#7c3128", seed=4, killer=True):
    """Hand-cut circular postmark: double ring, city on the top arc, date
    in the middle, stars on the bottom arc, wavy cancellation bars to the
    right. The grunge filter eats the ink unevenly — rasterised once."""
    w = 236 if killer else 156
    f = _INK_GRUNGE.format(f=.14, s=seed)
    bars = ("<g fill='none' stroke-width='3.4' stroke-linecap='round'>"
            + "".join(f"<path d='M156 {52 + i * 17} q14 7 28 0 t28 0' stroke='{ink}'/>"
                      for i in range(4)) + "</g>") if killer else ""
    return svg_uri(
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='156' "
        f"viewBox='0 0 {w} 156'><defs>"
        "<path id='ta' d='M78 138 A60 60 0 1 1 78.01 138'/>"
        "<path id='tb' d='M20 78 A58 58 0 0 0 136 78'/></defs>"
        f"{f}<g filter='url(#g)'>"
        f"<circle cx='78' cy='78' r='72' fill='none' stroke='{ink}' stroke-width='3.6'/>"
        f"<circle cx='78' cy='78' r='66' fill='none' stroke='{ink}' stroke-width='1.4'/>"
        f"<circle cx='78' cy='78' r='45' fill='none' stroke='{ink}' stroke-width='1.2' "
        "stroke-dasharray='3 4'/>"
        f"<text fill='{ink}' font-family='Courier New,Courier,monospace' font-weight='700' "
        f"font-size='16.5' letter-spacing='2'><textPath href='#ta' startOffset='50%' "
        f"text-anchor='middle'>{esc(city)}</textPath></text>"
        f"<text fill='{ink}' font-family='Courier New,Courier,monospace' font-weight='700' "
        "font-size='13' letter-spacing='6'><textPath href='#tb' startOffset='50%' "
        "text-anchor='middle'>&#9733; &#9733; &#9733;</textPath></text>"
        f"<text x='78' y='72' fill='{ink}' text-anchor='middle' "
        "font-family='Courier New,Courier,monospace' font-weight='700' "
        f"font-size='19'>{esc(mon)} {day}</text>"
        f"<text x='78' y='92' fill='{ink}' text-anchor='middle' "
        "font-family='Courier New,Courier,monospace' font-weight='700' "
        f"font-size='15' letter-spacing='3'>{year}</text>"
        f"{bars}</g></svg>")


def rect_stamp_uri(lines, ink="#9c352c", w=210, h=74, seed=6, fs=26):
    """Office rubber stamp: double box + condensed capitals, uneven ink.
    The type is sized to FIT: `fs` is the ceiling, and when the longest line
    would run past the inner box (Courier advance ≈ .6em + letter-spacing)
    both the size and the spacing scale down together — a long station pair
    like "Oslo S → Myrdal" stays complete instead of losing both ends."""
    f = _INK_GRUNGE.format(f=.16, s=seed)
    n = len(lines)
    step = h / (n + 1)
    avail = w - 30                       # inner rule at 9px + a little air
    scale = 1.0
    for i, t in enumerate(lines):
        size, ls = (fs, 3) if i == 0 else (fs * .52, 2)
        # Courier advance: Latin ≈ .6em, but CJK glyphs come from the fallback
        # face at a full 1em — count them so mixed station names still fit
        ems = sum(1.0 if ord(c) > 0x2E7F else .6 for c in t)
        need = ems * size + max(len(t) - 1, 0) * ls
        if need > avail:
            scale = min(scale, avail / need)
    fs *= scale
    txt = "".join(
        f"<text x='{w / 2}' y='{step * (i + 1) + (fs if n == 1 else fs * .72) * .36:.0f}' "
        f"fill='{ink}' text-anchor='middle' font-family='Courier New,Courier,monospace' "
        f"font-weight='700' font-size='{fs if i == 0 else fs * .52:.0f}' "
        f"letter-spacing='{round((3 if i == 0 else 2) * scale, 1):g}'>{esc(t)}</text>"
        for i, t in enumerate(lines))
    return svg_uri(
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' "
        f"viewBox='0 0 {w} {h}'>{f}<g filter='url(#g)'>"
        f"<rect x='3' y='3' width='{w - 6}' height='{h - 6}' rx='6' fill='none' "
        f"stroke='{ink}' stroke-width='3.4'/>"
        f"<rect x='9' y='9' width='{w - 18}' height='{h - 18}' rx='3' fill='none' "
        f"stroke='{ink}' stroke-width='1.3'/>{txt}</g></svg>")


def rstamp(uri, w, cls="", rot=None, extra=""):
    # The URI is fully %-encoded by svg_uri (quote safe="") — no quotes,
    # parens or spaces — so it MUST be written unquoted: url("…") inside a
    # double-quoted style attribute truncates the attribute at the inner
    # quote and the browser resolves url("") → the stamp silently dies.
    r = rot if rot is not None else RNG.uniform(-9, 9)
    return (f'<span class="rstamp {cls}" aria-hidden="true" style="'
            f'background-image:url({uri});width:{w}px;--rot:{r:.1f}deg;{extra}"></span>')


# ------------------------------------------------------------- paperclip ----
PCLIP = svg_uri(
    "<svg xmlns='http://www.w3.org/2000/svg' width='30' height='66' viewBox='0 0 30 66'>"
    "<path d='M10 16 v34 a5.5 5.5 0 0 0 11 0 V12 a8 8 0 0 0 -16 0 v40 a12.5 12.5 0 0 0 25 0 V18' "
    "fill='none' stroke='#6f6a5e' stroke-width='3' stroke-linecap='round'/>"
    "<path d='M10 16 v34 a5.5 5.5 0 0 0 11 0 V12' fill='none' stroke='#a9a294' "
    "stroke-width='1.2' stroke-linecap='round'/></svg>")

# ---------------------------------------------------------------- washi -----
WT_KINDS = ["wt-red", "wt-navy", "wt-gold", "wt-sage"]


def wt(cls="", style=""):
    """CSS washi strip: semi-transparent, torn ends, multiply blend."""
    _uid[0] += 1
    kind = WT_KINDS[_uid[0] % 4]
    return (f'<span class="wt {kind} {cls}" aria-hidden="true" '
            f'style="{style}"></span>')

TORN_ENV = ("polygon(0.6% 1.8%, 6% 0.4%, 13% 1.6%, 21% 0.2%, 30% 1.4%, 39% 0.5%, "
            "48% 1.7%, 57% 0.3%, 66% 1.5%, 75% 0.4%, 84% 1.6%, 92% 0.2%, 99.4% 1.5%, "
            "99.8% 12%, 99.1% 25%, 99.9% 39%, 99.2% 53%, 99.8% 68%, 99.1% 82%, 99.7% 94%, "
            "98.6% 99.3%, 90% 98.2%, 81% 99.6%, 71% 98.1%, 61% 99.5%, 51% 98.3%, "
            "41% 99.7%, 31% 98.2%, 21% 99.4%, 12% 98.1%, 4% 99.6%, 0.4% 98.4%, "
            "1% 86%, 0.2% 72%, 0.9% 57%, 0.1% 43%, 0.8% 28%, 0.2% 14%)")
TORN_SLIP = ("polygon(0.8% 3%, 9% 0.8%, 22% 3.4%, 36% 0.6%, 50% 3%, 64% 0.9%, "
             "78% 3.2%, 91% 0.7%, 99.2% 2.8%, 99.6% 50%, 99% 97%, 88% 99.2%, "
             "74% 96.8%, 60% 99.4%, 46% 96.9%, 32% 99.2%, 18% 97%, 6% 99.3%, "
             "0.5% 97.2%, 0.9% 50%)")

KIND_MARK = {"anchor": "●", "hop": "→", "free": "○"}


def paper_chain(n):
    """n+1 paper tones so every chapter gradient interlocks with the next."""
    base = ["#f4ead6", "#efe3c8", "#f2e7d0", "#ecdfc0", "#f1e6cd", "#eee1c4"]
    return [base[i % len(base)] for i in range(n + 1)]


_pm_cache = {}


def postmark(date, extra_cls="", killer=True, city=None):
    """Ring postmark for a date; the CAPS city comes from art days[d].mark
    (or is passed in for the endcap) and is simply blank when unknown."""
    d = datetime.date.fromisoformat(date)
    if city is None:
        city = ART.day(date, THEME).get("mark", "") or ""
    key = (date, killer, city)
    if key not in _pm_cache:
        _pm_cache[key] = postmark_uri(city, MON[d.month], d.day, d.year,
                                      seed=3 + d.day, killer=killer)
    rot = RNG.uniform(-11, 11)
    # unquoted url() on purpose — see rstamp(): the URI is %-encoded, and a
    # quoted url("…") would truncate the double-quoted style attribute.
    return (f'<span class="pm {extra_cls}" aria-hidden="true" style="'
            f'background-image:url({_pm_cache[key]});--rot:{rot:.1f}deg"></span>')


# ------------------------------------------------- data-driven marginalia ---
MGN_INKS = ["mgn-sep", "mgn-blu", "mgn-red"]
_MGN_POOL = {
    "pin": ["don't miss!", "the big one!", "circle this ↑", "worth the trip alone"],
    # pinned logistics rows (kind != anchor) get discipline notes, not awe
    "pinlog": ["no slipping!", "hard stop!", "set an alarm ⏰", "stick to it!"],
    "meal": ["must try!", "come hungry", "yum!!", "save room for this"],
    "opener": ["be first in line!", "doors open — go!"],
    "free": ["free!", "$0 — love that", "costs nothing!"],
}


def _mgn(text, extra_cls=""):
    ink = MGN_INKS[RNG.randrange(3)]
    rot = RNG.uniform(-5, 4)
    return (f'<i class="mgn {ink} {extra_cls}" aria-hidden="true" '
            f'style="--mr:{rot:.1f}deg">{esc(text)}</i>')


def day_marginalia(day):
    """English hand-notes hung on real timeline rows. Times come straight
    from the data (never invented); the exclamations are diary flavour."""
    rows = day.get("timeline", [])
    picks = {}          # row index -> html
    first_time_done = False
    meals = [i for i, r in enumerate(rows) if r.get("kind") == "meal"]
    pins = [i for i, r in enumerate(rows) if r.get("tag") == "pinned"]
    opens = [i for i, r in enumerate(rows) if r.get("tag") == "opener"]
    frees = [i for i, r in enumerate(rows)
             if r.get("price") in ("免费", "free", "Free", "FREE")]
    if opens:
        i = opens[0]
        t = (rows[i].get("t", "") or "").split("-")[0].strip()
        picks[i] = _mgn(f"{t} sharp!" if t else RNG.choice(_MGN_POOL["opener"]), "mgn-u")
        first_time_done = True
    if pins:
        # prefer a pinned ANCHOR (a sight worth gushing over); a pinned
        # logistics row only ever gets a time-discipline note
        anchor_pins = [i for i in pins if rows[i].get("kind") == "anchor"]
        i = (anchor_pins[RNG.randrange(len(anchor_pins))] if anchor_pins
             else pins[RNG.randrange(len(pins))])
        if i not in picks:
            pool = "pin" if rows[i].get("kind") == "anchor" else "pinlog"
            if not first_time_done and rows[i].get("t"):
                t = rows[i]["t"].split("-")[0].strip()
                picks[i] = _mgn(f"{t} — {RNG.choice(_MGN_POOL[pool])}", "mgn-u")
                first_time_done = True
            else:
                picks[i] = _mgn(RNG.choice(_MGN_POOL[pool]), "mgn-u")
    if meals:
        i = meals[RNG.randrange(len(meals))]
        picks.setdefault(i, _mgn(RNG.choice(_MGN_POOL["meal"])))
    if frees and len(picks) < 3:
        i = frees[RNG.randrange(len(frees))]
        picks.setdefault(i, _mgn(RNG.choice(_MGN_POOL["free"])))
    head = ""
    sun = day.get("sun") or ""
    if "🌇" in sun:
        # take the HH:MM right after 🌇 — a suffix like "(AEST" or "(弗洛姆)"
        # glued to the time used to ride along and truncate the margin line
        m_ = re.search(r"\d{1,2}:\d{2}", sun.split("🌇")[-1])
        t = m_.group(0) if m_ else sun.split("🌇")[-1].strip().split()[0].strip("·")
        head = _mgn(RNG.choice([
            f"sunset {t} — chase it!", f"golden hour ≈ {t}",
            f"{t}: look west!", f"light dies at {t}, use it all",
            f"sunset {t}, be somewhere high"]), "mgn-head")
    elif day.get("travel_day"):
        head = _mgn("wheels up today ✈", "mgn-head")
    return picks, head


def render_tag(tag):
    if not tag:
        return ""
    if tag.startswith("swap"):
        body = tag.split("→", 1)[-1]
        return f'<span class="tg tg-swap">⇄ {T("tag.swap")}:{esc(body)}</span>'
    label = tag_pretty(tag)
    cls = {"pinned": "tg-pin", "skippable": "tg-cut", "opener": "tg-go"}.get(tag, "tg-cut")
    return f'<span class="tg {cls}">{esc(label)}</span>'


def render_rows(day, marg=None):
    marg = marg or {}
    rows = []
    for n, r in enumerate(day.get("timeline", [])):
        kind = r.get("kind", "anchor")
        mark = ic("meal") if kind == "meal" else KIND_MARK.get(kind, "●")
        est = '<sup class="est">est</sup>' if r.get("verify") == "est" else ""
        price = (f' <span class="pr">{esc(r["price"])}</span>'
                 if r.get("price") else "")
        nav = ""
        if r.get("link"):
            nav = (f'<a class="gonav" href="{esc(r["link"])}" target="_blank" '
                   f'rel="noopener" aria-label="{esc(t("nav_to"))}{esc(r.get("what", ""))[:18]}">'
                   f'{ic("pin")}</a>')
        rows.append(
            f'<div class="en k-{kind}"><span class="mk" aria-hidden="true">{mark}</span>'
            f'<span class="en-t">{esc(r.get("t", ""))}</span>'
            f'<div class="en-x">{et(r.get("what", ""))}{est}{price} '
            f'{render_tag(r.get("tag", ""))}{marg.get(n, "")}{nav}</div></div>')
    return "".join(rows)


def render_pocket(day, i):
    links = []
    if day.get("day_map"):
        links.append(f'<a class="stub" href="{esc(day["day_map"])}" target="_blank" '
                     f'rel="noopener">{esc(t("day_route"))}</a>')
    for n, u in enumerate(day.get("hop_links", []), 1):
        links.append(f'<a class="stub" href="{esc(u)}" target="_blank" '
                     f'rel="noopener">{esc(t("hop_n").format(n=n))}</a>')
    embed = day_embed_url(day)
    if not (links or embed):
        return ""
    emb = (f'<div class="m-embed" data-src="{esc(embed)}">'
           f'<p class="m-ph">{esc(t("pocket_ph"))}</p></div>'
           if embed else "")
    stubs = f'<div class="stubs">{"".join(links)}</div>' if links else ""
    return (f'<details class="pocket"><summary>{ic("compass")} {esc(t("pocket").format(i=i))}'
            f' {ic("chevron", "chev")}</summary>{emb}{stubs}</details>')


def render_slips(day):
    notes = []
    wk = day.get("walking_km")
    if isinstance(wk, dict):
        notes.append(("walk", f"{T('walk')} ≈{wk.get('total', '?')} km", wk.get("how", "")))
    elif wk:
        notes.append(("walk", f"{T('walk')} ≈{wk} km", ""))
    if day.get("rain_alt"):
        notes.append(("rain", t("rain"), day["rain_alt"]))
    if day.get("late_cut"):
        notes.append(("clock", T("late_cut"), day["late_cut"]))
    if day.get("note"):
        notes.append(("note", t("note"), day["note"]))
    out = []
    for n, (icn, lab, b) in enumerate(notes):
        rot = ".7deg" if n % 2 else "-.6deg"
        body = f"<p>{et(b)}</p>" if b else ""
        # every other scrap gets a second washi across its lower corner
        w2 = wt("wt-s", f"--rot:{RNG.uniform(24, 42):.0f}deg") if n % 2 else ""
        out.append(f'<aside class="slip reveal" style="--rot:{rot}">{tape()}{w2}'
                   f'<b>{ic(icn)} {esc(lab)}</b>{body}</aside>')
    return "".join(out)


# diary-flavour quips (no itinerary facts) for days without a sketch doodle;
# dealt from a seeded shuffle so no two spreads repeat the same line
_QUIPS = ["what a day!", "legs = jelly, heart = full", "coffee first ☕",
          "note to self: sleep early", "worth every step", "pinch me…",
          "wish you were here", "already planning the return"]
_QUIP_DECK = RNG.sample(_QUIPS, len(_QUIPS))
_quip_i = [0]


def _next_quip():
    q = _QUIP_DECK[_quip_i[0] % len(_QUIP_DECK)]
    _quip_i[0] += 1
    return q


def render_day(i, day):
    date = day.get("date", "")
    art = ART.day(date, THEME)
    theme = ART.day_theme(date, day.get("city", ""))
    photo = data_uri(art.get("photo", ""))
    cap, cap_en = (list(art.get("caption") or []) + ["", ""])[:2]
    rot = "1.6deg" if i % 2 else "-1.4deg"
    marg, headnote = day_marginalia(day)
    pol = ""
    if photo:
        # corner fastening alternates: scanned tape / CSS washi (mock has both)
        if i % 3 == 0:
            corner = wt("wt-c1" if i % 2 else "wt-c2")
        else:
            corner = tape(rot=-38, cls="tape-c1") if i % 2 else tape(rot=42, cls="tape-c2")
        pstn = ""
        if i % 4 == 2:   # a ring soaked into the polaroid border
            pstn = ('<span class="stn s-ring pstn" aria-hidden="true" style="'
                    f'width:{RNG.uniform(78, 108):.0f}px;right:-14%;bottom:-12%;'
                    f'--rot:{RNG.uniform(-30, 30):.0f}deg;--sx:1;opacity:.5"></span>')
        figcap = (f'<figcaption>{esc(cap)}<i class="cur">{esc(cap_en)}</i></figcaption>'
                  if (cap or cap_en) else "")
        pol = (f'<figure class="pol reveal" style="--rot:{rot}">{tape()}{corner}{pstn}'
               f'<img src="{photo}" alt="{esc(cap)}">{figcap}'
               '</figure>')
    # extra 70s kodak prints for the day, straight from the timeline subjects
    extras = ""
    for n, ph in enumerate(art.get("photos2") or []):
        uri2 = data_uri(ph.get("stem", ""))
        if not uri2:
            continue
        r2 = RNG.uniform(1.2, 2.6) * (1 if (i + n) % 2 else -1)
        corner2 = (tape(rot=-38, cls="tape-c1") if n % 2
                   else tape(rot=42, cls="tape-c2"))
        cap2 = (f'<figcaption class="cav">{esc(ph["en"])}</figcaption>'
                if ph.get("en") else "")
        extras += (f'<figure class="pol kodak reveal" style="--rot:{r2:.1f}deg">'
                   f'{tape()}{corner2}<img src="{uri2}" alt="{esc(ph.get("alt", ""))}">'
                   f'{cap2}</figure>')
    # rail collage props from the kit (see docstring); a postcard, if any,
    # replaces the whole prop and is built after it
    prop, postcard = "", None
    for pr in art.get("props") or []:
        if pr.get("kind") == "postcard":
            postcard = pr
        else:
            prop += prop_html(pr)
    if prop:
        pw = wt("wt-p", f"--rot:{RNG.uniform(-14, 14):.0f}deg")
        prop = f'<span class="propw">{pw}{prop}</span>'
    # a farewell-style spread gets a postcard instead of a prop: taped in at
    # an angle, franked like real mail — one of the stamp scans plus a small
    # ring postmark cancelling its corner — and signed off with one Caveat
    # line (art: echo the day's data, e.g. the crater sunrise time).
    # Without a stem the postcard is the theme's plain linen card: the note
    # hand-written on the message half, the address rules on the other, the
    # stamp slot in the corner (dashed box when the trip has no scan) and
    # the same postmark — a picture-less card any trip can send.
    if postcard is not None:
        pc_uri = data_uri(postcard.get("stem", ""), "md") if postcard.get("stem") else ""
        st = postcard.get("stamp") or {}
        st_cls = slot(st.get("cls", ""))
        pc_stamp = (f'<span class="stampd {st_cls} pc-stamp" aria-hidden="true" '
                    f'style="--rot:{_rot(st.get("rot"))}deg"></span>'
                    if stamp_ok(st_cls) else "")
        if pc_uri:
            pc_note = (f'<figcaption class="cav pc-note">{esc(postcard["note"])}</figcaption>'
                       if postcard.get("note") else "")
            prop = (f'<figure class="postcard reveal" style="--rot:{_rot(postcard.get("rot"))}deg">'
                    f'{tape(rot=-7)}'
                    f'<span class="pc-card"><img src="{pc_uri}"'
                    f' alt="{esc(postcard.get("alt", ""))}"></span>'
                    f'{pc_stamp}'
                    f'{postmark(date, "pm-pc", killer=False)}'
                    f'{pc_note}'
                    '</figure>')
        elif not postcard.get("stem"):
            note_lines = "<br>".join(esc(l) for l in str(postcard.get("note", "")).split("\n"))
            pc_msg = (f'<span class="cav pc-msg" aria-hidden="true">{note_lines}</span>'
                      if postcard.get("note") else "")
            box = pc_stamp or '<span class="pc-box" aria-hidden="true"></span>'
            prop = (f'<figure class="postcard pc-plain reveal" style="--rot:{_rot(postcard.get("rot"))}deg">'
                    f'{tape(rot=-7)}'
                    f'<span class="pc-card pc-linen">{pc_msg}'
                    '<span class="pc-div" aria-hidden="true"></span>'
                    '<span class="pc-addr" aria-hidden="true"><i></i><i></i><i></i></span>'
                    f'{box}</span>'
                    f'{postmark(date, "pm-pc", killer=False)}'
                    '</figure>')
    # a poster day hangs its WPA-style print in the notes column: brass tack
    # up top, fabric tape on the corners (the mock pins its poster with
    # gingham), one Caveat line hand-set in the poster's blank kraft band.
    # No stem → the theme's own kraft-paper vintage frame: double rule,
    # `title` set big in Kaiti (Latin titles read as small caps), `line`
    # hand-written in the band, same tack and tapes.
    poster = ""
    po = art.get("poster") or {}
    po_uri = data_uri(po.get("stem", ""), "md") if po.get("stem") else ""
    if po_uri:
        pline = (f'<span class="cav pline" aria-hidden="true">{esc(po["line"])}</span>'
                 if po.get("line") else "")
        poster = (f'<figure class="poster reveal" style="--rot:{_rot(po.get("rot"))}deg">'
                  '<span class="ptack" aria-hidden="true"></span>'
                  '<span class="tape tp-g pst-1" aria-hidden="true" style="rotate:-42deg"></span>'
                  '<span class="tape tp-f pst-2" aria-hidden="true" style="rotate:38deg"></span>'
                  f'<img src="{po_uri}"'
                  f' alt="{esc(po.get("alt", ""))}">'
                  f'{pline}'
                  '</figure>')
    elif po and not po.get("stem") and (po.get("title") or po.get("line")):
        title = str(po.get("title", ""))
        t_lines = "<br>".join(esc(l) for l in title.split("\n"))
        n_t = max((sum(1 if ord(c) > 0x2E7F else 0.6 for c in l)   # CJK 1, Latin .6
                   for l in title.split("\n")), default=0)
        t_cls = ("po-t3" if n_t <= 3.2 else "po-t4" if n_t <= 4.2
                 else "po-t6" if n_t <= 6.2 else "po-t9")
        po_title = (f'<span class="hand po-title {t_cls}">{t_lines}</span>' if title else "")
        pline = (f'<span class="cav pline pline-css" aria-hidden="true">{esc(po["line"])}</span>'
                 if po.get("line") else "")
        poster = (f'<figure class="poster poster-css reveal" style="--rot:{_rot(po.get("rot"))}deg">'
                  '<span class="ptack" aria-hidden="true"></span>'
                  '<span class="tape tp-g pst-1" aria-hidden="true" style="rotate:-42deg"></span>'
                  '<span class="tape tp-f pst-2" aria-hidden="true" style="rotate:38deg"></span>'
                  f'<span class="po-sheet" role="img" aria-label="{esc(po.get("alt", title))}">'
                  '<span class="po-sun" aria-hidden="true"></span>'
                  f'{po_title}<span class="po-rule" aria-hidden="true"></span>{pline}</span>'
                  '</figure>')
    flora_edge = eflora(FLORA_EDGE_DAYS[i]) if i in FLORA_EDGE_DAYS else ""
    leg = LEG_BY_DATE.get(date)
    stamp = ""
    if leg and leg.get("from") and leg.get("to"):
        d = datetime.date.fromisoformat(date)
        uri = rect_stamp_uri([f"{leg['from']} → {leg['to']}",
                              f"DEPARTED {MON[d.month]} {d.day}"],
                             ink="#33567a", w=220, h=80, seed=30 + i, fs=27)
        stamp = rstamp(uri, RNG.uniform(150, 172), "rs-air")
    annot = art.get("annot", "")
    annot_html = (f'<p class="annot">✎ {esc(annot)}</p>' if annot else "")
    doodle = doodle_html(art.get("doodle") or {})
    if not doodle:
        q = _next_quip()
        doodle = (f'<div class="doodle" style="--rot:{RNG.uniform(-2.5, 2.5):.1f}deg" '
                  f'aria-hidden="true"><span class="dd-tail">{ARROW}'
                  f'<span class="cur dd-note dd-quip">{esc(q)}</span></span></div>')
    fly = ('<span class="fly">' + ic("plane") + f" {esc(t('travel_day'))}</span>"
           if day.get("travel_day") else "")
    # the sun tool writes 天亮 (zh) or dawn (en); show it in the page language
    sun = (f'<span class="dsun">{et(day["sun"].replace("天亮", T("sun.dawn")).replace("dawn", T("sun.dawn")))}</span>'
           if day.get("sun") else "")
    ribbon = (f'<p class="ribbon">{et(day["ribbon"])}</p>'
              if day.get("ribbon") else "")
    stains = stainfield(n_edge=RNG.randrange(2, 5), n_field=RNG.randrange(0, 2))
    en_html = (f'<span class="cur dsub">{esc(art["en"])}</span>'
               if art.get("en") else "")
    return f"""
<section class="day chap c{i}" id="d{i}">
 <div class="wrap dgrid">
  {stains}{flora_edge}
  <div class="spine"><span class="pin" aria-hidden="true">{i:02d}</span></div>
  <header class="dhead reveal">
    {postmark(date)}
    <p class="dsup">DAY {i:02d} · {esc(date[5:])} {weekday(date)} · {esc(day.get("city", ""))} {fly}</p>
    <h2 class="hand">{esc(theme)} {en_html}</h2>
    <p class="dlabel">{esc(day.get("label", ""))} {sun} {headnote}</p>
    {annot_html}
    {ribbon}
  </header>
  <div class="dmain">
    <div class="entries">{render_rows(day, marg)}</div>
    {render_pocket(day, i)}
  </div>
  <div class="drail">{pol}{extras}{prop}{stamp}</div>
  <div class="dnotes">{poster}{render_slips(day)}{doodle}</div>
  <div class="dfoot">
    <button class="xbtn no-export" data-x-for="#d{i}" data-x-label="DAY{i:02d}"
      title="{esc(t("save_day_title"))}">{esc(T("btn.save_day"))}</button>
  </div>
 </div>
</section>"""


def render_navpins(days):
    out = [(f'<a href="#top" aria-label="{esc(t("nav_cover_aria"))}">'
            f'<span class="pbead hand">{esc(t("nav_cover"))}</span></a>')]
    for i, d in enumerate(days, 1):
        theme = ART.day_theme(d.get("date", ""), d.get("city", ""))
        out.append(f'<a href="#d{i}" data-spy="d{i}" aria-label="{esc(t("nav_day_aria").format(i=i, theme=theme))}">'
                   f'<span class="pbead">{i}</span></a>')
    out.append(f'<a href="#appendix" data-spy="appendix" aria-label="{esc(t("nav_appx_aria"))}">'
               f'<span class="pbead hand">{esc(t("nav_appx"))}</span></a>')
    # the one tab that is not a page: a wide paper label, highlighter-washed
    # and ringed in red pen, because a lone 存 among eleven day tabs was a
    # feature nobody found (owner: 不是测试这个功能我都不一定会注意到)
    out.append('<a href="#" class="xbtn no-export" data-x-page '
               f'aria-label="{esc(t("nav_page_aria"))}" '
               f'title="{esc(t("nav_page_title"))}">'
               f'<span class="pbead pb-x hand">{esc(T("btn.save_page"))}</span></a>')
    return "".join(out)


def render_legs(legs):
    out = []
    for n, l in enumerate(legs):
        rot = ".5deg" if n % 2 else "-.5deg"
        backup = (f'<details class="bkp"><summary>{esc(t("backup"))}</summary>'
                  f'<p>{et(l["backup"])}</p></details>' if l.get("backup") else "")
        link = (f'<a class="stub" href="{esc(l["link"])}" target="_blank" '
                f'rel="noopener">{esc(T("price.check"))}</a>' if l.get("link") else "")
        pin = ('<span class="pclip" aria-hidden="true"></span>' if n == 0
               else wt("wt-pass", f"--rot:{RNG.uniform(-58, -34):.0f}deg"))
        out.append(f"""
<article class="pass reveal" style="--rot:{rot}">
  {pin}
  <div class="pass-l">
    <p class="pass-kind">{esc(l.get("type", ""))} · {esc(l.get("carrier", ""))}</p>
    <p class="pass-route">{esc(l.get("from", ""))} <span aria-hidden="true">✈</span>→ {esc(l.get("to", ""))}</p>
    <p class="pass-row">{esc(l.get("date", ""))} · {esc(l.get("dep", ""))} → {esc(l.get("arr", ""))}</p>
    <p class="pass-row">{esc(l.get("price", ""))} · {esc(l.get("bags", ""))}</p>
    {backup}
  </div>
  <div class="pass-r">{ic("plane", "pass-pl")}{link}</div>
</article>""")
    return "".join(out)


def render_hotels(hotels):
    out = []
    for h in hotels:
        opts = "".join(
            f'<li><a href="{esc(o.get("link", "#"))}" target="_blank" rel="noopener">'
            f'{esc(o.get("name", ""))}</a> <span class="mono band">{esc(o.get("band", ""))}</span></li>'
            for o in h.get("options", []))
        out.append(f'<div class="htl"><h3 class="hand">{ic("hotel")} {esc(h.get("base", ""))}'
                   f' · {esc(h.get("area", ""))}</h3><p class="why">{et(h.get("why", ""))}</p>'
                   f'<ul>{opts}</ul></div>')
    return "".join(out)


def render_budget(budget, total):
    rows = "".join(
        f'<tr><td>{esc(b.get("cat", ""))}</td>'
        f'<td class="amt">{esc(b.get("per_person", ""))}</td>'
        f'<td class="bnote">{esc(b.get("note", ""))}</td></tr>' for b in budget)
    return (f'<div class="tscroll"><table class="ledger">'
            f'<tr><th>{esc(t("th_item"))}</th><th>{esc(t("th_cost"))}</th><th>{esc(t("th_note"))}</th></tr>{rows}'
            f'<tr class="total"><td>{esc(t("total"))}</td><td colspan="2">{esc(total)}</td></tr>'
            '</table></div>')


def render_checklist(items):
    out = []
    for c in items:
        link = (f' <a class="stub" href="{esc(c["link"])}" target="_blank" '
                f'rel="noopener">{esc(c.get("link_text", T("link")))}</a>'
                if c.get("link") else "")
        note = f'<p class="cknote">{et(c["note"])}</p>' if c.get("note") else ""
        out.append(f'<li><b>{et(c.get("item", ""))}</b>'
                   f' <span class="ddl">{esc(t("ddl"))}{esc(c.get("deadline", ""))} · {esc(c.get("price", ""))}</span>'
                   f'{link}{note}</li>')
    return '<ol class="ck">' + "".join(out) + "</ol>"


def render_brief(brief):
    cells = []
    titles = brief_titles(ART)
    for k, v in brief.items():
        t = titles.get(k, k)
        # each memo is filed under a little washi index sticker
        sticker = wt("wt-m", f"--rot:{RNG.uniform(-6, 6):.0f}deg")
        cells.append(f'<div class="memo">{sticker}<h3 class="hand">{esc(t)}</h3>'
                     f'<p>{et(v)}</p></div>')
    return "".join(cells)


def _js_lit(s):
    """Single-quoted JS literal (zh: '当日路线地图' — the historical bytes)."""
    return "'" + str(s).replace("\\", "\\\\").replace("'", "\\'").replace("</", "<\\/") + "'"


def sec_head(anchor, seal_char, title, stamp=""):
    aid = f' id="{anchor}"' if anchor else ""
    return (f'<h2 class="sec hand"{aid}><span class="sqseal" aria-hidden="true">'
            f'{seal_char}</span>{esc(title)}{stamp}</h2>')


def h1_size_cls(title):
    """(class, style attr) for the cover word by its length: CJK counts 1, Latin/digits
    ~0.6 (Kaiti sets them narrower). h1-3 = the original size (2-3 chars),
    h1-4 a notch down, h1-6 smaller, h1-x = shrink-to-fit for anything
    longer (the CSS also caps every tier ≥4 by container width, so a title
    never breaks into two lines at any viewport)."""
    n = sum(1 if ord(c) > 0x2E7F else 0.6 for c in title.strip())
    if n <= 3.2:
        return "h1-3", ""
    if n <= 4.2:
        return "h1-4", ""
    if n <= 6.2:
        return "h1-6", ""
    return "h1-x", f' style="--n:{n:.1f}"'      # shrink-to-fit needs the count


def cover_pol(uri, ph, cap):
    """The cover polaroid (art themes.journal.cover.photo); '' without one."""
    if not uri:
        return ""
    alt = ph.get("alt") or cap[0]
    figcap = (f'<figcaption>{esc(cap[0])}<i class="cur">{esc(cap[1])}</i></figcaption>'
              if (cap[0] or cap[1]) else "")
    return (f'<figure class="pol covpol reveal" style="--rot:2.4deg">{tape()}\n'
            f'     <img src="{uri}" alt="{esc(alt)}">\n'
            f'     {figcap}\n'
            '   </figure>')


def render_endcap(end, end_date):
    """The closing spread: postmark (needs end.date), the hand-written line,
    the fine print — each only when art supplies it — then the chop + seal."""
    pm = postmark(end_date, "pm-big", city=end.get("mark", "") or "") if end_date else ""
    line = f'<p class="hand endline">{esc(end["line"])}</p>' if end.get("line") else ""
    fine = f'<p class="endfine">{esc(end["fine"])}</p>' if end.get("fine") else ""
    return f"""{pm}
    {line}
    {fine}""" if (pm or line or fine) else ""


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
    tj = ART.theme(THEME)
    cover = ART.cover(THEME)
    end = ART.end(THEME)
    first_date = days[0].get("date", "") if days else ""
    pm_date = cover.get("postmark_date") or first_date
    year = pm_date[:4]
    # h1 = cover.zh (the theme's own poem title wins over the common one via
    # Art.cover's merge); kick is only the <title>/filename prefix
    kick = title_kick(ART, THEME) or cover.get("zh") or t("fallback_title")
    title_head = " ".join(x for x in (kick, "" if year and year in kick else year) if x)  # "MEXICO 2026" → year once
    h1 = cover.get("zh") or cover.get("kick") or t("fallback_title")
    h1_cls, h1_style = h1_size_cls(h1)
    # airport-code stamps read the legs array — the authoritative field —
    # never sniffed out of prose (manual: don't infer what the data states)
    for leg in p.get("legs", []):
        LEG_BY_DATE.setdefault(leg.get("date", ""), leg)

    tones = paper_chain(len(days) + 2)   # cover + 11 days + appendix
    chap_css = "".join(
        f".c{i}{{background:"
        f"url(\"{NOISE}\"),linear-gradient(180deg,{tones[i]},{tones[i + 1]})}}\n"
        for i in range(len(days) + 2))

    days_html = "".join(render_day(i + 1, d) for i, d in enumerate(days))
    decisions = "".join(f"<li>{et(x)}</li>" for x in p.get("decisions", []))
    unverified = "".join(f'<li>{ic("alert", "warn")} {et(x)}</li>'
                         for x in p.get("unverified", []))
    dates_txt = short_dates(meta.get("dates", "")).replace(" → ", " – ").replace("-", ".")

    css = CSS
    css = css.replace("__CAVEAT__", base64.b64encode(
        (HERE / "assets" / "caveat-vf.woff2").read_bytes()).decode())
    css = css.replace("__NOISE__", NOISE)
    css = css.replace("__ROUTE_D__", route_tile(88, 560, 30, 3.6))
    css = css.replace("__ROUTE_M__", route_tile(44, 300, 14, 2.6))
    css = css.replace("__TORN_ENV__", TORN_ENV)
    css = css.replace("__TORN_SLIP__", TORN_SLIP)
    css = css.replace("__PCLIP__", PCLIP)
    css = css.replace("__TORN_TILE__", TORN_TILE)
    css = css.replace("__SPECK__", SPECK)
    for k, u in STN_URIS.items():
        css = css.replace(f"__STN_{k.upper()}__", u)
    for cls, stem in (("tp-a", "journal-tape-a"), ("tp-b", "journal-tape-b"),
                      ("tp-c", "journal-tape-c"), ("tp-d", "journal-tape-d"),
                      ("tp-e", "journal-washi-floral"), ("tp-f", "journal-washi-ticking"),
                      ("tp-g", "journal-washi-gingham"),
                      ("fl-a", "journal-flower-a"), ("fl-b", "journal-flower-b"),
                      ("fl-daisy", "journal-flora-daisy"), ("fl-fern", "journal-flora-fern"),
                      ("fl-maple", "journal-flora-maple"),
                      ("sealbg", "journal-seal"), ("bagtag", "journal-tag")):
        css = css.replace(f"__{cls.upper().replace('-', '_')}__", data_uri(stem))
    # the three stamp slots take whatever scans art assigned; an empty slot
    # paints nothing (and stamp_ok() keeps it out of the HTML anyway)
    stems = stamp_stems()
    for cls in STAMP_SLOTS:
        uri = data_uri(stems.get(cls, ""))
        tok = f'url("__{cls.upper().replace("-", "_")}__")'
        css = css.replace(tok, f'url("{uri}")' if uri else "none")
    css += chap_css
    css += flora_custom_css()      # trip-owned pressings met while rendering days
    if lang() != "zh":
        css += CSS_EN              # Latin-length fixes; zh bytes untouched

    cover_stamps = (
        '<div class="stamps" aria-hidden="true">'
        + "".join(f'<span class="stampd {slot(s.get("cls", ""))}" style="--rot:{_rot(s.get("rot"))}deg"></span>'
                  for s in (tj.get("cover_stamps") or []) if stamp_ok(s.get("cls", "")))
        + (f'{postmark(pm_date, "pm-cover")}' if pm_date else "") + '</div>')
    cov_photo = cover.get("photo") or {}
    cov_uri = data_uri(cov_photo.get("stem", "")) if isinstance(cov_photo, dict) else ""
    cov_cap = (list(cov_photo.get("caption") or []) + ["", ""])[:2] if cov_uri else ["", ""]
    # cover copy = cover.sub only ("\n" = line break); the poem word is the h1
    cov_copy = "<br>".join(esc(x) for x in str(cover.get("sub") or "").split("\n") if x)
    cov_copy = f'<p class="cov-copy">{cov_copy}</p>' if cov_copy else ""
    cov_credit = (f'<p class="cov-credit">{esc(cover["credit"])}</p>'
                  if cover.get("credit") else "")
    n_legs = len(p.get("legs", []))
    ntxt = NUM_ZH[n_legs] if (lang() == "zh" and n_legs <= 10) else str(n_legs)

    # office-stamp props (all SVG, zero-cost): cover airmail chop, the
    # appendix section chops, and the farewell chop on the endcap
    st_airmail = rstamp(rect_stamp_uri(["AIR MAIL", "FIRST FLIGHT OUT"],
                                       ink="#33567a", w=236, h=84, seed=41, fs=30),
                        168, "rs-cover", rot=7.5)
    st_change = rstamp(rect_stamp_uri(["SUBJECT TO CHANGE"], ink="#33567a",
                                      w=344, h=58, seed=42, fs=24),
                       206, "rs-sec", rot=-4)
    st_paid = rstamp(rect_stamp_uri(["PAID", "EST. ONLY"],
                                    ink="#9c352c", w=220, h=88, seed=43, fs=34),
                     150, "rs-sec", rot=-8)
    st_appr = rstamp(rect_stamp_uri(["APPROVED"], ink="#9c352c", w=250, h=62,
                                    seed=44, fs=30),
                     162, "rs-sec", rot=-6)
    st_done = rstamp(rect_stamp_uri(["TRIP COMPLETE", end.get("farewell") or "HOMEWARD BOUND"],
                                    ink="#9c352c", w=280, h=88, seed=45, fs=28),
                     196, "rs-end", rot=-5)
    ghost_pm = ""
    if pm_date:
        d0 = datetime.date.fromisoformat(pm_date)
        ghost_pm = ('<span class="pm pm-ghost" aria-hidden="true" style="'
                    f'background-image:url({postmark_uri("FIRST DAY OF ISSUE", MON[d0.month], d0.day, d0.year, seed=51)});'
                    '--rot:14deg"></span>')
    cover_stains = stainfield(4, 1)
    appx_stains = stainfield(5, 2)

    html_out = f"""<!doctype html>
<html lang="{T("html_lang")}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title_head)} · {esc(t("title_suffix"))}</title>
<style>
{css}
</style>
</head>
<body>
{sprite()}

<div class="book">
<header class="chap cover c0" id="top">
 <div class="covroute" aria-hidden="true"></div>
 <div class="wrap cov">
  {cover_stains}
  {ghost_pm}
  {cover_stamps}
  {wt("wt-cov1", "--rot:-38deg")}
  {wt("wt-cov2", "--rot:26deg")}
  <div class="envelope reveal" style="--rot:-1.1deg">
   <div class="env-in">
    {st_airmail}
    <span class="airmail">{ic("plane")} VIA AIR MAIL</span>
    <p class="eyebrow">{esc(t("eyebrow"))} · {year}</p>
    <h1 class="hand {h1_cls}"{h1_style}>{esc(h1)}</h1>
    <p class="dates">{esc(dates_txt)}</p>
    {cov_copy}
    {cov_credit}
    <p class="cov-route">{esc(meta.get("route", ""))}</p>
   </div>
  </div>
  <div class="cov-side">
   <p class="cur covq">the world is a book, and those<br>who do not travel<br>read only one page.</p>
   <span class="sealbg" aria-hidden="true"></span>
   {cover_pol(cov_uri, cov_photo, cov_cap)}
  </div>
  <span class="flower fl-a" aria-hidden="true"></span>
  <a class="cue" href="#d1"><span class="hand">{esc(t("cue"))}</span>
    <svg width="16" height="26" viewBox="0 0 16 26" aria-hidden="true"><path d="M8 1 C 6 8 10 12 8 18 M3 14 L8 21 L13 14" fill="none" stroke="#8f2f27" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></a>
 </div>
</header>

<nav class="pins" aria-label="{esc(t("nav_aria"))}"><div class="pinrow">{render_navpins(days)}</div></nav>

<main>
<div class="dayswrap">
  <div class="route" aria-hidden="true"></div>
  {days_html}
</div>

<section class="chap appendix c{len(days) + 1}" id="appendix">
 <div class="wrap">
  {appx_stains}{eflora("L")}
  {sec_head("legs", t("seal_legs"), t("sec_legs"), st_change)}
  <p class="secsub">{esc(t("legs_sub").format(n=ntxt))}</p>
  {render_legs(p.get("legs", []))}

  {sec_head("hotels", t("seal_hotels"), t("sec_hotels"))}
  {render_hotels(p.get("hotels", []))}

  {sec_head("budget", t("seal_budget"), t("sec_budget"), st_paid)}
  {render_budget(p.get("budget", []), meta.get("budget_total", ""))}

  {sec_head("checklist", t("seal_check"), t("sec_check"), st_appr)}
  {render_checklist(p.get("checklist", []))}

  {sec_head("", t("seal_brief"), T("sec.brief"))}
  <div class="memos">{render_brief(p.get("brief", {}))}</div>

  {sec_head("", t("seal_dec"), T("sec.decisions"))}
  <ol class="dec">{decisions}</ol>

  {sec_head("", t("seal_unv"), T("sec.unverified"))}
  <ul class="unv">{unverified}</ul>

  <div class="endcap">
    {render_endcap(end, end.get("date", ""))}
    {st_done}
    <span class="sealbg seal-end" aria-hidden="true"></span>
  </div>

  <footer>
    {esc(p.get("trip", ""))}<br>
    {esc(meta.get("party", ""))} · {esc(t("fx"))} {esc(meta.get("fx", ""))}<br>
    {esc(meta.get("generated", ""))} · {esc(meta.get("self_check", ""))}<br>
    {esc(t("foot_ai"))}
  </footer>

  <div class="dfoot dfoot-appx">
    <button class="xbtn no-export xbtn-appx" data-x-for="#appendix"
      data-x-label="{esc(T("label.appendix"))}" title="{esc(t("save_appx_title"))}">{esc(T("btn.save_appendix"))}</button>
  </div>
 </div>
</section>
</main>
</div>

<script>
(function () {{
  document.documentElement.classList.add('js');
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  try {{
    if (reduce) {{
      document.querySelectorAll('.reveal').forEach(function (n) {{ n.classList.add('in'); }});
    }} else {{
      var io = new IntersectionObserver(function (es) {{
        es.forEach(function (e) {{
          if (e.isIntersecting) {{ e.target.classList.add('in'); io.unobserve(e.target); }}
        }});
      }}, {{ rootMargin: '0px 0px -7% 0px' }});
      document.querySelectorAll('.reveal').forEach(function (n) {{ io.observe(n); }});
    }}
  }} catch (err) {{
    document.querySelectorAll('.reveal').forEach(function (n) {{ n.classList.add('in'); }});
  }}

  // map pocket: the embed is only glued in when the pocket is opened
  document.querySelectorAll('details.pocket').forEach(function (d) {{
    d.addEventListener('toggle', function () {{
      if (!d.open) return;
      var box = d.querySelector('.m-embed');
      if (!box || box.dataset.on) return;
      box.dataset.on = '1';
      var f = document.createElement('iframe');
      f.referrerPolicy = 'no-referrer-when-downgrade';
      f.src = box.dataset.src;
      f.title = {_js_lit(t("map_title"))};
      f.addEventListener('load', function () {{
        var ph = box.querySelector('.m-ph'); if (ph) ph.remove();
      }});
      box.appendChild(f);
    }});
  }});

  // brass-pin scrollspy: the pin nearest the reading line presses down.
  try {{
    var spyIds = [];
    document.querySelectorAll('.pins a[data-spy]').forEach(function (a) {{
      spyIds.push(a.getAttribute('data-spy'));
    }});
    var strip = document.querySelector('.pinrow');
    var ticking = false;
    function mark() {{
      ticking = false;
      var line = innerHeight * 0.38, act = null;
      for (var i = 0; i < spyIds.length; i++) {{
        var el = document.getElementById(spyIds[i]);
        if (el && el.getBoundingClientRect().top <= line) act = spyIds[i];
      }}
      document.querySelectorAll('.pins a').forEach(function (a) {{
        var on = a.getAttribute('data-spy') === act;
        a.classList.toggle('on', on);
        if (on && strip) {{
          var x = a.offsetLeft - strip.clientWidth / 2 + a.offsetWidth / 2;
          strip.scrollTo({{ left: x, behavior: reduce ? 'auto' : 'smooth' }});
        }}
      }});
    }}
    addEventListener('scroll', function () {{
      if (!ticking) {{ ticking = true; requestAnimationFrame(mark); }}
    }}, {{ passive: true }});
    addEventListener('resize', mark);
    mark();
  }} catch (err) {{}}
}})();
</script>
<script>
EXPORT_JS_PLACEHOLDER
</script>
</body>
</html>"""
    html_out = html_out.replace("EXPORT_JS_PLACEHOLDER", export_js(
        theme_name(THEME), "#241a10",
        extra_css=(".reveal,.js .reveal,.reveal.in{opacity:1!important;"
                   "transform:rotate(var(--rot,0deg))!important}"),
        page_root=".book", file_prefix=export_prefix(ART, meta, THEME)))
    out = pathlib.Path(args.out)
    out.write_text(html_out, encoding="utf-8")
    print(f"{out.name}: {out.stat().st_size // 1024}KB, days={len(days)}, "
          f"assets={asset_count()}")


CSS = """
  /* Caveat variable font (wght 400-700) © Impallari Type — SIL Open Font
     License 1.1; embedded as a data URI so the double-clicked file:// page
     stays fully offline. The url() is deliberately unquoted (defect ⑧). */
  @font-face { font-family:'Caveat'; font-style:normal; font-weight:400 700;
    font-display:swap;
    src:url(data:font/woff2;base64,__CAVEAT__) format('woff2'); }
  :root {
    --hand:"Kaiti SC","STKaiti",KaiTi,"TW-Kai",cursive;
    --mono:"Courier Prime","Courier New",Courier,monospace;
    /* every English hand-note leads with Caveat; the old platform cursive
       stack stays behind it as the fallback voice. Caveat sets narrower and
       lighter than Snell at equal px, so its sizes run +1-2px throughout. */
    --curs:'Caveat',"Snell Roundhand","Apple Chancery","Segoe Script",cursive;
    /* ink ramp re-derived for the parchment tile: every token holds AA on
       the darkest chapter tone + mottle + a faint under-text stain (worst
       case #dacaa9, all ≥4.5 — computed, not eyeballed) */
    --ink:#35291a; --soft:#57472f; --blue:#2c4a63; --blue-soft:#36536c;
    --red:#852b23; --gold:#63490e; --rule:rgba(44,74,99,.16);
    --spinew:88px;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  html { scroll-behavior:smooth; }
  /* the journal is an OBJECT lying on a dark desk — everything lives inside
     .book; the desk only exists so the paper has something to be real on */
  body { color:var(--ink); font-family:var(--hand),serif; overflow-x:clip;
    background:#241a10;
    background-image:radial-gradient(130% 90% at 50% -8%, rgba(126,94,52,.30), transparent 62%); }
  /* NO overflow:clip here — a rounded clip mask over a 12k-px element makes
     compositors rasterise the whole book as one texture and give up (same
     failure family as the clay road's world-length paths). The few px of
     chapter colour that poke past the 5-9px corner radii are invisible. */
  .book { position:relative; max-width:1380px;
    margin:clamp(8px,2.5vw,40px) auto clamp(16px,3vw,52px);
    background:#f4ead6; border-radius:5px 9px 8px 6px;
    box-shadow:0 1px 0 #e6d9bd, 0 3px 0 #ddcda9, 0 5px 0 #d3c096,
      0 34px 70px -22px rgba(0,0,0,.72); }
  /* age lives ON the paper: toasted edges, corner scorch, a breathing
     vignette and foxing blotches — painted over the chapter gradients (z:2)
     but under every wrap's content (tree order). Edge bands stay inside the
     wrap padding so body type never sits on the darkest zones. */
  .book::before { content:""; position:absolute; inset:0; z-index:2;
    pointer-events:none; border-radius:inherit;
    background:
      radial-gradient(300px 210px at 6% 9%, rgba(150,108,55,.13), transparent 70%),
      radial-gradient(360px 250px at 95% 24%, rgba(150,108,55,.10), transparent 70%),
      radial-gradient(320px 240px at 12% 64%, rgba(150,108,55,.11), transparent 70%),
      radial-gradient(280px 220px at 88% 86%, rgba(150,108,55,.12), transparent 70%),
      radial-gradient(240px 180px at 50% 3%, rgba(150,108,55,.07), transparent 70%),
      radial-gradient(140% 120% at 50% 42%, transparent 58%, rgba(104,72,30,.05) 78%,
        rgba(92,62,24,.12) 96%),
      radial-gradient(190px 190px at 0% 0%, rgba(96,62,22,.20), transparent 72%),
      radial-gradient(190px 190px at 100% 0%, rgba(96,62,22,.16), transparent 72%),
      radial-gradient(220px 220px at 0% 100%, rgba(96,62,22,.18), transparent 72%),
      radial-gradient(220px 220px at 100% 100%, rgba(96,62,22,.20), transparent 72%),
      linear-gradient(90deg, rgba(116,82,38,.22), rgba(116,82,38,.07) 1.1%, transparent 2.6%,
        transparent 97.4%, rgba(116,82,38,.07) 98.9%, rgba(116,82,38,.22)),
      linear-gradient(180deg, rgba(116,82,38,.18), rgba(116,82,38,.05) .9%, transparent 2%,
        transparent 98%, rgba(116,82,38,.06) 99.1%, rgba(116,82,38,.24)); }
  /* dog-eared bottom-right corner */
  .book::after { content:""; position:absolute; right:0; bottom:0; z-index:2;
    width:74px; height:74px; pointer-events:none; border-radius:0 0 8px 0;
    background:linear-gradient(315deg, #241a10 8%, #cbb98f 9.5%, #f8efdc 27%,
      rgba(244,234,214,0) 52%); }

  /* ---- the stain family: one small pre-rasterised SVG per species ---- */
  .stn { position:absolute; z-index:-1; pointer-events:none;
    background:center/contain no-repeat;
    transform:rotate(var(--rot,0deg)) scaleX(var(--sx,1)); }
  .s-ring { background-image:url("__STN_RING__"); aspect-ratio:210/200; }
  .s-ink  { background-image:url("__STN_INK__");  aspect-ratio:190/170; }
  .s-wtr  { background-image:url("__STN_WTR__");  aspect-ratio:260/240; }
  .s-fp   { background-image:url("__STN_FP__");   aspect-ratio:96/118; }
  .s-wax  { background-image:url("__STN_WAX__");  aspect-ratio:150/130; }
  .s-smg  { background-image:url("__STN_SMG__");  aspect-ratio:220/90; }
  .s-spat { background-image:url("__STN_SPAT__"); aspect-ratio:160/140; }
  .pstn { z-index:1; }   /* soaked into a polaroid's border, above its paper */
  [id] { scroll-margin-top:84px; }
  a { color:var(--blue); }
  :focus-visible { outline:3px solid var(--blue); outline-offset:3px; border-radius:3px; }
  .hand { font-family:var(--hand),serif; }
  .mono, .en-t, .pr, .ddl, .band, .est, .dsup, .amt { font-family:var(--mono); }
  .cur { font-family:var(--curs); color:var(--gold); font-style:normal; }
  .ic { width:1em; height:1em; fill:none; stroke:currentColor; stroke-width:1.9;
    stroke-linecap:round; stroke-linejoin:round; vertical-align:-.12em; }
  .ic.warn { color:var(--red); }

  .wrap { max-width:1240px; margin:0 auto; padding-left:clamp(18px,4vw,56px);
    padding-right:clamp(18px,4vw,56px); }
  .chap { position:relative; }
  /* .chap is positioned, so chapter backgrounds paint in tree order AFTER the
     route (which comes first in the DOM). The route must sit ABOVE chapter
     paper (z:1) and BELOW every chapter's content (wrap z:2) — this is the
     "global decoration line vs chapter backgrounds" defect class from the
     manual, solved by explicit layering instead of hope. */
  .chap > .wrap { position:relative; z-index:2; }

  /* ---- the pen route stitched down the spine of every day ---- */
  .dayswrap { position:relative; }
  .route { position:absolute; top:0; bottom:0; z-index:1; pointer-events:none;
    left:calc(max(0px, 50% - 620px) + clamp(18px,4vw,56px));
    width:var(--spinew);
    background:url("__ROUTE_D__") 50% 0 / var(--spinew) auto repeat-y; }

  /* ---- brass push-pins ---- */
  .pin { display:inline-grid; place-items:center; width:52px; height:52px;
    border-radius:50%;
    background:radial-gradient(circle at 35% 28%, #e6c97f, #b58f3f 55%, #7a5c22 94%);
    box-shadow:inset 0 2px 4px rgba(255,240,200,.65), inset 0 -3px 5px rgba(60,40,5,.45),
      0 5px 10px -3px rgba(50,35,8,.55);
    color:#2a2008; font:700 15px/1 var(--mono); letter-spacing:.04em;
    text-shadow:0 1px 0 rgba(255,235,180,.4); }
  .spine { display:flex; justify-content:center; padding-top:14px; }

  /* sticky index-tab nav: a strip of the SAME parchment torn off across the
     desk, with paper index tabs glued on — no dark chrome, no leather, no
     "modern UI" material anywhere near it */
  .pins { position:sticky; top:0; z-index:40;
    background:url("__NOISE__"), linear-gradient(180deg,#f0e3c4,#e9dab7 76%,#e2d1a9);
    box-shadow:0 8px 16px -10px rgba(40,26,8,.55); }
  .pins::after { content:""; position:absolute; left:0; right:0; bottom:-8px;
    height:9px; pointer-events:none;
    background:url("__TORN_TILE__") left top/72px 9px repeat-x; }
  .pinrow { position:relative; display:flex; gap:7px; overflow-x:auto;
    scrollbar-width:none; padding:6px 14px 7px; }
  .pinrow::-webkit-scrollbar { display:none; }
  .pins a { flex:0 0 auto; min-width:44px; height:46px; display:grid;
    place-items:center; text-decoration:none; position:relative; }
  .pbead { width:33px; height:39px; border-radius:3px 3px 7px 7px;
    display:grid; place-items:center; position:relative;
    background:linear-gradient(180deg,#f7edd5,#eadcba);
    box-shadow:0 2px 3px rgba(96,66,28,.30), inset 0 -2px 0 rgba(116,82,38,.16),
      inset 0 1px 0 rgba(255,250,235,.7);
    color:#3c2f1a; font:700 12.5px/1 var(--mono);
    transition:translate .18s ease; }
  .pbead.hand { font:700 13.5px/1 var(--hand); }
  /* index tabs cycle through pale sticker tints, like a tab-divider set */
  .pins a:nth-child(4n+2) .pbead { background:linear-gradient(180deg,#eee7cd,#dfd8b4); }
  .pins a:nth-child(4n+3) .pbead { background:linear-gradient(180deg,#f2e6cf,#e6d2b2); }
  .pins a:nth-child(4n) .pbead   { background:linear-gradient(180deg,#ebe3d0,#dcd4bc); }
  .pins a:nth-child(odd) .pbead { rotate:.9deg; }
  .pins a:nth-child(even) .pbead { rotate:-.8deg; }
  /* the active tab is circled by hand in red ink and pulled down a notch */
  .pins a.on .pbead { translate:0 3px; background:linear-gradient(180deg,#fbf3de,#f0e3c2); }
  /* :not(.xbtn) — the spy toggles `on` by comparing data-spy to the active id,
     and both are null on the export tab, so it inherited the cover's ring and
     wore a red ellipse on top of its own red box */
  .pins a.on:not(.xbtn) .pbead::after { content:""; position:absolute; inset:-1px -6px -3px -6px;
    border:2.2px solid rgba(138,45,37,.78);
    border-radius:46% 54% 50% 50% / 60% 46% 58% 42%; rotate:-3deg; }

  /* ---- cover: an airmail envelope torn open on the first page ---- */
  .cover { min-height:100svh; display:flex; align-items:center; }
  .cov { display:grid; grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);
    gap:clamp(20px,4vw,54px); align-items:center; width:100%;
    padding-top:96px; padding-bottom:110px; position:relative; }
  .stamps { position:absolute; top:26px; right:clamp(18px,4vw,56px);
    display:flex; gap:12px; align-items:flex-start; }
  .stampd { display:inline-block; width:74px; height:80px;
    background-position:center; background-repeat:no-repeat; background-size:contain;
    rotate:var(--rot,0deg);
    filter:drop-shadow(0 3px 4px rgba(60,42,10,.3)); }
  /* the three slots: st-a / st-b portrait, st-wide landscape (art may still
     say st-lib / st-gg / st-bis — normalised before it reaches the HTML) */
  .st-a    { background-image:url("__ST_A__"); }
  .st-b    { background-image:url("__ST_B__"); }
  .st-wide { background-image:url("__ST_WIDE__"); width:84px; }
  /* postmarks are SVG rubber stamps now — grunge-inked circles with wavy
     cancellation bars, one per date, struck straight into the paper */
  .pm { display:inline-block; width:148px; aspect-ratio:236/156;
    background:left center/contain no-repeat; rotate:var(--rot,8deg); }
  .pm-cover { margin-left:-40px; margin-top:30px; }
  .pm-big { width:196px; }
  .pm-ghost { position:absolute; width:300px; left:30%; top:6%; opacity:.16;
    pointer-events:none; z-index:0; }

  /* office rubber stamps (APPROVED / PAID / airport chops) */
  .rstamp { display:inline-block; aspect-ratio:var(--ar,8/3);
    background:center/contain no-repeat; rotate:var(--rot,-6deg);
    pointer-events:none; }
  .rs-air { aspect-ratio:220/80; margin-top:6px; align-self:center; }
  .rs-cover { position:absolute; right:16px; top:14px; aspect-ratio:236/84;
    opacity:.92; }
  .rs-sec { aspect-ratio:auto; height:44px; margin-left:18px; flex:0 0 auto;
    translate:0 -4px; }
  .rs-end { aspect-ratio:280/88; }

  /* CSS washi: translucent (multiply) so the paper grain reads through,
     torn short ends, four sticker patterns cycling like the tape scans */
  .wt { position:absolute; width:92px; height:27px; pointer-events:none;
    z-index:2; mix-blend-mode:multiply; opacity:.82; rotate:var(--rot,-8deg);
    filter:drop-shadow(0 1px 1.5px rgba(60,42,10,.28));
    clip-path:polygon(2.5% 0%, 97% 3%, 99.2% 14%, 97.8% 32%, 100% 48%, 97.6% 66%,
      99.5% 82%, 96.4% 100%, 3% 97%, .6% 84%, 2.8% 64%, 0% 46%, 2.2% 28%, .4% 12%); }
  .wt-red { background:
    repeating-linear-gradient(90deg, rgba(176,58,48,.60) 0 9px, rgba(248,240,222,.55) 9px 18px); }
  .wt-navy { background:
    radial-gradient(circle 3px at 7px 8px, rgba(248,240,222,.75) 92%, transparent),
    radial-gradient(circle 3px at 16px 19px, rgba(248,240,222,.75) 92%, transparent),
    rgba(51,86,122,.52); background-size:18px 22px, 18px 22px, auto; }
  .wt-gold { background:
    repeating-linear-gradient(0deg, transparent 0 5px, rgba(255,251,238,.5) 5px 6.5px),
    rgba(198,150,58,.5); }
  .wt-sage { background:
    repeating-linear-gradient(90deg, transparent 0 6px, rgba(255,251,238,.55) 6px 7.5px),
    repeating-linear-gradient(0deg, transparent 0 6px, rgba(255,251,238,.55) 6px 7.5px),
    rgba(122,138,94,.5); }
  .wt-c1 { bottom:-12px; left:-24px; width:74px; }
  .wt-c2 { bottom:-12px; right:-24px; width:74px; }
  .wt-p { top:-13px; left:50%; margin-left:-44px; }
  .wt-s { bottom:6px; right:-6px; width:70px; height:22px; }
  .wt-pass { position:absolute; top:-11px; left:-20px; width:78px; z-index:3; }
  .wt-m { position:static; display:block; width:64px; height:20px; margin-bottom:8px; }
  .wt-cov1 { left:26%; top:9%; width:110px; height:30px; z-index:3; }
  .wt-cov2 { left:56.5%; bottom:17%; width:96px; z-index:3; }

  /* metal paperclip over the first flight ticket */
  .pclip { position:absolute; top:-16px; left:26px; width:30px; height:66px;
    z-index:3; pointer-events:none; background:url("__PCLIP__") center/contain no-repeat;
    rotate:6deg; filter:drop-shadow(0 2px 2px rgba(40,30,10,.35)); }

  /* washi anchor wrapper for glued props */
  .propw { position:relative; display:inline-block; }

  /* marginalia: Caveat English asides inked beside real rows */
  .mgn { display:inline-block; font:16.5px/1.35 var(--curs); font-style:normal;
    letter-spacing:.02em; margin-left:10px; rotate:var(--mr,-3deg);
    translate:0 -2px; white-space:nowrap; }
  .mgn-sep { color:#4a3a24; } .mgn-blu { color:#334c69; } .mgn-red { color:#852b23; }
  .mgn-u { text-decoration:underline wavy currentColor 1px;
    text-underline-offset:4px; }
  .mgn::before { content:"← "; font-size:13px; opacity:.85; }
  .mgn-head::before { content:"✎ "; }
  .mgn-head { font-size:17.5px; margin-left:14px; }

  .envelope { clip-path:__TORN_ENV__; rotate:var(--rot,0deg);
    background:repeating-linear-gradient(45deg,
      #b03a30 0 14px, #f6eedb 14px 26px, #33567a 26px 40px, #f6eedb 40px 52px);
    padding:13px; filter:drop-shadow(0 14px 22px rgba(60,42,10,.35)); }
  /* container-type lets the h1 measure its own column (cqw) — the envelope
     column is a fixed fr track, so inline-size containment changes nothing
     about the layout; the tilt on .envelope already made the stacking context */
  .env-in { position:relative; background:linear-gradient(160deg,#f8f0dd,#f2e7cd);
    padding:clamp(26px,4vw,52px) clamp(22px,3.5vw,48px) clamp(30px,4vw,48px);
    container-type:inline-size; }
  .airmail { display:inline-flex; align-items:center; gap:7px;
    background:#33567a; color:#f4ead6; font:700 11px/1 var(--mono);
    letter-spacing:.22em; padding:7px 12px 6px; border-radius:2px; rotate:-1deg; }
  .eyebrow { margin-top:22px; font-size:13px; letter-spacing:.42em; color:var(--soft); }
  h1 { font-size:clamp(64px,10vw,118px); line-height:1.14; font-weight:700;
    color:var(--gold); letter-spacing:.1em; margin:6px 0 4px;
    text-shadow:0 1px 0 rgba(255,250,235,.6); white-space:nowrap; }
  /* the cover word never folds: 2-3 chars keep the full size (above); longer
     titles step down a tier AND are capped by the envelope's own width
     (100cqw = .env-in content box; --n = char count, ~1.12em per char with
     the tracking), so 「秋水长天」 sits on one line at every viewport */
  .h1-4 { font-size:min(clamp(54px,8.4vw,98px), calc(100cqw / 4.5)); letter-spacing:.07em; }
  .h1-6 { font-size:min(clamp(42px,6.4vw,74px), calc(100cqw / 6.6)); letter-spacing:.05em; }
  .h1-x { font-size:min(clamp(28px,4.8vw,58px), calc(100cqw / (var(--n,8) * 1.06)));
    letter-spacing:.03em; }
  .dates { display:inline-block; font:700 clamp(17px,2vw,22px)/1 var(--mono);
    color:var(--red); letter-spacing:.14em; border:2.5px solid rgba(143,47,39,.75);
    padding:8px 14px 7px; rotate:-1.4deg; border-radius:2px; margin:10px 0 18px; }
  .cov-copy { font-size:clamp(16px,1.8vw,19px); line-height:2; color:var(--ink); }
  .cov-credit { margin-top:8px; font-size:12.5px; line-height:1.9; color:var(--soft);
    letter-spacing:.02em; }
  .cov-route { margin-top:14px; font-size:12.5px; line-height:1.9; color:var(--soft); }
  .cov-side { display:flex; flex-direction:column; align-items:center; gap:18px; }
  .covq { font-size:clamp(19px,2.1vw,23px); line-height:1.65; text-align:center;
    rotate:2deg; }
  .sealbg { width:96px; height:99px; background:url("__SEALBG__") center/contain no-repeat;
    filter:drop-shadow(0 4px 6px rgba(60,42,10,.4)); }
  .covpol { max-width:240px; }
  .flower { position:absolute; left:clamp(6px,2vw,40px); bottom:84px; width:84px;
    background-position:center; background-size:contain; background-repeat:no-repeat;
    opacity:.9; rotate:-8deg; pointer-events:none; }
  /* the pen route already leaves the envelope on the cover, fading in from
     nothing and handing over seamlessly to .route at the fold (same tile,
     both anchored to the tile's centre-ended seam) */
  .covroute { position:absolute; bottom:0; height:190px; pointer-events:none;
    left:calc(max(0px, 50% - 620px) + clamp(18px,4vw,56px));
    width:var(--spinew);
    background:url("__ROUTE_D__") 50% 100% / var(--spinew) auto no-repeat;
    -webkit-mask-image:linear-gradient(180deg, transparent, #000 58%);
    mask-image:linear-gradient(180deg, transparent, #000 58%); }
  .cue { position:absolute; bottom:20px; left:50%; translate:-50% 0;
    display:flex; flex-direction:column; align-items:center; gap:2px;
    text-decoration:none; color:var(--red); font-size:15px;
    animation:bob 2s ease-in-out infinite; }
  @keyframes bob { 50% { transform:translateY(7px); } }

  /* ---- days ---- */
  .dgrid { display:grid; column-gap:clamp(16px,2.4vw,32px);
    grid-template-columns:var(--spinew) minmax(0,1fr) clamp(220px,24vw,300px);
    padding-top:58px; padding-bottom:30px; }   /* .dfoot now fills the rest */
  .spine  { grid-column:1; grid-row:1 / span 3; align-items:flex-start; }
  .dhead  { grid-column:2; grid-row:1; position:relative; padding-right:158px; min-width:0; }
  .dmain  { grid-column:2; grid-row:2 / span 2; min-width:0; padding-top:18px; }
  .drail  { grid-column:3; grid-row:1 / span 2; min-width:0;
    display:flex; flex-direction:column; align-items:center; gap:26px; }
  .dnotes { grid-column:3; grid-row:3; min-width:0; display:flex;
    flex-direction:column; gap:22px; padding-top:26px; }
  .dhead .pm { position:absolute; right:-8px; top:-12px; }
  .dsup { font-size:11.5px; letter-spacing:.16em; color:var(--blue); }
  .dsup .fly { display:inline-flex; align-items:center; gap:4px; margin-left:8px;
    font-size:10px; letter-spacing:.18em; color:var(--blue-soft);
    border:1px solid rgba(65,96,122,.55); padding:2px 7px 1px; border-radius:2px; }
  .dhead h2 { font-size:clamp(27px,3.2vw,34px); letter-spacing:.08em;
    margin:8px 0 6px; font-weight:700; }
  .dsub { font-size:clamp(18px,1.9vw,22px); margin-left:12px; letter-spacing:.02em; }
  .dlabel { font-size:15px; color:var(--ink); line-height:1.9; }
  .dsun { font-size:12.5px; color:var(--soft); margin-left:10px; white-space:nowrap; }
  .ribbon { margin-top:8px; font-size:13px; line-height:2; color:var(--soft);
    border-bottom:1px dashed rgba(93,76,51,.45); display:inline-block;
    padding-bottom:3px; max-width:100%; overflow-wrap:anywhere; }
  /* the day's inked aside — 「第一站:纽约…」 in the mock's handwriting voice */
  .annot { margin-top:10px; font-size:15px; line-height:2.1; color:#364f6a;
    max-width:36em; letter-spacing:.02em; }

  /* entries: ruled journal lines, no boxes */
  .en { display:flex; gap:10px; padding:9px 2px 8px; align-items:baseline;
    border-bottom:1px solid var(--rule); }
  .en:last-of-type { border-bottom:0; }
  .mk { flex:0 0 20px; text-align:center; color:var(--red); font-size:12px; }
  .k-hop .mk { color:var(--blue); font-size:14px; }
  .k-free .mk { color:var(--soft); }
  .k-meal .mk { color:var(--gold); font-size:14px; }
  .en-t { flex:0 0 96px; text-align:right; font-size:12.5px; font-weight:700;
    color:var(--blue); letter-spacing:.01em; }
  .en-x { flex:1 1 0; min-width:0; overflow-wrap:anywhere; font-size:14.5px;
    line-height:2; }
  .k-hop .en-x { color:var(--blue-soft); font-size:13.5px; }
  .k-hop .en-t { font-weight:400; }
  .k-free .en-x { color:var(--soft); }
  .est { font-size:9px; font-weight:700; color:var(--red); vertical-align:super;
    margin-left:2px; letter-spacing:.08em; }
  .pr { font-size:11.5px; color:var(--soft); margin-left:4px; }
  .tg { font-size:12px; margin-left:6px; }
  .tg-pin { display:inline-block; color:var(--red); font-weight:700;
    border:1.6px solid rgba(143,47,39,.8); padding:0 8px 1px;
    border-radius:46% 54% 48% 52% / 58% 42% 56% 44%; rotate:-1.6deg; }
  .tg-cut { color:var(--soft); border-bottom:1.5px dashed rgba(93,76,51,.7);
    padding-bottom:1px; }
  .tg-go { color:var(--ink); font-weight:700; padding:0 5px;
    background:linear-gradient(178deg, transparent 12%, rgba(231,190,94,.62) 13% 86%, transparent 87%); }
  .tg-swap { color:var(--blue-soft); border-bottom:1.5px dashed rgba(65,96,122,.6); }
  .gonav { display:inline-flex; align-items:center; justify-content:center;
    min-width:44px; min-height:44px; margin:-14px -10px -14px 0;
    color:var(--red); vertical-align:middle; }
  .gonav .ic { width:15px; height:15px; }

  /* map pocket: a kraft pocket sewn onto the page */
  .pocket { margin-top:20px; background:linear-gradient(#e9dbba,#e2d1a9);
    border:1.5px dashed #9a8455; border-radius:4px 16px 4px 4px;
    box-shadow:0 6px 14px -9px rgba(60,42,10,.5); }
  .pocket summary { list-style:none; cursor:pointer; user-select:none;
    display:flex; align-items:center; gap:10px; min-height:48px;
    padding:10px 16px; font-size:15.5px; color:#4a3b22; }
  .pocket summary::-webkit-details-marker { display:none; }
  .pocket summary::after { content:""; flex:1; border-bottom:1.5px dashed rgba(120,95,55,.45); }
  .pocket .chev { transition:transform .25s ease; }
  .pocket[open] .chev { transform:rotate(180deg); }
  .pocket > :not(summary) { margin:0 14px 14px; }
  .m-embed { border:1px solid #b7a172; background:#efe6cf; }
  .m-embed iframe { display:block; width:100%; height:300px; border:0; }
  .m-ph { padding:22px 16px; font-size:13px; color:#4a3b22; text-align:center;
    line-height:1.9; }
  .stubs { display:flex; flex-wrap:wrap; gap:8px; margin-top:12px !important; }
  .stub { display:inline-flex; align-items:center; min-height:44px;
    padding:0 15px 0 17px; background:#efe4c9; border:1px solid #b7a172;
    border-left:2.5px dotted #9a8455; border-radius:0 5px 5px 0;
    font:700 12px/1 var(--mono); letter-spacing:.08em; color:#54431f;
    text-decoration:none; rotate:-.4deg; }
  .stub:nth-child(even) { rotate:.5deg; }
  .stub:hover { background:#f4ebd4; }

  /* rail: polaroids and glued props */
  .pol { background:#fbf6ea; padding:10px 10px 13px; max-width:290px; width:100%;
    box-shadow:0 12px 24px -10px rgba(60,42,10,.5); position:relative;
    rotate:var(--rot,0deg); }
  .pol img { display:block; width:100%; height:auto; }
  .pol figcaption { padding-top:10px; text-align:center; font-size:15px;
    color:#4c3d28; line-height:1.7; }
  .pol figcaption .cur { display:block; font-size:15.5px; }
  .tape { position:absolute; top:-15px; left:50%; margin-left:-44px; width:88px;
    height:34px; background-position:center; background-size:contain;
    background-repeat:no-repeat; pointer-events:none; z-index:2;
    filter:drop-shadow(0 2px 3px rgba(60,42,10,.25)); }
  /* second strip pinning a corner, like the mock's doubly-taped polaroids */
  .tape-c1 { top:auto; bottom:-13px; left:-25px; margin-left:0; width:70px; }
  .tape-c2 { top:auto; bottom:-13px; left:auto; right:-25px; margin-left:0; width:70px; }
  .tp-a { background-image:url("__TP_A__"); } .tp-b { background-image:url("__TP_B__"); }
  .tp-c { background-image:url("__TP_C__"); } .tp-d { background-image:url("__TP_D__"); }
  /* the three wishlist fabric tapes ride the same counter as the scans */
  .tp-e { background-image:url("__TP_E__"); } .tp-f { background-image:url("__TP_F__"); }
  .tp-g { background-image:url("__TP_G__"); }
  .prop { rotate:var(--rot,0deg); filter:drop-shadow(0 6px 10px rgba(60,42,10,.35));
    max-width:100%; height:auto; }
  /* pressed-flora pool: one data URI per stem lives here in the stylesheet,
     so every placement (day prop, page-edge scatter, cover sprig) is just a
     class + width and repeats cost no extra bytes */
  .fl-a     { background-image:url("__FL_A__");     aspect-ratio:134/302; }
  .fl-b     { background-image:url("__FL_B__");     aspect-ratio:130/286; }
  .fl-daisy { background-image:url("__FL_DAISY__"); aspect-ratio:233/401; }
  .fl-fern  { background-image:url("__FL_FERN__");  aspect-ratio:284/451; }
  .fl-maple { background-image:url("__FL_MAPLE__"); aspect-ratio:314/417; }
  .propfl { display:inline-block; background-position:center;
    background-size:contain; background-repeat:no-repeat; }
  .eflora { position:absolute; z-index:2; pointer-events:none; opacity:.96;
    background-position:center; background-size:contain; background-repeat:no-repeat;
    rotate:var(--rot,0deg); filter:drop-shadow(0 4px 7px rgba(60,42,10,.32)); }
  .bagtag { display:inline-grid; place-items:center; width:120px; height:132px;
    background:url("__BAGTAG__") center/contain no-repeat; rotate:var(--rot,0deg);
    filter:drop-shadow(0 5px 9px rgba(60,42,10,.35)); }
  .bagtag-txt { font:700 17px/1.3 var(--mono); color:#4a3417; letter-spacing:.06em;
    text-align:center; margin-top:26px; rotate:-2deg; }
  .seal-sm { width:64px; height:66px; rotate:var(--rot,0deg); }

  /* 70s kodak prints: same white frame + tape system as the polaroids, a
     notch smaller so the day's hero photo keeps the lead; a light unifying
     age wash so the new scans sit in the same faded family */
  .cav { font-family:var(--curs); font-style:normal; }
  .pol.kodak { max-width:254px; }
  .pol.kodak img { filter:sepia(.11) saturate(.9) contrast(.96); }
  .pol.kodak figcaption { font-family:var(--curs); font-size:17px;
    line-height:1.45; padding-top:8px; }

  /* the WPA poster, tacked + fabric-taped into the notes column; the Caveat
     legend is hand-set inside the artwork's own blank kraft band (band ink
     #2e4636 on sampled band #dfad64 = 5.03:1, computed not eyeballed) */
  .poster { position:relative; max-width:300px; width:100%; align-self:center;
    margin-bottom:6px; filter:drop-shadow(0 14px 20px rgba(50,34,8,.4)); }
  .poster img { display:block; width:100%; height:auto;
    filter:sepia(.07) contrast(.97) saturate(.96); }
  .ptack { position:absolute; top:-8px; left:50%; margin-left:-8px; width:16px;
    height:16px; border-radius:50%; z-index:2;
    background:radial-gradient(circle at 35% 28%, #e6c97f, #b58f3f 55%, #7a5c22 94%);
    box-shadow:inset 0 1px 2px rgba(255,240,200,.65), 0 3px 4px -1px rgba(50,35,8,.55); }
  .pst-1 { top:-12px; left:-24px; margin-left:0; }
  .pst-2 { top:auto; bottom:-12px; left:auto; right:-24px; margin-left:0; }
  .pline { position:absolute; left:5%; right:5%; bottom:6.4%; text-align:center;
    font:700 21px/1.2 var(--curs); color:#2e4636; rotate:-.8deg; }
  /* the theme's own kraft poster (art poster without a stem): aged kraft
     sheet, a double rule, sun-disc, big Kaiti title, hand line in the band */
  .po-sheet { position:relative; display:flex; flex-direction:column;
    align-items:center; justify-content:center; gap:10px; width:100%;
    aspect-ratio:3/4; padding:11% 9% 15%; text-align:center;
    background:url("__NOISE__"),
      radial-gradient(120% 90% at 50% 8%, rgba(255,240,205,.5), transparent 60%),
      linear-gradient(170deg,#d9b57e,#c99c5f 55%,#b98a4d);
    box-shadow:inset 0 0 0 5px rgba(78,50,14,.28), inset 0 0 0 7px rgba(78,50,14,0),
      inset 0 0 0 8px rgba(78,50,14,.22), inset 0 0 40px rgba(78,50,14,.18); }
  .po-sun { position:absolute; left:50%; top:9%; width:38%; aspect-ratio:1;
    translate:-50% 0; border-radius:50%; pointer-events:none;
    background:radial-gradient(circle, rgba(226,120,64,.55) 0 55%, transparent 57%),
      repeating-radial-gradient(circle, transparent 0 4px, rgba(90,54,14,.16) 4px 5px);
    -webkit-mask-image:linear-gradient(180deg,#000 55%,transparent);
    mask-image:linear-gradient(180deg,#000 55%,transparent); }
  .po-title { position:relative; color:#3a2a12; font-weight:700; line-height:1.15;
    letter-spacing:.14em; margin-top:22%; text-shadow:0 1px 0 rgba(255,236,196,.55); }
  .po-t3 { font-size:54px; }
  .po-t4 { font-size:44px; letter-spacing:.1em; }
  .po-t6 { font-size:33px; letter-spacing:.08em; }
  .po-t9 { font-size:23px; letter-spacing:.06em; white-space:nowrap; }
  .po-rule { display:block; width:34%; height:0; border-top:2px solid rgba(58,42,18,.55);
    border-bottom:1px solid rgba(58,42,18,.45); padding-top:3px; }
  .pline-css { position:static; left:auto; right:auto; bottom:auto; margin-top:2px;
    color:#2e4636; }

  /* the hula postcard: taped in, franked like real mail (liberty stamp scan
     + a small ring postmark cancelling its corner), signed off in Caveat */
  .postcard { position:relative; max-width:288px; width:100%; }
  .pc-card { display:block; background:#f9f2e0; padding:7px 7px 9px;
    box-shadow:0 12px 22px -10px rgba(60,42,10,.5); }
  .pc-card img { display:block; width:100%; height:auto;
    filter:sepia(.05) saturate(.94); }
  .pc-stamp { position:absolute; top:13px; right:11px; width:56px; height:60px;
    z-index:2; opacity:.96; }
  .pm-pc { position:absolute; top:-16px; right:-18px; width:96px;
    aspect-ratio:1/1; z-index:3; opacity:.85; }
  .pc-note { display:block; margin-top:9px; font:600 18px/1.5 var(--curs);
    color:var(--blue); text-align:center; rotate:-1.2deg; }
  /* the plain postcard (art postcard without a stem): linen weave, message
     half + divider + address rules, stamp corner (dashed box when the trip
     has no scan for the slot); the ring postmark cancels it as always */
  .pc-linen { position:relative; display:grid; grid-template-columns:1fr auto 1fr;
    gap:0 10px; aspect-ratio:3/2; padding:44px 12px 14px 14px;
    background:
      repeating-linear-gradient(0deg, rgba(120,96,60,.07) 0 1px, transparent 1px 3px),
      repeating-linear-gradient(90deg, rgba(120,96,60,.07) 0 1px, transparent 1px 3px),
      linear-gradient(160deg,#f6efe0,#efe4cd); }
  .pc-msg { grid-column:1; align-self:end; font:600 16px/1.45 var(--curs);
    color:var(--blue); text-align:left; rotate:-1.6deg; overflow-wrap:anywhere; }
  .pc-div { grid-column:2; width:0; border-left:1.5px solid rgba(90,70,40,.35);
    margin:0 2px; }
  .pc-addr { grid-column:3; align-self:end; display:flex; flex-direction:column;
    gap:14px; padding-bottom:6px; }
  .pc-addr i { display:block; height:0; border-bottom:1.5px solid rgba(90,70,40,.35); }
  .pc-box { position:absolute; top:12px; right:12px; width:52px; height:58px;
    border:1.5px dashed rgba(90,70,40,.45); }
  /* vintage park entrance ticket, all CSS: deckled edge + double inner rule */
  .vtk { position:relative; display:grid; justify-items:center; gap:4px;
    width:156px; padding:16px 12px 14px; rotate:var(--rot,0deg);
    clip-path:__TORN_SLIP__; font-family:var(--mono); text-align:center;
    filter:drop-shadow(0 5px 8px rgba(60,42,10,.3)); }
  .vtk::before { content:""; position:absolute; inset:7px;
    border:1.5px solid currentColor; opacity:.5; pointer-events:none; }
  .vtk-green { background:linear-gradient(160deg,#dce4cd,#cbd6ba); color:#42522f; }
  .vtk-brown { background:linear-gradient(160deg,#e9dcc0,#dcc9a2); color:#5a4426; }
  .vtk b { font-size:14.5px; letter-spacing:.12em; }
  .vtk i { font-size:8.5px; letter-spacing:.14em; font-style:normal; opacity:.85; }
  .vtk em { font-size:17px; font-style:normal; font-weight:700; letter-spacing:.1em;
    border-top:1px solid currentColor; border-bottom:1px solid currentColor;
    padding:3px 9px 2px; margin:2px 0; opacity:.9; }
  .vtk u { font-size:9px; text-decoration:none; letter-spacing:.22em; opacity:.75; }

  /* slips: torn scraps taped into the margin */
  .slip { position:relative; background:linear-gradient(180deg,#f6ecd2,#efe2c0);
    clip-path:__TORN_SLIP__; padding:16px 15px 13px; width:100%;
    font-size:13.5px; line-height:1.95; color:var(--soft);
    rotate:var(--rot,0deg); filter:drop-shadow(0 7px 9px rgba(60,42,10,.3)); }
  .slip b { color:var(--ink); font-size:14px; font-weight:700; display:inline-block;
    border-bottom:2px solid rgba(143,47,39,.5); padding-bottom:2px; margin-bottom:5px; }
  .slip b .ic { color:var(--red); }
  .slip .tape { top:-8px; }

  /* margin doodles: one-line ink sketches with a hand note and a red arrow */
  /* flex-wrap + max-width: a note too wide for the row drops under the
     sketch instead of pushing the doodle out of the page */
  .doodle { align-self:center; display:flex; align-items:flex-end; gap:10px;
    flex-wrap:wrap; max-width:100%;
    rotate:var(--rot,0deg); color:#4a3b28; opacity:.85; padding:10px 4px 0; }
  .dd { width:auto; height:86px; flex:0 0 auto; }
  .dd path { fill:none; stroke:currentColor; stroke-width:1.7;
    stroke-linecap:round; stroke-linejoin:round; }
  .dd-arrow { width:30px; height:26px; margin-bottom:18px; flex:0 0 auto; }
  .dd-arrow path { fill:none; stroke:#8f2f27; stroke-width:1.8;
    stroke-linecap:round; stroke-linejoin:round; }
  /* nowrap: the author breaks lines with "\n"; without it a CJK note's
     min-content is ONE character and the flex row squeezed it into a
     one-char-per-line column (AU/Nordic test trips, 2026-08-15). max-width
     + hidden overflow keep an over-long line inside the column. */
  .dd-tail { display:flex; align-items:flex-end; gap:10px; max-width:100%;
    min-width:0; }
  .dd-note { font-size:14px; line-height:1.75; color:#4a3b28; white-space:nowrap;
    max-width:100%; overflow:hidden; text-overflow:ellipsis; padding-bottom:6px; }
  .cur.dd-note { font-size:16px; }     /* Caveat runs small — see --curs note */
  /* the theme's own English quips keep their old soft wrap at 9em */
  .dd-quip { padding-bottom:0; white-space:normal; max-width:9em; overflow:visible; }

  /* ---- appendix ---- */
  .appendix > .wrap { padding-top:26px; padding-bottom:40px; }
  .sec { font-size:clamp(23px,2.6vw,28px); letter-spacing:.1em; margin:64px 0 10px;
    display:flex; align-items:center; gap:13px; }
  .sec:first-of-type { margin-top:26px; }
  .sqseal { display:inline-grid; place-items:center; width:38px; height:38px;
    background:#9c352c; color:#f8ecd8; border-radius:6px; font-size:20px;
    font-family:var(--hand); rotate:-3deg;
    box-shadow:inset 0 0 0 2px rgba(248,236,216,.35);
    -webkit-mask-image:url("__SPECK__"); mask-image:url("__SPECK__"); }
  .secsub { font-size:13px; color:var(--soft); margin-bottom:8px; }

  .pass { display:grid; grid-template-columns:minmax(0,1fr) 128px; margin-top:20px;
    background:linear-gradient(120deg,#e6edf2,#dbe4ea); border-radius:6px;
    box-shadow:0 10px 18px -10px rgba(50,60,70,.55); rotate:var(--rot,0deg);
    position:relative; max-width:760px; }
  .pass::after { content:""; position:absolute; top:6px; bottom:6px; right:128px;
    border-right:2px dashed rgba(36,69,94,.4); }
  .pass-l { padding:16px 20px 14px; min-width:0; }
  .pass-kind { font-size:12.5px; color:#385470; letter-spacing:.06em; }
  .pass-route { font:700 clamp(19px,2.2vw,23px)/1.4 var(--mono); color:#24455e;
    letter-spacing:.05em; margin:6px 0 4px; overflow-wrap:anywhere; }
  .pass-row { font:12.5px/1.9 var(--mono); color:#385470; overflow-wrap:anywhere; }
  .pass-r { display:flex; flex-direction:column; align-items:center;
    justify-content:center; gap:6px; padding:12px 10px; }
  .pass-pl { width:30px; height:30px; color:rgba(36,69,94,.5); }
  .pass-r .stub { background:#eef3f6; border-color:#8ba2b4; border-left-color:#8ba2b4;
    color:#24455e; }
  .bkp { margin-top:8px; font-size:12.5px; color:#385470; }
  .bkp summary { cursor:pointer; font-family:var(--mono); letter-spacing:.1em;
    min-height:24px; }
  .bkp p { padding:6px 0 4px 12px; line-height:1.9; overflow-wrap:anywhere; }

  .htl { margin-top:30px; border-top:2px solid rgba(143,47,39,.5); padding-top:12px;
    max-width:820px; }
  .htl h3 { font-size:18px; letter-spacing:.05em; }
  .htl h3 .ic { color:var(--red); }
  .why { font-size:13.5px; line-height:2; color:var(--soft); margin-top:6px; }
  .htl ul { margin:10px 0 0 22px; font-size:14px; line-height:2.1; }
  .band { font-size:11.5px; color:var(--soft); }

  .tscroll { overflow-x:auto; }
  .ledger { width:100%; border-collapse:collapse; font-size:14px; max-width:1000px; }
  .ledger th { text-align:left; font-weight:700; font-size:12px; letter-spacing:.2em;
    color:var(--soft); border-bottom:2px solid rgba(143,47,39,.6); padding:0 18px 8px 0; }
  .ledger td { border-bottom:1px solid rgba(93,76,51,.28); padding:11px 18px 10px 0;
    vertical-align:top; line-height:1.9; overflow-wrap:anywhere; }
  .ledger td:first-child { min-width:11em; }
  .amt { font-size:12.5px; color:#634415; white-space:normal; }
  .bnote { font-size:12.5px; color:var(--soft); }
  .total td { font-weight:700; font-size:15px; border-top:2px solid var(--red);
    border-bottom:4px double var(--red); padding:13px 18px 12px 0; }

  .ck { list-style:none; max-width:860px; }
  .ck li { position:relative; padding-left:36px; margin-top:18px; font-size:15px;
    line-height:1.95; }
  .ck li::before { content:""; position:absolute; left:2px; top:6px; width:16px;
    height:16px; border:2px solid var(--ink); border-radius:2px; rotate:-3deg; }
  .ck b { font-weight:700; }
  .ddl { font-size:11.5px; color:var(--red); letter-spacing:.02em; margin-left:6px; }
  .ck .stub { min-height:34px; padding:0 12px 0 14px; margin-left:6px;
    vertical-align:middle; }
  .cknote { font-size:13px; color:var(--soft); line-height:1.9; margin-top:2px; }

  .memos { display:grid; grid-template-columns:repeat(auto-fit,minmax(17rem,1fr));
    column-gap:clamp(24px,3.5vw,52px); row-gap:26px; max-width:1100px; }
  .memo h3 { font-size:17px; color:var(--red); letter-spacing:.08em;
    text-decoration:underline wavy rgba(143,47,39,.45) 1.5px;
    text-underline-offset:6px; margin-bottom:9px; }
  .memo p { font-size:13.5px; line-height:2.05; color:var(--soft);
    overflow-wrap:anywhere; }

  .dec { margin-left:22px; max-width:860px; }
  .dec li { margin-top:14px; font-size:14px; line-height:2.05; }
  .unv { list-style:none; max-width:860px; }
  .unv li { margin-top:12px; font-size:13.5px; line-height:2; color:#6d3a24;
    padding-left:4px; }

  .endcap { margin:90px auto 30px; text-align:center; display:flex;
    flex-direction:column; align-items:center; gap:14px; }
  .endline { font-size:clamp(24px,3vw,30px); letter-spacing:.12em; rotate:-1deg; }
  .endfine { font-size:13px; color:var(--soft); }
  .seal-end { width:78px; height:80px; }
  footer { margin:30px auto 26px; max-width:820px; text-align:center;
    font-size:11.5px; line-height:2.1; color:var(--soft); }

  /* export chips: the label is written straight onto a highlighter swipe —
     the mark this journal already makes when a line must not be missed.
     Type size is untouched (13px); the yellow is what gets it noticed, and
     it stays a small annotation in the margin, not a call-to-action slab.
     Parked at the chapter's bottom-right, clear of the doodle field. */
  /* IN FLOW, never absolute: parked in the chapter's bottom margin it sat
     on the doodle notes (measured 40x2 and 86x4 of real overlap on d5/d9 —
     the doodles carry a seeded rotation, so no fixed offset is ever safe).
     A grid row of its own can't collide with anything. position:relative is
     load-bearing: it makes the stacking context the ::before swipe hides in. */
  .dfoot { grid-column:1 / -1; grid-row:4; display:flex;
    justify-content:flex-end; padding-top:16px; }
  .dfoot-appx { display:flex; justify-content:flex-end; padding-top:6px; }
  .xbtn { position:relative; z-index:1;
    border:0; background:none; padding:4px 13px 5px; cursor:pointer;
    color:#3f2a11; font-family:var(--hand),cursive; font-size:13px;
    letter-spacing:.06em; rotate:-1.2deg;
    transition:translate .18s ease, color .18s ease; }
  /* the swipe: one pass of a chisel tip, feathered at both ends where the
     pen lifts, laid a hair off-square to the writing. z-index:-1 keeps it
     under the label — .xbtn's own z-index makes the stacking context. */
  .xbtn::before { content:""; position:absolute; z-index:-1;
    left:-4px; right:-4px; top:1px; bottom:0;
    background:linear-gradient(93deg, rgba(246,203,46,0) 0,
      rgba(246,203,46,.92) 5%, rgba(253,228,108,.96) 44%,
      rgba(243,196,36,.9) 92%, rgba(243,196,36,0) 100%);
    clip-path:polygon(0 9%, 100% 0, 100% 91%, 0 100%); }
  /* the short second pass, where the pen went over the line twice */
  .xbtn::after { content:""; position:absolute; z-index:-1;
    left:12%; right:9%; bottom:2px; height:38%; rotate:-.7deg;
    background:rgba(232,178,20,.5); }
  .xbtn:hover, .xbtn:focus-visible { translate:0 -1px; color:#2b1a06; }
  .xbtn:hover::before, .xbtn:focus-visible::before {
    filter:saturate(1.2) brightness(1.05); }

  /* the nav's odd one out — a WIDE tab with a real label, washed with the
     same highlighter and boxed in red pen. Everything else in the strip is
     one pale character wide, so this reads as "not a page" at a glance.
     Marker lives in a background layer, which always paints under the text
     (a positioned pseudo would paint over it). */
  .pins .xbtn { position:static; border:none; background:none; padding:0;
    rotate:none; margin-left:6px; }
  .pins .xbtn::before, .pins .xbtn::after { content:none; }
  .pins a .pbead.pb-x { width:auto; padding:0 11px; letter-spacing:.05em;
    color:#3f2a0c; border:1.6px solid rgba(148,44,34,.82);
    background:
      linear-gradient(93deg, rgba(243,190,24,0) 0, rgba(243,190,24,.82) 7%,
        rgba(243,190,24,.82) 93%, rgba(243,190,24,0) 100%)
        0 calc(100% - 8px)/100% 17px no-repeat,
      linear-gradient(180deg,#fdf1c6,#f8de92);
    box-shadow:0 2px 3px rgba(96,66,28,.32),
      inset 0 -2px 0 rgba(158,116,28,.18), inset 0 1px 0 rgba(255,253,240,.75); }
  .pins .xbtn:hover .pbead.pb-x, .pins .xbtn:focus-visible .pbead.pb-x {
    translate:0 1px; border-color:rgba(148,44,34,1); }
  @media print { .xbtn, .dfoot { display:none; } }

  /* reveal: pieces settle onto the page (rotation rides on transform so the
     settle animation and the resting tilt are one system). Only SMALL pasted
     pieces animate — the big blocks (.entries timeline) stay static: each
     animating element becomes its own compositor layer, and page-tall layers
     springing up mid-scroll is exactly the jank the owner felt. Short travel,
     short clock, composite-only properties. */
  .reveal { rotate:none; transform:rotate(var(--rot,0deg));
    transition:opacity .34s ease-out, transform .38s ease-out; }
  .js .reveal { opacity:0;
    transform:translateY(9px) rotate(calc(var(--rot,0deg) - 0.7deg)); }
  .reveal.in { opacity:1; transform:translateY(0) rotate(var(--rot,0deg)); }

  @media (prefers-reduced-motion:reduce) {
    html { scroll-behavior:auto; }
    .reveal, .js .reveal { opacity:1; transform:rotate(var(--rot,0deg)); transition:none; }
    .cue { animation:none; }
    .pbead, .pocket .chev { transition:none; }
  }

  @media (max-width:1100px) {
    :root { --spinew:56px; }
    .route { background-image:url("__ROUTE_M__"); background-size:44px auto;
      background-position:50% 0; }
    .dgrid { grid-template-columns:var(--spinew) minmax(0,1fr); }
    .spine { grid-row:1 / span 5; }
    .dfoot { grid-row:5; }
    .dhead { grid-column:2; grid-row:1; }
    .drail { grid-column:2; grid-row:2; flex-direction:row; flex-wrap:wrap;
      justify-content:flex-start; align-items:flex-start; gap:30px 34px;
      padding-top:24px; }
    .dmain { grid-column:2; grid-row:3; }
    .dnotes { grid-column:2; grid-row:4; flex-direction:row; flex-wrap:wrap;
      gap:20px; }
    .slip { width:auto; flex:1 1 250px; }
    .pol { max-width:270px; }
  }
  @media (max-width:760px) {
    [id] { scroll-margin-top:72px; }
    .book { margin:5px 5px 12px; border-radius:4px; }
    .book::after { width:52px; height:52px; }
    /* edge flora live in the wide-screen gutters; on phones those gutters
       are gone, so the scatter steps aside (clay's chapter-deco precedent) */
    .eflora { display:none; }
    .cov { grid-template-columns:minmax(0,1fr); padding-top:120px;
      padding-bottom:96px; }
    .stamps { top:14px; gap:6px; }
    .stampd { width:56px; height:62px; } .st-wide { width:64px; }
    .pm-cover { margin-left:-22px; margin-top:26px; width:104px; }
    .pm-ghost { width:210px; left:auto; right:4%; top:3%; }
    .rs-cover { right:8px; top:10px; width:118px !important; }
    .wt-cov1 { left:12%; top:6%; }
    .flower { display:none; }
    .covq { rotate:0deg; }
    .dhead { padding-right:0; }
    .dhead .pm { position:static; display:inline-block; margin-bottom:8px;
      width:126px; }
    .rs-sec { height:34px; margin-left:10px; }
    .dsub { display:block; margin-left:0; margin-top:2px; }
    .dsun { display:block; margin-left:0; white-space:normal; }
    .en { gap:8px; }
    .mk { flex-basis:14px; }
    .en-t { flex-basis:78px; font-size:11px; }
    .en-x { font-size:14px; }
    .pass { grid-template-columns:minmax(0,1fr); }
    .pass::after { top:auto; bottom:64px; left:6px; right:6px; border-right:0;
      border-bottom:2px dashed rgba(36,69,94,.4); }
    .pass-r { flex-direction:row; padding:10px 14px 14px; }
    .pm-big { width:150px; }
  }
  @media (max-width:560px) {
    :root { --spinew:40px; }
    .pin { width:38px; height:38px; font-size:12px; }
    .route { background-size:34px auto; }
    .pol { max-width:100%; }
    /* cursive asides may wrap on narrow phones instead of overflowing */
    .mgn { white-space:normal; font-size:15px; }
    .mgn-head { font-size:16px; }
    /* full-width polaroids: corner tapes tuck inside the page edge */
    .tape-c1 { left:-8px; bottom:-11px; }
    .tape-c2 { right:-8px; bottom:-11px; }
    /* the ledger re-stacks: one hand-written entry per line group */
    .ledger th { display:none; }
    .ledger tr { display:block; padding:12px 0 4px;
      border-bottom:1px solid rgba(93,76,51,.28); }
    .ledger td { display:block; border-bottom:0; padding:1px 0; }
    .ledger td:first-child { min-width:0; font-size:15px; }
    .amt { font-size:13px; }
    .ledger tr.total { border-top:2px solid var(--red);
      border-bottom:4px double var(--red); padding:12px 0 10px; }
    .total td { border:0; padding:2px 0; }
  }

  @media print {
    .pins, .route, .cue, .tape, .pm, .stampd, .gonav, .pocket, .flower,
    .sealbg, .prop, .propw, .bagtag, .stn, .wt, .rstamp, .mgn, .pclip,
    .covroute, .doodle, .vtk, .eflora, .ptack,
    .book::before, .book::after { display:none !important; }
    body, .chap { background:#fff !important; }
    .book { max-width:none; margin:0; box-shadow:none; border-radius:0;
      background:#fff; overflow:visible; }
    .js .reveal, .reveal { opacity:1 !important; transform:none !important; }
    .envelope { clip-path:none; background:none; filter:none; padding:0;
      border:1.5px solid #35291a; }
    .airmail { background:none; color:#24455e; border:1.5px solid #24455e; }
    .pin { background:none; border:2px solid #7a5c22; box-shadow:none;
      color:#35291a; text-shadow:none; }
    .pass { background:none; box-shadow:none; border:1.5px solid #24455e; }
    .pol, .slip, .poster, .pc-card, .po-sheet, .pc-linen { box-shadow:none; filter:none;
      clip-path:none; border:1px solid #c9b791; background:#fff; }
    .postcard { filter:none; }
    .pol img, .pc-card img, .poster img { filter:none; }
    .tg-go { background:none; border-bottom:2.5px solid #b98b1e; }
    .sqseal { background:none; color:#9c352c; box-shadow:none;
      border:2px solid #9c352c; }
    .stub { background:none; }
    .dgrid, .cov { display:block; }
    .pass, .htl, .memo, .slip, .pol { break-inside:avoid; }
  }
"""

# en-only overrides, appended after CSS when the page language is not zh (the
# zh build stays byte-identical). Latin runs 30-40% longer than the CJK these
# boxes were cut for (Mexico test, 2026-08-16):
#   cover — the theme's three-line quote in .cov-side sat under the postmark
#           ring (first line ran to x≈1036, ring starts at 1000): drop the side
#           column 80px on wide screens so the quote clears the stamps row
#           (on phones the cover stacks and never collides);
#   slips — the second washi across the lower-right corner covered the tail of
#           a full last line: those scraps get the strip's reach as bottom
#           padding and the strip sits lower on the corner.
CSS_EN = """
  @media (min-width:761px) { .cov-side { padding-top:80px; } }
  .slip:has(.wt-s) { padding-bottom:40px; }
  .slip .wt-s { bottom:0; right:-10px; }
"""


if __name__ == "__main__":
    main()
