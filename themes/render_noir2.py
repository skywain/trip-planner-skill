#!/usr/bin/env python3
"""Noir renderer v2 — 一镜到底: one unbroken tracking shot.

Paradigm (deliberately a different species from clay's road-through-terrain
and glass's frosted panes over crossfading photos):

* ONE image plane for the whole document — a `position:sticky` 100svh stage
  holding all seven night scenes. It never ends, so there are no chapter
  slabs and no seams to hide. Days scroll OVER it; the plane only changes
  what it is showing.
* The cross-dissolve is timed to land on a HOP INTERSTITIAL — a near-empty
  band carrying only the flight/drive in letterspaced mono — so two days
  never butt against each other. The transition is a piece of content.
* Continuity thread = LIGHT, not shape: one fixed radial glow whose x, hue
  and elevation are driven by a single document-progress variable, so the
  light visibly tracks the trip from its first city to its last across the
  page.
* Type is burned INTO the negative (`mix-blend-mode:overlay`), never put in
  a caption box; the itinerary is one full-width hairline ledger that never
  restarts, not a centred island per chapter.
* One rAF loop is the only animation JS. Reduced-motion un-sticks the same
  DOM into an honest filmstrip; print collapses it to a contact sheet.

Art (art.json, see ART-SCHEMA.md) — everything ABOUT the trip comes from here;
the renderer itself carries no place, date or picture name:

  cover.zh          the display title (h1). Missing → the theme's own word 夜航.
  cover.en          English line under it. Missing → the line is not emitted.
  cover.credit      allusion / source line. Missing → not emitted.
  cover.kick        short trip word prefixed to the date span on the cover kick
                    ("美国行 · 09-25 — 10-07") and, with the year, in <title>
                    and the export filename prefix (en page: cover.kick_en
                    wins there when set — theme_common.title_kick).
                    Missing → the kick is the date span alone; <title> = year ·
                    夜航版.
  cover.kick_en     CAPS trip word for the export frame stamp ("US 2026 · 夜航
                    NIGHT FLIGHT · DAY 03"). Missing → the stamp starts at 夜航.
  days[date].theme  the burned-in 4-character chapter title (art.day_theme).
                    Missing → the day's `city` from the plan.
  brief_titles      {plan.brief key: title} for the 行前须知 log rows, over the
                    shared theme_common.BRIEF_TITLES (visa→签证 …). Missing →
                    shared defaults; keys not in either table print as they are.
  themes.noir.plates      asset stems of the night plates in reel order; [0] is
                    the cover plate. Missing/empty → the sticky stage is empty
                    and the page sits on the theme's flat gradient (bg + veil),
                    no photographs, no export atmosphere band, and the footer
                    drops the "NIGHT SCENES AI-GENERATED" credit.
  themes.noir.day_plate   {"<date>" | "<day number>": plate index} — keys may
                    be ISO dates ("2026-10-03", matches days[].date, survives
                    inserting/removing a day) or 1-based day numbers ("3");
                    both may be mixed and a date key wins over a number key
                    for the same day. Missing key → plate 1 (or 0 when there
                    is only one plate). When the number of keys differs from
                    the number of days a one-line warning goes to stderr (the
                    page still renders). Plates whose file is absent simply
                    contribute no background image.
  (themes.noir.cover.* overrides cover.* per Art.cover.)

Kit (the theme's own, nothing to pick in art): the sticky 100svh stage +
cross-dissolve, the hop interstitial band, the travelling amber glow, the
burned-in gliding title, the hairline ledger, the export-only atmosphere band.

Usage: python3 render_noir2.py <plan.geo.json> [--art <art.json>|none]
                                [--assets DIR ...] -o <out.html>
Assets (the plate webps) are searched in the plan's directory, every --assets
DIR, then themes/assets/ (theme_common.data_uri).
"""
import argparse
import pathlib
import sys

from theme_common import (LUCIDE, T, add_art_arg, asset_count, brief_titles, data_uri,
                          day_embed_url, esc, export_js, export_prefix, init_lang, lang,
                          load_art, load_plan, short_dates, theme_name, title_head)

HERE = pathlib.Path(__file__).parent


# Icons are inlined as full <svg><path> markup instead of <use> sprite refs:
# the PNG exporter captures one module's subtree at a time, and a <use>
# pointing at a sprite that lives OUTSIDE that subtree resolves to nothing in
# the SVG-image rasteriser (glyphs silently vanish from the export). Local
# overrides, same signatures as theme_common.ic/et.
def ic(name, cls=""):
    c = f"ic {cls}".strip()
    return f'<svg class="{c}" viewBox="0 0 24 24" aria-hidden="true">{LUCIDE[name]}</svg>'


def et(s):
    t = esc(s)
    return (t.replace("✈️", ic("plane")).replace("✈", ic("plane"))
             .replace("⚠️", ic("alert", "warn")).replace("⚠", ic("alert", "warn"))
             .replace("☀", ic("sunrise")).replace("🌇", ic("sunset")))

THEME = "noir"

# The theme's own voice, per language. Shared UI words (buttons, section
# names, tags) come from theme_common.T(); only what is noir's alone lives
# here. zh values are the byte-frozen originals.
L = {
    "zh": {
        "cover_word": "夜航", "stamp": "夜航 NIGHT FLIGHT · ",
        "nav_to": "导航到 ", "late": "晚点", "note": "注",
        "route_map": "路线地图", "map_ph": "地图需联网加载",
        "save_day_tip": "把这一天存成图片,可发朋友圈",
        "save_appx_tip": "把附录(航段/住宿/预算/清单)存成图片,可发朋友圈",
        "checklist": "行前清单", "total": "合计", "colon": ":",
    },
    "en": {
        "cover_word": "Night Flight", "stamp": "NIGHT FLIGHT · ",
        "nav_to": "Navigate to ", "late": "if late", "note": "note",
        "route_map": "Route map", "map_ph": "The map needs a connection to load",
        "save_day_tip": "Save this day as an image to share",
        "save_appx_tip": "Save the appendix (legs / stays / budget / checklist) as an image to share",
        "checklist": "Checklist", "total": "Total", "colon": ": ",
    },
}


