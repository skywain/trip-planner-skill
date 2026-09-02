#!/usr/bin/env python3
"""Render a trip plan JSON into one self-contained, printable, phone-friendly HTML
file. Part of the trip-planner skill; stdlib only, Python 3.9+.

  python3 render_plan.py plan.json -o trip.html [--lang zh|en]

UI language: --lang > plan["lang"] > plan["meta"]["lang"] > zh. Only the page's own
chrome (section names, table headers, pills, footer) is translated; plan content is
printed as written. Keys mirror themes/theme_common.STRINGS where a shared name exists.

The SAME plan JSON feeds route_tools.py (which reads days[].stops) — keeping one
canonical file is what stops the map links, the KML and the written plan from
drifting apart. Every field is optional: render early and often, and the sections you
have not filled in yet simply do not appear.

Schema (all keys optional except days[].date):
{
 "trip": "Japan 12 days",
 "meta": {"dates","party","route","budget_total","fx","generated","self_check"},
 "decisions": ["open-jaw into KIX out of NRT: refunds a backtracking day", ...],
 "checklist": [{"item","deadline","price","link","link_text","note"}],
 "legs":      [{"type","date","carrier","from","to","dep","arr","price","bags",
                "link","note","backup"}],
 "days": [{"date","city","label","sun","day_map","ribbon","rain_alt","late_cut",
           // HONEST total: on-foot ×1.3 + strolls + in-venue. Either a number or
           // {"total": 7.5, "how": "on foot 2.1×1.3 + in-station 0.8 + in-venue 4.0"}
           "walking_km": 5.4,
           "travel_day": true,
           "timeline": [{"t","what","kind":"anchor|hop|meal|free","price","note",
                         "tag":"pinned|opener|skippable|swap→X",
                         "verify":"verified|est","link",
                         "map": false}],   // map:false = flight/rail hop covered by
                                           // legs — excluded from links --write
           "hop_links": ["url", ...],      // parked by route_tools when rows and
                                           // mapped hops don't align; rendered as
                                           // a hop-by-hop maps row under the day card
           "stops": [{"name","query","lat","lon"}]}],   // mirrors the timeline's
                                                        // places, in visit order
 "hotels": [{"base","area","why","options":[{"name","band","link"}]}],
 "budget": [{"cat","per_person","total","note"}],
 "brief":  {"visa","emergency","safety","health","holidays","weather","money",
            "connectivity","insurance","baggage", ...},   # canonical order: output-template §Brief templates
 "unverified": ["teamLab hours could not be confirmed", ...]
}
"""
import argparse
import html
import json
import math
import sys
from pathlib import Path

# UI strings. zh values are the historical ones — do not touch them (the kyoto sample
# render must stay byte-identical); en is the same shell in English.
STRINGS = {
    "zh": {
        "html_lang": "zh",
        "link": "地图/链接", "verify.est": "est.", "verify.verified": "verified",
        "map.cap": "示意图 · 约 {km:.1f} km 跨度 · 真实导航见上方链接",
        "sec.decisions": "为你做的决定 / Decisions made for you",
        "sec.checklist": "预订清单 / Booking checklist",
        "th.item": "项目", "th.deadline": "截止/提前量", "th.price": "价格", "th.link": "链接",
        "btn.book": "预订",
        "sec.legs": "航班与城际交通 / Flights & intercity",
        "th.date": "日期", "th.route": "行程", "th.carrier": "承运",
        "leg.backup": "备选: ", "link.view": "查看",
        "sec.days": "每日行程 / Day by day",
        "map.here": "↗地图", "map.day": "整日路线图", "hop.map": "逐跳导航: ",
        "hop.n": "第{}跳",
        "walk.how": "步行约 {} km<span class=\"note\"> — {}</span>",
        "walk": "步行约 {} km(含街道系数、散步段与馆内)",
        "rain_alt": "雨天备选: ",
        "sec.hotels": "住宿 / Hotels",
        "sec.budget": "预算 / Budget",
        "th.cat": "类别", "th.pp": "每人", "th.total": "合计", "th.note": "备注",
        "sec.brief": "目的地简报 / Country brief",
        "sec.unverified": "⚠️ 未核实项 / Unverified",
        "footer": "生成于 {} · 价格会变,链接才是准绳 · 离线地图: 把 trip.kml 导入 "
                  "Organic Maps 或 Google My Maps · 日出日落数据 sunrise-sunset.org · 地理编码 "
                  "© OpenStreetMap contributors{}",
    },
    "en": {
        "html_lang": "en",
        "link": "map/link", "verify.est": "est.", "verify.verified": "verified",
        "map.cap": "schematic · about {km:.1f} km across · real navigation in the links above",
        "sec.decisions": "Decisions made for you",
        "sec.checklist": "Booking checklist",
        "th.item": "Item", "th.deadline": "Deadline / lead time", "th.price": "Price", "th.link": "Link",
        "btn.book": "book",
        "sec.legs": "Flights & intercity",
        "th.date": "Date", "th.route": "Route", "th.carrier": "Carrier",
        "leg.backup": "Backup: ", "link.view": "view",
        "sec.days": "Day by day",
        "map.here": "↗map", "map.day": "full-day route map", "hop.map": "hop-by-hop maps: ",
        "hop.n": "hop {}",
        "walk.how": "walk ~{} km<span class=\"note\"> — {}</span>",
        "walk": "walk ~{} km (street factor, strolls and in-venue included)",
        "rain_alt": "Rain plan: ",
        "sec.hotels": "Hotels",
        "sec.budget": "Budget",
        "th.cat": "Category", "th.pp": "Per person", "th.total": "Total", "th.note": "Note",
        "sec.brief": "Country brief",
        "sec.unverified": "⚠️ Unverified",
        "footer": "Generated {} · prices move, the links are the truth · offline map: import "
                  "trip.kml into Organic Maps or Google My Maps · sun times sunrise-sunset.org · "
                  "geocoding © OpenStreetMap contributors{}",
    },
}
_LANG = "zh"


