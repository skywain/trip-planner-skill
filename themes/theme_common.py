#!/usr/bin/env python3
"""Shared plumbing for every theme renderer.

Anything a theme can share WITHOUT flattening its identity lives here:
plan-JSON reading helpers (load_plan → norm_plan type-normalises the plan's
sections and WARNs instead of crashing), the lucide sprite, the keyless
Google-Maps embed recipe, the art layer (Art / load_art), the <title> /
filename words (title_kick / title_head / export_prefix) and the PNG export
engine (export_js). Everything that carries the look —
layout, type, colour, motion, affordances — deliberately stays inside each
renderer, because that is the part that has to differ.

Import with:  from theme_common import *
Renderers with a different icon class (the timetable uses square-capped
"pic" glyphs) call set_icon_base("pic") once at module load.

Assets: data_uri(stem, size) searches a list of directories — the plan's
own directory (added by load_art), any --assets DIR (add_art_arg), and this
directory last (the shared library). See add_asset_dir().
"""
import base64
import html as _html
import json
import math
import pathlib

__all__ = [
    "TAG_PRETTY", "esc", "et", "ic", "sprite", "set_icon_base",
    "data_uri", "day_embed_url", "dist_km", "load_plan", "norm_plan", "PLAN_SHAPE", "LUCIDE", "asset_count",
    "Art", "load_art", "add_art_arg", "short_dates", "export_prefix", "title_kick", "title_head",
    "add_asset_dir", "asset_dirs", "date_span", "BRIEF_TITLES", "BRIEF_TITLES_EN", "brief_titles",
    "STRINGS", "THEME_NAMES", "set_lang", "lang", "T", "tag_pretty", "theme_name", "weekday", "init_lang", "ASSETS",
]

HERE = pathlib.Path(__file__).parent

# Asset search path for data_uri(). Later additions win; themes/assets/ (the
# shared image library beside this file) is always the last resort.
# load_art() adds the plan's own directory, so a trip that keeps its webps
# beside its plan/art never has to copy them into themes/assets/.
ASSETS = HERE / "assets"
_ASSET_DIRS = [ASSETS]

# Day titles (4-char editorial labels) live in the trip's art.json — see
# Art.day_theme(). The old DAY_THEME table was deleted 2026-08-15 once the
# last live renderer (portal) migrated; retired -v1/board/chart renderers
# that still import it are kept on disk for archaeology only.
TAG_PRETTY = {"pinned": "钉死", "skippable": "可砍", "opener": "开门冲"}   # zh (legacy name)

# ------------------------------------------------------------------ i18n --
# The page language is a PLAN fact (plan["lang"] or plan["meta"]["lang"]:
# "zh" default | "en"), overridable with --lang. Renderers keep their own
# theme-voice strings in a local {lang: {...}} table and use lang() to pick;
# the strings every theme shares live here so they cannot drift apart.
# zh must reproduce today's pages byte for byte — never edit a zh value
# without rebuilding the US baselines.
_LANG = "zh"
STRINGS = {
    "zh": {
        "tag.pinned": "钉死", "tag.skippable": "可砍", "tag.opener": "开门冲",
        "tag.swap": "换",
        "btn.save_day": "保存这一天", "btn.save_appendix": "保存附录",
        "btn.save_page": "生成长图",
        "toast.saved": "已保存", "toast.making_page": "长图生成中,几秒钟…",
        "toast.failed": "生成失败", "toast.too_big": "这一块太大,换小一点的区块试试",
        "toast.too_big_page": "生成失败:内容太大,试试单块保存",
        "toast.hidden": "这一块现在不可见,先滚到它再试",
        "toast.module_only": "这一版只支持单块保存",
        "toast.no_browser": "生成失败:浏览器不支持,换 Chrome 试试",
        "label.page": "整页", "label.day": "DAY", "label.appendix": "附录", "label.module": "模块",
        "sec.brief": "行前须知", "sec.decisions": "关键取舍", "sec.unverified": "出票前待复核",
        "sec.legs": "航段", "sec.hotels": "住宿", "sec.budget": "预算", "sec.checklist": "清单",
        "sec.appendix": "附录", "sec.route": "路线", "sec.map": "沿途地图",
        "sun.dawn": "天亮", "walk": "步行", "rain_alt": "雨备", "late_cut": "晚点剪法",
        "hop.map": "逐跳导航", "verify.est": "est", "price.check": "查价", "link": "链接",
        "week": ["週一", "週二", "週三", "週四", "週五", "週六", "週日"],
        "html_lang": "zh-CN",
    },
    "en": {
        "tag.pinned": "pinned", "tag.skippable": "optional", "tag.opener": "go first",
        "tag.swap": "swap",
        "btn.save_day": "Save this day", "btn.save_appendix": "Save appendix",
        "btn.save_page": "Save long image",
        "toast.saved": "Saved", "toast.making_page": "Rendering the long image, a few seconds…",
        "toast.failed": "Could not save", "toast.too_big": "This block is too large — try a smaller one",
        "toast.too_big_page": "Could not save: too large, try a single block",
        "toast.hidden": "This block is not visible right now — scroll to it and retry",
        "toast.module_only": "This theme saves single blocks only",
        "toast.no_browser": "Could not save: browser unsupported, try Chrome",
        "label.page": "page", "label.day": "DAY", "label.appendix": "appendix", "label.module": "block",
        "sec.brief": "Before you go", "sec.decisions": "Key decisions", "sec.unverified": "Verify before booking",
        "sec.legs": "Flights & legs", "sec.hotels": "Stays", "sec.budget": "Budget", "sec.checklist": "Checklist",
        "sec.appendix": "Appendix", "sec.route": "Route", "sec.map": "Maps along the way",
        "sun.dawn": "dawn", "walk": "walk", "rain_alt": "rain plan", "late_cut": "if running late",
        "hop.map": "hop-by-hop maps", "verify.est": "est", "price.check": "check price", "link": "link",
        "week": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "html_lang": "en",
    },
}
THEME_NAMES = {   # used in <title> and export filenames
    "zh": {"journal": "手账版", "noir": "夜航版", "illustrated": "插画版", "clay": "黏土版",
           "glass": "玻璃版", "zine": "Zine版", "splash": "闪屏版", "portal": "穿越版", "picker": "风格选型"},
    "en": {"journal": "Journal", "noir": "Night Flight", "illustrated": "Illustrated", "clay": "Clay",
           "glass": "Glass", "zine": "Zine", "splash": "Splash", "portal": "Portal", "picker": "Style picker"},
}


