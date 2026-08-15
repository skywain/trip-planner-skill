#!/usr/bin/env python3
"""Illustrated-theme renderer v2 — cover-as-menu, breakout grid, papercraft.

Mockup-driven redesign (gpt-image-2 mock-cover/mock-day/mock-flow):
full-viewport cover (eyebrow dates → 4-char display title → ornament
subtitle → horizontal paper-card menu strip → circled scroll cue),
sticky 「第N天」scrollspy chips, per-day tinted full-bleed plates with
outline ghost numerals + polaroid stickers + 4-char day themes, spine
timeline with kind icons, taped margin note cards, handwritten endcap.
Single file, no external requests.

PNG export (share to 朋友圈/Twitter/IG) rides theme_common.export_js: every
day and the appendix close with an in-flow 〔保存这一天〕/〔保存附录〕bracket
annotation, highlighted the way a two-colour press marks a line it wants you
to find (gold tint block + mis-registered terracotta rule); the chips bar ends
in 〔生成长图〕 for the whole paper scroll (.folio root). The buttons sit in
normal flow at the end of the day block — never absolutely placed over the
plate, where they used to land inside the giant outline .ghost numeral.
Because those rows (and the hop-link <details>) are in-flow .no-export, the
engine is asked to size the canvas from the capture clone (export_js
measure_clone=True) — sizing from the live scrollHeight left ~1000-2600px of
blank paper at the foot of the long image (fixed 2026-08-16).

ART CONTRACT (what this renderer reads from the trip's art.json — schema in
ART-SCHEMA.md — and how it degrades when a field is missing; the renderer
never carries a place, a date or a picture name of its own):

  common (themes.illustrated.cover.* / .end.* override cover.* / end.* per key)
    cover.kick        short trip word: cover eyebrow prefix ("美国行 · 09-25 —
                      10-07"), <title> ("美国行 2026 · 插画版行程") and the
                      export filename prefix (theme_common.export_prefix;
                      en page: cover.kick_en wins in both when set)
                                                        → eyebrow = dates only,
                                                          <title> = "<year> · 插画版行程"
    cover.zh          the cover <h1> display title (4 chars fits the design)
                                                        → cover.kick, then "旅程"
    cover.en          letterspaced English line under the h1 → omitted
    cover.credit      the allusion / its source, small   → omitted
    cover.sub         the ornament subtitle (—— … ——)   → omitted
    home.city         alt text of the endcap picture ("回到北京") → alt=""
    end.line          hand-written closing line          → not written
    end.fine          fine print under it                → not written
                      (the endcap block is dropped entirely when it has no
                      picture, no line and no fine print)
    days[d].theme     4-char day title: menu card + plate <h2>
                                                        → the plan's city
                                                          (spaces stripped)
    brief_titles      {plan.brief key: section title} for the 行前须知 cards,
                      over theme_common.BRIEF_TITLES (visa→签证 …)
                                                        → shared defaults;
                                                          unknown keys print raw
  themes.illustrated
    cover.hero        asset stem of the full-bleed cover painting → no cover
                      picture (the paper scrims still paint the cover)
    end.hero          asset stem of the endcap cut-out    → no picture
    days[d].hero      asset stem of the day's cut-out illustration; the same
                      stem is inlined three ways by the kit — .sm on the menu
                      card, .md as the plate sticker, .lg as the faint tilted
                      backdrop (data_uri size chain)     → no picture in any of
                      the three slots (menu card is text-only, plate has no
                      sticker, no backdrop)
    days[d].feature   true → the day's menu card is a wide "feature" card
                      (170px, bigger cut-out) — the trip picks its two or three
                      headline days                     → normal card

Kit (the theme's own, nothing to pick in art): paper palette + the four plate
tints cycled by day number, the outline ghost numeral, alternating sticker
tilt (t0/t1) and backdrop side (side-l/side-r), the spine timeline with kind
icons, taped margin note cards, the 〔…〕bracket export annotations, the
appendix ledger.

Usage: python3 render_theme2.py <plan.geo.json> [--art <art.json>|none]
                                [--assets DIR ...] -o <out.html>
Assets (webp cut-outs) are searched in the plan's directory, every --assets
DIR, then themes/assets/ (theme_common.data_uri).
"""
import argparse
import pathlib
import urllib.parse

from theme_common import (LUCIDE, T, Art, add_art_arg, asset_count, brief_titles,
                          data_uri, day_embed_url, esc, export_js, export_prefix, init_lang,
                          lang, load_art, load_plan, short_dates, theme_name, title_head)

HERE = pathlib.Path(__file__).parent
THEME = "illustrated"

# ------------------------------------------------------------------ i18n --
# The theme's own voice (cover fallback word, chip wording, ledger heads,
# the 〔…〕bracket annotations, tooltips, footer). Shared UI words (tags,
# section names, save buttons, walk / rain / late-cut …) come from
# theme_common.T(). zh values are the page's historical bytes — never edit
# one without rebuilding the US baseline.
L = {
    "zh": {
        "cover_fallback": "旅程", "page_title": "插画版行程",
        "menu_aux": "航段 · 住宿<br>预算 · 清单",
        "chip_day": "第{i}天",
        "br_l": "〔", "br_r": "〕",
        "tag_swap": "swap",                    # free-form swap notes print raw
        "note": "注", "day_route": "整日路线", "route_map": "路线地图",
        "hop_summary": "{hop} · {n} 条",
        "map_ph": "地图加载中…(需联网;离线请用下方链接)",
        "nav_to": "导航到 {what}",
        "tip_day": "把这一天存成图片,可发朋友圈",
        "tip_appendix": "把附录(航段·住宿·预算·清单)存成图片,可发朋友圈",
        "tip_page": "把整卷行程拼成一张长图,可发朋友圈",
        "backup": "备选",
        "th_item": "项目", "th_cost": "费用", "th_note": "注", "total": "合计",
        "sec_legs": "航段速览", "sec_checklist": "行前清单",
        "back_to": "回到{city}",
        "menu_aria": "行程目录", "cue_aria": "下滑查看行程",
        "fx": "汇率",
        "footer": "日出日落数据:sunrise-sunset.org · 插画与设计稿由 AI 生成,仅作示意 · 价格以预订渠道实时为准",
    },
    "en": {
        "cover_fallback": "Journey", "page_title": "Illustrated itinerary",
        "menu_aux": "Flights · Stays<br>Budget · Checklist",
        "chip_day": "Day {i}",
        "br_l": "[ ", "br_r": " ]",
        "tag_swap": "swap",
        "note": "Note", "day_route": "Full-day route", "route_map": "Route map",
        "hop_summary": "{hop} · {n}",
        "map_ph": "Loading map… (needs internet; offline, use the links below)",
        "nav_to": "Navigate to {what}",
        "tip_day": "Save this day as an image to share",
        "tip_appendix": "Save the appendix (flights · stays · budget · checklist) as an image",
        "tip_page": "Stitch the whole itinerary into one long image to share",
        "backup": "Backup",
        "th_item": "Item", "th_cost": "Cost", "th_note": "Note", "total": "Total",
        "sec_legs": "Flights & legs", "sec_checklist": "Checklist",
        "back_to": "Back to {city}",
        "menu_aria": "Itinerary contents", "cue_aria": "Scroll to the itinerary",
        "fx": "FX",
        "footer": "Sunrise/sunset data: sunrise-sunset.org · Illustrations and layouts are AI-generated, for illustration only · Prices are live at the booking channel",
    },
}


