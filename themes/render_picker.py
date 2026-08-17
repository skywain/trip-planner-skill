#!/usr/bin/env python3
"""Picker — one page that makes the live themes comparable at a glance.

Not a screenshot gallery: each card carries a small SVG SCHEMATIC of that
theme's actual structure (where the art lives, where the reading column is,
which way it moves), its palette, and the four identity axes the family is
differentiated on. Screenshots would flatter; a schematic tells the truth
about layout, which is what you are actually choosing between.

Usage: python3 render_picker.py <plan.geo.json> [--art F|none] -o out.html
                                [--products DIR] [--prefix NAME]

The eight rendered pages are expected as {prefix}-{theme}.html in --products
(default: the output file's directory), where {theme} is the English theme
key — illustrated / clay / noir / glass / journal / zine / splash / portal,
the canonical trip-<theme>.html of SKILL.md Phase 6. The old Chinese tags
(插画版/黏土版/夜航版/玻璃版/手账版/Zine版/闪屏版/穿越版) are still picked up
when they are what is on disk; their sizes are read from there.
--prefix defaults to art cover.kick_en with spaces → "-" ("US 2026" →
"US-2026"), else "trip". Card titles come from art themes.<key>.cover.zh
(falling back to cover.zh); the page title from cover.kick + trip year
(en: cover.kick_en when set — theme_common.title_kick).

Language: plan.lang / meta.lang / --lang (theme_common.init_lang). The zh
card copy is inline in THEMES (byte-stable); the English copy lives in
THEMES_EN and the page voice in L. In en the card title prefers cover.en,
the English display name ({prefix}-Night Flight.html) joins the product
lookup as a further candidate, and the retired-editions footnote (US
history) is dropped.
"""
import argparse
import html
import pathlib
import re

from theme_common import (T, add_art_arg, init_lang, lang, load_art,
                          load_plan, theme_name, title_kick)

HERE = pathlib.Path(__file__).parent


def esc(s):
    return html.escape(str(s), quote=True)


def kb(products, name):
    p = products / name
    return f"{p.stat().st_size // 1024}KB" if p.exists() else "—"


# ---- page voice (shared UI words go through theme_common.T) ---------------
L = {
    "zh": {
        "trip": "旅程",
        "open": "打开", "open_this": "打开这一版 →", "schematic": "版式示意",
        "ax.principle": "组织原则", "ax.motion": "交互", "ax.voice": "字体声音",
        "ax.shape": "形状语言", "ax.art": "图像",
        "th.edition": "版本", "th.size": "体积", "caption": "一览",
        "lead_pre": "同一份行程数据 ", "lead_post": ",八种渲染。它们不是换皮:组织原则、交互方式、字体声音、形状语言四项各不相同。",
        "note1_pre": "缩略图是", "note1_b": "版式示意",
        "note1_post": "而非截图——示意图说的是结构(图在哪、读的那一列在哪、往哪个方向动),这才是你要挑的东西。点缩略图或按钮打开真页面。",
        "note2_pre": "除穿越版外,每一版都能", "note2_b": "存成图片分享",
        "note2_post": ":每天(或每章)末尾有「保存这一天」;手账、插画、黏土、Zine、闪屏五版还在导航或页首有「生成长图」把整份行程拼成一张长图(夜航、玻璃两版是层叠滚动结构,只出单块)。",
        "svg_text": {},
        "retired": "已放弃:时刻表版(2026-08-08,纯文本设计,与「后续版本必须带图片」的方向不符)、航图版(2026-08-15,视觉不过关)。文件保留:<code>{prefix}-时刻表版.html</code> / <code>{prefix}-航图版.html</code>。",
    },
    "en": {
        "trip": "Trip",
        "open": "Open ", "open_this": "Open this edition →", "schematic": " layout schematic",
        "ax.principle": "PRINCIPLE", "ax.motion": "MOTION", "ax.voice": "TYPE",
        "ax.shape": "SHAPE", "ax.art": "IMAGERY",
        "svg_text": {">星垂<": ">Stars<", ">拾<": ">ZI<", ">景<": ">NE<"},
        "th.edition": "EDITION", "th.size": "SIZE", "caption": "AT A GLANCE",
        "lead_pre": "One itinerary, ", "lead_post": ", rendered eight ways. They are not reskins: "
                    "organising principle, motion, type voice and shape language all differ.",
        "note1_pre": "Thumbnails are ", "note1_b": "layout schematics",
        "note1_post": ", not screenshots — a schematic tells you the structure (where the art sits, "
                      "where the reading column is, which way it moves), which is what you are "
                      "actually choosing between. Click a thumbnail or button to open the real page.",
        "note2_pre": "Every edition except Portal can be ", "note2_b": "saved as an image",
        "note2_post": ": each day (or chapter) ends with “Save this day”; Journal, Illustrated, Clay, "
                      "Zine and Splash also offer “Save long image” in the nav or page head to stitch "
                      "the whole trip into one tall image (Night Flight and Glass are layered scroll "
                      "structures and export single blocks only).",
        "retired": "",
    },
}