def set_lang(lang):
    global _LANG
    _LANG = lang if lang in STRINGS else "zh"
    return _LANG


def lang():
    return _LANG


def T(key, default=None):
    """Shared UI string in the current language (falls back to zh, then key)."""
    v = STRINGS.get(_LANG, {}).get(key)
    if v is None:
        v = STRINGS["zh"].get(key, default if default is not None else key)
    return v


def tag_pretty(tag):
    """Timeline degradation tag label: pinned/skippable/opener/swap→X."""
    if not tag:
        return ""
    if tag.startswith("swap"):
        return tag            # "swap→X" is shown as written in every theme (baseline)
    return T("tag." + tag, tag)


def theme_name(key):
    return THEME_NAMES.get(_LANG, THEME_NAMES["zh"]).get(key, key)


def weekday(date_str):
    """'2026-09-25' → 週五 / Fri in the current language ('' if unparsable)."""
    import datetime
    try:
        d = datetime.date.fromisoformat(date_str)
    except (TypeError, ValueError):
        return ""
    return T("week")[d.weekday()]


def init_lang(args, plan):
    """Renderer main(): pick --lang, else plan.lang / plan.meta.lang, else zh."""
    lang_ = getattr(args, "lang", None) or plan.get("lang") or (plan.get("meta") or {}).get("lang") or "zh"
    return set_lang(lang_)

LUCIDE = {k: _html.unescape(v) for k, v in
          json.loads((HERE / "lucide-icons.json").read_text())["icons"].items()}

_ICON_BASE = "ic"
_uri_cache = {}


def set_icon_base(name):
    """Themes that style their glyphs differently use their own class base."""
    global _ICON_BASE
    _ICON_BASE = name


def esc(s):
    return _html.escape(str(s), quote=True)


def ic(name, cls=""):
    c = f"{_ICON_BASE} {cls}".strip()
    return f'<svg class="{c}" aria-hidden="true"><use href="#i-{name}"/></svg>'


def sprite():
    syms = "".join(f'<symbol id="i-{n}" viewBox="0 0 24 24">{b}</symbol>'
                   for n, b in LUCIDE.items())
    return f'<svg style="display:none" aria-hidden="true"><defs>{syms}</defs></svg>'


def et(s):
    """esc + swap the emojis that live in plan data for sprite glyphs."""
    t = esc(s)
    return (t.replace("✈️", ic("plane")).replace("✈", ic("plane"))
             .replace("⚠️", ic("alert", "warn")).replace("⚠", ic("alert", "warn"))
             .replace("☀", ic("sunrise")).replace("🌇", ic("sunset")))


def add_asset_dir(path):
    """Prepend a directory to data_uri()'s search path (may be called many
    times; the LAST one added is searched FIRST, themes/assets/ is the fallback).
    None / "" / a non-directory is ignored; duplicates are moved to the front
    rather than added twice."""
    if not path:
        return
    p = pathlib.Path(path).expanduser().resolve()
    if not p.is_dir():
        return
    if p in _ASSET_DIRS:
        _ASSET_DIRS.remove(p)
    _ASSET_DIRS.insert(0, p)


def asset_dirs():
    """The current search path, first-searched first (for logs/debugging)."""
    return list(_ASSET_DIRS)


def data_uri(stem, size=None):
    """Inline an asset as base64. `size` picks a pre-scaled variant
    (md / sm / lg / band / strip); the chain then falls back to the cut-out
    and finally the full-size file. Always pick the smallest variant the
    layout actually displays — inlining a 640px image into a 128px slot has
    bloated this project twice.

    Files are looked up in every asset dir (see add_asset_dir; load_art adds
    the plan's directory), best variant first: for each candidate filename
    the dirs are tried in order, so a trip-local `foo.webp` beats a
    themes/assets `foo.webp`, but a themes/assets `foo.md.webp` still beats a
    trip-local `foo.webp` when size="md" (variant rank outranks location).
    The cache key is stem+size only — the first hit wins for the process."""
    if not stem:
        return ""
    key = f"{stem}.{size}" if size else stem
    if key in _uri_cache:
        return _uri_cache[key]
    cands = ([f"{stem}.{size}.webp"] if size else [])
    cands += [f"{stem}.md.webp", f"{stem}.cut.webp", f"{stem}.webp"]
    for cand in cands:
        for d in _ASSET_DIRS:
            p = d / cand
            if p.exists():
                uri = "data:image/webp;base64," + base64.b64encode(p.read_bytes()).decode()
                _uri_cache[key] = uri
                return uri
    return ""


def asset_count():
    return len(_uri_cache)


def dist_km(a, b):
    dlat = (a[0] - b[0]) * 111.0
    dlon = (a[1] - b[1]) * 111.0 * math.cos(math.radians((a[0] + b[0]) / 2))
    return (dlat * dlat + dlon * dlon) ** 0.5


