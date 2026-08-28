#!/usr/bin/env python3
"""Glass renderer v2 — Apple Liquid Glass over one photographic world.

Paradigm: a FIXED full-viewport photo backdrop that cross-fades between
zones as you scroll; content floats above it on LIQUID GLASS surfaces
(WWDC-2025 material, not 2020 frosted cards):
  * low blur + high saturate (blur 3-14px, saturate 180%) — the backdrop
    stays legible through the material instead of being scattered away;
  * specular rim — directional inset-highlight stack, strong on top;
  * edge LENSING — an SVG feImage displacement map bends the backdrop in a
    ~16px rim band only (center stays neutral); Chromium-only, gated by a
    JS-set `lens` class, others keep the blur+saturate base;
  * ::after sheen sweep, buoyancy on press (scale + glow), concentric
    corner radii (inner = outer − padding), glass floats above content and
    never stacks on other glass.

ART CONTRACT (art.json, see ART-SCHEMA.md) — everything ABOUT the trip comes
from here; the renderer carries no place, date, poem or picture name:

  cover.zh          the hero-card display title (h1). Missing → the theme's
                    own word 玻璃.
  cover.en          English line under it. Missing → the line is not emitted.
  cover.sub         subtitle / route line — rendered as one small glass strip
                    under the h1 (+ en); "\n" breaks a line inside the strip.
                    Missing → the strip is not emitted. (Read since 2026-08-15;
                    before that the field was silently dropped by this theme.)
  cover.credit      allusion / source line. Missing → not emitted.
  brief_titles      (art common) {brief key: display title} overlay on
                    theme_common.BRIEF_TITLES — the 行前须知 pill labels
                    ("visa" → 签证 · EVUS). Unknown keys print as they are.
  cover.kick        short trip word: with the year it opens <title>
                    ("美国行 2026 · 玻璃版") and the export filename prefix
                    (export_prefix); on an en page cover.kick_en wins when set
                    (theme_common.title_kick). Missing → <title> = "<year> ·
                    玻璃版", filenames "<year>-".
  days[date].theme  the 4-character day title (art.day_theme) shown as the day
                    h2 and in the rail. Missing → the day's `city` from the plan.
  themes.glass.plates     asset stems of the fixed backdrop world, one per zone,
                    in scroll order; [0] is the hero (cover) backdrop, the LAST
                    one also sits behind the appendix. Missing/empty → no
                    backdrop layers at all: the page rests on the theme's flat
                    #eef2f4 + scrim, and the footer drops the AI-scenery credit.
                    A plate whose file is absent contributes no layer (its zone
                    still exists; the cross-fade simply keeps the previous one).
  themes.glass.zones      optional zone ids parallel to `plates` (the data-zone
                    slugs the cross-fade JS keys on — purely internal, never
                    displayed). Missing/short → "hero", "z1", "z2", … .
  themes.glass.day_plate  {"<date>" | "<day number>": plate index} — which zone
                    a day scrolls in. Keys may be ISO dates ("2026-10-03",
                    matches days[].date, survives inserting a day) or 1-based
                    day numbers ("3"); mixed is fine, a date key wins. Missing
                    key → plate 1 (or 0 when there is ≤1 plate). Count mismatch
                    / stray keys → one stderr warning each, page still renders.
  (themes.glass.cover.* overrides cover.* per Art.cover.)

  ASSET SIZE VARIANTS this theme resolves (theme_common.data_uri): `plates`
  are read with NO size argument — the lookup order is <stem>.md.webp →
  <stem>.cut.webp → <stem>.webp — so ship one 16:9 backdrop per plate as
  <stem>.webp (a stray <stem>.md.webp of the same stem would win). Nothing
  else in this theme is a picture.

  TEXT LIMITS (measured 2026-08-15 in headless Chrome, 1200px viewport: h1
  62px/.16em tracked, hero-card max 620px = 500px of text; 390px viewport:
  h1 40px, 298px of text). One line holds at most:
    h1       10 Latin caps ("MOON OF QIN" = 11 → wraps) · 6 CJK    (1200px)
              9 Latin caps · 5 CJK                                  (390px)
    en       45 Latin (11.5px caps, .36em)
    sub      66 Latin / 32 CJK per line inside the strip (13px; wraps, or
             break it yourself with "\n" — keep to 2 lines)
    credit   85 Latin / 39 CJK per line (12.5px; wraps freely)
  Anything longer wraps (never overflows) — the h1 just stops being one
  line, which on this cover reads as a defect.

Kit (the theme's own, nothing to pick in art): the liquid-glass material and
lensing filter, the cross-fading fixed backdrop stage, the glass rail/dock, the
hairline ledger, the export chips and the export-only solid-glass CSS.

Usage: python3 render_glass2.py <plan.geo.json> [--art <art.json>|none]
                                 [--assets DIR ...] -o <out.html>
Assets (the backdrop webps) are searched in the plan's directory, every
--assets DIR, then themes/assets/ (theme_common.data_uri).
"""
import argparse
import pathlib
import sys

from theme_common import (LUCIDE, T, add_art_arg, asset_count, brief_titles, data_uri,
                          day_embed_url, esc, export_js, export_prefix, init_lang, lang,
                          load_art, load_plan, short_dates, theme_name, title_head,
                          title_kick)

HERE = pathlib.Path(__file__).parent
THEME = "glass"