def t(k):
    return L.get(lang(), L["zh"]).get(k, L["zh"][k])


# English copies of each card's four axes + imagery line (zh lives inline in
# THEMES below and is byte-stable). Imagery here is described neutrally —
# medium, not this trip's picture count.
THEMES_EN = {
    "illustrated": {
        "name": "Illustrated",
        "principle": "A long paper scroll · one book",
        "motion": "Vertical scroll",
        "voice": "All serif, no monospace",
        "shape": "No pills: 〔bracket〕 notes, footnotes [n], printed rules",
        "art": "Hand-painted gouache plates",
    },
    "clay": {
        "name": "Clay",
        "principle": "One continuous clay landscape",
        "motion": "Vertical scroll + mini road navigation",
        "voice": "Rounded sans first",
        "shape": "Hand-pinched irregular corners (same curve as the milestone stones)",
        "art": "Clay-figure dioramas",
    },
    "noir": {
        "name": "Night Flight",
        "principle": "One take: a single plate for the whole page",
        "motion": "Vertical scroll; the plate only changes in transit bands",
        "voice": "Monospace body, serif for the big titles only",
        "shape": "No boxes: hairlines + letter-spaced labels",
        "art": "Night scenes, stacked on one stage",
    },
    "glass": {
        "name": "Glass",
        "principle": "A fixed image world with content floating over it",
        "motion": "Vertical scroll + cross-fading image layers",
        "voice": "Sans-serif first",
        "shape": "Pills (it is an app) + the focus ring is a pane of glass too",
        "art": "High-key aerial photography",
    },
    "journal": {
        "name": "Journal",
        "principle": "An open travel journal: one continuous sheet, real objects stuck on",
        "motion": "Vertical scroll + a dotted pen route, brass pins as anchors",
        "voice": "Handwritten margin notes + typewriter times",
        "shape": "Torn paper / tape / stubs / postmarks / wax seals, body slightly rotated",
        "art": "Vintage photographs + journal ephemera",
    },
    "zine": {
        "name": "Zine",
        "principle": "Real scenes as anchors: photos pinned at the corners, saturated colour blocks carry the structure, paper breathes",
        "motion": "Vertical scroll + torn ticket index down the left edge",
        "voice": "Structured sans, big vertical type + riso two-colour misregistration",
        "shape": "Torn edges + colour blocks; anti-card, anti-rounded",
        "art": "Film photographs + single-line drawings",
    },
    "splash": {
        "name": "Splash",
        "principle": "A game splash poster stretched into a scroll: an abstract light field all the way down",
        "motion": "Vertical scroll + glowing ribbon road + fixed-seed particles",
        "voice": "Impasto title art + rounded 900, brush-stroke big numerals",
        "shape": "Big silhouettes + slanted badges, no white cards",
        "art": "Impasto illustrations (hero cluster + floating-island day nodes)",
    },
    "portal": {
        "name": "Portal",
        "principle": "Video: scrolling is flying, floating worlds in one take",
        "motion": "Vertical scroll = flight progress; let go to hold, scroll back to fly in reverse (the family's only video edition)",
        "voice": "Big sans titles + letter-spaced notes, times in amber monospace",
        "shape": "No cards: captions float straight on the footage (shadow-backed), the sky turns with the itinerary",
        "art": "AI video clips (the video directory travels with the page)",
    },
}


def field(th, k):
    """Card text in the current language (zh inline, en from THEMES_EN)."""
    if lang() == "zh":
        return th[k]
    return THEMES_EN.get(th["id"], {}).get(k, th[k])