def set_lang(lang):
    global _LANG
    _LANG = lang if lang in STRINGS else "zh"
    return _LANG


def T(key):
    return STRINGS.get(_LANG, {}).get(key, STRINGS["zh"][key])


CSS = """
:root{--bg:#fff;--fg:#1c1c1e;--dim:#6b6b70;--line:#e3e3e6;--card:#fafafa;
--accent:#2b6cb0;--warn:#b45309;--pin:#b91c1c;--ok:#15803d}
@media (prefers-color-scheme:dark){:root{--bg:#16171a;--fg:#e9e9ec;--dim:#9c9ca3;
--line:#2c2d31;--card:#1d1e22;--accent:#7aa7d9;--warn:#d99b3f;--pin:#e08585;--ok:#6cc08b}}
*{box-sizing:border-box}
body{margin:0;padding:20px 16px 60px;background:var(--bg);color:var(--fg);
font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",
"Hiragino Sans","Noto Sans CJK SC",sans-serif;-webkit-text-size-adjust:100%}
main{max-width:760px;margin:0 auto}
h1{font-size:1.6rem;margin:0 0 4px}h2{font-size:1.15rem;margin:32px 0 10px;
padding-bottom:5px;border-bottom:2px solid var(--line)}
h3{font-size:1rem;margin:0 0 6px}
a{color:var(--accent);overflow-wrap:anywhere}
a:focus-visible,button:focus-visible,summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.sub{color:var(--dim);font-size:.9rem;margin:0 0 2px}
.metagrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
gap:6px 18px;margin:14px 0 0;font-size:.92rem}
.metagrid div{color:var(--dim)}.metagrid b{color:var(--fg);font-weight:600}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
table{border-collapse:collapse;width:100%;font-size:.92rem}
th,td{text-align:left;padding:7px 9px;border-bottom:1px solid var(--line);
vertical-align:top}
th{font-size:.78rem;text-transform:uppercase;letter-spacing:.04em;color:var(--dim)}
.day{background:var(--card);border-left:4px solid var(--accent);border-radius:6px;
padding:12px 14px;margin:0 0 16px}
.day.travel{border-left-color:var(--warn)}
.day h3{display:flex;flex-wrap:wrap;gap:8px;align-items:baseline}
.day h3 .sun{font-weight:400;color:var(--dim);font-size:.85rem}
.tl{width:100%;font-size:.92rem}
.tl td{border-bottom:1px solid var(--line);padding:6px 8px 6px 0}
.tl tr:last-child td{border-bottom:0}
.tl .t{white-space:nowrap;font-variant-numeric:tabular-nums;color:var(--dim);
width:1%;padding-right:12px}
.tl tr.hop td{color:var(--dim);font-size:.87rem}
.tl tr.meal .what::before{content:"🍽 "}
.note{color:var(--dim);font-size:.87rem}
.pill{display:inline-block;font-size:.72rem;padding:1px 7px;border-radius:20px;
border:1px solid var(--line);margin-left:6px;white-space:nowrap;color:var(--dim)}
.pill.pinned{color:var(--pin);border-color:var(--pin)}
.pill.opener{color:var(--warn);border-color:var(--warn)}
.pill.verified{color:var(--ok);border-color:var(--ok)}
.ribbon{font-size:.87rem;color:var(--dim);margin:10px 0 0;overflow-wrap:anywhere}
.daymap{display:block;margin:10px 0 0;max-width:100%}
.daymap polyline{fill:none;stroke:var(--accent);stroke-width:2;stroke-dasharray:5 4;
opacity:.8}
.daymap circle{fill:var(--accent);opacity:.92}
.daymap text{fill:var(--bg);font-size:12px;font-weight:600}
.daymap text.cap{fill:var(--dim);font-size:11px;font-weight:400}
.dayfoot{font-size:.87rem;margin:8px 0 0}
.warn{color:var(--warn)}
ul{padding-left:20px;margin:8px 0}li{margin:3px 0}
footer{margin:40px 0 0;padding-top:12px;border-top:1px solid var(--line);
color:var(--dim);font-size:.83rem}
input[type=checkbox]{width:17px;height:17px}
@media print{body{padding:0;font-size:11pt}a{color:inherit;text-decoration:none}
h2{page-break-after:avoid}.day{page-break-inside:avoid;background:none;
border:1px solid #ccc}footer{page-break-before:avoid}}
"""