def t(k):
    return L.get(lang(), L["zh"]).get(k, L["zh"][k])


def br(s):
    """The theme's bracket annotation: 〔…〕 in zh, [ … ] in en."""
    return f'{t("br_l")}{s}{t("br_r")}'
# the trip's art direction (set in main from --art); every trip-specific
# choice — pictures, feature days, cover words, closing line — comes from here
ART = Art()


def ic(name, cls=""):
    """Local, sprite-free glyphs (shadows theme_common.ic).

    The export engine serialises only the cloned capture root, so a shared
    <defs> sprite at body level is never part of the SVG image and every
    <use href="#i-…"> inside a captured module would dangle — glyphs silently
    vanish from the PNG. This theme therefore inlines each lucide body
    directly; no sprite element is emitted at all."""
    c = f"ic {cls}".strip()
    return (f'<svg class="{c}" viewBox="0 0 24 24" aria-hidden="true">'
            f"{LUCIDE[name]}</svg>")


def et(s):
    """esc + emoji→glyph swaps, on the local inline ic (shadows theme_common.et)."""
    t = esc(s)
    return (t.replace("✈️", ic("plane")).replace("✈", ic("plane"))
             .replace("⚠️", ic("alert", "warn")).replace("⚠", ic("alert", "warn"))
             .replace("☀", ic("sunrise")).replace("🌇", ic("sunset")))

KIND_CLASS = {"anchor": "k-anchor", "hop": "k-hop", "meal": "k-meal", "free": "k-free"}



def icon_uri(body):
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
           'viewBox="0 0 24 24" fill="none" stroke="#6d9a94" stroke-width="2" '
           'stroke-linecap="round" stroke-linejoin="round">' + body + "</svg>")
    return "data:image/svg+xml," + urllib.parse.quote(svg)


ICONS = {
    "k-anchor": icon_uri(LUCIDE["pin"]),
    "k-meal": icon_uri(LUCIDE["meal"]),
    "k-hop": icon_uri(LUCIDE["arrow"]),
    "k-free": icon_uri(LUCIDE["moon"]),
}


def short_city(city):
    return city.replace(" ", "")


def render_menu(days):
    cards = []
    for i, d in enumerate(days, 1):
        da = ART.day(d.get("date", ""), THEME)
        art = data_uri(da.get("hero", ""), "sm")
        feature = " feature" if da.get("feature") else ""
        img = f'<img src="{art}" alt="">' if art else ""
        date_short = d.get("date", "")[5:].replace("-", ".")
        theme = ART.day_theme(d.get("date", ""), "")
        cards.append(
            f'<a class="mcard{feature}" href="#d{i}">{img}'
            f'<span class="m-day">DAY {i} · {date_short}</span>'
            f'<span class="m-city">{esc(theme or short_city(d.get("city","")))}</span></a>')
    cards.append('<a class="mcard aux" href="#legs">'
                 f'<span class="m-day">{esc(T("sec.appendix"))}</span>'
                 f'<span class="m-city">{t("menu_aux")}</span></a>')
    return "".join(cards)


def render_chips(days):
    chips = ['<a href="#top" class="chip-home">☰</a>']
    for i, _ in enumerate(days, 1):
        chips.append(f'<a href="#d{i}" data-spy="d{i}">{esc(t("chip_day").format(i=i))}</a>')
    chips.append(f'<a href="#legs" data-spy="legs">{esc(T("sec.appendix"))}</a>')
    chips.append('<a href="#" class="xbtn xbtn-page no-export" data-x-page '
                 f'title="{esc(t("tip_page"))}">{esc(br(T("btn.save_page")))}</a>')
    return "".join(chips)


def render_timeline(day):
    rows = []
    for r in day.get("timeline", []):
        kind = KIND_CLASS.get(r.get("kind", ""), "k-anchor")
        est = ' <span class="est">est</span>' if r.get("verify") == "est" else ""
        chips = ""
        tag = r.get("tag", "")
        if tag:
            label = (t("tag_swap") + tag[4:] if tag.startswith("swap")
                     else T("tag." + tag, tag))
            filled = " chip-filled" if tag == "pinned" else ""
            chips = f'<span class="chip{filled}">{esc(label)}</span>'
        price = r.get("price", "")
        price_html = f' <span class="price">{esc(price)}</span>' if price else ""
        nav = (f' <a class="rownav" href="{esc(r["link"])}" target="_blank" rel="noopener"'
               f' aria-label="{esc(t("nav_to").format(what=r.get("what", "")[:18]))}">{ic("pin")}</a>'
               if r.get("link") else "")
        rows.append(
            f'<div class="tl-row {kind}"><div class="tl-t">{esc(r.get("t",""))}{est}</div>'
            f'<div class="tl-what">{et(r.get("what",""))}{price_html} {chips}{nav}</div></div>')
    return "".join(rows)


def meta_notes(day):
    notes = []
    wk = day.get("walking_km")
    if isinstance(wk, dict):
        notes.append(("walk", "%s ≈%s km" % (T("walk"), wk.get("total", "?")), wk.get("how", "")))
    elif wk:
        notes.append(("walk", f"{T('walk')} ≈{wk} km", ""))
    if day.get("rain_alt"):
        notes.append(("rain", T("rain_alt"), day["rain_alt"]))
    if day.get("late_cut"):
        notes.append(("clock", T("late_cut"), day["late_cut"]))
    if day.get("note"):
        notes.append(("note", t("note"), day["note"]))
    return notes