def schematic(th):
    """The card's SVG; the stand-in glyphs inside it (a mock title, a
    vertical two-character heading) get Latin stand-ins in en."""
    svg = th["svg"]
    for a, b in t("svg_text").items():
        svg = svg.replace(a, b)
    return svg


def display_name(th):
    return th["zh"] if lang() == "zh" else THEMES_EN.get(th["id"], {}).get("name", theme_name(th["id"]))


# ---- the eight, each with a schematic drawn from its real structure -------
# schematic grammar: 200x125 box; fills = art, rules = text, arrow = motion
THEMES = [
    {
        "id": "illustrated", "tag": "插画版",
        "zh": "插画版", "en": "A BOOK",
        "principle": "纸上长卷 · 一本书",
        "motion": "纵向滚动",
        "voice": "全衬线,零等宽",
        "shape": "零胶囊:〔方括号〕注记、脚注 [n]、印刷横线",
        "art": "水粉手绘 12 张",
        "pal": ["#f6efe3", "#A6472A", "#3F6E67", "#efe4cf"],
        "svg": """<rect x="0" y="0" width="200" height="46" fill="#e8dcc6"/>
<path d="M0 30 Q40 18 80 30 T160 26 T200 34 V46 H0Z" fill="#cfc0a4"/>
<rect x="66" y="14" width="68" height="9" rx="1" fill="#A6472A"/>
<g fill="#bcae94"><rect x="10" y="52" width="46" height="4"/><rect x="10" y="60" width="30" height="3"/></g>
<g fill="#8d8474"><rect x="66" y="52" width="124" height="2.5"/><rect x="66" y="60" width="118" height="2.5"/>
<rect x="66" y="68" width="124" height="2.5"/><rect x="66" y="76" width="104" height="2.5"/>
<rect x="66" y="84" width="124" height="2.5"/><rect x="66" y="92" width="92" height="2.5"/>
<rect x="66" y="100" width="124" height="2.5"/><rect x="66" y="108" width="70" height="2.5"/></g>
<g fill="#A6472A"><rect x="10" y="52" width="3" height="4"/></g>""",
    },
    {
        "id": "clay", "tag": "黏土版",
        "zh": "黏土版", "en": "ONE WORLD",
        "principle": "一整块连续的黏土大地",
        "motion": "纵向滚动 + 迷你路导航",
        "voice": "圆体为主",
        "shape": "手捏不规则圆角(和里程碑石头同一条曲线)",
        "art": "黏土手办 17 张",
        "pal": ["#dcefe6", "#cfe8c9", "#f0c9a0", "#C43D28"],
        "svg": """<defs><linearGradient id="cg" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#f6e2e0"/><stop offset=".34" stop-color="#cfe8c9"/>
<stop offset=".7" stop-color="#f0c9a0"/><stop offset="1" stop-color="#7fc9c6"/></linearGradient></defs>
<rect width="200" height="125" fill="url(#cg)"/>
<path d="M52 6 C110 30 40 52 96 74 C150 94 70 108 108 124" stroke="#f0e2c4" stroke-width="11"
 fill="none" stroke-linecap="round"/>
<path d="M52 6 C110 30 40 52 96 74 C150 94 70 108 108 124" stroke="#fff" stroke-width="1.6"
 fill="none" stroke-dasharray="5 6"/>
<g fill="#f2b28c" stroke="rgba(74,68,88,.25)"><circle cx="72" cy="30" r="7"/><circle cx="70" cy="66" r="7"/>
<circle cx="118" cy="98" r="7"/></g>
<g fill="rgba(255,253,247,.82)"><rect x="108" y="18" width="82" height="26" rx="13"/>
<rect x="14" y="54" width="76" height="24" rx="12"/><rect x="112" y="86" width="76" height="24" rx="12"/></g>""",
    },
    {
        "id": "noir", "tag": "夜航版",
        "zh": "夜航版", "en": "ONE TAKE",
        "principle": "一镜到底:整页只有一块底片",
        "motion": "纵向滚动,换片只发生在过场带",
        "voice": "等宽当正文,衬线只留巨题",
        "shape": "零方框:发丝线 + 字距标签",
        "art": "夜景 7 张(叠在同一个舞台)",
        "pal": ["#0b0d12", "#E9A94F", "#b2b8c3", "#1b2430"],
        "svg": """<rect width="200" height="125" fill="#0b0d12"/>
<rect width="200" height="125" fill="#16202e"/>
<ellipse cx="34" cy="112" rx="86" ry="42" fill="#E9A94F" opacity=".22"/>
<ellipse cx="150" cy="30" rx="70" ry="30" fill="#2b3b52" opacity=".7"/>
<text x="12" y="52" font-family="Georgia,serif" font-size="26" fill="#fff" opacity=".55">星垂</text>
<g fill="#ece7dd" opacity=".82"><rect x="12" y="66" width="24" height="2"/><rect x="46" y="66" width="142" height="2"/>
<rect x="12" y="78" width="24" height="2"/><rect x="46" y="78" width="120" height="2"/>
<rect x="12" y="90" width="24" height="2"/><rect x="46" y="90" width="142" height="2"/></g>
<g fill="#E9A94F"><rect x="12" y="66" width="24" height="2"/><rect x="12" y="78" width="24" height="2"/>
<rect x="12" y="90" width="24" height="2"/></g>
<g stroke="#5b6470"><line x1="12" y1="106" x2="72" y2="106"/><line x1="128" y1="106" x2="188" y2="106"/></g>
<text x="84" y="109" font-family="monospace" font-size="7" fill="#9aa0ab">HOP</text>""",
    },
    {
        "id": "glass", "tag": "玻璃版",
        "zh": "玻璃版", "en": "LIQUID GLASS",
        "principle": "固定影像世界,内容浮在其上",
        "motion": "纵向滚动 + 影像层交叉淡入",
        "voice": "无衬线为主",
        "shape": "胶囊(它是 App)+ 焦点也是一片玻璃",
        "art": "高调航拍 6 张",
        "pal": ["#eef2f4", "#ffffff", "#15171a", "#9fc8d8"],
        "svg": """<defs><linearGradient id="gg" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#cfe6f0"/><stop offset=".55" stop-color="#eaf2f5"/>
<stop offset="1" stop-color="#bcd8c9"/></linearGradient></defs>
<rect width="200" height="125" fill="url(#gg)"/>
<rect width="200" height="125" fill="#fff" opacity=".55"/>
<g fill="#15171a" opacity=".5"><rect x="10" y="14" width="4" height="4"/><rect x="18" y="14" width="26" height="4"/>
<rect x="10" y="26" width="4" height="4"/><rect x="18" y="26" width="20" height="4"/>
<rect x="10" y="38" width="4" height="4"/><rect x="18" y="38" width="24" height="4"/></g>
<rect x="58" y="10" width="132" height="40" rx="14" fill="#fff" opacity=".72" stroke="#fff"/>
<rect x="58" y="58" width="132" height="56" rx="14" fill="#fff" opacity=".62" stroke="#fff"/>
<g fill="#15171a" opacity=".45"><rect x="70" y="70" width="20" height="2.5"/><rect x="98" y="70" width="80" height="2.5"/>
<rect x="70" y="82" width="20" height="2.5"/><rect x="98" y="82" width="66" height="2.5"/>
<rect x="70" y="94" width="20" height="2.5"/><rect x="98" y="94" width="80" height="2.5"/></g>""",
    },
    {
        "id": "journal", "tag": "手账版",
        "zh": "手账拼贴版", "en": "A JOURNAL",
        "principle": "一本摊开的旅行手账:整页连续纸面,实物是贴上去的",
        "motion": "纵向滚动 + 钢笔虚线路线,黄铜图钉 01-11 锚点",
        "voice": "楷体手写批注 + 打字机时刻",
        "shape": "撕纸 / 胶带 / 票根 / 邮戳 / 火漆,正文微旋转",
        "art": "复古照片 12 张 + 手账小物 13 件",
        "pal": ["#f0e6cf", "#c94f43", "#3d5a72", "#b58f3f"],
        "svg": """<rect width="200" height="125" fill="#f0e6cf"/>
<rect x="14" y="16" width="86" height="62" fill="#f7efdd" stroke="#c94f43" stroke-width="1.5" stroke-dasharray="6 3"/>
<rect x="24" y="30" width="48" height="10" rx="1" fill="#8a6d3b"/>
<rect x="24" y="48" width="34" height="4" fill="#b5a284"/>
<rect x="24" y="58" width="52" height="3" fill="#cbbb9c"/>
<rect x="118" y="16" width="54" height="48" fill="#fffdf4" stroke="#d9cdb2"/>
<rect x="124" y="22" width="42" height="28" fill="#c9b394"/>
<rect x="132" y="10" width="26" height="9" fill="#d9b96a" opacity=".85" transform="rotate(-8 145 14)"/>
<circle cx="185" cy="24" r="9" fill="none" stroke="#a05c50" stroke-width="1.4" stroke-dasharray="2.5 2"/>
<path d="M22 92 C56 82 92 102 126 90 S 176 96 190 92" stroke="#5a4632" stroke-width="1.5" fill="none" stroke-dasharray="4 4"/>
<g fill="#b58f3f" stroke="#8a6d3b" stroke-width="1"><circle cx="22" cy="92" r="6"/><circle cx="104" cy="95" r="6"/><circle cx="190" cy="92" r="6"/></g>
<path d="M12 108 h40 l-3 6 h-37Z" fill="#e9ddc2"/>""",
    },
    {
        "id": "zine", "tag": "Zine版",
        "zh": "Zine 拼贴版", "en": "A ZINE",
        "principle": "真景为锚:照片压角,高饱和纯色块承担结构,纸面呼吸",
        "motion": "纵向滚动 + 左缘撕纸小票索引 01-11",
        "voice": "结构化无衬线,竖排大字 + riso 双色错位",
        "shape": "撕纸边 + 色块,反卡片反圆角",
        "art": "胶片照片 4 张 + 单线插画 7 幅",
        "pal": ["#2036B1", "#EB4B32", "#E3B004", "#F2EAD8"],
        "svg": """<rect width="200" height="125" fill="#2036B1"/>
<rect x="10" y="8" width="54" height="66" fill="#b9b4a6"/>
<path d="M10 74 l8 -3 9 4 8 -4 9 4 8 -3 8 4 4 -2 v6 h-54Z" fill="#d8d3c5"/>
<text x="184" y="34" font-family="system-ui,sans-serif" font-size="26" font-weight="800" fill="#F2EAD8" text-anchor="end">拾</text>
<text x="184" y="62" font-family="system-ui,sans-serif" font-size="26" font-weight="800" fill="#F2EAD8" text-anchor="end">景</text>
<path d="M0 86 l12 -3 14 4 12 -4 14 4 13 -3 14 4 13 -4 14 4 13 -3 14 4 13 -4 14 4 12 -3 14 3 V125 H0Z" fill="#F2EAD8"/>
<text x="12" y="116" font-family="system-ui,sans-serif" font-size="22" font-weight="800" fill="#C22C15">05</text>
<g fill="#3a342c"><rect x="46" y="100" width="60" height="2.5"/><rect x="46" y="108" width="48" height="2.5"/><rect x="46" y="116" width="56" height="2.5"/></g>
<rect x="132" y="96" width="58" height="29" fill="#E3B004"/>
<circle cx="161" cy="110" r="8" fill="none" stroke="#C22C15" stroke-width="1.6"/>""",
    },
    {
        "id": "splash", "tag": "闪屏版",
        "zh": "闪屏版", "en": "SPLASH ART",
        "principle": "一张游戏闪屏海报延展成卷轴:抽象光场连续到底",
        "motion": "纵向滚动 + 发光缎带路 + 固定种子粒子",
        "voice": "厚涂标题图 + 圆体 900,画笔感大数字",
        "shape": "大轮廓剪影 + 斜切徽章,零白卡",
        "art": "厚涂插画 10 张(hero 集群/标题 + 8 天浮岛节点)",
        "pal": ["#7a2fd0", "#FFEFC9", "#8fd8c8", "#ff9c4a"],
        "svg": """<defs><linearGradient id="spg" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#8a3ae0"/><stop offset="1" stop-color="#451c86"/></linearGradient></defs>
<rect width="200" height="125" fill="url(#spg)"/>
<path d="M-10 30 L210 6" stroke="#a765ec" stroke-width="10" opacity=".35"/>
<path d="M26 125 C76 98 40 62 96 46 C152 30 122 14 176 6" stroke="#ff8de0" stroke-width="5" fill="none" opacity=".9"/>
<ellipse cx="56" cy="44" rx="24" ry="30" fill="#8fd8c8"/>
<circle cx="88" cy="30" r="9" fill="#ffd77a"/>
<rect x="120" y="76" width="28" height="17" rx="7" fill="#ff9c4a"/>
<rect x="26" y="10" width="60" height="16" rx="3" fill="#FFEFC9"/>
<g fill="#ff9cc7"><circle cx="150" cy="40" r="3"/><circle cx="170" cy="98" r="3"/><circle cx="106" cy="102" r="2.5"/></g>
<g fill="#8fe0ff"><path d="M160 60 l5 8 h-10Z"/><path d="M44 96 l4 7 h-8Z"/></g>""",
    },
    # 时刻表版(board)2026-08-08 放弃:纯文本无图,与「后续版本必须带图片」的方向不符。
    # 文件与 render_board.py 保留在盘上,只从选型页下架。
    # 航图版(chart)2026-08-15 放弃:owner「不好看」。render_chart.py 与产物同样留盘、下架。
    {
        "id": "portal", "tag": "穿越版",
        "zh": "穿越版", "en": "ONE FLIGHT",
        "principle": "视频态:滚动即飞行,十个悬浮小世界一镜到底",
        "motion": "纵向滚动 = 飞行进度,松手即停,倒滚倒飞(全家唯一视频态)",
        "voice": "无衬线巨题 + 字距拉开的注记,时刻走琥珀等宽",
        "shape": "零卡片:字幕直接浮在画面上(阴影托底),天色随行程昼夜流转",
        "art": "AI 视频 19 条 35MB(需 assets/portal 视频素材同行)",
        "pal": ["#0d0b14", "#ffd98a", "#c9bfe0", "#7fc9a8"],
        "svg": """<defs><linearGradient id="ptg" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#3d2050"/><stop offset=".52" stop-color="#0d0b14"/>
<stop offset="1" stop-color="#3a1f38"/></linearGradient></defs>
<rect width="200" height="125" fill="url(#ptg)"/>
<g opacity=".4"><ellipse cx="38" cy="20" rx="16" ry="5" fill="#5e4a86"/>
<path d="M27 22 L38 36 L49 22Z" fill="#453064"/></g>
<path d="M50 26 C68 34 78 42 90 52" stroke="#c9bfe0" stroke-width="1.2" stroke-dasharray="3 3.5" fill="none" opacity=".55"/>
<g stroke="#9f8fd0" stroke-width="1" opacity=".5">
<line x1="6" y1="4" x2="72" y2="44"/><line x1="188" y1="2" x2="130" y2="42"/>
<line x1="2" y1="98" x2="66" y2="72"/><line x1="182" y1="116" x2="132" y2="80"/></g>
<g stroke="#ffd98a" stroke-width="1.5" fill="none" opacity=".85">
<path d="M60 36 h-9 v9"/><path d="M140 36 h9 v9"/>
<path d="M60 90 h-9 v-9"/><path d="M140 90 h9 v-9"/></g>
<path d="M72 64 C80 84 92 90 100 104 C108 90 120 84 128 64Z" fill="#443061"/>
<ellipse cx="100" cy="63" rx="30" ry="9" fill="#7fc9a8"/>
<g fill="#f2e2c4"><rect x="87" y="49" width="9" height="15" rx="1"/>
<rect x="100" y="43" width="7" height="21" rx="1"/><rect x="111" y="52" width="8" height="12" rx="1"/></g>
<circle cx="103" cy="38" r="2.6" fill="#ffd98a"/>
<ellipse cx="54" cy="106" rx="34" ry="8" fill="#c9bfe0" opacity=".18"/>
<ellipse cx="158" cy="16" rx="26" ry="6" fill="#c9bfe0" opacity=".14"/>
<g><rect x="12" y="97" width="18" height="2.5" fill="#ffd98a"/>
<rect x="12" y="104" width="46" height="4.5" fill="#e8e0f5"/>
<rect x="12" y="113" width="34" height="2.5" fill="#c9bfe0" opacity=".8"/></g>
<text x="186" y="13" font-family="monospace" font-size="7" fill="#9f8fd0" text-anchor="end">CLIP 7/19</text>
<rect x="191" y="18" width="4" height="101" rx="2" fill="#2a2140"/>
<rect x="191" y="44" width="4" height="24" rx="2" fill="#ffd98a"/>
<path d="M190 73 l3 4.5 3 -4.5" stroke="#ffd98a" stroke-width="1.4" fill="none" opacity=".8"/>""",
    },
]