def day_embed_url(day, max_hop_km=150):
    """Keyless Google Maps directions embed for a day.

    Two rules learned the hard way:
      * daddr starts the chain and the FINAL stop ends it — writing the
        destination first silently scrambles the route order;
      * only embed the longest run of consecutive stops whose hops are all
        under `max_hop_km`, so flights and tour-bus return hauls drop out
        and the sightseeing chain survives.
    """
    pts = [(float(s["lat"]), float(s["lon"])) for s in day.get("stops", [])
           if s.get("lat") and s.get("lon")]
    if len(pts) < 2:
        return ""
    runs, cur = [], [pts[0]]
    for a, b in zip(pts, pts[1:]):
        if dist_km(a, b) <= max_hop_km:
            cur.append(b)
        else:
            runs.append(cur)
            cur = [b]
    runs.append(cur)
    pts = max(runs, key=len)
    if len(pts) < 2:
        return ""
    fmt = lambda q: f"{q[0]:.6f},{q[1]:.6f}"
    chain = fmt(pts[1]) + "".join(f"+to:{fmt(q)}" for q in pts[2:])
    return (f"https://maps.google.com/maps?saddr={fmt(pts[0])}"
            f"&daddr={chain}&dirflg=r&output=embed")


# Top-level plan sections and the shape every renderer assumes for them.
# (kind, item type, hint keys): "list" of dict / str, or "dict". A plan written
# from the prose alone tends to get these wrong (budget as {note, rows:[…]},
# legs as a table with invented column names) — norm_plan() turns that into
# a stderr WARN plus a fallback the renderers can iterate, never a traceback.
PLAN_SHAPE = {
    "days":       ("list", dict, ("date", "city", "label", "timeline", "stops")),
    "legs":       ("list", dict, ("type", "date", "carrier", "from", "to", "dep", "arr", "price")),
    "hotels":     ("list", dict, ("base", "area", "why", "options")),
    "budget":     ("list", dict, ("cat", "per_person", "total", "note")),
    "checklist":  ("list", dict, ("item", "deadline", "price", "link", "note")),
    "decisions":  ("list", str, ()),
    "unverified": ("list", str, ()),
    "brief":      ("dict", str, ()),
    "meta":       ("dict", None, ()),
}
_PLAN_DOC = "see references/output-template.md / assets/plan.example.json"


def norm_plan(plan, warn=None):
    """Type-normalise the top-level sections of a plan IN PLACE and return it.

    For every key in PLAN_SHAPE: a section of the wrong type is reported as
    `WARN plan.<key>: expected list of objects, got dict — see …` on stderr
    (or through `warn(msg)`) and replaced by a usable fallback — a dict
    where a list of objects was expected is salvaged from its first list-of-
    objects value ({note, rows:[…]} → rows), non-object rows are dropped, a
    stray string becomes a one-item list, anything else becomes empty. Rows
    that carry none of the section's known keys get a WARN too (that is the
    "renders, but every cell is blank" case). days[].timeline / stops are
    checked the same way. A plan that already has the right shapes passes
    through untouched — output identical, no WARN."""
    import sys
    if warn is None:
        warn = lambda m: sys.stderr.write(m + "\n")
    if not isinstance(plan, dict):
        warn(f"WARN plan: expected an object at the top level, got {type(plan).__name__} — {_PLAN_DOC}")
        return {}

    def fix_list(key, v, item_type, hint):
        want = "list of objects" if item_type is dict else "list of strings"
        if isinstance(v, dict):
            inner = [x for x in v.values() if isinstance(x, list)]
            if item_type is dict:
                inner = [x for x in inner if x and all(isinstance(i, dict) for i in x)]
            if inner:
                fb, how = inner[0], "using its inner list"
            elif item_type is str:
                fb, how = [f"{k}: {x}" for k, x in v.items()], "flattening it to 'key: value' lines"
            else:
                fb, how = [], "rendering it empty"
            warn(f"WARN plan.{key}: expected {want}, got dict — {how}; {_PLAN_DOC}")
            v = fb
        elif isinstance(v, str):
            warn(f"WARN plan.{key}: expected {want}, got a string — {_PLAN_DOC}")
            v = [v] if item_type is str else []
        elif not isinstance(v, list):
            warn(f"WARN plan.{key}: expected {want}, got {type(v).__name__} — rendering it empty; {_PLAN_DOC}")
            v = []
        if item_type is dict:
            bad = sum(1 for x in v if not isinstance(x, dict))
            if bad:
                warn(f"WARN plan.{key}: {bad} row(s) are not objects — dropped; {_PLAN_DOC}")
                v = [x for x in v if isinstance(x, dict)]
            if hint and v and not any(k in x for x in v for k in hint):
                warn(f"WARN plan.{key}: no row carries any of the expected keys "
                     f"({', '.join(hint)}) — every cell will render blank; {_PLAN_DOC}")
        return v

    for key, (kind, item_type, hint) in PLAN_SHAPE.items():
        if key not in plan:
            continue
        v = plan[key]
        if kind == "list":
            plan[key] = fix_list(key, v, item_type, hint)
        elif not isinstance(v, dict):
            warn(f"WARN plan.{key}: expected an object, got {type(v).__name__} — rendering it empty; {_PLAN_DOC}")
            plan[key] = {}
    for i, d in enumerate(plan.get("days") or []):
        for sub in ("timeline", "stops"):
            if sub in d and not (isinstance(d[sub], list) and all(isinstance(r, dict) for r in d[sub])):
                d[sub] = fix_list(f"days[{i}].{sub}", d[sub], dict, ())
    return plan


def load_plan(path):
    """Read plan.geo.json and normalise its section types (norm_plan)."""
    return norm_plan(json.loads(pathlib.Path(path).read_text()))