JS = """
(function(){var k='tripcheck:'+document.title;
var s=JSON.parse(localStorage.getItem(k)||'{}');
document.querySelectorAll('input[type=checkbox][data-k]').forEach(function(b){
 if(s[b.dataset.k])b.checked=true;
 b.addEventListener('change',function(){s[b.dataset.k]=b.checked;
  localStorage.setItem(k,JSON.stringify(s));});});})();
"""


def e(v):
    return html.escape(str(v)) if v is not None else ""


def link(url, label=None):
    if not url:
        return ""
    return '<a href="{}" target="_blank" rel="noopener">{}</a>'.format(
        e(url), e(label or T("link")))


def pills(item):
    out = ""
    tag = item.get("tag")
    if tag:
        t = str(tag)
        cls = "pinned" if t.startswith("pinned") else (
            "opener" if t.startswith("opener") else "")
        out += '<span class="pill {}">{}</span>'.format(cls, e(tag))
    v = item.get("verify")
    if v:
        label = T("verify.verified") if v == "verified" else T("verify.est")
        out += '<span class="pill {}">{}</span>'.format(
            "verified" if v == "verified" else "", label)
    return out


def section(title, body):
    return "<h2>{}</h2>\n{}".format(e(title), body) if body else ""


def day_svg(stops, w=680, h=170, pad=26):
    """A schematic of the day's shape from the stop coordinates — numbered dots in
    visiting order, joined in sequence. Deliberately NOT a street map: it has no
    tiles, so it works offline and inside a strict CSP, and it answers the only
    question a glance can answer — does today zig-zag across town or flow in a line?
    Real navigation stays in the per-hop links."""
    pts = [(float(s["lat"]), float(s["lon"]), s.get("name", ""))
           for s in stops
           if isinstance(s, dict) and s.get("lat") is not None
           and s.get("lon") is not None]
    if len(pts) < 2:
        return ""
    lats = [p[0] for p in pts]
    lons = [p[1] for p in pts]
    mlat = sum(lats) / len(lats)
    kx = math.cos(math.radians(mlat))            # equirectangular: shrink lon
    xs = [p[1] * kx for p in pts]
    ys = [-p[0] for p in pts]
    spanx, spany = max(xs) - min(xs), max(ys) - min(ys)
    if spanx <= 0 and spany <= 0:
        return ""
    scale = min((w - 2 * pad) / spanx if spanx > 0 else 1e9,
                (h - 2 * pad) / spany if spany > 0 else 1e9)
    cx = (w - spanx * scale) / 2 - min(xs) * scale
    cy = (h - spany * scale) / 2 - min(ys) * scale
    xy = [(x * scale + cx, y * scale + cy) for x, y in zip(xs, ys)]
    # scale bar: 1 degree of latitude ≈ 111.2 km, and y is in degrees of latitude
    km_across = spany * 111.2 if spany > 0 else spanx / kx * 111.2
    poly = " ".join("{:.1f},{:.1f}".format(x, y) for x, y in xy)
    dots = "".join(
        '<circle cx="{:.1f}" cy="{:.1f}" r="11"/>'
        '<text x="{:.1f}" y="{:.1f}" text-anchor="middle" dy="4">{}</text>'
        '<title>{}</title>'.format(x, y, x, y, i, e(p[2]))
        for i, ((x, y), p) in enumerate(zip(xy, pts), 1))
    return ((
        '<svg class="daymap" viewBox="0 0 {w} {h}" width="100%" height="{h}" '
        'role="img" aria-label="route shape"><polyline points="{poly}"/>{dots}'
        '<text class="cap" x="8" y="{cap}">' + T("map.cap") + '</text></svg>').format(
            w=w, h=h, poly=poly, dots=dots, cap=h - 7, km=max(km_across, 0.1)))