def card(th, art, products):
    lk, ok = (("zh", "en") if lang() == "zh" else ("en", "zh"))
    title = (art.cover(th["id"], lk) or art.cover(th["id"], ok)) if art else ""
    name = display_name(th)
    pal = "".join(f'<i style="background:{c}"></i>' for c in th["pal"])
    rows = "".join(
        f'<div class="r"><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>'
        for k, v in ((t("ax.principle"), field(th, "principle")), (t("ax.motion"), field(th, "motion")),
                     (t("ax.voice"), field(th, "voice")), (t("ax.shape"), field(th, "shape")),
                     (t("ax.art"), field(th, "art"))))
    return f"""
<article class="card" id="{th['id']}">
  <a class="thumb" href="{esc(th['file'])}" aria-label="{t('open')}{esc(name)}">
    <svg viewBox="0 0 200 125" role="img" aria-label="{esc(name)}{t('schematic')}">{schematic(th)}</svg>
  </a>
  <div class="meta">
    <header>
      <h2>{esc(name)}<span class="en">{esc(th['en'])}</span></h2>
      <p class="ttl">{esc(title)}</p>
    </header>
    <div class="pal">{pal}<span class="size">{kb(products, th['file'])}</span></div>
    <dl>{rows}</dl>
    <a class="open" href="{esc(th['file'])}">{t('open_this')}</a>
  </div>
</article>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan", help="plan.geo.json (the trip the pages were rendered from)")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--products", type=pathlib.Path, default=None, metavar="DIR",
                    help="where the rendered pages live (default: the output's dir)")
    ap.add_argument("--prefix", default=None,
                    help='page filename prefix (default: cover.kick_en, spaces → "-")')
    add_art_arg(ap)
    args = ap.parse_args()
    plan = load_plan(args.plan)
    init_lang(args, plan)
    art = load_art(args.plan, args.art, args.assets)
    meta = plan.get("meta", {})
    out = pathlib.Path(args.out)
    products = args.products or out.parent
    prefix = args.prefix or (art.cover(None, "kick_en") or "").replace(" ", "-") or "trip"
    m = re.search(r"\d{4}", meta.get("dates", "") or "")
    year = m.group(0) if m else ""
    kick = title_kick(art) or t("trip")      # kick_en on an en page (theme_common)
    if year and year in kick:
        year = ""
    page_title = " ".join(x for x in (kick, year) if x) + " · " + theme_name("picker")
    plan_name = pathlib.Path(args.plan).name
    for th in THEMES:
        # products are named {prefix}-{theme}.html. Canonical is the English
        # theme key (trip-illustrated.html, SKILL.md Phase 6); pages exported
        # before that used the zh tag ({prefix}-插画版) and en trips
        # sometimes the English display name. Take whichever is on disk, and
        # fall back to the canonical name when none of them is.
        cands = [f"{prefix}-{th['id']}.html", f"{prefix}-{th['tag']}.html"]
        if lang() != "zh":
            cands.insert(1, f"{prefix}-{theme_name(th['id'])}.html")
        th["file"] = next((c for c in cands if (products / c).exists()), cands[0])
    cards = "".join(card(th, art, products) for th in THEMES)
    table = "".join(
        f'<tr><th scope="row">{esc(display_name(th))}</th><td>{esc(field(th, "principle"))}</td>'
        f'<td>{esc(field(th, "motion"))}</td><td>{esc(field(th, "voice"))}</td>'
        f'<td class="n">{kb(products, th["file"])}</td></tr>' for th in THEMES)
    retired = t("retired").replace("{prefix}", esc(prefix))
    retired_html = f'\n  <p class="note" style="margin:0 0 60px">{retired}</p>' if retired else ""

    html_out = f"""<!doctype html>