def short_dates(meta_dates):
    """'2026-09-25 → 2026-10-07' → '09-25 → 10-07' (any year, both ends).
    Renderers then swap the arrow for their own dash — that part is voice.

    CONTRACT for plan meta.dates: keep it a bare `YYYY-MM-DD → YYYY-MM-DD`
    (arrow or dash between). Prose such as "10.01 抵达 – 10.08 离开(…)"
    is passed through verbatim after stripping years — it will land on the
    cover date line of every theme exactly as written."""
    import re
    return re.sub(r"\b\d{4}-", "", meta_dates or "")


def date_span(meta_dates):
    """(first_iso, last_iso) found in meta.dates, or ("", "") — for renderers
    that want the two ends rather than the whole string."""
    import re
    ds = re.findall(r"\d{4}-\d{2}-\d{2}", meta_dates or "")
    return (ds[0], ds[-1]) if ds else ("", "")


# Country-brief section titles: plan.brief keys are English identifiers
# (visa / holidays / weather / money / connectivity …). Every theme labels
# them from this one table, overlaid by the trip's art common `brief_titles`
# (e.g. "签证 · EVUS"); unknown keys (a trip's own Chinese headings) print
# as they are.
BRIEF_TITLES = {
    "visa": "签证", "holidays": "节假与人流", "weather": "天气",
    "money": "货币与小费", "connectivity": "通信", "insurance": "保险",
    "safety": "安全", "baggage": "行李", "altitude": "高原与海拔",
    "navigation": "导航",
}
BRIEF_TITLES_EN = {
    "visa": "Visa & entry", "holidays": "Holidays & crowds", "weather": "Weather",
    "money": "Money & tipping", "connectivity": "Connectivity", "insurance": "Insurance",
    "safety": "Safety", "baggage": "Baggage", "altitude": "Altitude",
    "navigation": "Maps & navigation",
}


def brief_titles(art=None):
    """Merged {brief key: display title} in the current language —
    theme_common defaults under the art file's common `brief_titles`.
    Renderers: `titles.get(k, k)`. Keys are matched case-insensitively with
    spaces/underscores ignored, so a plan whose brief keys are already
    display strings ("Visa & entry") passes through untouched."""
    t = dict(BRIEF_TITLES if _LANG == "zh" else BRIEF_TITLES_EN)
    if art:
        t.update(art.get("brief_titles", default={}) or {})
    return t


# --------------------------------------------------------------- art layer --
class Art:
    """Per-trip art direction — the part of a themed page that is ABOUT this
    trip rather than about the theme: which picture each day gets, the
    hand-written captions, the cover title, the closing line, the postmark
    codes. It lives in `<plan>.art.json` next to the plan (schema:
    ART-SCHEMA.md) so a renderer never hardcodes a date, a place or an asset
    name; a new trip is a new plan + a new art file, zero code.

    Layout: {"cover": {...}, "end": {...}, "days": {date: {...}},
             "themes": {theme: {"cover": {...}, "days": {date: {...}}, ...}}}
    Everything is optional. A renderer must render a usable page from an
    EMPTY Art (no image, no caption — never a crash, never a stale line
    from another trip). Lookups merge the theme's block over the common
    block so a theme can override just one field.
    """

    def __init__(self, data=None, path=None):
        self.data = data or {}
        self.path = path

    def __bool__(self):
        return bool(self.data)

    # -- generic -------------------------------------------------------
    def get(self, *keys, default=None):
        cur = self.data
        for k in keys:
            if not isinstance(cur, dict) or k not in cur:
                return default
            cur = cur[k]
        return cur

    def theme(self, theme):
        """The theme's trip-level block: themes.<theme> (may be empty)."""
        return self.get("themes", theme, default={}) or {}

    # -- cover / end -----------------------------------------------------
    def cover(self, theme=None, key=None, default=""):
        """cover.<key>, with themes.<theme>.cover.<key> winning when set."""
        base = dict(self.get("cover", default={}) or {})
        if theme:
            base.update(self.get("themes", theme, "cover", default={}) or {})
        if key is None:
            return base
        v = base.get(key)
        return default if v in (None, "") else v

    def end(self, theme=None, key=None, default=""):
        """end.<key> (the closing spread: date / line / fine print), same
        override rule as cover()."""
        base = dict(self.get("end", default={}) or {})
        if theme:
            base.update(self.get("themes", theme, "end", default={}) or {})
        if key is None:
            return base
        v = base.get(key)
        return default if v in (None, "") else v

    # -- days ------------------------------------------------------------
    def day(self, date, theme=None):
        """Merged per-day dict: days[date] overlaid with
        themes.<theme>.days[date]. Always a dict, possibly empty."""
        d = dict(self.get("days", date, default={}) or {})
        if theme:
            d.update(self.get("themes", theme, "days", date, default={}) or {})
        return d

    def day_theme(self, date, default=""):
        """The 4-character editorial day title (was DAY_THEME)."""
        return self.get("days", date, "theme", default=None) or default


def load_art(plan_path, art_path=None, assets=None):
    """Resolve the art file for a plan.

    art_path None  → sidecar next to the plan: foo.geo.json / foo.json →
                     foo.art.json; missing sidecar = empty Art (renders plain)
    art_path "none" → explicitly empty (what a foreign plan gets)
    art_path <file> → that file

    Side effect (asset search path, see add_asset_dir): the plan's directory
    is added first, then the art file's directory when it differs, then
    every entry of `assets` (str or list, e.g. argparse's --assets) — so the
    last --assets wins, then art dir, then plan dir, then themes/assets/. A trip
    keeps its webps next to its plan and never copies them into themes/assets/.
    """
    p = pathlib.Path(plan_path)
    add_asset_dir(p.parent)
    if art_path and art_path != "none":
        add_asset_dir(pathlib.Path(art_path).parent)
    if isinstance(assets, (str, pathlib.Path)):
        assets = [assets]
    for a in assets or []:
        add_asset_dir(a)
    if art_path == "none":
        return Art({}, None)
    if art_path:
        ap = pathlib.Path(art_path)
    else:
        stem = p.name
        for suf in (".geo.json", ".plan.json", ".json"):
            if stem.endswith(suf):
                stem = stem[: -len(suf)]
                break
        ap = p.with_name(stem + ".art.json")
    if not ap.exists():
        return Art({}, None)
    return Art(json.loads(ap.read_text(encoding="utf-8")), ap)