def render_day(i, day):
    stem = ART.day(day.get("date", ""), THEME).get("hero", "")
    art = data_uri(stem, "md")
    bg = data_uri(stem, "lg")
    side = "side-r" if i % 2 else "side-l"
    bg_html = (f'<img class="day-bg {side}" src="{bg}" alt="" aria-hidden="true">'
               if bg else "")
    art_html = (f'<figure class="polaroid t{i % 2}"><img src="{art}" alt=""></figure>'
                if art else "")
    # sun --write may say 天亮 or dawn depending on the language it ran in;
    # print the current language's word either way
    sun_raw = esc(day.get("sun", "").replace("天亮", T("sun.dawn")).replace("dawn", T("sun.dawn")))
    sun_raw = sun_raw.replace("☀", ic("sunrise")).replace("🌇", ic("sunset"))
    sun = f'<span class="sun">{sun_raw}</span>' if sun_raw else ""
    # no 4-char title in art → the plan's city, so the plate never loses its h2
    theme = ART.day_theme(day.get("date", ""), short_city(day.get("city", "")))
    theme_html = f'<span class="theme">{esc(theme)}</span>' if theme else ""

    notes_html = "".join(
        f'<aside class="note-card"><b>{ic(icn)} {esc(t)}</b>'
        + (f"<p>{esc(b)}</p>" if b else "") + "</aside>"
        for icn, t, b in meta_notes(day))

    links = []
    if day.get("day_map"):
        links.append(f'<a href="{esc(day["day_map"])}" target="_blank" rel="noopener">{esc(t("day_route"))}</a>')
    for n, u in enumerate(day.get("hop_links", []), 1):
        links.append(f'<a href="{esc(u)}" target="_blank" rel="noopener">{n}</a>')
    embed = day_embed_url(day)
    embed_html = (f'<div class="map-embed" data-src="{esc(embed)}">'
                  f'<p class="map-ph">{esc(t("map_ph"))}</p></div>'
                  if embed else "")
    summary_txt = esc(t("hop_summary").format(hop=T("hop.map"), n=len(links))
                      if links else t("route_map"))
    btns = f'<div class="hop-btns">{" ".join(links)}</div>' if links else ""
    # no-export: an interactive map/details affordance is dead weight in a PNG
    links_html = (
        f'<details class="hoplinks no-export"><summary>{ic("compass")} {summary_txt}'
        f' {ic("chevron", "chev")}</summary>{embed_html}{btns}</details>'
        if (links or embed) else "")

    return f"""
<section class="day tint{i % 4} reveal" id="d{i}">
  {bg_html}
  <header class="plate">
    <span class="ghost" aria-hidden="true">{i:02d}</span>
    {art_html}
    <div class="plate-txt">
      <span class="day-no">DAY {i} · {esc(day.get("date",""))} · {esc(day.get("city",""))}</span>
      <h2>{theme_html}</h2>
      <p class="label">{esc(day.get("label",""))}</p>
      {sun}
    </div>
  </header>
  <div class="day-body">
    <div class="tl">{render_timeline(day)}{links_html}</div>
    <div class="margin-rail">{notes_html}</div>
  </div>
  <div class="xrow no-export">
    <button class="xbtn" data-x-for="#d{i}" data-x-label="DAY{i:02d}"
      title="{esc(t("tip_day"))}">{esc(br(T("btn.save_day")))}</button>
  </div>
</section>"""


def render_legs(legs):
    rows = []
    for l in legs:
        backup = f'<details><summary>{esc(t("backup"))}</summary><p>{esc(l["backup"])}</p></details>' if l.get("backup") else ""
        link = f' <a href="{esc(l["link"])}" target="_blank" rel="noopener">{esc(T("price.check"))}</a>' if l.get("link") else ""
        rows.append(
            f'<div class="leg"><b>{esc(l.get("date",""))}</b> {esc(l.get("from",""))} → {esc(l.get("to",""))}'
            f' <span class="mini">{et(l.get("carrier",""))} · {esc(l.get("dep",""))}→{esc(l.get("arr",""))}'
            f' · {esc(l.get("price",""))} · {esc(l.get("bags",""))}{link}</span>{backup}</div>')
    return "".join(rows)


def render_hotels(hotels):
    out = []
    for h in hotels:
        opts = "".join(
            f'<li><a href="{esc(o.get("link","#"))}" target="_blank" rel="noopener">{esc(o.get("name",""))}</a>'
            f' <span class="mini">{esc(o.get("band",""))}</span></li>'
            for o in h.get("options", []))
        out.append(f'<div class="hotel"><h3>{esc(h.get("base",""))} · {esc(h.get("area",""))}</h3>'
                   f'<p class="mini">{esc(h.get("why",""))}</p><ul>{opts}</ul></div>')
    return "".join(out)


TOTAL_BUDGET = ""


def render_budget(budget):
    rows = "".join(
        f'<tr><td>{esc(b.get("cat",""))}</td><td>{esc(b.get("per_person",""))}</td>'
        f'<td class="mini">{esc(b.get("note",""))}</td></tr>' for b in budget)
    return (f'<table class="budget"><tr><th>{esc(t("th_item"))}</th><th>{esc(t("th_cost"))}</th>'
            f'<th>{esc(t("th_note"))}</th></tr>{rows}'
            f'<tr class="total"><td>{esc(t("total"))}</td><td colspan="2">{esc(TOTAL_BUDGET)}</td></tr>'
            '</table>')


def render_checklist(items):
    out = []
    for c in items:
        link = (f' <a href="{esc(c["link"])}" target="_blank" rel="noopener">{esc(c.get("link_text", T("link")))}</a>'
                if c.get("link") else "")
        note = f'<p class="mini">{et(c["note"])}</p>' if c.get("note") else ""
        out.append(f'<li><b>{et(c.get("item",""))}</b> — {esc(c.get("deadline",""))}'
                   f' · {esc(c.get("price",""))}{link}{note}</li>')
    return "<ol>" + "".join(out) + "</ol>"