<html lang="{T("html_lang")}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(page_title)}</title>
<style>
  :root {{ --ink:#1b1c20; --dim:#6b6f76; --line:#e3e2de; --bg:#fbfaf8; --hi:#1b1c20; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:var(--bg); color:var(--ink); line-height:1.6;
    font-family:system-ui,-apple-system,"PingFang SC","Helvetica Neue",sans-serif; }}
  a {{ color:inherit; }}
  :focus-visible {{ outline:2.5px solid var(--hi); outline-offset:3px; }}
  .wrap {{ max-width:1120px; margin:0 auto; padding:0 clamp(16px,4vw,40px); }}
  header.top {{ padding:56px 0 12px; }}
  header.top h1 {{ font-size:clamp(26px,4vw,40px); letter-spacing:.06em; font-weight:700; }}
  header.top p {{ color:var(--dim); font-size:14px; margin-top:10px; max-width:44em; }}
  .note {{ margin-top:14px; font-size:12.5px; color:var(--dim);
    border-left:3px solid var(--line); padding-left:12px; }}

  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(min(100%,430px),1fr));
    gap:26px; padding:30px 0 10px; }}
  .card {{ border:1px solid var(--line); background:#fff; display:flex;
    flex-direction:column; overflow:hidden; }}
  .thumb {{ display:block; border-bottom:1px solid var(--line); }}
  .thumb svg {{ display:block; width:100%; height:auto; }}
  .meta {{ padding:18px 20px 20px; display:flex; flex-direction:column; gap:12px; flex:1; }}
  .meta h2 {{ font-size:19px; letter-spacing:.04em; }}
  .en {{ font-size:9.5px; letter-spacing:.28em; color:var(--dim); margin-left:10px;
    font-family:ui-monospace,Menlo,monospace; }}
  .ttl {{ font-size:13px; color:var(--dim); margin-top:2px; }}
  .pal {{ display:flex; align-items:center; gap:5px; }}
  .pal i {{ width:20px; height:20px; border:1px solid rgba(0,0,0,.08); }}
  .size {{ margin-left:auto; font:10px/1 ui-monospace,Menlo,monospace; color:var(--dim);
    letter-spacing:.1em; }}
  dl {{ display:flex; flex-direction:column; gap:7px; }}
  .r {{ display:grid; grid-template-columns:66px minmax(0,1fr); gap:10px;
    font-size:12.5px; align-items:baseline; }}
  dt {{ color:var(--dim); font-size:10px; letter-spacing:.16em; }}
  dd {{ overflow-wrap:anywhere; }}
  .open {{ margin-top:auto; align-self:flex-start; text-decoration:none;
    border:1.5px solid var(--ink); padding:10px 16px; font-size:12.5px;
    letter-spacing:.06em; min-height:44px; display:inline-flex; align-items:center; }}
  .open:hover {{ background:var(--ink); color:#fff; }}

  table {{ width:100%; border-collapse:collapse; margin:34px 0 70px; font-size:13px; }}
  caption {{ text-align:left; font-size:11px; letter-spacing:.24em; color:var(--dim);
    padding-bottom:10px; }}
  th, td {{ text-align:left; padding:11px 12px 11px 0; border-bottom:1px solid var(--line);
    vertical-align:top; }}
  thead th {{ font-size:10px; letter-spacing:.16em; color:var(--dim);
    border-bottom:2px solid var(--ink); }}
  tbody th {{ white-space:nowrap; font-weight:700; }}
  td.n {{ font:11px/1.6 ui-monospace,Menlo,monospace; color:var(--dim); white-space:nowrap; }}
  @media (max-width:640px) {{
    table, thead, tbody, tr, th, td {{ display:block; }}
    thead {{ display:none; }}
    tbody tr {{ border-bottom:1px solid var(--line); padding:10px 0; }}
    th, td {{ border:0; padding:2px 0; }}
    tbody th {{ font-size:15px; }}
  }}
  @media print {{ .open {{ display:none; }} .card {{ break-inside:avoid; }} }}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <h1>{esc(page_title)}</h1>
    <p>{t("lead_pre")}<code>{esc(plan_name)}</code>{t("lead_post")}</p>
    <p class="note">{t("note1_pre")}<strong>{t("note1_b")}</strong>{t("note1_post")}</p>
    <p class="note">{t("note2_pre")}<strong>{t("note2_b")}</strong>{t("note2_post")}</p>
  </header>

  <div class="grid">{cards}</div>

  <table>
    <caption>{t("caption")}</caption>
    <thead><tr><th>{t("th.edition")}</th><th>{t("ax.principle")}</th><th>{t("ax.motion")}</th><th>{t("ax.voice")}</th><th>{t("th.size")}</th></tr></thead>
    <tbody>{table}</tbody>
  </table>
{retired_html}
</div>
</body>
</html>"""
    out = pathlib.Path(args.out)
    out.write_text(html_out, encoding="utf-8")
    print(f"{out.name}: {out.stat().st_size // 1024}KB, themes={len(THEMES)}")


if __name__ == "__main__":
    main()