def title_kick(art, theme=None):
    """The trip word that opens <title> and the download-filename prefix
    (never a displayed headline — that is cover.zh/en). zh page: cover.kick
    ("美国行"). en page: cover.kick_en when the art has one ("MOROCCO 2026"),
    else kick — portal's rule, shared by every renderer since 2026-08-16 so
    one art file cannot yield "Morocco 2026 · Glass" beside "MOROCCO 2026 ·
    Portal". themes.<theme>.cover overrides apply as in Art.cover()."""
    if not art:
        return ""
    kick = art.cover(theme, "kick")
    if _LANG != "zh":
        return art.cover(theme, "kick_en") or kick
    return kick


def title_head(art, theme=None, year=""):
    """'{kick} {year}' — the head of <title> ("美国行 2026", "MOROCCO 2026").
    The year is dropped when the kick already spells it, so a kick_en of
    "MEXICO 2026" does not become "MEXICO 2026 2026". Renderers append their
    own theme word: " · ".join(x for x in (title_head(...), theme_name(T)) if x)."""
    kick = title_kick(art, theme)
    if year and year in kick:
        year = ""
    return f"{kick} {year}".strip()


def export_prefix(art, meta, theme=None):
    """Download-filename prefix from the trip's art: "{kick}{year}-" — the
    US trip's is "美国行2026-"; a trip with no kick gets "{year}-", no year
    gets "trip-". The kick is title_kick() (kick_en on an en page) and the
    year is not repeated when the kick already carries it ("MEXICO 2026-").
    Pass the result to export_js(file_prefix=...)."""
    import re
    kick = title_kick(art, theme)
    m = re.search(r"\d{4}", (meta or {}).get("dates", "") or "")
    year = m.group(0) if m else ""
    if year and year in kick:
        year = ""
    return f"{kick}{year}-" if (kick or year) else "trip-"


def add_art_arg(ap):
    """argparse hook shared by every renderer: --art <file|none> and
    --assets DIR (repeatable). Renderers then call
    load_art(args.plan, args.art, args.assets)."""
    ap.add_argument("--art", default=None,
                    help="art.json for this trip (default: <plan>.art.json "
                         "beside the plan; 'none' = render without art)")
    ap.add_argument("--lang", default=None, choices=sorted(STRINGS),
                    help="UI language (default: plan.lang / plan.meta.lang, else zh)")
    ap.add_argument("--assets", action="append", default=[], metavar="DIR",
                    help="extra directory to search for image assets "
                         "(repeatable; later wins). The plan's own directory "
                         "and themes/assets/ are always searched.")
    return ap


