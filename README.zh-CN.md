[English](README.md) | [简体中文](README.zh-CN.md)

# Trip Planner Skill · 旅行规划 skill

*`skywain/trip-planner-skill`*

**逐小时、经过核实、可直接照着订的行程规划 —— 一个 Claude Code skill。** 你用一句话
描述这趟旅行;拿回一份能一条链接一条链接订下去的计划,外加一份离线地图,以及(如果你
想要)同一份计划在八种视觉主题里任选一种的设计版。

<p align="center">
  <img src="docs/showcase/hero-grid.webp" alt="九趟测试行程经主题渲染器生成的封面:noir、journal、illustrated、splash、glass、journal、glass、clay、zine" width="720">
</p>

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-3776AB.svg)
![Claude Code skill](https://img.shields.io/badge/Claude%20Code-skill-8A63D2.svg)

## 你会得到什么

说一句 *「日本,10 月去 12–15 天,中等预算,历史 + 美食。」* 这个 skill 会给你:

- **一条跨城路线**,先给 2–3 套骨架让你挑,再给一个日期网格的真实机票价格,以及每一段
  城际交通的火车 vs 飞机结论。
- **每一天的逐小时安排** —— 营业时间和闭馆日都用工具查过,停留时长和缓冲来自一套写下来的
  排程方法,附带节假日与节庆撞车扫描,每一跳都有可点开的地图链接。
- **`plan.geo.json`**,唯一真源,渲染成一份**朴素的自包含 HTML**(离线、可打印、手机友好),
  以及一份给 Google Earth / Organic Maps 用的**离线 KML**。
- **按片区给出的酒店候选清单**(带日期的深链,不编造房价)、一份用你本币计的预算汇总,
  和一份**按截止日排序的预订清单**。
- 可选:同一份计划过一遍**八种主题渲染器** —— illustrated、clay、noir、glass、journal、
  zine、splash、portal —— 每一种都是一个自包含页面,自带离线**分享图按钮**
  (存这一天 / 存附录 / 存一张长图;八种里有六种支持整页导出 —— noir 和 glass 只导出单日模块)。

核心不是文采,是**核实**:价格和营业时间一律来自工具而非模型记忆,每条都带来源和查询
日期;查不到的明确标 ⚠️,绝不假装查到了。

它从不代订、不付款、不填个人信息。链接由你自己点。

## 快速开始

**1. 安装** —— Claude Code 按目录发现 skill,所以直接 clone 到位:

```bash
git clone https://github.com/skywain/trip-planner-skill.git ~/.claude/skills/trip-planner
pip3 install --user fast-flights Pillow   # 可选:机票比价扫描器 · 素材流水线
```

其余全部只用 Python 3.9+ 标准库。没有 `fast-flights`,扫描器降级成一个 Google Flights
链接;没有 Pillow,你依然可以用随仓库附带的图库渲染每一种主题。(仓库名在首次公开发布前
可能会改;届时上面的 clone 地址会同步更新。)

**30 秒试一下** —— 不需要 key,也不需要 Claude Code,在仓库根目录执行:

```bash
python3 scripts/render_plan.py examples/kyoto-sample.plan.geo.json -o kyoto.html          # 朴素页面
python3 themes/render_clay2.py examples/turkey-2026/turkey.geo.json -o turkey-clay.html \
  && python3 themes/qc.py turkey-clay.html                                                # 一个主题页面 + 它的 QC(退出码 0)
```

**2. 规划一趟旅行** —— 在 Claude Code 里,一句话。遇到旅行 / 机票 / 行程类请求这个 skill
会自己触发,也可以显式调用:

```
/trip-planner 10月从上海出发,日本12-15天,中等预算,历史+美食,日期可±3天,中国护照
/trip-planner Japan, 12-15 days in October from London, mid budget, history and food, dates ±3 days
```

计划页面的界面语言跟着你提问用的语言走(计划里的 `"lang": "zh"|"en"`;每个渲染器都可以用
`--lang` 覆盖)。会根据你的问法在四种模式里挑一种:

| 模式 | 触发 | 会跑什么 |
|---|---|---|
| **整趟旅行** | 「帮我规划日本 12 天」 | 全部阶段:意图收集 → 国家简报 → 路线骨架 → 机票 → 每日计划 → 酒店 → 汇总 + 自检 |
| **单日** | 「我们在罗马有一天」 | 节假日 / 节庆检查 + 这一天 + 自检;跳过机票和酒店 |
| **空档填充** | 「我在 X 附近,有 2 小时空」 | 15 分钟半径内给 2–3 个选项,各带步行时间、地图链接、必须往回走的时刻 |
| **临场重排** | 「火车没赶上 / 下暴雨了」 | 只根据降级标签重建受影响的那一天 |

**3. 想要设计版?** 三条命令,在仓库根目录执行(完整手册:
[`themes/README.md`](themes/README.md)、[`references/themes.md`](references/themes.md)):

```bash
# 可选:plan 旁边的 <plan>.art.json 会被自动读取 —— 封面标题、每天的标题、哪张图放在哪里
python3 themes/render_<theme>.py plan.geo.json -o trip-<theme>.html   # theme2 clay2 noir2 glass2 journal zine splash portal
python3 themes/qc.py trip-<theme>.html                                # 退出码 0 = 干净;退出码即 FAIL 条数
themes/xprobe.sh trip-<theme>.html module '#d5' out.png              # 无头点一次真正的分享按钮,然后亲眼看 out.png
```

美术契约见 [`themes/ART-SCHEMA.md`](themes/ART-SCHEMA.md);每个字段都是可选的,一份空的
art 文件也必须能渲染出来。图片按 `--assets` → art 目录 → plan 目录 → `themes/assets/`
的顺序解析。

**4. 图片和视频:优先用自己的生成能力,没有才配 key。** 先复用附带的图库 ——
[`themes/assets/IMAGE-LIBRARY.md`](themes/assets/IMAGE-LIBRARY.md) 按主题索引了 301 个词干
(444 张 webp,26 MB)。缺的那些:**如果跑这个 skill 的 AI / agent 自己就能生图或生视频,直接用
自己的能力,不用配任何 key**(规格、提示词、`split_sheet.py` → `cutout.py` → `towebp.py` →
行程 manifest 这几步都不变;契约见 `themes/ART-SCHEMA.md`「生成器选择」)。只有没有原生生成能力
的环境才走备胎脚本:新建 `themes/.auth_header`,内容只有一行 ——
`Authorization: Bearer <你的 OpenRouter key>`(已 gitignore,只从那个目录读;两个脚本都是
把它当 curl 的 header 文件传进去的,所以必须是完整的 header 行,不是裸 key)。`--dry-run`
会打印它将要读取的凭证路径:

```bash
python3 themes/gen.py <trip>/jobs.json --outdir <trip> --manifest <trip>/manifest.<trip>.json      # gpt-image-2;先 --dry-run
python3 themes/genvideo.py jobs.json --outdir <trip>/portal --manifest <trip>/manifest.<trip>.json  # 默认 veo-3.1-lite;--models 看价格
```

来自随仓库示例的真实成本:**每趟旅行 $0.25–0.46 的图片生成费**(7–11 次 `gpt-image-2`
调用)。没有 key 你就只能用图库 —— 除了一切目的地专属的东西之外,图库足以撑起每一种
主题:封面、主视觉插图、标题贴纸、地形色带、splash 岛屿、journal 照片(`IMAGE-LIBRARY.md`
里的图库规则禁止这些跨行程复用)。**portal** 是唯一需要视频素材的主题:要么在云上跑 `genvideo.py`
(`google/veo-3.1-lite`,720p,约 $0.03/秒 → 一条十个世界的链条大约 $3;只在一段 4 秒
片子上冒烟测过,$0.12),要么用本地 GPU(作者的回归测试素材来自 RTX 5090 上的 ComfyUI,
经 `themes/build_portal_jobs.py` 生成)。`themes/assets/portal/` 里附带的那条链条(19 段
片子,约 35 MB)属于催生这套设计的那趟美国行程;换一趟旅行就得有自己的一套。

## 作品展示

九趟测试行程,每一趟都由一个全新的 agent 用这个 skill 端到端规划出来,然后各渲染两种
主题。缩略图是渲染出来的封面(`docs/showcase/`);其中七趟作为可复现示例收在
[`examples/`](examples/) 下(每趟含 plan + art + KML + 一份渲染好的 HTML)。

| 行程 · 日期 | 语言 | 第一种主题 | 第二种主题 | 示例 |
|---|---|---|---|---|
| **澳大利亚** — 北京 PEK → Sydney → Cairns → 北京 · 2026-10-01 → 10-08 | zh | journal 手账 ·「澳洲行」<br><img src="docs/showcase/au-journal-cover.webp" width="150"> | noir 夜航 ·「九万里风 / NINETY THOUSAND MILES OF WIND」<br><img src="docs/showcase/au-noir-cover.webp" width="150"> | — |
| **北欧** — 北京 PEK → Oslo → Flåm / Nærøyfjord → Bergen → 北京 · 10-01 → 10-08 | zh | journal 手账 ·「秋水长天 / WHERE WATER MEETS SKY」<br><img src="docs/showcase/nordic-journal-cover.webp" width="150"> | noir 夜航 ·「天接云涛 / SEA OF CLOUDS」<br><img src="docs/showcase/nordic-noir-cover.webp" width="150"> | [nordic-2026](examples/nordic-2026/)(noir) |
| **日本** — London → Tokyo → Hakone → Kyoto → Osaka KIX → London(缺口程 open-jaw)· 11-21 → 11-28 | en | zine · "KOYO"<br><img src="docs/showcase/japan-zine-cover.webp" width="150"> | illustrated 插画 · "Late Maples"<br><img src="docs/showcase/japan-illustrated-cover.webp" width="150"> | [japan-2026](examples/japan-2026/)(illustrated) |
| **中国** — New York → Beijing → Xi'an → Beijing → New York · 11-11 → 11-18 | en | clay 黏土 · "MOON OF QIN"<br><img src="docs/showcase/china-clay-cover.webp" width="150"> | splash 闪屏 · "MOON OF QIN"<br><img src="docs/showcase/china-splash-cover.webp" width="150"> | [china-2026](examples/china-2026/)(splash) |
| **意大利** — Singapore → Rome → Florence → Venice → Singapore · 10-13 → 10-22 | zh | glass 玻璃 ·「千江月 / A Thousand River Moons」<br><img src="docs/showcase/italy-glass-cover.webp" width="150"> | portal 穿越 ·「天接云涛」—— 三维罗马世界的定格画面;需自备视频素材<br><img src="docs/showcase/italy-portal-cover.webp" width="150"> | — |
| **墨西哥** — Berlin → Mexico City → Oaxaca → Berlin · 10-28 → 11-06(亡灵节 Día de Muertos) | en | journal · "Marigold"<br><img src="docs/showcase/mexico-journal-cover.webp" width="150"> | noir · "Night Vigil / CANDLES ON THE HILL OF THE DEAD"<br><img src="docs/showcase/mexico-noir-cover.webp" width="150"> | [mexico-2026](examples/mexico-2026/)(journal) |
| **摩洛哥** — Toronto → Marrakech → Aït Benhaddou → Merzouga → Fes → Chefchaouen → Casablanca → Toronto · 11-06 → 11-15 | en | glass · "Ochre Road / MARRAKECH TO THE BLUE MOUNTAIN"<br><img src="docs/showcase/morocco-glass-cover.webp" width="150"> | portal · "Through Morocco" —— 定格画面;视频素材不随仓库分发<br><img src="docs/showcase/morocco-portal-cover.webp" width="150"> | [morocco-2026](examples/morocco-2026/)(glass) |
| **土耳其** — Shanghai → Istanbul → Cappadocia →(夜班大巴)→ Pamukkale → Istanbul → Shanghai · 10-01 → 10-09 | zh | illustrated 插画 ·「天接云涛 / SEA OF CLOUDS AT DAYBREAK」<br><img src="docs/showcase/turkey-illustrated-cover.webp" width="150"> | clay 黏土 ·「九万里风」<br><img src="docs/showcase/turkey-clay-cover.webp" width="150"> | [turkey-2026](examples/turkey-2026/)(clay) |
| **越南** — Shenzhen → Hanoi → Ha Long Bay →(夜班火车)→ Hoi An / Da Nang → Ho Chi Minh City → Shenzhen · 12-12 → 12-21 | zh | zine ·「人海 / A SEA OF FACES」<br><img src="docs/showcase/vietnam-zine-cover.webp" width="150"> | splash 闪屏 ·「千江月 / A THOUSAND RIVER MOONS」<br><img src="docs/showcase/vietnam-splash-cover.webp" width="150"> | [vietnam-2026](examples/vietnam-2026/)(zine) |

内页 —— 分享按钮导出的正是「一天」这个模块:

| journal · 墨西哥 day 03(en) | clay · 中国 day 3(en) | splash · 越南 day 3(zh) |
|---|---|---|
| <img src="docs/showcase/mexico-journal-page.webp" width="280"> | <img src="docs/showcase/china-clay-page.webp" width="280"> | <img src="docs/showcase/vietnam-splash-page.webp" width="280"> |

**穿越版动起来** —— 页面用滚动来「刮」的摩洛哥视频链:俯冲进马拉喀什 → 首尾帧相接的过场 →
俯冲进阿伊特本哈杜(九段里的三段,1.25 倍速,不带 HUD;实际页面还会叠上每日信息,往回滚就是倒飞)。
在本地 GPU 上生成(MiniMax-H3,五个世界 21 分钟);有原生视频生成能力的 agent 或 `genvideo.py`
出的是同样的一条链。

<p align="center">
  <img src="docs/showcase/morocco-portal-chain.webp" alt="穿越版:两个摩洛哥世界之间 俯冲 → 过场 → 俯冲(动图)" width="640">
</p>

其余的内页(澳大利亚 journal day 04、北欧 noir、日本 zine、意大利 glass、
摩洛哥 portal 开场、土耳其 illustrated)在 [`docs/showcase/`](docs/showcase/) 里。
朴素的、未上主题的页面长这样:[`examples/kyoto-sample.html`](examples/kyoto-sample.html)。

### 八种主题

每一种都是一个独立的设计物种,不是换皮;它们读的都是同一份 `plan.geo.json`。

| 主题 | 渲染器 | 一句话 |
|---|---|---|
| **illustrated 插画** | `render_theme2.py` | 纸上的一本画册 —— 衬线字、色带、图片作背景 |
| **clay 黏土** | `render_clay2.py` | 一整片连续的黏土地景,一条路串起沿途的里程碑石头 |
| **noir 夜航** | `render_noir2.py` | 一整段夜色负片的跟拍长镜头;正文等宽字,日与日之间溶接 |
| **glass 玻璃** | `render_glass2.py` | 液态玻璃面板浮在一个交叉淡入淡出的照片世界之上 |
| **journal 手账** | `render_journal.py` | 深色桌面上的一本旧旅行手账 —— 胶带、印章、邮戳、拍立得 |
| **zine** | `render_zine.py` | 撕边的 riso 海报拼贴,巨大的双色竖排字形 |
| **splash 闪屏** | `render_splash.py` | 一张被拉长成长卷的游戏启动画面:浮空岛屿,天空成链 |
| **portal 穿越** | `render_portal.py` | 随滚动逐帧擦洗的视频穿行 —— 唯一需要视频素材的主题 |

`render_picker.py` 会生成一个风格选择页,链接到某趟旅行所有已渲染的版本。

## 工作原理

**流水线。** `SKILL.md` 是 Claude Code 照着走的剧本:Phase 0 意图收集(只问缺的,一条
消息问完)→ Phase 1 国家简报(签证取自官方来源、节假日 API + 有预算上限的节庆搜索、
天气、货币、治安)→ Phase 2 路线骨架 → 检查点 → Phase 3 机票与城际交通
(`scripts/flight_scan.py`)→ Phase 4 各城市的每日计划(并行的城市 subagent,搜索预算写死)
→ Phase 5 酒店 → Phase 6 汇总、对抗式自检、交付。与用户之间只有两个检查点,不再多。

**一个文件,一个真源。** `plan.geo.json` 只写一次,所有东西都读它:
`scripts/route_tools.py`(`geocode` · `check` · `links --write` · `kml` · `sun`)从它的
`stops` 生成地图链接和 KML;`scripts/render_plan.py` 生成朴素 HTML;每个主题渲染器读的都是
同一份文件加它的 `art.json`。这就是文字计划、地图链接和好看版本不会各自漂移的原因。
Schema 模板:[`assets/plan.example.json`](assets/plan.example.json) —— 复制一份,把
`PLACEHOLDER` 填掉,再渲染(没填完的副本 `render_plan.py` 会拒绝,除非加 `--force`)。

**硬规则**(提炼自 [`SKILL.md`](SKILL.md) 和 `references/`):

1. 从不代订、付款、占位或填写个人信息 —— 只给链接和清单。
2. 价格和营业时间来自工具,绝不来自记忆;查不到的价格写成「—,点链接查」。
3. 先便宜后贵:先用自带脚本和免密钥 API,浏览器排第二;绝不 curl OTA 或航司网站。
4. 搜索预算是显式的,写进每一个 subagent 的 prompt。
5. 估算就明说是估算:交通时长以 `(est.)` 区间交付,除非核实过。
6. 超过约 3 个月之外,没人会公布那一天的营业时间 —— 核实季节性规律,盖上「截至 {date}」,
   并在清单上加一条二次确认任务。
7. 计划必须先过自检才能交付:闭馆扫描、链条算术、最晚入场时间、步行总量、缺口程一致性。

**数据来源** —— 全部免密钥且免费;价格是用来横向比较的,计划里的深链才是真源
([`references/data-sources.md`](references/data-sources.md)):

| 数据源 | 用途 | 备注 |
|---|---|---|
| Google Flights(经 `fast-flights`) | 机票价格网格 | 只列出程;回程时刻反推 |
| Nominatim / OpenStreetMap | 景点坐标 | 脚本内强制 1 req/s + User-Agent;非拉丁文名字识别弱 |
| Nager.Date | 法定节假日 | 不含宗教 / 农历节日 —— 由有预算上限的节庆搜索补上 |
| Open-Meteo | 对应日期的天气与气候 | 首次调用可能要约 10 秒 |
| sunrise-sunset.org | 黄金时刻排程 | **要求在计划页脚注明来源** |
| frankfurter.dev → open.er-api.com | 汇率 | ECB 每日更新,约 30 种主要货币;小币种 / 已停用币种回落到 open.er-api.com |
| Google Maps / Booking / 运营方官网 | 酒店价格带、交通细节、门票 | 浏览器,只取深链 |

酒店没有可用的免密钥 API,所以这个 skill 只推荐片区、生成带日期的深链,而不去报一个
它无法核实的房价。

## 仓库结构

```
README.md  README.zh-CN.md    本页,英文版与中文版
THIRD-PARTY-NOTICES.md        随仓库再分发的字体与图标的许可证全文(Caveat OFL、Lucide ISC)
SKILL.md                      剧本:各阶段、硬规则、快捷模式
references/
  data-sources.md             每个 API + URL 配方,含回落链
  scheduling.md               停留时长、缓冲、日子类型、常见坑、核验清单
  navigation.md               地图链接、跳转行格式、核实 vs 估算的策略
  country-quick-notes.md      分国家的通票、易售罄项、闭馆规律(+「目的地不在列表里」清单)
  output-template.md          城市块交接格式 + 最终交付物结构
  cover-titles.md             中英双语诗意封面标题库 + 陈词滥调黑名单
  themes.md                   主题渲染手册:八种主题、如何加一种、缺陷检查清单
  art-schema.md               指向 themes/ART-SCHEMA.md
scripts/
  flight_scan.py              Google Flights 价格网格扫描器(免密钥,从中心往外扩)
  route_tools.py              geocode → 距离检查 → 地图链接 → KML → 日出日落
  render_plan.py              plan JSON → 自包含可打印 HTML
themes/
  README.md                   这里有什么、三条命令、图片从哪来
  render_theme2.py …          八个渲染器:theme2(illustrated)· clay2 · noir2 · glass2 · journal · zine · splash · portal
  render_picker.py            风格选择页
  theme_common.py             共享工具函数、i18n、离线分享图引擎
  qc.py  xprobe.sh  xt.sh     静态 QC · 无头导出探针
  gen.py  genvideo.py         备胎生成器(OpenRouter gpt-image-2 / 视频,共用一把 key),给没有原生生成能力的 agent
  towebp.py cutout.py split_sheet.py build_manifest.py build_portal_jobs.py
                              素材流水线(png→webp、抠图、拼版切分、manifest、portal 任务)
  ART-SCHEMA.md               art.json 契约(唯一副本)
  assets/                     图库:444 张 webp(301 个词干)、Caveat 字体、manifest.json、
                              IMAGE-LIBRARY.md(按主题索引)、portal/*.mp4(19 段)
assets/plan.example.json      schema 模板 —— 复制一份,填掉 PLACEHOLDER 再渲染(或加 --force 先预览)
examples/                     七趟带主题的旅行(plan + art + KML + 渲染好的 HTML + README)和朴素的京都样例
docs/
  showcase/                   README 用图(封面、单日模块、hero 拼图)
  verification.md             这个 skill 是怎么被打磨硬的,以及评审抓到了什么
  KNOWN-ISSUES.md             26 条在册缺陷与硬性限制,每条带来源指针,外加路线图
```

不在仓库里的东西:个人旅行数据(`trips/`)、PNG 原图,以及 `gen.py` / `genvideo.py`
读取的 OpenRouter 凭证文件 `themes/.auth_header`。

## 核验方式

- **静态 QC** —— `themes/qc.py page.html` 检查离线契约(无网络、无外部请求)、无 JS 时能否
  存活、打印、焦点顺序和链接卫生;退出码就是 FAIL 条数。七个带主题的示例都能用各自 README
  里的命令重新渲染出逐字节一致的结果,并且通过检查;`render_plan.py` 的朴素页面
  (`examples/kyoto-sample.html`)同样通过。
- **导出探针** —— `themes/xprobe.sh` / `xt.sh` 驱动无头 Chrome 去点页面上真正的分享
  按钮,并把它产出的图片写下来,这样导出缺陷是被看见的,不是被假设的。只支持 macOS 且
  Google Chrome 装在 `/Applications` 下(路径在探针里写死)。请串行运行。
- **摩擦测试** —— 最有价值的一招:给一个从没见过这个 skill 的全新 agent 一个真实的旅行
  需求,让它按顺序照着说明走,把它每一处犯迷糊的地方当成首要交付物。上面那九趟行程就是
  这么规划出来的(每趟一个从没见过这个 skill 的全新 agent 会话),在更早的京都和罗马两轮之上;这些
  摩擦点后来变成了 `references/` 里的规则和 `country-quick-notes.md` 里的条目。
- **对抗式评审** —— 七个独立 agent 做了三轮(脚本折磨测试者、外部事实核查员、领队视角的
  现实性攻击者、跨文件一致性评审员、两个端到端搭建者)。他们抓到了什么、由此产生了哪些
  规则:[`docs/verification.md`](docs/verification.md)。

## 状态与已知问题

能用的、个人自用的软件,仍在积极开发中。当前代码树里每一条在册缺陷和硬性限制都列在
[`docs/KNOWN-ISSUES.md`](docs/KNOWN-ISSUES.md) 里 —— 横跨导出 / 渲染器、规划脚本、素材与
范围的 26 条,每条都有症状、绕行办法和来源指针,外加一份简短路线图(整页导出的尺寸、
journal 的 `zh` 封面修复、picker 文案、竖版 portal 链条、旅行后的相册、联盟营销通路,
以及一个名字)。

**运行要求。** Python 3.9+(macOS 自带的 Python 就行);只用标准库,除了可选的
`fast-flights`(机票扫描器)和 Pillow(素材流水线:`towebp.py`、`cutout.py`、
`split_sheet.py`、`gen.py`)。`gen.py` / `genvideo.py` 需要 `themes/.auth_header`
(一行:`Authorization: Bearer <OpenRouter key>`)—— 且只在 agent 自己没有原生生图/生视频
能力时才需要。导出探针需要 macOS 且 Google Chrome
装在 `/Applications` 下(路径写死)。用附带图库渲染任意主题,以上这些一个都不需要。

**限制与非目标。**

- **个人自用定位。** 里面的浏览器和抓取步骤,就是一个旅行者会手动做的那些事。要做成给别人
  用的托管服务,得接联盟营销通路(Travelpayouts、Amadeus 生产密钥、Viator/GetYourGuide
  的 API)—— 这里用的免费数据源并没有再分发的授权。
- **不是实时的。** 它做规划;它不追踪延误,也不改签。
- **价格会变。** 每个数字都带一个「截至」日期,正是为此。
- **portal 需要视频素材**,得你自己生成或渲染;附带的那条链条属于某一趟旅行。

## 参与贡献

欢迎 issue 和 pull request。最有用的三类贡献:

- **一个新国家** —— 按
  [`references/country-quick-notes.md`](references/country-quick-notes.md) 文件顶部
  「Destination not listed?」那份清单(通票、易售罄项、闭馆规律、节假日数据源的缺口)
  往里加一节,最好是在你真的用这个 skill 规划过一趟那里的旅行之后。
- **一种新主题** —— 读 [`references/themes.md`](references/themes.md) 的 §4(加一种主题)
  和 §5(反复出现的缺陷检查清单,每一项都要在每一种新主题上过一遍);美术契约是
  `themes/ART-SCHEMA.md`,共享工具函数在 `themes/theme_common.py`。
- **一份摩擦报告** —— 以第一次用的人的身份用这个 skill 规划一趟旅行,把说明跟你较劲的每一处
  都记下来提上来。现在的规则大多就是这么被找出来的。

开 PR 之前:对你渲染出的任何主题页面跑 `python3 themes/qc.py`(退出码 0),亲眼看过一次
`xprobe.sh` 的导出,并重新渲染 `examples/` 里的一趟旅行确认结果仍然逐字节一致。

## 致谢

- [Caveat](https://fonts.google.com/specimen/Caveat)(SIL 开放字体许可 1.1)—— journal 主题里
  内嵌的手写体 webfont(`themes/assets/caveat-vf.woff2`)。
- [Lucide](https://lucide.dev/)(ISC)—— `themes/lucide-icons.json` 里的图标雪碧图。
  两者的许可证全文:[`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md)。
- [OpenStreetMap](https://www.openstreetmap.org/copyright) 贡献者与
  [Nominatim](https://operations.osmfoundation.org/policies/nominatim/) —— 地理编码,遵守
  其使用政策(1 req/s、可识别的 User-Agent)。
- [sunrise-sunset.org](https://sunrise-sunset.org/) —— 日出日落时刻;凡展示该数据处都必须
  标注来源,渲染出的计划页面会把它印在页脚。
- [Nager.Date](https://date.nager.at/)、[Open-Meteo](https://open-meteo.com/)、
  [frankfurter.dev](https://frankfurter.dev/)、[open.er-api.com](https://www.exchangerate-api.com/)
  —— 节假日、天气、汇率。
- 生成图片:`openai/gpt-image-2`,经 [OpenRouter](https://openrouter.ai/)。随仓库附带的
  portal 片子(`themes/assets/portal/`,19 段 mp4)是在本地用 ComfyUI 跑 MiniMax-H3 渲染的;
  `genvideo.py` 里的云端替代方案是经 OpenRouter 的 `google/veo-3.1-lite`(默认)或
  `minimax/hailuo-3`。

## 许可证

MIT —— 见 [LICENSE](LICENSE)。© 2026 skywain。