def render_brief(brief):
    # plan.brief keys are English identifiers (visa / holidays …); label them
    # from the shared table (theme_common.BRIEF_TITLES) overlaid by the art
    # file's common brief_titles; unknown keys print as they are
    titles = brief_titles(ART)
    return "".join(
        f'<div class="brief-card"><h3>{esc(titles.get(k, k))}</h3><p>{et(v)}</p></div>'
        for k, v in brief.items())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("-o", "--out", required=True)
    add_art_arg(ap)
    args = ap.parse_args()
    p = load_plan(args.plan)
    init_lang(args, p)
    global ART, TOTAL_BUDGET
    ART = load_art(args.plan, args.art, args.assets)

    meta = p.get("meta", {})
    TOTAL_BUDGET = meta.get("budget_total", "")
    days = p.get("days", [])
    days_html = "".join(render_day(i + 1, d) for i, d in enumerate(days))
    unverified = "".join(f"<li>{et(u)}</li>" for u in p.get("unverified", []))
    decisions = "".join(f"<li>{et(u)}</li>" for u in p.get("decisions", []))
    dates = short_dates(meta.get("dates", "")).replace(" → ", " — ")
    year = (meta.get("dates", "") or "")[:4]
    year = year if year.isdigit() else ""

    # cover words — all the trip's, all optional
    kick = ART.cover(THEME, "kick")
    cover_zh = ART.cover(THEME, "zh") or kick or t("cover_fallback")
    cover_en = ART.cover(THEME, "en")
    cover_credit = ART.cover(THEME, "credit")
    cover_sub = ART.cover(THEME, "sub")
    page_title = " · ".join(x for x in (title_head(ART, THEME, year), t("page_title")) if x)
    eyebrow = f"{esc(kick)} · {esc(dates)}" if kick and dates else esc(kick or dates)
    cover_lines = "".join((
        f'\n    <p class="en-title">{esc(cover_en)}</p>' if cover_en else "",
        f'\n    <p class="quote">{esc(cover_credit)}</p>' if cover_credit else "",
        f'\n    <p class="subtitle">{esc(cover_sub)}</p>' if cover_sub else ""))
    cover = data_uri(ART.cover(THEME, "hero"))
    cover_html = f'\n  <img class="cover-art" src="{cover}" alt="">' if cover else ""

    # endcap: picture (alt = 回到<home city>), closing line, fine print — any
    # subset; nothing at all → no endcap block
    endcap = data_uri(ART.end(THEME, "hero"), "md")
    home_city = ART.get("home", "city", default="") or ""
    end_line = ART.end(THEME, "line")
    end_fine = ART.end(THEME, "fine")
    endcap_parts = [x for x in (
        f'<img src="{endcap}" alt="{esc(t("back_to").format(city=home_city) if home_city else "")}">' if endcap else "",
        f"<p>{esc(end_line)}</p>" if end_line else "",
        f'<p class="fine">{esc(end_fine)}</p>' if end_fine else "") if x]
    endcap_html = ('\n  <div class="endcap reveal">\n    ' + "\n    ".join(endcap_parts)
                   + "\n  </div>\n") if endcap_parts else ""

    icon_css = "".join(
        f'.{k} .tl-what::after {{ background-image:url("{v}"); }}' for k, v in ICONS.items())

    html_out = f"""<!doctype html>
<html lang="{T("html_lang")}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(page_title)}</title>
<style>
  :root {{
    --paper:#f6efe3; --ink:#3f3a33; --muted:#6B6355; --terracotta:#A6472A;
    --teal:#3F6E67; --card:#fffaf1; --line:#d8cdb9; --sand:#efe4cf;
    --terracotta-lite:#c46f4f;   /* decorative only: rules, bars, display type */
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  body {{ background:var(--paper); color:var(--ink);
    font-family:"Songti SC","Noto Serif SC",Georgia,serif; }}
  a {{ color:var(--teal); }}
  .mini {{ font-size:12px; color:var(--muted); line-height:1.7; }}
  .ic {{ width:1em; height:1em; fill:none; stroke:currentColor; stroke-width:1.75;
    stroke-linecap:round; stroke-linejoin:round; vertical-align:-0.125em; }}
  :focus-visible {{ outline:3px solid var(--terracotta); outline-offset:3px; border-radius:4px; }}
  .mcard:focus-visible, .chips a:focus-visible {{ outline-offset:4px; }}
  .rownav {{ display:inline-flex; align-items:center; justify-content:center;
    min-width:44px; min-height:44px; margin:-13px -8px -13px 0; color:var(--teal);
    vertical-align:middle; }}
  .rownav .ic {{ width:14px; height:14px; }}
  .ic.warn {{ color:var(--terracotta); }}
  h2.sec .ic {{ width:22px; height:22px; color:var(--terracotta); margin-right:4px;
    stroke-dasharray:100; stroke-dashoffset:100; }}
  h2.sec.in .ic {{ stroke-dashoffset:0;
    transition:stroke-dashoffset 1.3s ease .15s; }}

  .progress {{ position:fixed; top:0; left:0; height:3px; width:100%;
    background:var(--terracotta-lite); transform-origin:0 50%; transform:scaleX(0); z-index:50; }}
  @supports (animation-timeline: scroll()) {{
    .progress {{ animation:grow linear both; animation-timeline:scroll(root); }}
    @keyframes grow {{ to {{ transform:scaleX(1); }} }}
  }}

  /* ---------- cover ---------- */
  .cover {{ position:relative; min-height:100vh; min-height:100svh;
    display:flex; flex-direction:column; }}
  .cover-art {{ position:absolute; inset:0; width:100%; height:100%;
    object-fit:cover; object-position:center 78%; }}
  /* bottom scrim doubles as the menu strip's backing — it lives on the cover
     (full width, never scrolls), NOT on the scrollable .menu, so there is no
     seam where the first viewport-width of ::before used to end */
  .cover::after {{ content:""; position:absolute; inset:0;
    background:linear-gradient(180deg, rgba(246,239,227,0) 54%, rgba(246,239,227,.55) 80%,
      rgba(246,239,227,.86) 93%, var(--paper) 100%);
    pointer-events:none; }}
  /* the title lives in the TOP 40% of the cover — the bottom scrim never reached it */
  .cover::before {{ content:""; position:absolute; inset:0 0 auto 0; height:58%; z-index:1;
    pointer-events:none;
    background:linear-gradient(180deg, rgba(246,239,227,.92) 0%, rgba(246,239,227,.74) 40%,
      rgba(246,239,227,0) 100%); }}
  .cover-txt {{ position:relative; z-index:3; text-align:center;
    padding-top:clamp(48px,14vh,140px); }}
  .eyebrow {{ font-size:clamp(12px,1.5vw,16px); letter-spacing:.5em; color:#8f3a22;
    font-family:inherit; }}
  .cover-txt h1 {{ font-size:clamp(56px,10vw,124px); font-weight:700; letter-spacing:.14em;
    margin:14px 0 10px; color:#8f3a22; text-indent:.14em; }}
  .en-title {{ font-size:clamp(11px,1.3vw,14px); letter-spacing:.46em; color:#33635c;
    font-family:inherit; margin-bottom:10px; text-indent:.46em; }}
  .quote {{ font-size:clamp(11px,1.3vw,13px); color:#5a5248;
    margin-bottom:14px; letter-spacing:.12em; }}
  .subtitle {{ font-size:clamp(12px,1.6vw,16px); color:#5a5248;
    letter-spacing:.24em; }}
  .subtitle::before, .subtitle::after {{ content:"——"; color:var(--terracotta);
    opacity:.6; margin:0 12px; }}

  .menu {{ position:relative; z-index:2; margin-top:auto; display:flex; gap:14px;
    overflow-x:auto; padding:26px clamp(16px,4vw,56px) 84px;
    scroll-snap-type:x proximity; scrollbar-width:none; }}
  .menu::-webkit-scrollbar {{ display:none; }}
  .mcard {{ flex:0 0 138px; scroll-snap-align:start;
    background:none; border:0; border-radius:0; padding:10px 8px 8px;
    backdrop-filter:none; -webkit-backdrop-filter:none;
    display:flex; flex-direction:column; align-items:center; justify-content:flex-end; gap:6px;
    text-decoration:none; color:var(--ink); box-shadow:none;
    transition:transform .18s ease; }}
  .mcard:hover {{ transform:translateY(-6px) rotate(-.6deg); }}
  .mcard:hover img {{ filter:drop-shadow(0 12px 12px rgba(63,58,51,.45)); }}
  .mcard img {{ max-height:64px; max-width:86%;
    filter:drop-shadow(0 6px 8px rgba(63,58,51,.4)); }}
  .mcard.feature {{ flex-basis:170px; }}
  .mcard.feature img {{ max-height:84px; }}
  .mcard.aux {{ justify-content:center; text-align:center; }}
  .m-day {{ font-size:10px; letter-spacing:.14em; color:var(--teal);
    font-family:inherit; }}
  .m-city {{ font-size:14px; font-weight:700; position:relative; padding-bottom:6px; }}
  .m-city::after {{ content:""; position:absolute; left:50%; bottom:0; translate:-50% 0;
    width:22px; border-bottom:2px solid var(--terracotta); }}

  .cue {{ position:absolute; bottom:24px; left:50%; translate:-50% 0; z-index:3;
    width:36px; height:36px; border:1.6px solid var(--terracotta); border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    background:rgba(253,246,233,.8); animation:bob 1.9s ease-in-out infinite; }}
  @keyframes bob {{ 50% {{ transform:translateY(7px); }} }}

  /* ---------- sticky chips ---------- */
  .chips {{ position:sticky; top:0; z-index:40; display:flex; gap:8px; overflow-x:auto;
    scrollbar-width:none; padding:10px clamp(14px,3vw,28px);
    background:rgba(246,239,227,.93); backdrop-filter:blur(5px);
    border-bottom:1px solid var(--line); }}
  .chips::-webkit-scrollbar {{ display:none; }}
  /* tabbed page edges, the way a book indexes itself — no capsules */
  .chips a {{ flex:0 0 auto; font-size:12px; padding:9px 14px; min-height:44px;
    display:inline-flex; align-items:center; border:0;
    border-bottom:2px solid transparent; color:var(--muted); text-decoration:none;
    background:none; }}
  .chips a:hover {{ color:var(--ink); }}
  .chips a.active {{ color:var(--terracotta); font-weight:700;
    border-bottom-color:var(--terracotta); background:none; }}
  .chip-home {{ color:var(--terracotta) !important; }}

  /* ---------- day sections ---------- */
  section[id], h2[id] {{ scroll-margin-top:52px; }}
  .day {{ padding-bottom:30px; position:relative; overflow:hidden; }}
  .day-bg {{ position:absolute; z-index:0; top:clamp(230px,32%,360px);
    max-width:clamp(300px,34vw,520px); max-height:460px; width:auto; height:auto;
    opacity:.15; pointer-events:none; user-select:none; }}
  .day-bg.side-l {{ left:max(-40px, calc(50% - 800px)); rotate:-6deg; }}
  .day-bg.side-r {{ right:max(-40px, calc(50% - 800px)); rotate:6deg; }}
  .plate {{ position:relative; z-index:1; overflow:hidden;
    border-top:1px dashed var(--line); border-bottom:1px dashed var(--line);
    padding:36px clamp(18px,7vw,110px); display:flex; align-items:center;
    gap:clamp(22px,4vw,44px); margin-bottom:30px; }}
  .tint1 .plate {{ background:rgba(196,111,79,.09); }}
  .tint2 .plate {{ background:rgba(109,154,148,.11); }}
  .tint3 .plate {{ background:rgba(214,177,96,.13); }}
  .tint0 .plate {{ background:var(--sand); }}
  .ghost {{ position:absolute; right:clamp(4px,3vw,44px); top:50%; translate:0 -50%;
    font-size:clamp(96px,15vw,190px); font-weight:700; color:transparent;
    -webkit-text-stroke:2.5px rgba(253,246,233,.9); paint-order:stroke;
    font-family:inherit; pointer-events:none; }}
  @supports not (-webkit-text-stroke:1px black) {{
    .ghost {{ color:rgba(253,246,233,.55); }}
  }}
  /* the art is an object in the world, not a matted print in a frame */
  .polaroid {{ flex:0 0 auto; background:none; padding:0; border:0; box-shadow:none; }}
  .polaroid img {{ display:block; max-height:132px; max-width:172px;
    filter:drop-shadow(0 12px 12px rgba(63,58,51,.26)); }}
  .polaroid.t0 {{ rotate:2deg; }}
  .polaroid.t1 {{ rotate:-2deg; }}
  .day-no {{ font-size:11px; letter-spacing:.2em; color:var(--teal);
    font-family:inherit; }}
  .theme {{ color:var(--terracotta); }}
  .plate-txt h2 {{ font-size:clamp(24px,3vw,32px); letter-spacing:.1em; margin:6px 0; }}
  .label {{ font-size:13.5px; color:var(--muted); max-width:34em; }}
  .sun {{ font-size:12px; color:var(--muted); }}

  .day-body {{ max-width:1120px; margin:0 auto; padding:0 clamp(16px,3vw,32px);
    position:relative; z-index:1; display:grid; grid-template-columns:minmax(0,1fr) 15.5rem; column-gap:2.8rem; }}
  .tl, .margin-rail {{ min-width:0; }}
  .tl {{ position:relative; padding-left:20px; }}
  .tl::before {{ content:""; position:absolute; left:3px; top:10px; bottom:10px;
    border-left:2px dashed var(--line); }}
  .tl-row {{ position:relative; display:flex; gap:14px; padding:8px 8px;
    border-bottom:1px dashed rgba(216,205,185,.55); border-radius:0; }}
  .tl-row:last-of-type {{ border-bottom:none; }}
  .tl-row::before {{ content:""; position:absolute; left:-21px; top:15px; width:8px; height:8px;
    border-radius:50%; background:var(--terracotta); border:2px solid var(--paper); }}
  .k-hop::before {{ background:var(--teal) !important; width:6px; height:6px; }}
  .k-meal::before {{ background:var(--sand) !important; border-color:var(--terracotta); }}
  .k-free::before {{ background:var(--line) !important; }}
  /* a book sets its times as marginalia: right-ranged, lining figures, no pill */
  .tl-t {{ flex:0 0 104px; font-size:12.5px; font-weight:400; color:var(--terracotta);
    text-align:right; padding-top:3px; letter-spacing:.02em;
    font-variant-numeric:lining-nums tabular-nums; }}
  .tl-what {{ font-size:13.5px; line-height:1.8; flex:1 1 0; min-width:0;
    overflow-wrap:anywhere; position:relative; padding-right:26px; }}
  .tl-what::after {{ content:""; position:absolute; right:0; top:4px; width:16px; height:16px;
    background-repeat:no-repeat; background-size:contain; opacity:.75; }}
  {icon_css}
  .k-hop .tl-t {{ color:var(--teal); font-weight:400; }}
  .k-hop .tl-what {{ color:#5d7a75; font-size:12.5px; }}
  .k-meal {{ background:rgba(239,228,207,.6); }}
  .k-free .tl-what {{ color:var(--muted); font-style:italic; }}
  .est {{ font-size:9px; color:var(--muted); vertical-align:super; }}
  .price {{ color:var(--muted); font-size:12px; }}
  /* no pills in a book — annotations are bracketed, and the pinned one is
     simply underscored in the accent ink */
  /* an inline annotation wraps with the sentence it annotates */
  .chip {{ display:inline; font-size:11.5px; color:var(--terracotta);
    margin-left:6px; letter-spacing:.04em; }}
  .chip::before {{ content:"{t("br_l")}"; }}
  .chip::after {{ content:"{t("br_r")}"; }}
  .chip-filled {{ font-weight:700;
    border-bottom:2px solid var(--terracotta); padding-bottom:1px; }}
  .hoplinks {{ margin-top:12px; font-size:12px; color:var(--muted); }}
  .hoplinks summary {{ cursor:pointer; list-style:none; display:flex;
    align-items:center; gap:10px; padding:10px 0 0; border:0;
    border-top:1px solid var(--line); user-select:none; min-height:44px; }}
  .hoplinks summary::after {{ content:""; flex:1 1 auto; height:1px;
    background:var(--line); }}
  .hoplinks summary::-webkit-details-marker {{ display:none; }}
  .hoplinks .chev {{ transition:transform .25s ease; }}
  .hoplinks[open] .chev {{ transform:rotate(180deg); }}
  .hop-btns {{ padding-top:8px; }}
  .map-embed {{ margin-top:10px; border:1px solid var(--line); border-radius:12px;
    overflow:hidden; background:var(--sand); }}
  .map-embed iframe {{ display:block; width:100%; height:320px; border:0; }}
  .map-ph {{ padding:20px; font-size:12px; color:var(--muted); text-align:center; }}
  .hoplinks a {{ display:inline-flex; align-items:center; justify-content:center;
    min-width:44px; min-height:44px; padding:0 8px; margin:2px; text-decoration:none;
    border:0; border-bottom:1px solid var(--teal); }}
  .hoplinks a::before {{ content:"["; opacity:.5; margin-right:1px; }}
  .hoplinks a::after {{ content:"]"; opacity:.5; margin-left:1px; }}

  .margin-rail {{ display:flex; flex-direction:column; gap:14px; align-content:start; }}
  .note-card {{ position:relative; background:var(--card); border:1px solid var(--line);
    border-radius:3px; padding:14px 13px 11px; font-size:12px; color:var(--muted);
    line-height:1.75; rotate:.6deg;
    box-shadow:0 8px 18px -12px rgba(63,58,51,.4); }}
  .note-card:nth-child(even) {{ rotate:-.6deg; background:#fbf6ea; }}
  .note-card:nth-child(3n) {{ background:rgba(109,154,148,.08); }}
  .note-card::before {{ content:""; position:absolute; top:-7px; left:50%; translate:-50% 0;
    width:44px; height:14px; background:rgba(109,154,148,.35); rotate:-2deg; }}
  .note-card b {{ color:var(--ink); font-size:12.5px; display:inline-block;
    border-bottom:2px solid rgba(196,111,79,.5); padding-bottom:2px; margin-bottom:4px; }}
  .note-card p {{ margin-top:4px; }}

  /* ---------- appendix ---------- */
  .appendix {{ max-width:900px; margin:0 auto; padding:0 clamp(16px,3vw,32px); }}
  .appendix.wide {{ max-width:1120px; }}
  h2.sec {{ margin:56px 0 16px; font-size:20px; letter-spacing:.12em;
    border-left:4px solid var(--terracotta); padding-left:12px; }}
  .leg {{ padding:9px 0; border-bottom:1px dashed var(--line); font-size:13.5px; }}
  .hotel {{ background:none; border:0; border-top:2px solid var(--terracotta);
    border-radius:0; padding:14px 0 0; margin-top:22px; }}
  .hotel h3 {{ font-size:15px; margin-bottom:4px; }}
  .hotel ul {{ margin:8px 0 0 18px; font-size:13px; }}
  /* ledger, not card: ink on paper, hairline rules, flush with the heading */
  table {{ width:100%; border-collapse:collapse; font-size:13px; background:none; }}
  th,td {{ border:0; border-bottom:1px solid var(--line); padding:10px 20px 10px 0;
    text-align:left; vertical-align:top; line-height:1.65;
    font-variant-numeric:tabular-nums; }}
  th:last-child, td:last-child {{ padding-right:0; }}
  th {{ background:none; border-bottom:2px solid var(--terracotta);
    font-size:11px; font-weight:700; letter-spacing:.18em; color:var(--muted);
    padding-bottom:8px; }}
  table.budget th:nth-child(1) {{ width:37%; }}
  table.budget th:nth-child(2) {{ width:31%; }}
  table.budget td:nth-child(2) {{ color:#7a4530; }}
  /* accounting close: single rule above, double rule below — no tinted block */
  tr.total td {{ background:none; font-weight:700; font-size:13.5px;
    border-top:2px solid var(--terracotta);
    border-bottom:4px double var(--terracotta); padding:12px 20px 11px 0; }}
  ol {{ margin-left:20px; font-size:13.5px; }}
  ol li {{ margin-top:10px; line-height:1.7; }}
  ul.warn {{ margin-left:20px; font-size:13px; color:#8a5a3c; }}
  ul.warn li {{ margin-top:6px; line-height:1.7; }}
  .brief-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));
    column-gap:2.8rem; row-gap:30px; }}
  .brief-card {{ background:none; border:0; border-top:2px solid var(--terracotta);
    border-radius:0; padding:12px 0 0; }}
  .brief-card h3 {{ font-size:14px; margin-bottom:6px; color:var(--terracotta); }}
  .brief-card p {{ font-size:12.5px; line-height:1.8; color:var(--muted); }}
  details {{ font-size:12.5px; color:var(--muted); margin-top:6px; }}
  details summary {{ cursor:pointer; }}
  details p {{ padding:6px 2px 2px 14px; line-height:1.8; }}

  /* ---------- export actions ---------- */
  /* still the 〔…〕annotation voice of the page — no capsule, no button
     chrome, same serif, same 12px. What makes it findable is the theme's own
     printing: a gold tint block laid under the note like a highlighter pass
     that ran out of ink at both ends, with the terracotta plate deliberately
     mis-registered a hair below it. Hover deepens the ink and pulls the two
     plates into register. It rides in normal flow at the end of the day
     block — never over the plate, where it used to sit inside the .ghost. */
  .xrow {{ max-width:1120px; margin:12px auto 0; padding:0 clamp(16px,3vw,32px);
    display:flex; justify-content:flex-end; position:relative; z-index:2; }}
  .xrow.narrow {{ max-width:900px; }}
  .xbtn {{ position:relative; isolation:isolate;
    display:inline-flex; align-items:center; min-height:44px;
    background:none; border:0; border-radius:0; padding:0 13px;
    font-family:inherit; font-size:12px; letter-spacing:.1em;
    color:#7A3418; cursor:pointer; text-decoration:none; }}
  /* the highlighter pass — a swipe, not a chip: the clip-path wedge keeps the
     ends slanted and the top edge un-level, and the ink runs out at both ends */
  .xbtn::before {{ content:""; position:absolute; z-index:-1; left:0; right:0;
    top:50%; height:1.95em; translate:0 -50%; rotate:-.9deg;
    background:linear-gradient(97deg, rgba(214,177,96,0) 0%, rgba(214,177,96,.74) 6%,
      rgba(220,187,114,.5) 48%, rgba(212,173,88,.76) 90%, rgba(214,177,96,.04) 100%);
    clip-path:polygon(1.2% 14%, 99.2% 3%, 98.4% 90%, .6% 99%);
    transition:background .22s ease, rotate .22s ease; }}
  /* the terracotta plate, printed off-register under the gold one */
  .xbtn::after {{ content:""; position:absolute; z-index:-2; left:3px; right:-3px;
    top:50%; height:1.95em; translate:0 calc(-50% + 3.5px); rotate:-.9deg;
    background:rgba(166,71,42,.22);
    clip-path:polygon(1.2% 14%, 99.2% 3%, 98.4% 90%, .6% 99%);
    transition:background .22s ease, translate .28s ease, rotate .22s ease; }}
  /* hover deepens the ink and pulls the two plates into register */
  .xbtn:hover::before, .xbtn:focus-visible::before {{ rotate:0deg;
    background:linear-gradient(97deg, rgba(214,177,96,.08) 0%, rgba(213,170,74,.92) 6%,
      rgba(223,190,116,.72) 48%, rgba(211,168,72,.94) 90%, rgba(214,177,96,.1) 100%); }}
  .xbtn:hover::after, .xbtn:focus-visible::after {{ rotate:0deg;
    translate:0 calc(-50% + 1.5px); background:rgba(166,71,42,.34); }}
  .backmatter {{ position:relative; max-width:1120px; margin:0 auto; }}
  .chips a.xbtn-page {{ margin-left:auto; border-bottom:0; color:#7A3418;
    padding:0 11px; min-width:44px; }}

  .endcap {{ text-align:center; margin:64px auto 8px; max-width:640px; padding:0 18px; }}
  .endcap img {{ max-height:150px; filter:drop-shadow(0 8px 8px rgba(63,58,51,.18)); }}
  .endcap p {{ font-size:15px; color:var(--ink); margin-top:14px; rotate:-1.5deg; }}
  .endcap .fine {{ font-size:12px; color:var(--muted); rotate:none; margin-top:8px; }}
  footer {{ margin:40px auto 60px; max-width:760px; font-size:11.5px; color:var(--muted);
    text-align:center; font-family:inherit; line-height:2;
    padding:0 18px; }}

  .js .reveal {{ opacity:0; transform:translateY(18px); filter:blur(2.5px);
    transition:opacity .6s ease, transform .6s ease, filter .7s ease; }}
  .reveal.in {{ opacity:1; transform:none; filter:none; }}
  @media (prefers-reduced-motion:reduce) {{
    .reveal {{ opacity:1; transform:none; filter:none; transition:none; }}
    h2.sec .ic {{ stroke-dashoffset:0; transition:none; }}
    .cue {{ animation:none; }}
    html {{ scroll-behavior:auto; }}
  }}

  @media (max-width:1023px) {{
    .day-bg {{ display:block; position:relative; inset:auto; width:100%;
      max-width:none; max-height:190px; object-fit:cover; opacity:.5; rotate:none;
      margin:0 0 -22px; -webkit-mask-image:linear-gradient(180deg,#000 52%,transparent);
      mask-image:linear-gradient(180deg,#000 52%,transparent); }}
  }}
  @media (max-width:1199px) {{
    .day-body {{ grid-template-columns:minmax(0,1fr); }}
    .margin-rail {{ flex-direction:row; flex-wrap:wrap; margin-top:16px; }}
    .note-card {{ flex:1 1 240px; rotate:0deg !important; }}
  }}
  @media (max-width:760px) {{
    .cover-txt {{ padding-top:16vh; }}
    .subtitle::before, .subtitle::after {{ display:none; }}
    .subtitle {{ letter-spacing:.14em; }}
    .plate {{ flex-direction:column; text-align:center; gap:16px; padding:28px 18px; }}
    .label {{ max-width:none; }}
    .ghost {{ font-size:100px; right:4px; }}
    .tl-row {{ flex-direction:row; gap:10px; padding:10px 4px; }}
    .tl-t {{ flex:0 0 58px; font-size:11px; padding-top:3px; }}
    .tl-what {{ padding-right:0; }}
    .tl-what::after {{ display:none; }}
    .brief-grid {{ grid-template-columns:1fr; }}
  }}

  @media print {{
    .progress, .cue, .chips, .day-bg, .hoplinks, .xbtn, .xrow {{ display:none; }}
    h2.sec .ic {{ stroke-dashoffset:0; }}
    .reveal {{ filter:none; }}
    .cover {{ min-height:auto; }}
    .cover-art {{ position:static; height:200px; width:100%; }}
    .cover::after, .cover::before {{ display:none; }}
    .menu {{ display:none; }}
    .reveal {{ opacity:1; transform:none; }}
    .day {{ break-inside:avoid-page; }}
    .plate {{ background:none !important; }}
    .chip-filled {{ color:var(--ink); background:none; border:1px solid var(--terracotta); }}
    .reveal {{ opacity:1; transform:none; filter:none; }}
  }}
</style>
</head>
<body>
<div class="progress" aria-hidden="true"></div>

<div class="folio">
<header class="cover" id="top">{cover_html}
  <div class="cover-txt">
    <span class="eyebrow">{eyebrow}</span>
    <h1>{esc(cover_zh)}</h1>{cover_lines}
  </div>
  <nav class="menu" aria-label="{esc(t("menu_aria"))}">{render_menu(days)}</nav>
  <a class="cue no-export" href="#d1" aria-label="{esc(t("cue_aria"))}"><svg width="18" height="10" viewBox="0 0 22 12" fill="none"><path d="M2 2 L11 10 L20 2" stroke="#c46f4f" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></path></svg></a>
</header>

<nav class="chips no-export" id="chipbar">{render_chips(days)}</nav>

<main>
{days_html}
{endcap_html}
  <div class="backmatter" id="backmatter">
  <div class="xrow narrow no-export">
    <button class="xbtn" data-x-for="#backmatter" data-x-label="{esc(T("label.appendix"))}"
      title="{esc(t("tip_appendix"))}">{esc(br(T("btn.save_appendix")))}</button>
  </div>
  <div class="appendix">
    <h2 class="sec reveal" id="legs">{ic("plane", "draw")} {esc(t("sec_legs"))}</h2>
    {render_legs(p.get("legs", []))}
    <h2 class="sec reveal" id="hotels">{ic("hotel", "draw")} {esc(T("sec.hotels"))}</h2>
    {render_hotels(p.get("hotels", []))}
  </div>
  <div class="appendix wide">
    <h2 class="sec reveal" id="budget">{ic("wallet", "draw")} {esc(T("sec.budget"))}</h2>
    {render_budget(p.get("budget", []))}
  </div>
  <div class="appendix">
    <h2 class="sec reveal" id="checklist">{ic("checklist", "draw")} {esc(t("sec_checklist"))}</h2>
    {render_checklist(p.get("checklist", []))}
  </div>
  <div class="appendix wide">
    <h2 class="sec reveal">{ic("book", "draw")} {esc(T("sec.brief"))}</h2>
    <div class="brief-grid">{render_brief(p.get("brief", {}))}</div>
  </div>
  <div class="appendix">
    <h2 class="sec reveal">{ic("brain", "draw")} {esc(T("sec.decisions"))}</h2>
    <ol>{decisions}</ol>
    <h2 class="sec reveal">{ic("alert", "draw")} {esc(T("sec.unverified"))}</h2>
    <ul class="warn">{unverified}</ul>
  </div>
  </div>

  <footer>
    {esc(meta.get("party",""))} · {esc(t("fx"))} {esc(meta.get("fx",""))}<br>
    {esc(t("footer"))}
  </footer>
</main>
</div>

<script>
(function () {{
  document.documentElement.classList.add('js');
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (!CSS.supports('animation-timeline: scroll()')) {{
    var bar = document.querySelector('.progress');
    addEventListener('scroll', function () {{
      var h = document.documentElement.scrollHeight - innerHeight;
      bar.style.transform = 'scaleX(' + (h > 0 ? scrollY / h : 0) + ')';
    }}, {{ passive: true }});
  }}

  var links = [].slice.call(document.querySelectorAll('.chips a[data-spy]'));
  var spy = new IntersectionObserver(function (es) {{
    es.forEach(function (e) {{
      if (!e.isIntersecting) return;
      links.forEach(function (l) {{
        l.classList.toggle('active', l.getAttribute('data-spy') === e.target.id);
      }});
      var act = document.querySelector('.chips a.active');
      var bar = document.getElementById('chipbar');
      if (act && bar) bar.scrollTo({{ left: act.offsetLeft - bar.clientWidth / 2 + act.offsetWidth / 2, behavior: reduce ? 'auto' : 'smooth' }});
    }});
  }}, {{ rootMargin: '-35% 0px -55% 0px' }});
  links.forEach(function (l) {{
    var t = document.getElementById(l.getAttribute('data-spy'));
    if (t) spy.observe(t);
  }});

  document.querySelectorAll('details.hoplinks').forEach(function (d) {{
    d.addEventListener('toggle', function () {{
      if (!d.open) return;
      var box = d.querySelector('.map-embed');
      if (!box || box.dataset.done) return;
      box.dataset.done = '1';
      var f = document.createElement('iframe');
      f.loading = 'lazy'; f.referrerPolicy = 'no-referrer-when-downgrade';
      f.src = box.dataset.src;
      f.addEventListener('load', function () {{
        var ph = box.querySelector('.map-ph'); if (ph) ph.remove();
      }});
      box.appendChild(f);
    }});
  }});

  if (reduce) {{
    document.querySelectorAll('.reveal').forEach(function (n) {{ n.classList.add('in'); }});
  }} else {{
    var rev = new IntersectionObserver(function (es) {{
      es.forEach(function (e) {{
        if (e.isIntersecting) {{ e.target.classList.add('in'); rev.unobserve(e.target); }}
      }});
    }}, {{ rootMargin: '0px 0px -8% 0px' }});
    document.querySelectorAll('.reveal').forEach(function (n) {{ rev.observe(n); }});
  }}
}})();
</script>
<script>
EXPORT_JS_PLACEHOLDER
</script>
</body>
</html>"""
    # PNG export engine. extra_css neutralises every scroll-driven state inside
    # the capture clone: .reveal opacity/translate/blur, the h2.sec icon
    # stroke-draw (ungated on .js — icons below the fold would export blank),
    # the fixed progress bar, and the viewport-height cover (100svh resolves
    # against the SVG image height — a 16k-tall page would balloon the cover).
    # measure_clone: this theme's share buttons (.xrow), the hop-link
    # <details> and the chip bar are in-flow .no-export elements — ~1100px of
    # them on a 10-day trip — and the cover is pinned to 940px above while the
    # live one is 100svh; sizing the canvas from the live scrollHeight left all
    # of that as blank paper at the foot of the long image (Turkey test,
    # 2026-08-16: ~2600px in a 2600px-tall probe window). The clone is measured
    # instead, so the export ends where the endcap does.
    html_out = html_out.replace("EXPORT_JS_PLACEHOLDER", export_js(
        theme_name(THEME), "#f6efe3",
        extra_css=(".reveal,.js .reveal,.reveal.in{opacity:1!important;"
                   "transform:none!important;filter:none!important}"
                   "h2.sec .ic{stroke-dashoffset:0!important}"
                   ".progress{display:none!important}"
                   ".cover{min-height:940px!important}"),
        page_root=".folio", file_prefix=export_prefix(ART, meta, THEME),
        measure_clone=True))
    out = pathlib.Path(args.out)
    out.write_text(html_out, encoding="utf-8")
    print(f"{out.name}: {out.stat().st_size//1024}KB, days={len(days)}, "
          f"assets={asset_count()}")


if __name__ == "__main__":
    main()