# ------------------------------------------------------------------ export --
def export_js(theme, page_bg, extra_css="", page_root="", file_prefix=None, ui=None,
              measure_clone=False):
    """Client-side PNG export engine (share to 朋友圈/Twitter/Instagram).

    Zero dependencies and fully offline — the pages must keep working from a
    double-clicked file://, so no html2canvas. Instead: clone the node, inline
    every <style> on the page (all assets are data URIs already, so nothing
    external ever blocks), wrap in <svg><foreignObject>, rasterise via canvas,
    download. Fonts embedded as data-URI @font-face render inside the SVG.

    theme     — filename tag (e.g. "手账版")
    page_bg   — canvas backdrop fill behind the capture (page paper/desk color)
    extra_css — per-theme overrides applied only inside the capture
                (e.g. neutralise scroll-reveal opacity states)
    page_root — selector for whole-page export; "" disables the whole-page
                button wiring (sticky/fixed composited themes: module-only)
    ui          — dict of toast/label strings; None = current language via T()
    file_prefix — start of the download filename, e.g. "美国行2026-" (build it
                from the trip's art: f"{kick}{year}-"; see export_prefix()).
                None → neutral "trip-" (only retired renderers omit it).
    measure_clone — True: size the canvas from the CAPTURE CLONE (mounted
                off-screen for a moment with the capture CSS applied) instead
                of the live element's scrollHeight. The live number counts
                every in-flow `.no-export` element (button rows, closed
                <details>) and ignores extra_css height pins, so a clone that
                is shorter than the live element leaves the difference as
                blank paper at the foot of the export (illustrated: ~900px on
                a laptop, ~2600px in a 2600px-tall probe window; every
                whole-page theme has some — see the 2026-08-16 note in
                render_theme2). Off by default ON PURPOSE: tried as the default
                on 2026-08-16 and the splash export came out 400px SHORTER
                than its content (出票前待复核 + end card cropped) — the
                off-screen clone does not lay out like the in-document page
                for every theme. Only illustrated (verified on the Turkey and
                US pages, head and tail) opts in; before enabling it for a
                theme, probe BOTH ANCHOR=bottom and the top of the export.

    Contract for renderers:
      · elements with  data-export="标签"  get per-module capture support
      · buttons carry  class="xbtn" data-x-for="<selector>"  (module)
                  or   class="xbtn" data-x-page               (whole page)
      · anything with .no-export (the buttons themselves included) is
        stripped from the capture clone.
      · <use href="#id"> sprite references are fine: the engine copies the
        referenced <symbol>s into the capture (a clone is a standalone SVG
        document — without the copies every icon exports blank).
    """
    # raw string: the JS regexes below carry \d \w \( — as a normal literal
    # those are invalid Python escapes (SyntaxError under -W error, warning
    # by default). '\n' inside stays a JS escape, which is what we want.
    js = r"""
(function () {
  var BG = __BG__, THEME = __THEME__, PAGE_ROOT = __ROOT__;
  var XCSS = __EXTRA__ +
    '.no-export{display:none!important}' +
    // the capture root's own margin would push the picture down inside the
    // foreignObject and crop the same amount off the bottom (scrollHeight
    // does not include it) — the wrap already sits flush, so drop it
    '.__xbody>*{margin:0!important}' +
    '*{animation:none!important;transition:none!important}';
  function styleText() {
    var t = '';
    Array.prototype.forEach.call(document.querySelectorAll('style'),
      function (s) { t += s.textContent + '\n'; });
    // The CSS is spliced into an XML document, so a bare '<' or '&' anywhere
    // in it — a comparison in a comment is enough — makes the whole SVG
    // unparseable and the export dies as "渲染引擎不支持". Escape both.
    return pxify(t + XCSS + bodyWrapCss())
      .replace(/&/g, '&amp;').replace(/</g, '&lt;');
  }
  // Inside a foreignObject, vh/svh resolve against the SVG box — which for a
  // whole-page capture is the WHOLE PAGE. A 100svh cover then eats the entire
  // image and everything after it falls off the canvas (the export looked
  // like "only the cover came out"). Freeze viewport units to the reader's
  // real viewport instead. Skipped inside url(...) because the base64 of an
  // embedded image can contain digit+"vh" by pure chance and would corrupt.
  function pxify(css) {
    var VH = innerHeight, VW = innerWidth;
    var RE = /(-?\d*\.?\d+)(dvh|svh|lvh|vh|dvw|svw|lvw|vw|vmin|vmax)(?![\w-])/g;
    // url() may be upper-case or carry a quoted payload with a literal ")"
    var URL_RE = /(url\((?:"[^"]*"|'[^']*'|[^)]*)\))/gi;
    return css.split(URL_RE).map(function (part, i) {
      if (i % 2) return part;                       // odd slots are url(...)
      return part.replace(RE, function (m, n, unit, off, str) {
        // no left boundary in RE (lookbehind would be a SyntaxError on
        // older Safari) — reject by hand when the match is the tail of an
        // identifier such as --pad-2vw or .h100vh
        if (off > 0 && /[\w-]/.test(str.charAt(off - 1))) return m;
        var base = unit === 'vmin' ? Math.min(VW, VH)
                 : unit === 'vmax' ? Math.max(VW, VH)
                 : unit.charAt(unit.length - 1) === 'h' ? VH : VW;
        return (parseFloat(n) * base / 100).toFixed(2) + 'px';
      });
    }).join('');
  }
  // The body's own rules never match inside the capture (there is no body
  // element in it), so the wrap has to restate what descendants inherit.
  // font-size is exact as computed px. line-height is NOT: computed style
  // hands back the used px value even when the author wrote a unitless
  // ratio, and a baked "25.2px" then applies to every smaller-font line in
  // the clone, growing it past the measured height and cropping the bottom.
  // So take the authored value from the CSSOM when there is one.
  function authoredLineHeight() {
    var v = '';
    function walk(rules) {
      Array.prototype.forEach.call(rules, function (r) {
        if (r.cssRules) {                          // @media / @supports …
          if (r.media && !matchMedia(r.media.mediaText).matches) return;
          walk(r.cssRules); return;
        }
        if (!r.style || !r.selectorText || !r.style.lineHeight) return;
        try { if (document.body.matches(r.selectorText)) v = r.style.lineHeight; }
        catch (e) {}
      });
    }
    try {
      Array.prototype.forEach.call(document.styleSheets, function (sh) {
        try { walk(sh.cssRules); } catch (e) {}
      });
    } catch (e) {}
    return v;
  }
  function bodyWrapCss() {
    var c = getComputedStyle(document.body);
    return '.__xbody{font-family:' + c.fontFamily +
      ';font-size:' + c.fontSize +
      ';color:' + c.color +
      ';line-height:' + (authoredLineHeight() || c.lineHeight) +
      ';background:' + BG + ';margin:0}';
  }
  // Symbols referenced by <use href="#id"> live in the page-top sprite,
  // which is not part of the clone; copy the ones actually used into the
  // capture so icons and particles render instead of exporting blank.
  function spriteFor(clone) {
    var ids = {}, XL = 'http://www.w3.org/1999/xlink';
    Array.prototype.forEach.call(clone.querySelectorAll('use'), function (u) {
      var h = u.getAttribute('href') || u.getAttributeNS(XL, 'href');
      if (h && h.charAt(0) === '#') ids[h.slice(1)] = 1;
    });
    var keys = Object.keys(ids);
    if (!keys.length) return null;
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('style', 'position:absolute;width:0;height:0;overflow:hidden');
    var n = 0;
    keys.forEach(function (k) {
      var s = document.getElementById(k);
      if (s) { svg.appendChild(s.cloneNode(true)); n++; }
    });
    return n ? svg : null;
  }
  function snap(el, label, whole) {
    var r = el.getBoundingClientRect();
    var w = Math.ceil(r.width), h = Math.ceil(el.scrollHeight || r.height);
    // a hidden or collapsed target would give a 0px canvas → null blob →
    // a misleading "too big" toast; say what actually happened
    if (!w || !h) { toast('这一块现在不可见,先滚到它再试'); return; }
    var clone = el.cloneNode(true);
    Array.prototype.forEach.call(clone.querySelectorAll('.no-export'),
      function (n) { n.remove(); });
    var holder = document.createElement('div');
    holder.className = '__xbody';
    holder.style.width = w + 'px';
    var sprite = spriteFor(clone);
    if (sprite) holder.appendChild(sprite);
    holder.appendChild(clone);
    var css = styleText();__MEASURE__
    var xml = new XMLSerializer().serializeToString(holder);
    function svgAt(hh) {
      return '<svg xmlns="http://www.w3.org/2000/svg" width="' + w +
        '" height="' + hh + '"><foreignObject width="100%" height="100%">' +
        '<div xmlns="http://www.w3.org/1999/xhtml"><style>' + css +
        '</style>' + xml + '</div></foreignObject></svg>';
    }
    // The SVG image can lay this same markup out TALLER than the live page
    // (font fallback / line wrapping differ inside an SVG image: measured
    // +5-7% overall on CJK-prose whole pages, up to +40% inside dense note
    // sections), and a foreignObject clips silently at the height attribute
    // — that is how zine/splash whole-page exports lost their decisions /
    // colophon / end-card tail while every bottom-anchored probe kept
    // showing plausible prose (2026-09-01). The live h is a floor, not the
    // truth. So: rasterise once with 35% headroom, find the lowest inked
    // row on a 64px-wide thumbnail (vs the BG fill; the tolerance eats
    // antialiasing), then raster the real canvas at that height. Ink clear
    // of the h floor takes the pre-fix code path — same-run output is
    // byte-identical to the unfixed engine (rasterisation itself jitters
    // across runs); ink at or past the floor grows the canvas instead of
    // vanishing. measure_clone cannot see this: it measures HTML layout,
    // and the growth only exists inside the SVG.
    var pad = Math.max(1200, Math.ceil(h * 0.35));
    function inkBottom(im, hh) {
      var pw = 64, ph = Math.max(1, Math.round(hh * pw / w));
      var bc = document.createElement('canvas'); bc.width = bc.height = 1;
      var bx = bc.getContext('2d'); bx.fillStyle = BG; bx.fillRect(0, 0, 1, 1);
      var bp = bx.getImageData(0, 0, 1, 1).data;
      var pc = document.createElement('canvas'); pc.width = pw; pc.height = ph;
      var px = pc.getContext('2d');
      px.fillStyle = BG; px.fillRect(0, 0, pw, ph);
      px.drawImage(im, 0, 0, pw, ph);
      var d = px.getImageData(0, 0, pw, ph).data;
      // summed-RGB threshold below eats antialiasing, but ink covering
      // ≲4% of a ~19px probe cell can read as background — a theme whose
      // tail ends in a lone tiny or near-invisible mark stays clipped;
      // keep real tails inked (see the tail bar in references/themes.md)
      for (var y = ph - 1; y >= 0; y--)
        for (var x = 0; x < pw; x++) {
          var i = (y * pw + x) * 4;
          if (Math.abs(d[i] - bp[0]) + Math.abs(d[i + 1] - bp[1]) +
              Math.abs(d[i + 2] - bp[2]) > 24)
            return Math.ceil((y + 1) * (hh / ph));
        }
      return 0;
    }
    var img = new Image();
    img.onload = function () {
      var bottom = 0;
      // a probe failure must never kill the export — fall back to live h
      try { bottom = inkBottom(img, h + pad); } catch (e) {}
      // Grow ONLY when ink actually reaches the h floor (the probe's
      // ~w/64-px row quantisation only ever rounds the detected bottom
      // DOWN the page, so growth can also trigger for ink ending within
      // ~a probe row + 8px of h — extra paper, never a clip): a page
      // whose ink stops clear of that band fits as-is and takes the
      // pre-fix code path. When it does grow, +140px keeps a little
      // paper under the text.
      var fh = bottom > h - 8 ? Math.min(h + pad, bottom + 140) : h;
      // Scale: 2x keeps a module crisp; a whole-page capture is thousands
      // of px tall, so the caps below decide instead. 30000 stays inside
      // Chrome's 32767-per-side ceiling and keeps a long page readable (a
      // tighter cap shrinks the width until the body text turns to mush).
      // Area budget: a module can afford a crisp 2x, but a whole-page
      // canvas of tens of millions of px makes toBlob hand back null on
      // real machines (46M px died here). Staying near 32M lands the first
      // attempt and keeps the long image ~1300px wide — wide enough to
      // read the body text.
      var budget = whole ? 3.2e7 : 2.6e8;
      var scale = Math.min(2, 2600 / w, 30000 / fh,
        Math.sqrt(budget / (w * fh)));
      if (scale < 0.2) { toast('这一块太大,换小一点的区块试试'); return; }
      // Format: a day module stays lossless PNG (2400×~2500 ≈ 6M px, a few
      // MB). Anything past 12M px — the whole page, or a long appendix
      // block (Zine's is 2400×11568 = 25 MB as PNG, unshareable) — goes
      // JPEG 0.92, same readable width at a tenth of the size. Day blocks
      // top out around 2400×4100 ≈ 10M px, so the threshold never touches
      // them.
      var jpeg = whole || (w * scale * fh * scale > 1.2e7);
      var img2 = new Image();
      function draw(sc, retried) {
        var c = document.createElement('canvas');
        c.width = Math.round(w * sc); c.height = Math.round(fh * sc);
        var ctx = c.getContext('2d');
        ctx.fillStyle = BG; ctx.fillRect(0, 0, c.width, c.height);
        ctx.drawImage(img2, 0, 0, c.width, c.height);
        try {
          c.toBlob(function (b) {
            // an over-budget canvas yields a null blob rather than throwing
            // — halve once and try again before giving up on the user
            if (!b) {
              if (!retried) { draw(sc / 2, true); return; }
              toast('生成失败:内容太大,试试单块保存'); return;
            }
            var a = document.createElement('a');
            a.href = URL.createObjectURL(b);
            a.download = __PREFIX__ + THEME + '-' + label +
              (jpeg ? '.jpg' : '.png');
            document.body.appendChild(a); a.click(); a.remove();
            setTimeout(function () { URL.revokeObjectURL(a.href); }, 4000);
            toast('已保存 · ' + label);
          }, jpeg ? 'image/jpeg' : 'image/png', jpeg ? 0.92 : undefined);
        } catch (e) {
          if (!retried) { draw(sc / 2, true); return; }
          toast('生成失败:' + e.message);
        }
      }
      img2.onload = function () { draw(scale, false); };
      img2.onerror = function () { toast('生成失败:浏览器不支持,换 Chrome 试试'); };
      img2.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgAt(fh));
    };
    img.onerror = function () { toast('生成失败:浏览器不支持,换 Chrome 试试'); };
    img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgAt(h + pad));
  }
  var tEl = null, tTimer = null;
  function toast(msg) {
    if (!tEl) {
      tEl = document.createElement('div');
      tEl.className = 'no-export';
      tEl.style.cssText = 'position:fixed;left:50%;bottom:34px;translate:-50% 0;' +
        'background:rgba(20,16,12,.88);color:#f5efe2;padding:9px 18px;' +
        'border-radius:99px;font-size:13px;z-index:999;letter-spacing:.08em;' +
        'pointer-events:none;opacity:0;transition:opacity .25s';
      document.body.appendChild(tEl);
    }
    tEl.textContent = msg; tEl.style.opacity = 1;
    clearTimeout(tTimer);
    tTimer = setTimeout(function () { tEl.style.opacity = 0; }, 2600);
  }
  addEventListener('click', function (ev) {
    var b = ev.target.closest && ev.target.closest('.xbtn');
    if (!b) return;
    ev.preventDefault();
    if (b.hasAttribute('data-x-page')) {
      // module-only themes ship PAGE_ROOT="" — querySelector('') throws
      if (!PAGE_ROOT) { toast('这一版只支持单块保存'); return; }
      var root = document.querySelector(PAGE_ROOT);
      if (root) { toast('长图生成中,几秒钟…'); setTimeout(function () { snap(root, '整页', true); }, 60); }
      return;
    }
    var sel = b.getAttribute('data-x-for');
    var el = sel ? document.querySelector(sel) : null;
    if (el) snap(el, b.getAttribute('data-x-label') ||
                 el.getAttribute('data-export') || '模块');
  }, false);
})();
"""
    if ui is None:
        ui = {k: T("toast." + k) for k in ("saved", "making_page", "failed", "too_big",
                                            "too_big_page", "hidden", "module_only", "no_browser")}
        ui["page"] = T("label.page")
        ui["module"] = T("label.module")
    # The JS is written with the zh literals; swap them for the current
    # language at build time (zh → identical bytes, so baselines hold).
    def _sq(t):
        return "'" + str(t).replace("\\", "\\\\").replace("'", "\\'").replace("</", "<\\/") + "'"
    for zh_lit, key in (("'这一块现在不可见,先滚到它再试'", "hidden"),
                        ("'这一块太大,换小一点的区块试试'", "too_big"),
                        ("'生成失败:内容太大,试试单块保存'", "too_big_page"),
                        ("'生成失败:浏览器不支持,换 Chrome 试试'", "no_browser"),
                        ("'这一版只支持单块保存'", "module_only"),
                        ("'长图生成中,几秒钟…'", "making_page"),
                        ("'整页'", "page"), ("'模块'", "module")):
        js = js.replace(zh_lit, _sq(ui[key]))
    js = js.replace("'已保存 · '", _sq(ui["saved"] + " · ")).replace("'生成失败:'", _sq(ui["failed"] + ":"))
    # measure_clone: JS spliced in only when asked for, so pages built without
    # it keep the engine text byte for byte (see the docstring)
    measure_js = r"""
    // size from the clone, not the live element: mount it off-screen with the
    // capture CSS for one layout pass, read its height, unmount. Same fonts,
    // same frozen viewport, minus the .no-export rows the live number counts.
    (function () {
      var mst = document.createElement('style'); mst.textContent = XCSS;
      holder.style.cssText = 'position:absolute;left:-100000px;top:0;width:' + w + 'px;visibility:hidden';
      document.head.appendChild(mst); document.body.appendChild(holder);
      var mh = Math.ceil(Math.max(holder.scrollHeight, holder.getBoundingClientRect().height));
      holder.remove(); mst.remove();
      holder.style.cssText = ''; holder.style.width = w + 'px';
      if (mh) h = mh;
    })();""" if measure_clone else ""
    js = js.replace("__MEASURE__", measure_js)
    if file_prefix is None:
        # every live renderer passes export_prefix(art, meta, theme); a caller
        # that does not gets a neutral prefix, never another trip's name
        file_prefix = "trip-"
    return (js.replace("__BG__", _js_str(page_bg))
              # single-quoted on purpose: that is how the literal was written
              # before it became a parameter, so unmigrated products stay
              # byte-identical
              .replace("__PREFIX__", "'" + file_prefix.replace("\\", "\\\\")
                       .replace("'", "\\'").replace("</", "<\\/") + "'")
              .replace("__THEME__", _js_str(str(theme).replace(" ", "-")))   # filename-safe
              .replace("__ROOT__", _js_str(page_root))
              .replace("__EXTRA__", _js_str(extra_css)))


def _js_str(s):
    """JSON string literal safe to embed in an inline <script>: json.dumps
    leaves "/" alone, so a "</script>" (or "<!--") inside extra_css would end
    the script tag mid-engine. Break every "</" the way browsers expect."""
    import json as _json
    return _json.dumps(s, ensure_ascii=False).replace("</", "<\\/")