def t(k):
    return L.get(lang(), L["zh"]).get(k, L["zh"][k])


def sun_text(day):
    """The plan's sun line; sun --write emits 天亮 in zh and dawn in en, but an
    older en plan may still carry 天亮 — swap it for the page language."""
    s = day.get("sun", "")
    if lang() != "zh" and isinstance(s, str):
        s = s.replace("天亮", T("sun.dawn"))
    return et(s)

# The plates of the tracking shot, in reel order, and which plate each day sits
# on, both come from art.json (themes.noir.plates / themes.noir.day_plate).
# The trip's own list used to live here; the reel mechanics stay.


def css_str(s):
    """A CSS string literal body: escape the two characters that end it."""
    return str(s).replace("\\", "\\\\").replace('"', '\\"')



def ledger_rows(day):
    rows = []
    for r in day.get("timeline", []):
        kind = r.get("kind", "anchor")
        est = '<sup>est</sup>' if r.get("verify") == "est" else ""
        tag = r.get("tag", "")
        chip = (f'<span class="tag{" hot" if tag == "pinned" else ""}">'
                f'{esc(T("tag." + tag, tag))}</span>' if tag else "")
        price = f' <span class="dim">{esc(r["price"])}</span>' if r.get("price") else ""
        nav = (f'<a class="rownav" href="{esc(r["link"])}" target="_blank" rel="noopener"'
               f' aria-label="{esc(t("nav_to"))}{esc(r.get("what", ""))[:18]}">{ic("pin")}</a>'
               if r.get("link") else "")
        rows.append(
            f'<div class="row k-{kind}" role="listitem"><span class="t">{esc(r.get("t",""))}{est}</span>'
            f'<span class="w">{et(r.get("what",""))}{price}{chip}</span>'
            f'<span class="n">{nav}</span></div>')
    return "".join(rows)


def meta_line(day):
    bits = []
    wk = day.get("walking_km")
    if isinstance(wk, dict):
        bits.append(f'{ic("walk")} ≈{wk.get("total","?")}km · {esc(wk.get("how",""))}')
    elif wk:
        bits.append(f'{ic("walk")} ≈{wk}km')
    for key, icn, label in (("rain_alt", "rain", T("rain_alt")), ("late_cut", "clock", t("late")),
                            ("note", "note", t("note"))):
        if day.get(key):
            bits.append(f'{ic(icn)} {esc(label)}{t("colon")}{et(day[key])}')
    return f'<p class="meta">{" · ".join(bits)}</p>' if bits else ""


def hop_band(prev_day, day, legs_by_date):
    """The transition organ: a near-empty band so two days never touch."""
    leg = legs_by_date.get(day.get("date", ""))
    if leg:
        text = (f'{esc(leg.get("carrier",""))} · {esc(leg.get("from",""))} → '
                f'{esc(leg.get("to",""))} · {esc(leg.get("dep",""))}—{esc(leg.get("arr",""))}')
    else:
        a = (prev_day.get("city", "") or "").split("→")[-1].strip()
        b = (day.get("city", "") or "").split("→")[0].strip()
        text = f"{esc(a)} → {esc(b)}" if a and b and a != b else esc(day.get("label", ""))
    return f'<div class="hop"><span>{text}</span></div>'