def render(p):
    meta = p.get("meta") or {}
    trip = p.get("trip") or "Trip plan"
    out = ['<main>', "<h1>{}</h1>".format(e(trip))]
    if meta.get("route"):
        out.append('<p class="sub">{}</p>'.format(e(meta["route"])))
    mg = [(k, meta.get(k)) for k in
          ("dates", "party", "budget_total", "fx", "self_check")]
    mg = [(k, v) for k, v in mg if v]
    if mg:
        out.append('<div class="metagrid">' + "".join(
            "<div>{}<br><b>{}</b></div>".format(e(k.replace("_", " ")), e(v))
            for k, v in mg) + "</div>")

    if p.get("decisions"):
        out.append(section(T("sec.decisions"),
                           "<ul>" + "".join("<li>{}</li>".format(e(d))
                                            for d in p["decisions"]) + "</ul>"))

    if p.get("checklist"):
        rows = []
        for i, c in enumerate(p["checklist"]):
            rows.append(
                "<tr><td><input type=checkbox data-k='c{}'></td><td>{}{}</td>"
                "<td>{}</td><td>{}</td><td>{}</td></tr>".format(
                    i, e(c.get("item")),
                    '<div class="note">{}</div>'.format(e(c["note"]))
                    if c.get("note") else "",
                    e(c.get("deadline")), e(c.get("price")),
                    link(c.get("link"), c.get("link_text") or T("btn.book"))))
        out.append(section(
            T("sec.checklist"),
            '<div class="scroll"><table><tr><th></th><th>{}</th><th>{}'
            "</th><th>{}</th><th>{}</th></tr>".format(
                T("th.item"), T("th.deadline"), T("th.price"), T("th.link"))
            + "".join(rows) + "</table></div>"))

    if p.get("legs"):
        rows = []
        for l in p["legs"]:
            route = "{} → {}".format(e(l.get("from")), e(l.get("to")))
            times = " ".join(x for x in [e(l.get("dep")), "→", e(l.get("arr"))] if x)
            extra = " · ".join(x for x in [e(l.get("bags")), e(l.get("note"))] if x)
            back = ('<div class="note">{}{}</div>'.format(T("leg.backup"), e(l["backup"]))
                    if l.get("backup") else "")
            rows.append(
                "<tr><td>{}<div class='note'>{}</div></td><td>{}<div class='note'>"
                "{}</div></td><td>{}</td><td>{}{}</td><td>{}</td></tr>".format(
                    e(l.get("date")), e(l.get("type")), route, times,
                    e(l.get("carrier")), e(l.get("price")),
                    '<div class="note">{}</div>'.format(extra) if extra else "",
                    link(l.get("link"), T("link.view")) + back))
        out.append(section(
            T("sec.legs"),
            '<div class="scroll"><table><tr><th>{}</th><th>{}</th><th>{}</th>'
            "<th>{}</th><th>{}</th></tr>".format(
                T("th.date"), T("th.route"), T("th.carrier"), T("th.price"), T("th.link"))
            + "".join(rows) + "</table></div>"))

    if p.get("days"):
        cards = []
        for d in p["days"]:
            head = " · ".join(x for x in [e(d.get("date")), e(d.get("city")),
                                          e(d.get("label"))] if x)
            sun = ('<span class="sun">{}</span>'.format(e(d["sun"]))
                   if d.get("sun") else "")
            rows = []
            for it in d.get("timeline", []):
                kind = it.get("kind", "anchor")
                what = e(it.get("what"))
                if it.get("link"):
                    what += " " + link(it["link"], T("map.here"))
                bits = [x for x in [e(it.get("price")), e(it.get("note"))] if x]
                if bits:
                    what += '<div class="note">{}</div>'.format(" — ".join(bits))
                rows.append('<tr class="{}"><td class="t">{}</td>'
                            '<td class="what">{}{}</td></tr>'.format(
                                e(kind), e(it.get("t")), what, pills(it)))
            foot = []
            if d.get("day_map"):
                foot.append(link(d["day_map"], T("map.day")))
            if d.get("hop_links"):
                foot.append(T("hop.map") + " ".join(
                    link(u, T("hop.n").format(i + 1))
                    for i, u in enumerate(d["hop_links"])))
            wk = d.get("walking_km")
            if isinstance(wk, dict):
                foot.append(T("walk.how").format(
                    e(wk.get("total")), e(wk.get("how", ""))))
            elif wk:
                foot.append(T("walk").format(e(wk)))
            if d.get("rain_alt"):
                foot.append(T("rain_alt") + e(d["rain_alt"]))
            fl = ('<div class="dayfoot">{}</div>'.format(" · ".join(foot))
                  if foot else "")
            lc = ('<div class="dayfoot warn">{}</div>'.format(e(d["late_cut"]))
                  if d.get("late_cut") else "")
            if d.get("ribbon"):
                lc = '<div class="ribbon">{}</div>'.format(e(d["ribbon"])) + lc
            cards.append(
                '<div class="day{}"><h3>{} {}</h3><table class="tl">{}</table>'
                "{}{}{}</div>".format(" travel" if d.get("travel_day") else "",
                                      head, sun, "".join(rows), fl, lc,
                                      day_svg(d.get("stops") or [])))
        out.append(section(T("sec.days"), "".join(cards)))

    if p.get("hotels"):
        blocks = []
        for h in p["hotels"]:
            opts = "".join(
                "<li>{} — {} {}</li>".format(e(o.get("name")), e(o.get("band")),
                                             link(o.get("link"), T("link.view")))
                for o in h.get("options", []))
            blocks.append("<h3>{} · {}</h3><p class='note'>{}</p><ul>{}</ul>".format(
                e(h.get("base")), e(h.get("area")), e(h.get("why")), opts))
        out.append(section(T("sec.hotels"), "".join(blocks)))

    if p.get("budget"):
        rows = "".join(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td class='note'>{}</td></tr>"
            .format(e(b.get("cat")), e(b.get("per_person")), e(b.get("total")),
                    e(b.get("note"))) for b in p["budget"])
        out.append(section(
            T("sec.budget"),
            '<div class="scroll"><table><tr><th>{}</th><th>{}</th><th>{}</th>'
            "<th>{}</th></tr>".format(T("th.cat"), T("th.pp"), T("th.total"), T("th.note"))
            + rows + "</table></div>"))

    if p.get("brief"):
        rows = "".join("<li><b>{}</b>: {}</li>".format(e(k), e(v))
                       for k, v in p["brief"].items() if v)
        out.append(section(T("sec.brief"), "<ul>" + rows + "</ul>"))

    if p.get("unverified"):
        out.append(section(T("sec.unverified"),
                           "<ul>" + "".join("<li>{}</li>".format(e(u))
                                            for u in p["unverified"]) + "</ul>"))

    out.append(
        "<footer>" + T("footer").format(
            e(meta.get("generated", "")),
            " · " + e(meta["self_check"]) if meta.get("self_check") else "")
        + "</footer></main>")
    return ("<!doctype html><html lang=\"{}\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>{}</title><style>{}</style></head><body>{}"
            "<script>{}</script></body></html>").format(
                T("html_lang"), e(trip), CSS, "\n".join(out), JS)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("-o", "--out", default="trip.html")
    ap.add_argument("--force", action="store_true",
                    help="render even with template scaffolding still in the plan")
    ap.add_argument("--lang", default=None, choices=sorted(STRINGS),
                    help="UI language (default: plan.lang > plan.meta.lang > zh)")
    a = ap.parse_args()
    try:
        plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    except Exception as ex:
        sys.exit("Bad plan JSON ({}) — see this script's docstring for the schema."
                 .format(ex))
    if not isinstance(plan, dict):
        sys.exit("Plan JSON must be an object with a \"days\" list.")
    set_lang(a.lang or plan.get("lang") or (plan.get("meta") or {}).get("lang") or "zh")
    # Scaffolding must never reach a traveller. Both of these mean the template was
    # edited field-by-field and something got missed.
    blob = json.dumps(plan, ensure_ascii=False)
    leftovers = []
    if "_readme" in plan:
        leftovers.append('the template\'s "_readme" key is still present')
    if "PLACEHOLDER" in blob:
        leftovers.append("{} PLACEHOLDER value(s) never filled in".format(
            blob.count("PLACEHOLDER")))
    if leftovers and not a.force:
        sys.exit("Refusing to render — " + "; ".join(leftovers)
                 + ".\nFix them, or pass --force to render anyway.")
    for w in leftovers:
        print("WARNING (forced): " + w)
    Path(a.out).write_text(render(plan), encoding="utf-8")
    print("wrote {} ({} days)".format(a.out, len(plan.get("days") or [])))


if __name__ == "__main__":
    main()