# The theme's own voice, per language. Shared UI words (buttons, section
# names, tags) come from theme_common.T(); only what is glass's alone lives
# here. zh values are the byte-frozen originals.
L = {
    "zh": {
        "cover_word": "玻璃", "start": "开始行程",
        "nav_in_maps": "在地图中导航:", "late": "晚点", "note": "注",
        "route_map": "路线地图", "map_ph": "地图需联网加载",
        "save_day_tip": "把这一天存成玻璃卡片图,可发朋友圈",
        "brief_short": "须知", "checklist": "行前清单", "total": "合计",
        "save_legs": "保存航段", "save_legs_tip": "把航段票价表存成图片,可发朋友圈",
        "save_hotels": "保存住宿", "save_hotels_tip": "把住宿清单存成图片,可发朋友圈",
        "save_budget": "保存预算", "save_budget_tip": "把预算表存成图片,可发朋友圈",
        "save_checklist": "保存清单", "save_checklist_tip": "把行前清单存成图片,可发朋友圈",
        "save_brief": "保存须知", "save_brief_tip": "把行前须知存成图片,可发朋友圈",
        "scenery_credit": " · 风景图由 AI 生成,仅作示意",
        "footer": "日出日落 sunrise-sunset.org{credit} · 价格以预订渠道实时为准",
    },
    "en": {
        "cover_word": "Glass", "start": "Start the trip",
        "nav_in_maps": "Navigate in maps: ", "late": "if late", "note": "note",
        "route_map": "Route map", "map_ph": "The map needs a connection to load",
        "save_day_tip": "Save this day as a glass card image to share",
        "brief_short": "Brief", "checklist": "Checklist", "total": "Total",
        "save_legs": "Save legs", "save_legs_tip": "Save the flights & legs table as an image to share",
        "save_hotels": "Save stays", "save_hotels_tip": "Save the stays list as an image to share",
        "save_budget": "Save budget", "save_budget_tip": "Save the budget table as an image to share",
        "save_checklist": "Save checklist", "save_checklist_tip": "Save the checklist as an image to share",
        "save_brief": "Save brief", "save_brief_tip": "Save the pre-trip brief as an image to share",
        "scenery_credit": " · Scenery is AI-generated, illustrative only",
        "footer": "Sun times sunrise-sunset.org{credit} · Prices are live at booking",
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


# Icons are inlined (not <use> sprite refs) because of the PNG export path:
# the export engine snapshots a module clone into a standalone SVG document,
# where fragment references back to the page's sprite can never resolve —
# every glyph would rasterise blank. Costs ~15KB over the sprite, buys
# glyph-faithful exports.
def ic(name, cls=""):
    c = f"ic {cls}".strip()
    return (f'<svg class="{c}" viewBox="0 0 24 24" aria-hidden="true">'
            f'{LUCIDE[name]}</svg>')


def et(s):
    """esc + swap plan-data emojis for glyphs (mirrors theme_common.et)."""
    t = esc(s)
    return (t.replace("✈️", ic("plane")).replace("✈", ic("plane"))
             .replace("⚠️", ic("alert", "warn")).replace("⚠", ic("alert", "warn"))
             .replace("☀", ic("sunrise")).replace("🌇", ic("sunset")))


# export-chip glyph: a picture, not a download arrow. The chip makes an IMAGE
# you send to friends; the tray-arrow glyph promises a file in a downloads
# folder, which is the wrong mental model (and the local icon set has neither).
X_ICON = ('<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">'
          '<rect x="3" y="4.5" width="18" height="15" rx="3"/>'
          '<circle cx="8.6" cy="10" r="1.4"/>'
          '<path d="m3.6 17.6 4.2-4.2a2 2 0 0 1 2.8 0l3 3"/>'
          '<path d="m13.4 15.2 1.9-1.9a2 2 0 0 1 2.8 0l2.3 2.3"/></svg>')


def xbtn(target, label, text, title):
    """A liquid-glass capsule that saves one module as a PNG (module-only
    theme: the fixed cross-fading backdrop makes whole-page export a lie)."""
    return (f'<button class="xbtn no-export" data-x-for="{target}" '
            f'data-x-label="{label}" title="{title}">{X_ICON} {text}</button>')

def js_str(s):
    """A JS single-quoted string literal (zone ids are ours or the art's,
    but never trust them into a script unescaped)."""
    return "'" + str(s).replace("\\", "\\\\").replace("'", "\\'") + "'"


# The backdrop world — zone → photo (a fixed layer that fades in while that
# zone is on screen) and which zone each day scrolls in — comes from art.json
# (themes.glass.plates / zones / day_plate); see the ART CONTRACT above.
def zone_id(zones, idx):
    """data-zone slug for plate `idx`: art's own name when given, else the
    kit's default ("hero" for the cover plate, "z<n>" after)."""
    if idx < len(zones) and zones[idx]:
        return str(zones[idx])
    return "hero" if idx == 0 else f"z{idx}"



def tl_rows(day):
    rows = []
    for r in day.get("timeline", []):
        kind = r.get("kind", "anchor")
        est = '<sup>est</sup>' if r.get("verify") == "est" else ""
        tag = r.get("tag", "")
        chip = (f'<span class="tag{" hot" if tag == "pinned" else ""}">'
                f'{esc(T("tag." + tag, tag))}</span>' if tag else "")
        price = f' <span class="dim">{esc(r["price"])}</span>' if r.get("price") else ""
        nav = (f' <a class="rownav" href="{esc(r["link"])}" target="_blank" rel="noopener"'
               f' aria-label="{esc(t("nav_in_maps"))}{esc(r.get("what", "")[:16])}">{ic("pin")}</a>'
               if r.get("link") else "")
        rows.append(f'<div class="li k-{kind}"><span class="tchip">{esc(r.get("t",""))}{est}</span>'
                    f'<span class="w">{et(r.get("what",""))}{price}{chip}{nav}</span></div>')
    return "".join(rows)


def meta_pills(day):
    out = []
    wk = day.get("walking_km")
    if isinstance(wk, dict):
        out.append((f'{ic("walk")} ≈{wk.get("total","?")}km', wk.get("how", "")))
    elif wk:
        out.append((f'{ic("walk")} ≈{wk}km', ""))
    for key, icn, label in (("rain_alt", "rain", T("rain_alt")), ("late_cut", "clock", t("late")),
                            ("note", "note", t("note"))):
        if day.get(key):
            out.append((f'{ic(icn)} {esc(label)}', day[key]))
    return "".join(
        (f'<details class="pillfold"><summary class="pill">{head}</summary>'
         f'<p>{et(body)}</p></details>') if body else
        f'<span class="pill">{head}</span>'
        for head, body in out)


def day_block(i, day, art, zone):
    date = day.get("date", "")
    theme = art.day_theme(date, day.get("city", ""))
    sun = sun_text(day)
    embed = day_embed_url(day)
    # .no-export: in a share image the map CTA is a dead control, and an
    # opened iframe would rasterise as a blank box — strip it from captures
    embed_html = (f'<details class="mapfold no-export"><summary class="cta">{ic("compass")} {esc(t("route_map"))}</summary>'
                  f'<div class="map-embed" data-src="{esc(embed)}">'
                  f'<p class="map-ph">{esc(t("map_ph"))}</p></div></details>' if embed else "")
    return f"""
<section class="day reveal" id="d{i}" data-zone="{esc(zone)}">
  <header class="dhead">
    <span class="k">DAY {i} · {date[5:].replace("-", ".")} · {esc(day.get("city",""))}</span>
    <h2>{esc(theme)}</h2>
    <p class="lbl">{esc(day.get("label",""))}</p>
    {f'<p class="sun">{sun}</p>' if sun else ""}
    {xbtn(f"#d{i}", f"DAY{i:02d}", esc(T("btn.save_day")), esc(t("save_day_tip")))}
  </header>
  <div class="glass sheet">{tl_rows(day)}</div>
  <div class="pills">{meta_pills(day)}{embed_html}</div>
</section>"""


def appendix(p, total, az, titles):
    legs = "".join(
        f'<div class="li k-hop"><span class="tchip">{esc(l.get("date",""))[5:]}</span>'
        f'<span class="w">{esc(l.get("from",""))} → {esc(l.get("to",""))}'
        f' <span class="dim">{et(l.get("carrier",""))} {esc(l.get("dep",""))}-{esc(l.get("arr",""))}'
        f' · {esc(l.get("price",""))} · {esc(l.get("bags",""))}</span></span></div>'
        for l in p.get("legs", []))
    hotels = "".join(
        f'<div class="li"><span class="tchip">{esc(h.get("base",""))}</span>'
        f'<span class="w">{esc(h.get("area",""))} <span class="dim">{esc(h.get("why",""))}</span><br>'
        + " · ".join(
            f'<a href="{esc(o.get("link","#"))}" target="_blank" rel="noopener">{esc(o.get("name",""))}</a>'
            f' <span class="dim">{esc(o.get("band",""))}</span>'
            for o in h.get("options", [])) + "</span></div>"
        for h in p.get("hotels", []))
    budget = "".join(
        f'<div class="li"><span class="tchip">{esc(b.get("cat",""))}</span>'
        f'<span class="w">{esc(b.get("per_person",""))}'
        f' <span class="dim">{esc(b.get("note",""))}</span></span></div>'
        for b in p.get("budget", []))
    checklist = "".join(
        f'<div class="li"><span class="tchip">{i:02d}</span><span class="w"><label>'
        f'<input type="checkbox"> {et(c.get("item",""))}</label>'
        f' <span class="dim">{esc(c.get("deadline",""))} · {esc(c.get("price",""))}</span>'
        + (f' <a href="{esc(c["link"])}" target="_blank" rel="noopener">{esc(c.get("link_text", T("link")))}</a>'
           if c.get("link") else "") + "</span></div>"
        for i, c in enumerate(p.get("checklist", []), 1))
    brief = "".join(
        f'<details class="pillfold wide"><summary class="pill">{esc(titles.get(k, k))}</summary>'
        f'<p>{et(v)}</p></details>' for k, v in p.get("brief", {}).items())
    decisions = "".join(f"<li>{et(u)}</li>" for u in p.get("decisions", []))
    unverified = "".join(f"<li>{et(u)}</li>" for u in p.get("unverified", []))
    return f"""
<section class="appx reveal" id="legs" data-zone="{az}">
  <h2>{ic("plane")} {esc(T("sec.legs"))}</h2>{xbtn("#legs", esc(T("sec.legs")), esc(t("save_legs")), esc(t("save_legs_tip")))}<div class="glass sheet">{legs}</div>
</section>
<section class="appx reveal" id="hotels" data-zone="{az}">
  <h2>{ic("hotel")} {esc(T("sec.hotels"))}</h2>{xbtn("#hotels", esc(T("sec.hotels")), esc(t("save_hotels")), esc(t("save_hotels_tip")))}<div class="glass sheet">{hotels}</div>
</section>
<section class="appx reveal" id="budget" data-zone="{az}">
  <h2>{ic("wallet")} {esc(T("sec.budget"))}</h2>{xbtn("#budget", esc(T("sec.budget")), esc(t("save_budget")), esc(t("save_budget_tip")))}<div class="glass sheet">{budget}</div>
  <p class="total">{esc(t("total"))} {esc(total)}</p>
</section>
<section class="appx reveal" id="checklist" data-zone="{az}">
  <h2>{ic("checklist")} {esc(t("checklist"))}</h2>{xbtn("#checklist", esc(T("sec.checklist")), esc(t("save_checklist")), esc(t("save_checklist_tip")))}<div class="glass sheet">{checklist}</div>
</section>
<section class="appx reveal" id="brief" data-zone="{az}">
  <h2>{ic("book")} {esc(T("sec.brief"))}</h2>{xbtn("#brief", esc(t("brief_short")), esc(t("save_brief")), esc(t("save_brief_tip")))}<div class="pills">{brief}</div>
  <h2>{ic("brain")} {esc(T("sec.decisions"))}</h2><ol>{decisions}</ol>
  <h2>{ic("alert", "warn")} {esc(T("sec.unverified"))}</h2><ul class="warn">{unverified}</ul>
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

    # cover words — all the trip's, all optional
    kick = title_kick(art, THEME)
    cover_zh = art.cover(THEME, "zh", t("cover_word"))
    cover_en = art.cover(THEME, "en")
    cover_sub = art.cover(THEME, "sub")
    cover_credit = art.cover(THEME, "credit")
    page_title = " · ".join(x for x in (title_head(art, THEME, year), theme_name(THEME)) if x)
    cover_en_html = f'\n    <p class="en">{esc(cover_en)}</p>' if cover_en else ""
    # the subtitle is its own small strip of glass under the title — the
    # only text on the cover that gets a surface of its own; "\n" = a line
    # break inside the strip
    cover_sub_html = ('\n    <p class="sub">'
                      + "<br>".join(esc(x) for x in str(cover_sub).split("\n"))
                      + '</p>') if cover_sub else ""
    cover_credit_html = (f'\n    <p class="credit">{esc(cover_credit)}</p>'
                         if cover_credit else "")

    # the backdrop world: plates in scroll order + day → plate map, from art
    tb = art.theme(THEME)
    plates = [s for s in (tb.get("plates") or []) if s]
    zones = list(tb.get("zones") or [])
    day_plate = {str(k): v for k, v in (tb.get("day_plate") or {}).items()}
    default_plate = 1 if len(plates) > 1 else 0
    if day_plate:
        mapped = sum(1 for n, d in enumerate(days)
                     if d.get("date", "") in day_plate or str(n + 1) in day_plate)
        if mapped != len(days):
            print(f"warning: themes.glass.day_plate covers {mapped} of {len(days)} "
                  f"days — unmapped days fall back to plate {default_plate}",
                  file=sys.stderr)
        known = ({d.get("date", "") for d in days}
                 | {str(n + 1) for n in range(len(days))})
        stray = sorted(k for k in day_plate if k not in known)
        if stray:
            print(f"warning: themes.glass.day_plate keys match no day "
                  f"(not a date in the plan, not 1..{len(days)}): {stray}",
                  file=sys.stderr)

    def plate_of(i, d):
        idx = day_plate.get(d.get("date", ""), day_plate.get(str(i), default_plate))
        try:
            idx = int(idx)
        except (TypeError, ValueError):
            idx = default_plate
        return idx if 0 <= idx < max(len(plates), 1) else default_plate

    backdrops = "".join(
        f'<div class="bd" data-zone="{esc(zone_id(zones, n))}" '
        f'style="background-image:url({data_uri(photo)})"></div>'
        for n, photo in enumerate(plates) if data_uri(photo))
    hero_zone = zone_id(zones, 0)
    appx_zone = zone_id(zones, len(plates) - 1 if plates else 0)
    scenery_credit = t("scenery_credit") if backdrops else ""
    footer = esc(t("footer").replace("{credit}", scenery_credit))
    blocks = "".join(day_block(i + 1, d, art, zone_id(zones, plate_of(i + 1, d)))
                     for i, d in enumerate(days))
    rail = "".join(
        f'<a href="#d{i}" data-spy="d{i}"><b>{i:02d}</b>'
        f'<span>{esc(art.day_theme(d.get("date", ""), d.get("city", "")))}</span></a>'
        for i, d in enumerate(days, 1))

    html_out = f"""<!doctype html>
<html lang="{T("html_lang")}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(page_title)}</title>
<style>
  :root {{
    --ink:#15171a; --dim:#474c52; --line:rgba(21,23,26,.10);
    --spring:cubic-bezier(0.16,1,0.3,1);
    --r:28px;               /* base glass radius; children stay concentric */
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; background:#eef2f4; }}
  body {{ color:var(--ink); overflow-x:clip;
    font-family:system-ui,-apple-system,"PingFang SC","Helvetica Neue",sans-serif; }}
  a {{ color:inherit; }}
  .dim {{ color:var(--dim); font-size:.85em; }}
  sup {{ font-size:8px; color:var(--dim); }}
  .ic {{ width:1em; height:1em; fill:none; stroke:currentColor; stroke-width:1.75;
    stroke-linecap:round; stroke-linejoin:round; vertical-align:-0.12em; }}
  .ic.warn {{ color:#c2603f; }}

  /* ---------- the world: fixed photo layers that cross-fade ---------- */
  #sky {{ position:fixed; inset:0; z-index:-2; }}
  .bd {{ position:absolute; inset:0; background-size:cover; background-position:center;
    opacity:0; transition:opacity 1.1s var(--spring); }}
  .bd.on {{ opacity:1; }}
  /* much lighter than before: the material does its own legibility work now,
     the photo is allowed to actually be there */
  #scrim {{ position:fixed; inset:0; z-index:-1; pointer-events:none;
    background:linear-gradient(180deg, rgba(255,255,255,.30) 0%, rgba(255,255,255,.42) 30%,
      rgba(255,255,255,.54) 100%); }}

  /* ---------- Liquid Glass primitive ----------
     lensing (Chromium, .lens) > frost base; NEVER heavy blur — that is the
     old glassmorphism tell. Rim = directional inset speculars, top strong. */
  .glass {{ position:relative; isolation:isolate; border-radius:var(--r);
    background:rgba(255,255,255,.36);
    border:1px solid rgba(255,255,255,.45);
    backdrop-filter:blur(10px) saturate(1.8) brightness(1.06);
    -webkit-backdrop-filter:blur(10px) saturate(1.8) brightness(1.06);
    box-shadow:0 14px 38px -16px rgba(21,23,26,.38),
      inset 0 1px 1px rgba(255,255,255,.75),
      inset 0 -1px 1px rgba(255,255,255,.34),
      inset 1px 0 1px rgba(255,255,255,.22),
      inset -1px 0 1px rgba(255,255,255,.22); }}
  .lens .glass {{ backdrop-filter:url(#lens) blur(3px) saturate(1.8) brightness(1.06); }}
  /* sheen sweep — light casting across the surface, never touching content */
  .glass::after {{ content:""; position:absolute; inset:0; border-radius:inherit;
    pointer-events:none; z-index:1; mix-blend-mode:screen;
    background:linear-gradient(135deg, rgba(255,255,255,.28) 0%,
      rgba(255,255,255,.05) 24%, transparent 50%); }}
  .glass > * {{ position:relative; z-index:2; }}

  /* ---------- hero ---------- */
  .hero {{ min-height:100svh; display:flex; align-items:center; justify-content:center;
    padding:0 20px; }}
  .hero-card {{ --r:44px; text-align:center; padding:46px clamp(26px,5vw,60px);
    max-width:620px; }}
  .hero-card .k {{ font-size:11px; letter-spacing:.44em; color:var(--dim);
    font-family:ui-monospace,Menlo,monospace; }}
  .hero-card h1 {{ font-size:clamp(40px,6vw,62px); font-weight:650; letter-spacing:.16em;
    margin:14px 0 6px; }}
  .hero-card .en {{ font-size:11.5px; letter-spacing:.36em; color:var(--dim);
    text-transform:uppercase; }}
  /* the subtitle strip: a small lit slab of the same material inside the
     hero card — its own fill + specular top edge (no backdrop-filter: nested
     filters have nothing to sample through the card) */
  .hero-card .sub {{ display:inline-block; margin-top:16px; padding:8px 20px;
    border-radius:999px; font-size:13px; line-height:1.7; letter-spacing:.06em;
    color:#2f343a; background:rgba(255,255,255,.46);
    border:1px solid rgba(255,255,255,.62);
    box-shadow:inset 0 1px 1px rgba(255,255,255,.9), 0 4px 12px -6px rgba(21,23,26,.28); }}
  .hero-card .credit {{ margin-top:14px; font-size:12.5px; color:var(--dim); }}
  .cta {{ display:inline-flex; align-items:center; gap:8px; background:#111; color:#fafafa;
    border-radius:999px; padding:11px 24px; font-size:12.5px; cursor:pointer;
    list-style:none; letter-spacing:.08em; margin-top:20px; text-decoration:none;
    box-shadow:inset 0 1px 1px rgba(255,255,255,.28), 0 6px 18px -8px rgba(0,0,0,.5);
    transition:transform .25s var(--spring), background .2s ease,
      box-shadow .25s var(--spring); }}
  .cta:hover {{ transform:translateY(-2px) scale(1.03); background:#2b2b2b;
    box-shadow:inset 0 1px 1px rgba(255,255,255,.28), 0 12px 26px -8px rgba(0,0,0,.5); }}
  .cta:active {{ transform:scale(.96); }}
  .cta .ic {{ color:#fafafa; }}

  /* ---------- layout: borderless rail + floating content ---------- */
  .shell {{ display:grid; grid-template-columns:210px minmax(0,1fr); gap:30px;
    max-width:1180px; margin:0 auto; padding:0 22px 70px; }}
  /* the rail is ONE floating glass capsule (the canonical liquid-glass nav
     layer) — the active row is a brighter concentric capsule inside it */
  .rail {{ --r:32px; position:sticky; top:16px; align-self:start;
    max-height:calc(100svh - 32px); overflow-y:auto;
    padding:12px 8px; scrollbar-width:none; }}
  .rail::-webkit-scrollbar {{ display:none; }}
  .rail a {{ display:flex; gap:9px; align-items:baseline; padding:7px 12px; margin-bottom:2px;
    border-radius:24px;   /* concentric: 32 outer − 8 gutter */
    text-decoration:none; color:#33383f; font-size:13px;
    transition:background .25s ease, color .25s ease, transform .25s var(--spring); }}
  .rail a:hover {{ transform:scale(1.04); }}
  .rail a:active {{ transform:scale(.96); }}
  .rail a b {{ font-size:10.5px; font-family:ui-monospace,Menlo,monospace; }}
  .rail a.active {{ background:rgba(255,255,255,.82); color:var(--ink); font-weight:600;
    box-shadow:inset 0 1px 1px rgba(255,255,255,.9), 0 3px 10px -4px rgba(21,23,26,.35); }}
  .rail .foot {{ margin-top:16px; padding:0 12px; font-size:10.5px; color:var(--dim);
    line-height:2; }}
  .rail .foot a {{ display:inline; padding:0; margin-right:8px; text-decoration:underline; }}

  main {{ min-width:0; padding-top:26px; }}
  .day {{ margin-bottom:76px; position:relative; }}
  /* the chip lives in the header's own second column instead of floating on
     top of it: two grid tracks can never intersect, so no scroll state and no
     long city name can ever put it over the type (measured, see xbtn below) */
  .dhead {{ padding:18px 22px 16px; margin-left:-16px;
    display:grid; grid-template-columns:minmax(0,1fr) auto; column-gap:18px;
    background:radial-gradient(126% 150% at 6% 0%, rgba(255,255,255,.94) 0%,
      rgba(255,255,255,.72) 46%, rgba(255,255,255,0) 100%); }}
  .dhead > * {{ grid-column:1; }}
  .dhead > .xbtn {{ grid-column:2; grid-row:1 / span 2; align-self:start;
    justify-self:end; }}
  .dhead .k {{ font-size:10.5px; letter-spacing:.26em; color:#2f343a;
    font-family:ui-monospace,Menlo,monospace; }}
  .dhead h2 {{ font-size:clamp(30px,4vw,44px); font-weight:650; letter-spacing:.1em;
    margin:8px 0 4px; }}
  .lbl {{ font-size:13.5px; color:#2f343a; max-width:34em; }}
  .sun {{ font-size:11.5px; color:#2f343a; margin-top:5px; }}

  /* a real pane now: the day's ledger floats on one liquid-glass panel */
  .sheet {{ padding:16px 26px; }}
  .li {{ display:flex; gap:14px; padding:12px 0; border-bottom:1px solid var(--line);
    font-size:14px; line-height:1.75; }}
  .li:last-child {{ border-bottom:none; }}
  /* no capsule: the time is ranged right against a hairline, like a spec sheet */
  .tchip {{ flex:0 0 96px; align-self:flex-start; text-align:right; font-size:11.5px;
    font-family:ui-monospace,Menlo,monospace; background:none; padding:2px 12px 2px 0;
    margin-top:2px; white-space:nowrap; border-right:1px solid rgba(21,23,26,.16);
    color:#3a3f45; }}
  .k-anchor .tchip {{ color:#111; font-weight:700; border-right-color:#111;
    border-right-width:2px; }}
  .k-meal .tchip {{ color:#7a6432; }}
  .k-hop .w, .k-free .w {{ color:var(--dim); font-size:13px; }}
  .w {{ min-width:0; overflow-wrap:anywhere; }}
  .tag {{ font-size:10px; border:1px solid rgba(21,23,26,.35); border-radius:999px;
    padding:1px 8px; margin-left:6px; white-space:nowrap; }}
  .tag.hot {{ background:#111; color:#fafafa; border-color:#111; }}
  .rownav {{ display:inline-flex; align-items:center; justify-content:center;
    min-width:44px; min-height:44px; margin:-12px 0 -12px 5px; vertical-align:middle; }}
  /* focus is another pane of glass, not a generic ring */
  :focus-visible {{ outline:2px solid rgba(255,255,255,.95); outline-offset:2px;
    box-shadow:0 0 0 4px rgba(21,23,26,.55); border-radius:3px; }}
  .rail a:focus-visible, .cta:focus-visible, summary:focus-visible {{ outline-offset:2px; }}

  .pills {{ display:flex; flex-wrap:wrap; gap:9px; margin-top:14px; padding:0 6px; }}
  .pill {{ display:inline-flex; align-items:center; gap:6px; font-size:12px;
    border-radius:999px; padding:7px 15px; list-style:none;
    background:rgba(255,255,255,.42); border:1px solid rgba(255,255,255,.5);
    backdrop-filter:blur(8px) saturate(1.8); -webkit-backdrop-filter:blur(8px) saturate(1.8);
    box-shadow:inset 0 1px 1px rgba(255,255,255,.7), 0 4px 12px -6px rgba(21,23,26,.3);
    transition:transform .25s var(--spring), background .2s ease; }}
  .pill:hover {{ transform:scale(1.05); background:rgba(255,255,255,.56); }}
  summary.pill:active {{ transform:scale(.95); }}
  .pillfold summary {{ cursor:pointer; }}
  .pillfold summary::-webkit-details-marker {{ display:none; }}
  .pillfold p {{ font-size:12.5px; color:var(--dim); line-height:1.85; padding:10px 8px 2px;
    max-width:56em; }}
  .pillfold.wide {{ flex-basis:100%; }}
  .mapfold {{ flex-basis:100%; }}
  .mapfold summary::-webkit-details-marker {{ display:none; }}
  .map-embed {{ margin-top:12px; border-radius:24px; overflow:hidden;
    border:1px solid rgba(255,255,255,.65);
    box-shadow:inset 0 1px 1px rgba(255,255,255,.6), 0 10px 28px -14px rgba(21,23,26,.4); }}
  .map-embed iframe {{ display:block; width:100%; height:330px; border:0; }}
  .map-ph {{ padding:18px; font-size:12px; color:var(--dim); text-align:center;
    background:rgba(255,255,255,.6); }}

  .appx {{ margin-bottom:54px; position:relative; }}
  /* max-content, not the default full-width block: the appendix chip sits at
     the same right edge, and a heading box that stretched across the section
     would sit under it even though the words never get near it */
  .appx h2 {{ font-size:15px; letter-spacing:.2em; padding:0 6px 12px; margin-top:26px;
    display:flex; gap:8px; align-items:center; width:max-content; max-width:100%; }}
  .appx h2:first-child {{ margin-top:0; }}
  .appx ol, .appx ul {{ margin:4px 0 0 30px; font-size:13.5px; line-height:1.95;
    color:var(--dim); }}
  .appx ul.warn li {{ color:#9a5637; }}
  .total {{ display:inline-block; margin:14px 6px 0; background:#111; color:#fafafa;
    border-radius:999px; padding:11px 22px; font-size:13.5px; font-weight:600; }}
  input[type=checkbox] {{ accent-color:#111; margin-right:5px; }}

  footer {{ text-align:center; font-size:11px; color:var(--dim); padding:20px 22px 50px;
    line-height:2; }}

  /* export chips: one small pane of the same liquid glass the app is made of.
     It used to sit at opacity .45 and disappear into the photograph; the fix
     is material, not size — the type stays 11.5px and gets read because the
     capsule is now a properly lit piece of glass: brighter fill than the
     sheets, a full specular top edge, and a cast shadow that lifts it off the
     backdrop. Still one notch quieter than .cta (the black pill) so it reads
     as a tool on the surface, not the page's call to action. */
  .xbtn {{ position:relative; z-index:5;
    display:inline-flex; align-items:center; gap:6px; min-height:34px;
    font:500 11.5px/1 system-ui,-apple-system,"PingFang SC","Helvetica Neue",sans-serif;
    letter-spacing:.08em; color:#15171a; cursor:pointer;
    border:1px solid rgba(255,255,255,.9); border-radius:999px; padding:0 15px;
    background:linear-gradient(176deg, rgba(255,255,255,.9), rgba(255,255,255,.6));
    backdrop-filter:blur(10px) saturate(1.9); -webkit-backdrop-filter:blur(10px) saturate(1.9);
    box-shadow:inset 0 1px 0 rgba(255,255,255,.98), inset 0 -1px 1px rgba(255,255,255,.5),
      0 6px 16px -8px rgba(21,23,26,.55), 0 1px 2px rgba(21,23,26,.12);
    transition:transform .25s var(--spring), background .2s ease,
      box-shadow .25s var(--spring); }}
  .xbtn .ic {{ width:13px; height:13px; color:#3d434a; }}
  .xbtn:hover, .xbtn:focus-visible {{ transform:scale(1.05);
    background:linear-gradient(176deg, #fff, rgba(255,255,255,.78));
    box-shadow:inset 0 1px 0 #fff, inset 0 -1px 1px rgba(255,255,255,.6),
      0 10px 24px -10px rgba(21,23,26,.6), 0 0 0 3px rgba(255,255,255,.34); }}
  .xbtn:active {{ transform:scale(.95); }}
  /* appendix sections have no header grid to donate a column, so the chip
     floats — pinned to the section's right edge, clear of the max-content
     heading box on its left */
  .appx .xbtn {{ position:absolute; right:0; top:-6px; }}

  .js .reveal {{ opacity:0; transform:translateY(28px);
    transition:opacity .8s var(--spring), transform .8s var(--spring); }}
  .reveal.in {{ opacity:1; transform:none; }}
  section[id] {{ scroll-margin-top:20px; }}
  @media (prefers-reduced-motion:reduce) {{
    .reveal {{ opacity:1; transform:none; transition:none; }}
    .bd, .pill, .cta, .rail a {{ transition:none; }}
    html {{ scroll-behavior:auto; }}
  }}

  @media (max-width:900px) {{
    .shell {{ grid-template-columns:1fr; gap:0; padding:0 14px 60px; }}
    /* the rail becomes a floating glass dock — one capsule, no glass-on-glass */
    .rail {{ position:fixed; left:10px; right:10px; bottom:10px; top:auto; z-index:40;
      max-height:none; display:flex; gap:4px; overflow-x:auto; overflow-y:hidden;
      --r:999px; padding:8px 10px;
      margin-bottom:env(safe-area-inset-bottom); }}
    .rail a {{ flex:0 0 auto; padding:7px 13px; margin:0; min-height:36px;
      align-items:center; }}
    .rail a span {{ display:none; }}
    .rail a b {{ font-size:12px; }}
    .rail .foot {{ display:flex; flex:0 0 auto; align-items:center; gap:4px;
      margin:0; padding:0; font-size:0; }}
    .rail .foot br {{ display:none; }}
    .rail .foot a {{ font-size:12px; min-height:36px; display:inline-flex;
      align-items:center; padding:0 13px; margin:0; text-decoration:none; }}
    main {{ padding-top:8px; }}
    /* the chip is a grid track now, not a floater — no reserved gutter needed;
       it just takes its own column and the title wraps in the one that's left */
    .dhead {{ column-gap:12px; }}
    .sheet {{ padding:10px 16px; border-radius:24px; }}
    .li {{ flex-direction:column; gap:4px; }}
    .tchip {{ align-self:flex-start; flex:0 0 auto; }}
    .day {{ margin-bottom:56px; }}
  }}
  @media print {{
    #sky, #scrim, .rail, .mapfold, .xbtn {{ display:none; }}
    .shell {{ grid-template-columns:1fr; }}
    .glass {{ background:#fff; border:none; box-shadow:none; backdrop-filter:none; }}
    .glass::after {{ display:none; }}
    .tchip, .k-anchor .tchip, .k-meal .tchip, .tag.hot, .total, .cta {{
      background:transparent !important; color:#111 !important;
      border:1px solid #111 !important; }}
    .reveal {{ opacity:1; transform:none; }}
    .day {{ break-inside:avoid-page; }}
  }}
</style>
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <filter id="lens" color-interpolation-filters="sRGB" x="0" y="0" width="100%" height="100%">
    <feImage href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='200'><defs><linearGradient id='gx' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='%23000000'/><stop offset='1' stop-color='%23ff0000'/></linearGradient><linearGradient id='gy' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='%23000000'/><stop offset='1' stop-color='%2300ff00'/></linearGradient><filter id='b'><feGaussianBlur stdDeviation='7'/></filter></defs><rect width='300' height='200' fill='url(%23gx)'/><rect width='300' height='200' fill='url(%23gy)' style='mix-blend-mode:screen'/><rect x='16' y='16' width='268' height='168' rx='26' fill='rgb(128,128,0)' filter='url(%23b)'/></svg>" x="0%" y="0%" width="100%" height="100%" preserveAspectRatio="none" result="map"/>
    <feDisplacementMap in="SourceGraphic" in2="map" scale="44" xChannelSelector="R" yChannelSelector="G"/>
  </filter>
</svg>
<div id="sky">{backdrops}</div>
<div id="scrim"></div>

<header class="hero" id="top" data-zone="{esc(hero_zone)}">
  <div class="glass hero-card">
    <span class="k">{esc(dates)}</span>
    <h1>{esc(cover_zh)}</h1>{cover_en_html}{cover_sub_html}{cover_credit_html}
    <a class="cta" href="#d1">{ic("arrow")} {esc(t("start"))}</a>
  </div>
</header>

<div class="shell">
  <nav class="glass rail" id="rail">
    {rail}
    <p class="foot">
      <a href="#legs">{esc(T("sec.legs"))}</a><a href="#hotels">{esc(T("sec.hotels"))}</a><a href="#budget">{esc(T("sec.budget"))}</a>
      <a href="#checklist">{esc(T("sec.checklist"))}</a><a href="#brief">{esc(t("brief_short"))}</a><br>
      {esc(dates)} · {esc(meta.get("party",""))}
    </p>
  </nav>
  <main>
    {blocks}
    {appendix(p, meta.get("budget_total", ""), appx_zone, brief_titles(art))}
    <footer>{footer}</footer>
  </main>
</div>

<script>
(function () {{
  document.documentElement.classList.add('js');
  // edge-lensing displacement is a Chromium-only backdrop-filter capability;
  // everyone else keeps the blur+saturate base material
  if (window.chrome) document.documentElement.classList.add('lens');
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- backdrop cross-fade: whichever zone owns the middle of the screen wins ---- */
  var layers = {{}};
  document.querySelectorAll('.bd').forEach(function (b) {{ layers[b.dataset.zone] = b; }});
  var current = null;
  function setZone(z) {{
    if (!z || z === current || !layers[z]) return;
    // fade the INCOMING layer in on top and leave the outgoing one beneath it,
    // so total alpha never dips and the page can't flash its base colour
    Object.keys(layers).forEach(function (k) {{ layers[k].style.zIndex = '0'; }});
    layers[z].style.zIndex = '1';
    layers[z].classList.add('on');
    var prev = current;
    current = z;
    setTimeout(function () {{
      if (current === z && prev && layers[prev]) layers[prev].classList.remove('on');
    }}, 1200);
  }}
  setZone({js_str(hero_zone)});
  var zoneSpy = new IntersectionObserver(function (es) {{
    es.forEach(function (e) {{ if (e.isIntersecting) setZone(e.target.dataset.zone); }});
  }}, {{ rootMargin: '-45% 0px -45% 0px' }});
  document.querySelectorAll('[data-zone]').forEach(function (n) {{ zoneSpy.observe(n); }});

  /* ---- rail scrollspy ---- */
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
  }}, {{ rootMargin: '-35% 0px -55% 0px' }});
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

  /* ---- lazy maps ---- */
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
    # PNG export engine, module-only (page_root=""): the paradigm is a FIXED
    # backdrop world cross-fading behind sticky-free content — a whole-page
    # capture can't carry that layer and would flatten to a 16000px lie.
    # extra_css runs only inside the capture clone:
    #   · reveal states forced visible (scroll-driven opacity would export blank)
    #   · backdrop-filter has no backdrop inside a foreignObject snapshot —
    #     swap glass for a same-family translucent solid so text stays readable
    #   · the clone document's "viewport" is the module width (~896px), which
    #     would trip the ≤900px mobile media block: pin the desktop timeline
    #     geometry (hairline time rail is this theme's identity) explicitly
    #   · .__xbody gets a soft sky gradient so the panels float on air, not
    #     on a dead flat fill
    html_out = html_out.replace("EXPORT_JS_PLACEHOLDER", export_js(
        theme_name(THEME), "#eef2f4",
        extra_css=(
            ".reveal,.js .reveal{opacity:1!important;transform:none!important}"
            ".glass{background:rgba(255,255,255,.86)!important;"
            "backdrop-filter:none!important;-webkit-backdrop-filter:none!important}"
            ".pill{background:rgba(255,255,255,.82)!important;"
            "backdrop-filter:none!important;-webkit-backdrop-filter:none!important}"
            ".sheet{padding:16px 26px!important;border-radius:28px!important}"
            ".li{flex-direction:row!important;gap:14px!important}"
            ".tchip{flex:0 0 96px!important}"
            ".dhead{padding:18px 22px 16px!important;margin-left:0!important}"
            ".__xbody{background:linear-gradient(180deg,#dfe9f0,#eef2f4 62%,#e8edf0)"
            "!important}"),
        page_root="", file_prefix=export_prefix(art, meta, THEME)))
    out = pathlib.Path(args.out)
    out.write_text(html_out, encoding="utf-8")
    print(f"{out.name}: {out.stat().st_size//1024}KB, days={len(days)}, assets={asset_count()}")


if __name__ == "__main__":
    main()