def chapter(i, day, art, day_plate, default_plate):
    date = day.get("date", "")
    sun = sun_text(day)
    embed = day_embed_url(day)
    embed_html = (f'<details class="mapfold"><summary>{ic("compass")} {esc(t("route_map"))}</summary>'
                  f'<div class="map-embed" data-src="{esc(embed)}">'
                  f'<p class="map-ph">{esc(t("map_ph"))}</p></div></details>' if embed else "")
    plate = day_plate.get(date, day_plate.get(str(i), default_plate))
    return f"""
<section class="chapter" id="d{i}" data-layer="{plate}"
         data-export="DAY {i:02d}" aria-labelledby="ct{i}">
  <h2 class="ch-title" id="ct{i}">{esc(art.day_theme(date, day.get("city", "")))}</h2>
  <div class="ch-meta">
    <span class="no">{i:02d}</span>
    <span class="dt">{esc(date)} · {esc(day.get("city",""))}</span>
    <span class="lb">{esc(day.get("label",""))}</span>
    {f'<span class="sn">{sun}</span>' if sun else ""}
  </div>
  <div class="log" role="list">{ledger_rows(day)}</div>
  {meta_line(day)}
  {embed_html}
  <button class="xbtn no-export" data-x-for="#d{i}" data-x-label="DAY{i:02d}"
    title="{esc(t("save_day_tip"))}">{esc(T("btn.save_day"))}</button>
</section>"""


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
    dates = short_dates(meta.get("dates", "")).replace(" → ", " — ")
    year = (meta.get("dates", "") or "")[:4]
    year = year if year.isdigit() else ""
    legs_by_date = {l.get("date", ""): l for l in p.get("legs", [])}

    # cover words — all the trip's, all optional
    kick = art.cover(THEME, "kick")
    kick_en = art.cover(THEME, "kick_en")
    cover_zh = art.cover(THEME, "zh", t("cover_word"))
    cover_en = art.cover(THEME, "en")
    cover_credit = art.cover(THEME, "credit")
    page_title = " · ".join(x for x in (title_head(art, THEME, year), theme_name(THEME)) if x)
    kick_line = f"{esc(kick)} · {esc(dates)}" if kick and dates else esc(kick or dates)
    cover_en_html = f'\n      <p class="en">{esc(cover_en)}</p>' if cover_en else ""
    cover_credit_html = (f'\n      <p class="credit">{esc(cover_credit)}</p>'
                         if cover_credit else "")
    stamp = css_str((f"{kick_en} · " if kick_en else "") + t("stamp"))

    # the plates: reel order + day → plate map, both from art
    tb = art.theme(THEME)
    layers = [s for s in (tb.get("plates") or []) if s]
    day_plate = {str(k): v for k, v in (tb.get("day_plate") or {}).items()}
    default_plate = 1 if len(layers) > 1 else 0
    if day_plate:
        mapped = sum(1 for n, d in enumerate(days)
                     if d.get("date", "") in day_plate or str(n + 1) in day_plate)
        if mapped != len(days):
            print(f"warning: themes.noir.day_plate covers {mapped} of {len(days)} "
                  f"days — unmapped days fall back to plate {default_plate}",
                  file=sys.stderr)
        known = ({d.get("date", "") for d in days}
                 | {str(n + 1) for n in range(len(days))})
        stray = sorted(k for k in day_plate if k not in known)
        if stray:
            print(f"warning: themes.noir.day_plate keys match no day "
                  f"(not a date in the plan, not 1..{len(days)}): {stray}",
                  file=sys.stderr)

    # One copy of each plate, parked in :root custom props: the sticky stage
    # AND the export-only atmosphere band both drink from the same URI, so
    # wiring the exporter costs no page weight.
    uris = [(n, data_uri(s)) for n, s in enumerate(layers)]
    ph_vars = "".join(f"--ph{n}:url({u});" for n, u in uris if u)
    lay_rules = "".join(
        f'#stage .lay[data-i="{n}"]{{background-image:var(--ph{n})}}'
        for n, u in uris if u)
    xlayer_rules = "".join(
        f'.__xbody .chapter[data-layer="{n}"]::before{{background-image:'
        f'linear-gradient(180deg,rgba(11,13,18,.62),rgba(11,13,18,.84)),var(--ph{n})}}'
        for n, u in uris if u and n > 0)
    stage = "".join(f'<i class="lay" data-i="{n}"></i>' for n, u in uris if u)
    has_cover_plate = bool(uris and uris[0][1])
    appx_x_rule = ("  .__xbody .appx::before { background-image:\n"
                   "    linear-gradient(180deg, rgba(11,13,18,.66), rgba(11,13,18,.86)), var(--ph0); }\n"
                   if has_cover_plate else "")
    scenes_credit = " · NIGHT SCENES AI-GENERATED" if any(u for _, u in uris) else ""

    reel = ""
    for n, d in enumerate(days):
        if n:
            reel += hop_band(days[n - 1], d, legs_by_date)
        reel += chapter(n + 1, d, art, day_plate, default_plate)

    rail = "".join(f'<a href="#d{i}" data-spy="d{i}">{i:02d}</a>'
                   for i in range(1, len(days) + 1))

    legs = "".join(
        f'<div class="row"><span class="t">{esc(l.get("date",""))[5:]}</span>'
        f'<span class="w">{esc(l.get("from",""))} → {esc(l.get("to",""))}'
        f' <span class="dim">{et(l.get("carrier",""))} {esc(l.get("dep",""))}—{esc(l.get("arr",""))}'
        f' · {esc(l.get("price",""))} · {esc(l.get("bags",""))}</span></span>'
        f'<span class="n"></span></div>' for l in p.get("legs", []))
    hotels = "".join(
        f'<div class="row"><span class="t">{esc(h.get("base",""))}</span>'
        f'<span class="w">{esc(h.get("area",""))} <span class="dim">{esc(h.get("why",""))}</span><br>'
        + " · ".join(
            f'<a href="{esc(o.get("link","#"))}" target="_blank" rel="noopener">{esc(o.get("name",""))}</a>'
            f' <span class="dim">{esc(o.get("band",""))}</span>'
            for o in h.get("options", []))
        + '</span><span class="n"></span></div>' for h in p.get("hotels", []))
    budget = "".join(
        f'<div class="row"><span class="t">{esc(b.get("cat",""))}</span>'
        f'<span class="w">{esc(b.get("per_person",""))}'
        f' <span class="dim">{esc(b.get("note",""))}</span></span>'
        f'<span class="n"></span></div>' for b in p.get("budget", []))
    checklist = "".join(
        f'<div class="row"><span class="t">{i:02d}</span><span class="w"><label>'
        f'<input type="checkbox"> {et(c.get("item",""))}</label>'
        f' <span class="dim">{esc(c.get("deadline",""))} · {esc(c.get("price",""))}</span>'
        + (f' <a href="{esc(c["link"])}" target="_blank" rel="noopener">'
           f'{esc(c.get("link_text", T("link")))}</a>' if c.get("link") else "")
        + '</span><span class="n"></span></div>'
        for i, c in enumerate(p.get("checklist", []), 1))
    # brief section titles: shared table + art common brief_titles;
    # unknown keys (a trip's own headings) print as they are
    titles = brief_titles(art)
    brief = "".join(
        f'<div class="row"><span class="t">{esc(titles.get(k, k))}</span>'
        f'<span class="w dim">{et(v)}</span><span class="n"></span></div>'
        for k, v in p.get("brief", {}).items())
    decisions = "".join(f"<li>{et(u)}</li>" for u in p.get("decisions", []))
    unverified = "".join(f"<li>{et(u)}</li>" for u in p.get("unverified", []))

    html_out = f"""<!doctype html>
<html lang="{T("html_lang")}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(page_title)}</title>
<style>
  :root {{
    --bg:#0b0d12; --ink:#ece7dd; --dim:#b2b8c3; --amber:#E9A94F;
    --hair:rgba(236,231,221,.16); --gut:clamp(16px,5vw,72px);
    --sun:0;
    {ph_vars}
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; background:var(--bg); }}
  /* a flight log is typed, not typeset — mono is the body voice here, and the
     serif is reserved for the display titles alone (the mirror of 插画版) */
  body {{ background:none; color:var(--ink); overflow-x:clip;
    font-family:ui-monospace,"SF Mono",Menlo,"Noto Sans Mono CJK SC",
      "PingFang SC",monospace; font-feature-settings:"tnum" 1; }}
  .lead h1, .ch-title {{ font-family:"Songti SC","Noto Serif SC",Georgia,serif; }}
  a {{ color:var(--amber); text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  .dim {{ color:var(--dim); font-size:.86em; }}
  sup {{ font-size:8px; color:var(--dim); margin-left:1px; vertical-align:top; }}
  .ic {{ width:1em; height:1em; fill:none; stroke:currentColor; stroke-width:1.75;
    stroke-linecap:round; stroke-linejoin:round; vertical-align:-0.12em; }}
  .ic.warn {{ color:var(--amber); }}
  :focus-visible {{ outline:2px solid var(--amber); outline-offset:3px; }}

  /* ---------- the single image plane ---------- */
  #reel {{ position:relative; }}
  /* the plane sits BEHIND the root content instead of the content being
     promoted above it — otherwise .over forms a stacking context and the
     title's mix-blend-mode can never reach the photograph */
  #stage {{ position:sticky; top:0; height:100svh; overflow:hidden; z-index:-3; }}
  #stage .lay {{ position:absolute; inset:0; display:block; background-size:cover;
    background-position:center; opacity:0; will-change:opacity, transform;
    transform:scale(1.06); }}
  #stage .lay[data-i="0"] {{ opacity:1; }}   /* survives JS never running */
  {lay_rules}
  /* the travelling light — noir's continuity thread */
  #glow {{ position:fixed; inset:0; z-index:-1; pointer-events:none; mix-blend-mode:screen;
    background:
      radial-gradient(120vmax 62vmax at calc(var(--sun) * 118% - 9%)
        calc(80% - var(--sun) * 34%),
        hsl(calc(38 - var(--sun) * 26) 82% 54% / .26) 0, transparent 62%),
      radial-gradient(70vmax 40vmax at calc(var(--sun) * 108% - 4%)
        calc(84% - var(--sun) * 30%),
        hsl(calc(32 - var(--sun) * 30) 90% 62% / .16) 0, transparent 58%); }}
  #veil {{ position:fixed; inset:0; z-index:-2; pointer-events:none;
    background:linear-gradient(180deg, rgba(11,13,18,.72) 0%, rgba(11,13,18,.70) 26%,
      rgba(11,13,18,.76) 62%, rgba(11,13,18,.88) 100%); }}

  /* ---------- chrome: 1px scrub + numbered rail ---------- */
  #scrub {{ position:fixed; left:0; top:0; height:1px; width:100%; z-index:60;
    background:var(--amber); transform-origin:0 50%; transform:scaleX(var(--sun)); }}
  .rail {{ position:fixed; left:0; right:0; bottom:0; z-index:50; display:flex;
    gap:2px; padding:10px var(--gut) calc(10px + env(safe-area-inset-bottom));
    overflow-x:auto; scrollbar-width:none;
    background:linear-gradient(0deg, rgba(11,13,18,.94), rgba(11,13,18,0)); }}
  .rail::-webkit-scrollbar {{ display:none; }}
  .rail a {{ flex:0 0 auto; font:10px/1 ui-monospace,Menlo,monospace; letter-spacing:.22em;
    color:var(--dim); padding:12px 9px; min-height:44px; display:inline-flex;
    align-items:center; }}
  .rail a.active {{ color:var(--amber); }}
  .rail a.active::before {{ content:""; width:5px; height:5px; border-radius:50%;
    background:var(--amber); margin-right:6px;
    animation:pulse 1.9s ease-in-out infinite; }}
  @keyframes pulse {{ 50% {{ opacity:.35; transform:scale(1.5); }} }}

  /* ---------- the traveller's type, over the plane ---------- */
  .over {{ position:relative; margin-top:-100svh; }}
  .lead {{ min-height:100svh; display:flex; flex-direction:column; justify-content:flex-end;
    padding:0 var(--gut) 16vh; }}
  .kick {{ font:11px/1 ui-monospace,Menlo,monospace; letter-spacing:.52em;
    color:var(--amber); }}
  .lead h1 {{ font-size:clamp(56px,12vw,168px); font-weight:400; letter-spacing:.1em;
    line-height:1.02; margin:16px 0 10px; }}
  .lead .en {{ font:11px/1 ui-monospace,Menlo,monospace; letter-spacing:.6em;
    color:var(--dim); }}
  .lead .credit {{ margin-top:18px; font-size:12.5px; color:var(--dim); letter-spacing:.14em; }}

  /* the burned-in sticky title keeps its ride (owner's call) — the overlap
     is solved in MOTION instead: as the day's text scrolls up to meet it,
     the title glides to the right margin and shrinks. No opacity fade —
     the overlay blend alone. Driven by the same rAF as the dissolve. */
  .chapter {{ padding:0 0 12vh; }}
  .ch-title {{ position:sticky; top:30vh; display:inline-block;
    pointer-events:none; user-select:none;
    font-size:clamp(46px,13vw,168px); line-height:.9; font-weight:400;
    letter-spacing:.06em; color:#fff; mix-blend-mode:overlay;
    padding:0 var(--gut); transform-origin:0 0;
    will-change:transform,opacity; }}
  @supports not (mix-blend-mode:overlay) {{ .ch-title {{ color:rgba(255,255,255,.9); }} }}
  .ch-meta {{ padding:34vh var(--gut) 22px; display:flex; flex-wrap:wrap; gap:0 18px;
    align-items:baseline; font:11.5px/2 ui-monospace,Menlo,monospace; color:var(--dim);
    letter-spacing:.16em; }}
  .ch-meta .no {{ color:var(--amber); font-size:13px; }}
  .ch-meta .lb {{ letter-spacing:.04em; font-size:13px; color:var(--ink); }}

  /* ---------- one ledger rule that never restarts ---------- */
  .log {{ padding:0 var(--gut); }}
  .row {{ display:grid; grid-template-columns:104px minmax(0,1fr) 44px; gap:0 18px;
    align-items:baseline; padding:13px 0; border-bottom:1px solid var(--hair);
    font-size:13px; line-height:1.9; letter-spacing:.01em; }}
  .row .t {{ font:12px/1.9 ui-monospace,Menlo,monospace; color:var(--amber);
    white-space:nowrap; }}
  .row .w {{ min-width:0; overflow-wrap:anywhere; }}
  .row .n {{ justify-self:end; }}
  .k-hop .t {{ color:var(--dim); }}
  .k-hop .w {{ color:var(--dim); font-size:13px; }}
  .k-free .w {{ color:var(--dim); font-style:italic; }}
  .k-meal .t {{ color:#d8c39a; }}
  .tag {{ font:10px/1 ui-monospace,Menlo,monospace; letter-spacing:.12em;
    border:1px solid var(--amber); color:var(--amber); padding:3px 8px; margin-left:8px;
    white-space:nowrap; }}
  .tag.hot {{ background:var(--amber); color:#14161c; }}
  .rownav {{ display:inline-flex; align-items:center; justify-content:center;
    min-width:44px; min-height:44px; margin:-13px -10px; }}
  .meta {{ padding:16px var(--gut) 0; font-size:12.5px; color:var(--dim); line-height:2.1; }}

  /* ---------- the transition organ ---------- */
  .hop {{ display:flex; align-items:center; gap:20px; min-height:52svh;
    padding:0 var(--gut); position:relative;
    font:11px/2.6 ui-monospace,Menlo,monospace; letter-spacing:.4em;
    color:var(--dim); text-transform:uppercase; }}
  .hop::before, .hop::after {{ content:""; flex:1 1 auto; height:1px;
    background:var(--hair); }}
  .hop span {{ flex:0 1 auto; text-align:center; }}

  .mapfold {{ padding:18px var(--gut) 0; }}
  /* no boxes in a theme whose premise is one unbroken rule: the affordance is
     the rule itself, extending under a letterspaced label */
  .mapfold summary {{ list-style:none; cursor:pointer; display:flex; gap:14px;
    align-items:center; font-size:11px; letter-spacing:.34em; color:var(--amber);
    border:0; border-top:1px solid rgba(233,169,79,.45); padding:16px 0 0;
    min-height:44px; }}
  .mapfold summary::after {{ content:""; flex:1 1 auto; height:1px;
    background:rgba(233,169,79,.28); }}
  .mapfold[open] summary::after {{ background:var(--amber); }}
  .mapfold summary::-webkit-details-marker {{ display:none; }}
  .map-embed {{ margin-top:12px; border:1px solid var(--hair); max-width:900px; }}
  .map-embed iframe {{ display:block; width:100%; height:330px; border:0;
    filter:grayscale(.25) brightness(.9); }}
  .map-ph {{ padding:20px; font-size:12px; color:var(--dim); text-align:center; }}

  /* ---------- appendix: same ledger, no new container ---------- */
  .appx {{ padding:0 0 8vh; position:relative; }}
  .appx h2 {{ font:12px/1 ui-monospace,Menlo,monospace; letter-spacing:.5em;
    color:var(--amber); padding:56px var(--gut) 14px; display:flex; gap:9px;
    align-items:center; }}
  .appx ol, .appx ul {{ padding:6px var(--gut) 0; margin-left:20px; font-size:13.5px;
    line-height:2; color:var(--dim); }}
  .appx ul.warn li {{ color:#d9a97e; }}
  /* appendix ledger labels are category names, not clock stamps: give them a
     wider track and let them wrap — nowrap in the 104px time column made the
     long ones (an international-flight leg, a 5-night hotel line) overlap the
     value column, live and in exports alike */
  .appx .row {{ grid-template-columns:208px minmax(0,1fr) 44px; }}
  .appx .row .t {{ white-space:normal; }}
  .total {{ padding:18px var(--gut) 0; }}
  .total b {{ display:inline-block; background:var(--amber); color:#14161c;
    padding:10px 20px; font-size:13.5px; }}
  input[type=checkbox] {{ accent-color:var(--amber); margin-right:6px; }}

  footer {{ padding:60px var(--gut) 14vh; border-top:1px solid var(--hair);
    font:10.5px/2.2 ui-monospace,Menlo,monospace; color:var(--dim);
    letter-spacing:.1em; text-align:center; }}

  /* ---------- export chips: the theme's own shape language — zero boxes,
     a hairline leader + letterspaced mono label (same grammar as .mapfold's
     rule-under-a-label). Visibility at rest comes from the ONE material this
     theme owns: amber filament light. The leader is a lit hairline, the label
     burns at the ledger's clock temperature, and both sit in a shallow pool
     of amber glow — no plate, no border, nothing that could read as a CTA.
     Hover pushes the filament out and turns the glow up. ---------- */
  .xbtn {{ appearance:none; -webkit-appearance:none; border:0; cursor:pointer;
    display:flex; width:max-content; align-items:center; gap:10px;
    font:10px/1 ui-monospace,Menlo,monospace; letter-spacing:.34em;
    color:var(--amber); padding:13px 14px; min-height:44px;
    position:relative; z-index:2;   /* stays crisp under the burned-in title */
    background:radial-gradient(56% 128% at 32% 50%,
      rgba(233,169,79,.15), rgba(233,169,79,0) 72%);
    text-shadow:0 0 12px rgba(233,169,79,.55), 0 1px 2px rgba(11,13,18,.92);
    transition:color .2s, background .2s, text-shadow .2s; }}
  .xbtn::before {{ content:""; width:26px; height:1px; flex:0 0 auto;
    background:linear-gradient(90deg, rgba(233,169,79,.18), var(--amber));
    box-shadow:0 0 7px rgba(233,169,79,.7);
    transition:width .2s, box-shadow .2s; }}
  .xbtn:hover, .xbtn:focus-visible {{ color:#ffdca8;
    background:radial-gradient(56% 128% at 32% 50%,
      rgba(233,169,79,.26), rgba(233,169,79,0) 74%);
    text-shadow:0 0 17px rgba(233,169,79,.85), 0 1px 2px rgba(11,13,18,.92); }}
  .xbtn:hover::before, .xbtn:focus-visible::before {{ width:44px;
    box-shadow:0 0 11px rgba(233,169,79,.95); }}
  /* Placement is measured, not guessed. The burned-in title is a 702×232px
     glyph that sticks at top:30vh and sweeps the whole chapter, so a chip in
     the log header collides with it no matter which end of the row it sits on
     (measured: 104×23px against a right-aligned chip, 114×3px against a
     left-aligned one). At the FOOT of the chapter the title is always fully
     glided — parked at the right edge, x≥820 — so a left-margin chip down
     there clears it by ~640px at every scroll position, and it lands in the
     same amber-affordance family as the 路线地图 rule right above it. The dash
     starts exactly on the ledger's left rule. */
  .chapter > .xbtn {{ margin:26px 0 0 calc(var(--gut) - 14px); }}
  .appx > .xbtn {{ margin:34px 0 0 calc(var(--gut) - 14px); }}
  /* the appendix chip opens the block, so the first heading drops its 56px
     opening padding — otherwise the two are a screen apart, and pulling the
     heading up with a negative margin put its box under the chip (measured
     118×18px) even though the words never came close */
  .appx > .xbtn + h2 {{ padding-top:20px; }}

  /* ---------- export-only atmosphere: these rules wake up inside the
     capture clone (the engine wraps it in .__xbody) and re-create what the
     sticky plane provides live — the day's night plate under a veil, a low
     amber glow, the film hairline, a letterspaced frame stamp. Inert on the
     live page: nothing here has a .__xbody ancestor. ---------- */
  .__xbody .chapter, .__xbody .appx {{ position:relative;
    border-top:1px solid rgba(233,169,79,.5);
    background:radial-gradient(92% 30% at 10% 100%,
      hsl(36 80% 55% / .1), transparent 62%); }}
  .__xbody .chapter > *, .__xbody .appx > * {{ position:relative; z-index:1; }}
  .__xbody .chapter::before, .__xbody .appx::before {{ content:"";
    position:absolute; left:0; top:0; right:0; height:min(58vw,620px); z-index:0;
    background-size:100% 100%, cover; background-position:0 0, center top;
    background-repeat:no-repeat;
    -webkit-mask-image:linear-gradient(180deg,#000 0,#000 30%,transparent 97%);
    mask-image:linear-gradient(180deg,#000 0,#000 30%,transparent 97%); }}
{appx_x_rule}  {xlayer_rules}
  .__xbody .chapter::after, .__xbody .appx::after {{
    content:"{stamp}" attr(data-export);
    position:absolute; left:var(--gut); bottom:26px; z-index:1;
    font:10px/1 ui-monospace,Menlo,monospace; letter-spacing:.5em;
    color:rgba(178,184,195,.62); }}

  @media (max-width:760px) {{
    .row {{ grid-template-columns:84px minmax(0,1fr) 40px; gap:0 12px; }}
    .row .t {{ font-size:11px; }}
    .appx .row {{ grid-template-columns:118px minmax(0,1fr) 40px; }}
    /* no room to glide on phones: static heading above the text flow —
       the readable state, never the overlapping one */
    .ch-title {{ position:static; font-size:clamp(40px,12vw,64px);
      letter-spacing:.1em; padding:26vh var(--gut) 0;
      transform:none !important; opacity:1 !important; }}
    .ch-meta {{ padding-top:16px; }}
    .hop {{ min-height:44svh; letter-spacing:.24em; }}
  }}

  /* ---------- honest fallbacks ---------- */
  @media (prefers-reduced-motion:reduce) {{
    html {{ scroll-behavior:auto; }}
    #stage {{ position:static; height:auto; overflow:visible; }}
    #stage .lay {{ position:relative; height:52svh; opacity:1; transform:none;
      -webkit-mask-image:linear-gradient(180deg,#0000 0,#000 18%,#000 82%,#0000 100%);
      mask-image:linear-gradient(180deg,#0000 0,#000 18%,#000 82%,#0000 100%); }}
    .over {{ margin-top:0; }}
    #glow {{ display:none; }}
    .ch-title {{ position:static; mix-blend-mode:normal;
      transform:none !important; opacity:1 !important; }}
    .rail a.active::before {{ animation:none; }}
  }}
  @media print {{
    :root {{ --ink:#111; --dim:#4f5560; --amber:#7a4c07; --hair:#ccc; }}
    html, body {{ background:#fff; color:#111; }}
    .tag {{ color:#7a4c07; border-color:#7a4c07; }}
    .tag.hot {{ background:none; color:#111; border-color:#111; }}
    .total b {{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
    #stage {{ position:static; height:auto; display:grid;
      grid-template-columns:repeat(4,1fr); gap:6px; }}
    #stage .lay {{ position:relative; height:120px; opacity:1; transform:none; }}
    #glow, #veil, #scrub, .rail, .mapfold, .xbtn {{ display:none; }}
    .over {{ margin-top:0; }}
    .lead {{ min-height:auto; padding:20px 0; }}
    .ch-title {{ position:static; mix-blend-mode:normal; color:#111;
      font-size:34px; padding:0; transform:none !important; opacity:1 !important; }}
    .ch-meta {{ padding:6px 0 10px; color:#444; }}
    .log, .meta, .appx h2, .appx ol, .appx ul, .total {{ padding-left:0; padding-right:0; }}
    .row {{ border-bottom:1px solid #ddd; }}
    .row .t {{ color:#8a5a1f; }}
    .tag.hot {{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
    .hop {{ min-height:auto; padding:14px 0; color:#666; }}
    .chapter {{ break-inside:avoid-page; padding-bottom:18px; }}
  }}
</style>
</head>
<body>
<div id="scrub" aria-hidden="true"></div>

<div id="reel">
  <div id="stage" aria-hidden="true">{stage}</div>
  <div id="veil" aria-hidden="true"></div>
  <div id="glow" aria-hidden="true"></div>

  <div class="over">
    <header class="lead" id="top">
      <span class="kick">{kick_line}</span>
      <h1>{esc(cover_zh)}</h1>{cover_en_html}{cover_credit_html}
    </header>
    {reel}

    <div class="appx" data-export="{esc(T("label.appendix"))}">
      <button class="xbtn no-export" data-x-for=".appx" data-x-label="{esc(T("label.appendix"))}"
        title="{esc(t("save_appx_tip"))}">{esc(T("btn.save_appendix"))}</button>
      <h2 id="legs">{ic("plane")} {esc(T("sec.legs"))}</h2><div class="log">{legs}</div>
      <h2 id="hotels">{ic("hotel")} {esc(T("sec.hotels"))}</h2><div class="log">{hotels}</div>
      <h2 id="budget">{ic("wallet")} {esc(T("sec.budget"))}</h2><div class="log">{budget}</div>
      <p class="total"><b>{esc(t("total"))} {esc(meta.get("budget_total",""))}</b></p>
      <h2 id="checklist">{ic("checklist")} {esc(t("checklist"))}</h2><div class="log">{checklist}</div>
      <h2 id="brief">{ic("book")} {esc(T("sec.brief"))}</h2><div class="log">{brief}</div>
      <h2>{ic("brain")} {esc(T("sec.decisions"))}</h2><ol>{decisions}</ol>
      <h2>{ic("alert", "warn")} {esc(T("sec.unverified"))}</h2><ul class="warn">{unverified}</ul>
    </div>

    <footer>
      {esc(meta.get("party",""))} · FX {esc(meta.get("fx",""))}<br>
      SUN DATA sunrise-sunset.org{scenes_credit} · PRICES LIVE AT BOOKING
    </footer>
  </div>
</div>

<nav class="rail" id="rail">{rail}</nav>

<script>
(function () {{
  var root = document.documentElement;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var lays = [].slice.call(document.querySelectorAll('#stage .lay'));
  var chaps = [].slice.call(document.querySelectorAll('.chapter'));
  var lead = document.querySelector('.lead');
  var hops = [].slice.call(document.querySelectorAll('.hop'));
  var marks = [];          // [{{c: centre, l: layer, r0/r1: dissolve window}}]
  var titles = [];         // per-chapter title glide bookkeeping
  var smooth = 0, target = 0, raf = 0;

  function ss(x) {{ x = x < 0 ? 0 : x > 1 ? 1 : x; return x * x * (3 - 2 * x); }}

  function measure() {{
    var y0 = scrollY;
    marks = [{{ c: lead.getBoundingClientRect().top + y0 + lead.offsetHeight * 0.5, l: 0 }}];
    chaps.forEach(function (ch) {{
      var r = ch.getBoundingClientRect();
      marks.push({{ c: r.top + y0 + r.height * 0.5, l: +ch.dataset.layer || 0 }});
    }});
    // the dissolve window for gap i is the hop band that physically sits in it,
    // so a plate is held at full strength for the whole time its day is readable
    for (var i = 1; i < marks.length; i++) {{
      var hop = hops[i - 2];
      if (hop) {{                       // the gap IS a hop band: ramp across it
        var hr = hop.getBoundingClientRect();
        marks[i].r0 = hr.top + y0; marks[i].r1 = hr.bottom + y0;
      }} else {{                          // lead → day 1: ramp as the hero leaves
        var lb = lead.getBoundingClientRect().bottom + y0, vh = innerHeight || 1;
        marks[i].r0 = lb - vh * 0.55; marks[i].r1 = lb - vh * 0.05;
      }}
    }}
    titles = chaps.map(function (ch) {{
      var m = ch.querySelector('.ch-meta');
      return {{ ch: ch, t: ch.querySelector('.ch-title'), m: m,
               pad: m ? parseFloat(getComputedStyle(m).paddingTop) || 0 : 0 }};
    }});
  }}

  function paint() {{
    var vh = innerHeight || 1;
    var docH = Math.max(1, document.body.scrollHeight - vh);
    var sun = Math.min(1, Math.max(0, smooth / docH));
    root.style.setProperty('--sun', sun.toFixed(4));
    if (reduce) return;   // never write inline styles over the filmstrip fallback

    // blend the two marks bracketing the viewport centre — the dissolve
    // therefore lands in the gap between chapters, i.e. on a .hop band
    var y = smooth + vh * 0.5, w = new Array(lays.length).fill(0);
    if (y <= marks[0].c) {{ w[marks[0].l] = 1; }}
    else if (y >= marks[marks.length - 1].c) {{ w[marks[marks.length - 1].l] = 1; }}
    else {{
      for (var i = 1; i < marks.length; i++) {{
        if (y <= marks[i].c) {{
          var a = marks[i - 1], b = marks[i];
          var t = ss((y - b.r0) / Math.max(1, b.r1 - b.r0));
          w[a.l] += 1 - t; w[b.l] += t;
          break;
        }}
      }}
    }}
    lays.forEach(function (el, i) {{
      var v = Math.min(1, w[i] || 0);
      el.style.opacity = v.toFixed(3);
      el.style.transform = 'scale(' + (1.06 - v * 0.05).toFixed(4) + ')';
    }});

    // title glide: the moment the day's first text line reaches the sticky
    // title, it slides to the right margin and shrinks — full-bleed for the
    // chapter opening, parked at the right edge while you read. Opacity is
    // untouched (owner's call): the overlay blend alone keeps it burned-in.
    if (innerWidth > 760) {{
      var t30 = vh * 0.30;
      titles.forEach(function (o) {{
        if (!o.t || !o.m) return;
        var cr = o.ch.getBoundingClientRect();
        if (cr.bottom < 0 || cr.top > vh) return;
        var th = o.t.offsetHeight || 1;
        var textTop = o.m.getBoundingClientRect().top + o.pad;
        var p = ss((t30 + th - textTop) / th);
        var sc = 1 - 0.45 * p;
        var dx = Math.max(0, innerWidth - o.t.offsetWidth * sc) * p;
        o.t.style.transform = 'translate3d(' + dx.toFixed(1) + 'px,0,0) scale(' + sc.toFixed(4) + ')';
      }});
    }}
  }}

  function tick() {{
    target = scrollY;
    smooth += (target - smooth) * (reduce ? 1 : 0.16);
    if (Math.abs(target - smooth) < 0.4) smooth = target;
    paint();
    raf = Math.abs(target - smooth) > 0.4 ? requestAnimationFrame(tick) : 0;
  }}
  function kick() {{ if (!raf) raf = requestAnimationFrame(tick); }}

  if (!reduce) {{
    addEventListener('scroll', kick, {{ passive: true }});
  }} else {{
    addEventListener('scroll', function () {{ smooth = scrollY; paint(); }}, {{ passive: true }});
  }}
  addEventListener('resize', function () {{ measure(); smooth = scrollY; paint(); }});
  document.addEventListener('toggle', function (e) {{
    if (e.target.tagName === 'DETAILS') {{ measure(); paint(); }}
  }}, true);
  addEventListener('load', function () {{ measure(); smooth = scrollY; paint(); }});
  measure(); smooth = scrollY; paint();

  /* rail scrollspy */
  var links = [].slice.call(document.querySelectorAll('.rail a[data-spy]'));
  var spy = new IntersectionObserver(function (es) {{
    es.forEach(function (e) {{
      if (!e.isIntersecting) return;
      links.forEach(function (l) {{
        l.classList.toggle('active', l.getAttribute('data-spy') === e.target.id);
      }});
      var act = document.querySelector('.rail a.active'), rail = document.getElementById('rail');
      if (act && rail.scrollWidth > rail.clientWidth)
        rail.scrollTo({{ left: act.offsetLeft - rail.clientWidth / 2 + act.offsetWidth / 2,
                        behavior: reduce ? 'auto' : 'smooth' }});
    }});
  }}, {{ rootMargin: '-40% 0px -50% 0px' }});
  chaps.forEach(function (c) {{ spy.observe(c); }});

  /* lazy maps */
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
    # PNG share engine — module-only: the sticky plane + rAF light live at
    # z:-1/-2/-3 behind the page and cannot survive a flat clone, so there is
    # deliberately NO whole-page button (page_root=""). extra_css neutralises
    # every rAF-written state inside the capture (plate opacity/scale, the
    # giant title's glide transform + overlay blend — inline styles ride along
    # with cloneNode) and re-pins the vh-based paddings, which would otherwise
    # resolve against the SVG viewport (= module height), not the window.
    html_out = html_out.replace("EXPORT_JS_PLACEHOLDER", export_js(
        theme_name(THEME), "#0b0d12",
        extra_css=(
            ".ch-title{position:static!important;mix-blend-mode:normal!important;"
            "color:#f2ede3!important;transform:none!important;opacity:1!important;"
            "padding:72px var(--gut) 0!important;"
            "text-shadow:0 2px 26px rgba(0,0,0,.6)}"
            ".ch-meta{padding:30px var(--gut) 22px!important}"
            ".chapter{padding:0 0 190px!important}"
            ".appx{padding:0 0 120px!important}"
            ".mapfold{display:none!important}"
            "#stage .lay{opacity:1!important;transform:none!important}"),
        page_root="", file_prefix=export_prefix(art, meta, THEME)))
    out = pathlib.Path(args.out)
    out.write_text(html_out, encoding="utf-8")
    print(f"{out.name}: {out.stat().st_size//1024}KB, days={len(days)}, "
          f"layers={asset_count()}")


if __name__ == "__main__":
    main()
