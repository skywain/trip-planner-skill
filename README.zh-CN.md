[English](README.md) | [简体中文](README.zh-CN.md)

# Trip Planner Skill

**一句话进,一份核实过的、逐小时的、可以直接照着订的行程计划出 —— 交付形态就是一个设计版
页面,八种视觉主题里挑一种。** 一个开放格式的 Agent Skill(`SKILL.md`),跑在你现在用的
那个 coding agent 里 —— Claude Code、Codex、Gemini CLI、Cursor、GitHub Copilot、OpenCode、
Qwen Code、Deep Code、Goose、Kiro、Roo Code,以及任何能加载 Agent Skills 的宿主:营业时间、
价格和节假日都用工具查,不靠猜;每一项预订都递给你一条链接;从不替你预订、也不替你付款。

![Agent Skills: open format](https://img.shields.io/badge/Agent%20Skills-open%20format-0A7B83.svg)
![Agents: Claude Code · Codex · Gemini CLI · Cursor · GitHub Copilot · OpenCode · Qwen Code · Deep Code · Goose · Kiro · Roo Code](https://img.shields.io/badge/agents-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20Gemini%20CLI%20%C2%B7%20Cursor%20%C2%B7%20GitHub%20Copilot%20%C2%B7%20OpenCode%20%C2%B7%20Qwen%20Code%20%C2%B7%20Deep%20Code%20%C2%B7%20Goose%20%C2%B7%20Kiro%20%C2%B7%20Roo%20Code-4C51BF.svg)

![Verified in: Claude Code (others untested)](https://img.shields.io/badge/verified%20in-Claude%20Code%20%28others%20untested%29-8A63D2.svg)
![Models: any](https://img.shields.io/badge/models-any-informational.svg)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-3776AB.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)

<p align="center">
  <img src="docs/showcase/hero-grid.webp" alt="八种主题各一张封面:illustrated、clay、noir、glass、journal、zine、splash、portal" width="900">
</p>

## 作品展示

八种主题,横跨四趟真实旅行(每趟两种主题)。下面每一趟都由一个全新的 agent 会话用这个
skill 端到端规划出来,再从它的 `plan.geo.json` + `art.json` 渲染而成;每一行的三张图分别是
封面、一个单日模块(七种静态主题的分享按钮导出的就是它)和长卷的结尾 —— 清单与收尾跨页。
八个页面里有四个原样收在 [`examples/`](examples/) 下;另外四个里有三个用一条命令就能从
同样的示例目录渲染出来(每个示例的 `art.json` 里都带着这趟旅行的两种主题);portal 还额外
需要视频素材(见下)。

**illustrated** —— 日本 · London → Tokyo → Hakone → Kyoto → Osaka(缺口程 open-jaw)→ London,
2026 年 11 月 21–28 日 · 纸上的一本手绘画册:封面就是目录,每一天是一块带幽灵数字的
套色 riso 印版,整卷可以导出成一张长图 ·
[examples/japan-2026](examples/japan-2026/)

| 封面 | 一天 | 结尾 |
|---|---|---|
| <img src="docs/showcase/illustrated-cover.webp" width="280"> | <img src="docs/showcase/illustrated-day.webp" width="280"> | <img src="docs/showcase/illustrated-end.webp" width="280"> |

**clay** —— 中国 · New York → Beijing → Xi'an → Beijing → New York,2026 年 11 月 11–18 日 ·
一整片连续的黏土定格地景,一条路串起沿途的里程碑石头 ·
渲染它:`python3 themes/render_clay2.py examples/china-2026/china.geo.json -o china-clay.html`
(中文版 clay 示例:[examples/turkey-2026](examples/turkey-2026/))

| 封面 | 一天 | 结尾 |
|---|---|---|
| <img src="docs/showcase/clay-cover.webp" width="280"> | <img src="docs/showcase/clay-day.webp" width="280"> | <img src="docs/showcase/clay-end.webp" width="280"> |

**noir** —— 墨西哥 · Berlin → Mexico City → Oaxaca → Berlin,2026 年 10 月 28 日 – 11 月 6 日
(亡灵节 Día de Muertos)· 一整段夜色负片的跟拍长镜头,正文等宽字,日与日之间彼此
溶接 · 渲染它:`python3 themes/render_noir2.py examples/mexico-2026/mexico.geo.json -o mexico-noir.html`
(中文版 noir 示例:[examples/nordic-2026](examples/nordic-2026/))

| 封面 | 一天 | 结尾 |
|---|---|---|
| <img src="docs/showcase/noir-cover.webp" width="280"> | <img src="docs/showcase/noir-day.webp" width="280"> | <img src="docs/showcase/noir-end.webp" width="280"> |

**glass** —— 摩洛哥 · Toronto → Marrakech → Aït Benhaddou → Merzouga → Fes → Chefchaouen →
Casablanca → Toronto,2026 年 11 月 6–15 日 · 液态玻璃面板浮在一个交叉淡入淡出的照片
世界之上,一个世界一块面板 · [examples/morocco-2026](examples/morocco-2026/)

| 封面 | 一天 | 结尾 |
|---|---|---|
| <img src="docs/showcase/glass-cover.webp" width="280"> | <img src="docs/showcase/glass-day.webp" width="280"> | <img src="docs/showcase/glass-end.webp" width="280"> |

**journal** —— 墨西哥 · Berlin → Mexico City → Oaxaca → Berlin,2026 年 10 月 28 日 – 11 月 6 日 ·
深色桌面上的一本旧旅行手账:胶带、印章、邮戳、拍立得,以及一整周绕开人潮安排的
亡灵节 · [examples/mexico-2026](examples/mexico-2026/)

| 封面 | 一天 | 结尾 |
|---|---|---|
| <img src="docs/showcase/journal-cover.webp" width="280"> | <img src="docs/showcase/journal-day.webp" width="280"> | <img src="docs/showcase/journal-end.webp" width="280"> |

**zine** —— 日本 · London → Tokyo → Hakone → Kyoto → Osaka(缺口程 open-jaw)→ London,
2026 年 11 月 21–28 日 · 撕边的 riso 海报拼贴,巨大的双色竖排字形,做得像一本复印出来的
同人 zine · 渲染它:`python3 themes/render_zine.py examples/japan-2026/japan.geo.json -o japan-zine.html`
(中文版 zine 示例:[examples/vietnam-2026](examples/vietnam-2026/))

| 封面 | 一天 | 结尾 |
|---|---|---|
| <img src="docs/showcase/zine-cover.webp" width="280"> | <img src="docs/showcase/zine-day.webp" width="280"> | <img src="docs/showcase/zine-end.webp" width="280"> |

**splash** —— 中国 · New York → Beijing → Xi'an → Beijing → New York,2026 年 11 月 11–18 日 ·
一张被拉长成长卷的游戏启动画面:浮空的日子岛屿悬在成链的天空下,路线特意先去西安,
好让长城和故宫都落在工作日 ·
[examples/china-2026](examples/china-2026/)

| 封面 | 一天 | 结尾 |
|---|---|---|
| <img src="docs/showcase/splash-cover.webp" width="280"> | <img src="docs/showcase/splash-day.webp" width="280"> | <img src="docs/showcase/splash-end.webp" width="280"> |

**portal** —— 摩洛哥 · Toronto → Marrakech → Aït Benhaddou → Merzouga → Fes → Chefchaouen →
Casablanca → Toronto,2026 年 11 月 6–15 日 · 滚动就是飞行:五个三维世界连成一镜到底,
俯冲 → 首尾帧相接的过场 → 再俯冲,当天的计划叠在画面之上;手一松它就停住,往回滚就是
倒着飞。唯一需要视频的主题(这里是九段片子,在本地 GPU 上渲染;有原生视频生成能力的
agent 或 `themes/genvideo.py` 出的是同样的一条链)。视频素材不随示例分发,所以这个页面
只有截图 —— 下面这段动态是从活着的页面上录下来的。

<p align="center">
  <img src="docs/showcase/portal-motion.webp" alt="穿越版动起来:俯冲进一个世界、接到下一个、当天信息叠在上面(动图)" width="640">
</p>

| 封面 | 一天 | 结尾 |
|---|---|---|
| <img src="docs/showcase/portal-cover.webp" width="280"> | <img src="docs/showcase/portal-day.webp" width="280"> | <img src="docs/showcase/portal-end.webp" width="280"> |

这七趟旅行的渲染命令、成本和文件清单都在 [`examples/README.md`](examples/README.md) 里。
朴素的、未上主题的页面长这样:[`examples/kyoto-sample.html`](examples/kyoto-sample.html)
(中文样例;同一个渲染器遇到 `"lang": "en"` 的计划就出英文界面)—— 它是可打印的附加物,
从来不是默认交付物;`themes/render_picker.py` 会生成一个风格选择页,按
`<prefix>-<theme>.html` 链接到某趟旅行所有已渲染的版本。

## 你会得到什么

说一句 *「日本,10 月去 12–15 天,中等预算,历史 + 美食。」* 这个 skill 会给你:

- **一条跨城路线** —— 先给 2–3 套骨架让你挑,再给一个日期网格的真实机票价格,以及每一段
  城际交通的火车 vs 飞机结论。
- **每一天的逐小时安排** —— 营业时间和闭馆日都用工具查过,停留时长和缓冲来自一套写下来的
  排程方法,附带节假日与节庆撞车扫描,每一跳都有可点开的地图链接。
- **交付物是一个设计版页面,不是一堵文字墙** —— 计划会经上面那**八种主题渲染器**里的一种
  (默认 **illustrated 插画版**)渲染成一个自包含、手机友好的文件:`trip-<theme>.html`。
  七种静态主题自带离线分享图按钮(*存这一天* / *存附录* / *存一张长图*;八种里有五种支持
  整页导出 —— noir 和 glass 只导出单日模块),portal(视频)没有分享按钮 —— 直接截屏。
  朴素的可打印页面是你可以额外要的东西。
- **`plan.geo.json`,唯一真源** —— 主题页面、地图链接,以及一份给 Organic Maps /
  Google My Maps 用的离线 KML,全都从这一个文件出。
- **按片区给出的酒店候选清单**(带日期的深链,不编造房价)、一份用你本币计的预算汇总,
  和一份**按截止日排序的预订清单**。
- **图片按你的 agent 能做到什么来** —— 三级台阶,在提到页面风格之前就静默判完:agent 的
  **原生**生图 → 你自己的 OpenRouter **key** → 内置的**素材库(stock kit)**。走到最后
  一级依然交付主题页面,并且把这件事明说出来(见下面《没有生图能力?》)。

中文用户直接用中文提就行:说「旅行规划」「帮我排个行程」「机票比价」都能触发,整趟跑完,
交付的页面也是中文的。

它不会做的事:预订、付款、占位、填写个人信息。链接由你自己点。

## 快速开始

**1. 安装** —— 支持 Agent Skills 的 agent 按目录发现 skill,所以直接 clone 到你的 skills
目录里(下面演示的是 Claude Code 的路径;其他 agent 见[兼容性](#兼容性)):

```bash
git clone https://github.com/skywain/trip-planner-skill.git ~/.claude/skills/trip-planner
pip3 install --user fast-flights Pillow   # 可选:机票比价扫描器 · 素材流水线
```

其余全部只用 Python 3.9+ 标准库。没有 `fast-flights`,扫描器降级成一个 Google Flights
链接;没有 Pillow,你依然可以用随仓库附带的图库渲染每一种主题。如果 `pip3 install --user`
被 `externally-managed-environment` 拒绝(PEP 668:Homebrew / Debian 的 Python 3.11+),
改装进一个 `python3 -m venv`,或者加 `--break-system-packages`。

**30 秒试一下** —— 不需要 key,也不需要 agent,在仓库根目录执行:

```bash
python3 scripts/render_plan.py examples/kyoto-sample.plan.geo.json -o kyoto.html          # 朴素页面(中文样例)
python3 themes/render_clay2.py examples/china-2026/china.geo.json -o china-clay.html \
  && python3 themes/qc.py china-clay.html                                                 # 一个英文主题页面 + 它的 QC(退出码 0)
```

(想要中文主题页面,把 plan 换成 `examples/turkey-2026/turkey.geo.json` 即可;另外六趟旅行
和它们各自的命令都在 [`examples/README.md`](examples/README.md) 里。)

**2. 规划一趟旅行** —— 在你的 agent 里,一句话。遇到旅行 / 机票 / 行程类请求这个 skill 会
自己触发,也可以显式调用:

```
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

**3. 设计版页面** —— 这就是这个 skill 交到你手上的东西,用你挑的那个主题(默认
**illustrated 插画版** = `render_theme2.py`),绝不会退化成一个朴素文字页面。三条命令,在
仓库根目录执行(完整手册:[`themes/README.md`](themes/README.md)、
[`references/themes.md`](references/themes.md)):

```bash
# 可选:plan 旁边的 <plan>.art.json 会被自动读取 —— 封面标题、每天的标题、哪张图放在哪里
python3 themes/render_<theme>.py plan.geo.json -o trip-<theme>.html   # theme2 clay2 noir2 glass2 journal zine splash portal
python3 themes/qc.py trip-<theme>.html                                # 退出码 0 = 干净;退出码即 FAIL 条数
themes/xprobe.sh trip-<theme>.html module '#d5' out.png              # 无头点一次真正的分享按钮,然后亲眼看 out.png(仅 macOS + Chrome)
```

美术契约见 [`themes/ART-SCHEMA.md`](themes/ART-SCHEMA.md);每个字段都是可选的,一份空的
art 文件也必须能渲染出来。图片按 `--assets` → art 目录 → plan 目录 →
`themes/assets/` 的顺序解析。

**4. 图片和视频:三级台阶,从好到次。** 这个 skill 自己会走这道台阶 —— 静默判定,在它开口
提页面风格之前:

1. **原生生成** —— 跑这个 skill 的 agent 自己就能生图或生视频,那就用它自己的能力:为这趟
   旅行现画,**不用配任何 key**(规格和提示词一样,`split_sheet.py` → `cutout.py` →
   `towebp.py` → 行程 manifest 这几步也一样;契约见 `themes/ART-SCHEMA.md` 的「生成器选择」
   一节)。
2. **一把 key** —— 没有原生生成能力:新建 `themes/.auth_header`,内容只有一行 ——
   `Authorization: Bearer <你的 OpenRouter key>` ——(已 gitignore,只从那个目录读;两个脚本
   都是把它当 curl 的 header 文件传进去的,所以必须是完整的 header 行,不是裸 key)。
   `--dry-run` 会打印它将要读取的凭证路径:

   ```bash
   python3 themes/gen.py <trip>/jobs.json --outdir <trip> --manifest <trip>/manifest.<trip>.json      # gpt-image-2;先 --dry-run
   python3 themes/genvideo.py jobs.json --outdir <trip>/portal --manifest <trip>/manifest.<trip>.json  # 默认 veo-3.1-lite;--models 看价格
   ```

3. **素材库(stock kit)** —— 以上两级都没有:图片取自随仓库附带的这套素材,页面依然是主题
   页面(见下一块)。

三级台阶上都是先复用附带的图库 ——
[`themes/assets/IMAGE-LIBRARY.md`](themes/assets/IMAGE-LIBRARY.md) 按主题索引了 301 个词干
(444 张 webp,26 MB),并且划下了那条线:通用件可以复用,凡目的地专属的(封面、主视觉插图、
标题贴纸、地形色带、splash 岛屿、journal 照片)必须属于它所在的那趟旅行。来自随仓库示例的
真实成本:**每趟旅行 $0.25–0.46 的图片生成费**(7–11 次 `gpt-image-2` 调用)。**portal** 是
唯一需要视频素材的主题:要么在云上跑 `genvideo.py`(`google/veo-3.1-lite`,720p,约
$0.03/秒 → 一条十个世界的链条大约 $3;只在一段 4 秒片子上冒烟测过,$0.12),要么用本地 GPU
(作者的回归测试素材来自 RTX 5090 上的 ComfyUI,经 `themes/build_portal_jobs.py` 生成)。
`themes/assets/portal/` 里附带的那条链条(19 段片子,约 35 MB)属于催生这套设计的那趟
美国行程;换一趟旅行就得有自己的一套。

**没有生图能力?照样是设计版页面。** 两条命令,计划就能出成一个真正的主题页面,而不是降级成
朴素文字:

```bash
python3 themes/stock_art.py plan.geo.json --theme illustrated -o plan.art.json
python3 themes/render_theme2.py plan.geo.json --art plan.art.json \
        --assets themes/assets/stock -o trip-illustrated.html   # 这里的 --assets 是必需的
```

这套素材(`themes/assets/stock/`,80 个基名 / 161 张 webp / 5.2 MB,全部是插画版的水粉风格)
包含 14 张大区封面画、30 个通用场景抠图和 36 个世界地标抠图;`stock_art.py` 按目的地国家挑
封面、按关键词打分给每天挑一张主图,文字(封面标题、每天的标题、图注)仍然交给 agent 写,
并把这行声明 —— *「图片来自内置素材库(本次未接入生图能力);接入生图模型或 KEY 后可为本次
行程定制生成。」* —— 写进页面的小字里(必须留着),同时在聊天总结里再说一遍。覆盖度:
**illustrated** 完整,**clay** 可用;其余六种主题仍然需要生成的图片。细节见
[`themes/assets/stock/README.md`](themes/assets/stock/README.md)。

## 工作原理

**流水线。** `SKILL.md` 是 agent 照着走的剧本:Phase 0 意图收集(只问缺的,一条消息问完)
→ Phase 1 国家简报(签证取自官方来源、节假日 API + 有预算上限的节庆搜索、天气、货币、
治安)→ Phase 2 路线骨架 → 检查点 → Phase 3 机票与城际交通(`scripts/flight_scan.py`)
→ Phase 4 各城市的每日计划(并行的城市 subagent,搜索预算写死)→ Phase 5 酒店 → Phase 6
汇总、对抗式自检、交付。与用户之间最多三次交互,通常只有两次:只有当核心事实缺失且推不出来
时才发的开场消息、从 2-3 套路线骨架里挑一套、以及最后交付。

**开场提问:请求里已经有的事实,一句都不问。** 「帮我安排今年 10.1 到 10.7 的德国之旅」
已经带了目的地和日期,于是一个问题都不问 —— 出发地和其余信息由它推断,并在第一个检查点
列成一块假设清单。只有真的缺了核心事实(目的地、什么时候 / 去几天、推不出来的出发地)才会
发出一条(且仅一条)开场消息,可选的偏好项也搭在同一条消息里,每一行都标着*跳过 = 用默认值*:
出行方式(公共交通 · 自驾 · 跟团)、住宿习惯与档位、景观口味(自然 / 城市 / 海滩 / 森林 /
湖泊 / 山地)、节奏、人数、预算、兴趣排序、日期弹性。你答的和它假设的都会写进计划顶层的
`prefs` 块([`assets/plan.example.json`](assets/plan.example.json)),这样之后临场重排不会
再问一遍。说一句「一次到位,别问了」,开场提问和路线检查点会一起跳过,每一条假设都摆在
结果最上面。

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

## 兼容性

- **是一种格式,不是某个产品的集成。** 这是一个 [Agent Skill](https://agentskills.io) ——
  一种开放格式:一份 `SKILL.md` 剧本,加上 `references/`、`scripts/` 和 `themes/`。任何能
  加载 Agent Skills 的宿主都能加载它;这里没有任何东西绑死在某一家的 agent 上。
- **那些 agent。** Claude Code、Codex、Gemini CLI、Cursor、GitHub Copilot、OpenCode、
  Qwen Code、Deep Code(DeepSeek)、Goose、Kiro 和 Roo Code 都声明支持 `SKILL.md` 形式的
  skill,而这里的脚本只用 Python 3.9+ 标准库。从本仓库的角度看,它们之间唯一的差别是各自
  期望把 skill 放在哪个目录 —— 所以快速开始里那条 `git clone` 的目标路径,就是你要改的
  那一行。
- **在 Claude Code 里验证过,其余的没测。** 本仓库里的每一趟旅行、每一次渲染和每一次导出
  都是在 Claude Code 里跑出来的,上面那条安装路径也是它的 skills 目录。**其他宿主我们没有
  逐个跑过 —— 欢迎反馈**,包括各自期望的 skills 目录在哪。
- **宿主需要具备什么。** 一个能跑 Python 3.9+ 的 shell(跑脚本),以及网页搜索 / 抓取工具
  (国家简报、每日计划和酒店阶段都要在线核实营业时间、价格和节假日)。锦上添花:subagent
  (Phase 4 按城市各派一个 agent 并行;没有的宿主就按顺序逐城规划)、浏览器工具(免密钥
  脚本失败时的机票 / 酒店价格回落方案),以及原生的生图 / 生视频能力(没有就用一把
  OpenRouter key,再没有就用附带的素材库 —— 无论哪种,页面都还是主题页面)。
- **任何模型。** 这个 skill 是说明加脚本;真正执行它的是你宿主里跑的那个模型(Claude、
  GPT、Gemini、Qwen、DeepSeek、Mistral……)。模型越强,越会老实守住那些核实规则;脚本的
  行为则与模型无关。
- **原生生成能力是可选的。** 图片和 portal 视频优先用 agent 自己的生图 / 生视频能力;
  没有才用 `themes/gen.py` / `themes/genvideo.py` 加一把 OpenRouter key;连 key 也没有就用
  `themes/stock_art.py` 加附带的素材库。只用附带图库或素材库渲染的话,一把 key 都不需要。

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
  render_picker.py            风格选择页(链接 <prefix>-<theme>.html)
  theme_common.py             共享工具函数、i18n、离线分享图引擎
  qc.py  xprobe.sh  xt.sh     静态 QC · 无头导出探针
  gen.py  genvideo.py         备胎生成器(OpenRouter gpt-image-2 / 视频,共用一把 key),给没有原生生成能力的 agent
  stock_art.py                没有生图能力也没有 key 时:用素材库拼出 art.json 的图片部分
  towebp.py cutout.py split_sheet.py build_manifest.py build_portal_jobs.py
                              素材流水线(png→webp、抠图、拼版切分、manifest、portal 任务)
  ART-SCHEMA.md               art.json 契约(唯一副本)
  assets/                     图库:444 张 webp(301 个词干)、Caveat 字体、manifest.json、
                              IMAGE-LIBRARY.md(按主题索引)、portal/*.mp4(19 段)
    stock/                    素材库:14 张大区封面 + 66 个抠图(161 张 webp,5.2 MB)、
                              index.json(查找表:archetype、225 个 ISO2、关键词、声明文案)、README.md
assets/plan.example.json      schema 模板 —— 复制一份,填掉 PLACEHOLDER 再渲染(或加 --force 先预览)
examples/
  README.md                   七趟旅行:主题、路线、成本、每一条渲染命令
  japan-2026/ …               每趟旅行一个目录:<trip>.geo.json + <trip>.art.json + <trip>-<theme>.html
  kyoto-sample.*              朴素页面的样例 plan、它的 HTML 和它的 KML
docs/
  showcase/                   README 用图(hero 拼图、每种主题的封面 / 单日 / 结尾三帧、portal 动态录屏)
  verification.md             这个 skill 是怎么被打磨硬的,以及评审抓到了什么
  KNOWN-ISSUES.md             30 条缺陷与硬性限制(29 条未修 / 已排期,1 条已解决),每条带来源指针,外加路线图
```

不在仓库里的东西:个人旅行数据(`trips/`)、PNG 原图,以及 `gen.py` / `genvideo.py`
读取的 OpenRouter 凭证文件 `themes/.auth_header`。

## 核验方式

- **静态 QC** —— `themes/qc.py page.html` 检查离线契约(无网络、无外部请求)、无 JS 时能否
  存活、打印、焦点顺序和链接卫生;退出码就是 FAIL 条数。七个带主题的示例都能用
  [`examples/README.md`](examples/README.md) 里的命令重新渲染出逐字节一致的结果,并且通过
  检查;`render_plan.py` 的朴素页面(`examples/kyoto-sample.html`)同样通过。
- **导出探针** —— `themes/xprobe.sh` / `xt.sh` 驱动无头 Chrome 去点页面上真正的分享按钮,
  并把它产出的图片写下来,这样导出缺陷是被看见的,不是被假设的。只支持 macOS 且 Google
  Chrome 装在 `/Applications` 下(路径在探针里写死)。请串行运行。
- **摩擦测试** —— 最有价值的一招:给一个从没见过这个 skill 的全新 agent 一个真实的旅行
  需求,让它按顺序照着说明走,把它每一处犯迷糊的地方当成首要交付物。九趟测试行程
  (澳大利亚、北欧、日本、中国、意大利、墨西哥、摩洛哥、土耳其、越南)就是这么规划出来的,
  每趟一个全新的 agent 会话,建立在更早的京都和罗马两轮之上;这些摩擦点后来变成了
  `references/` 里的规则和 `country-quick-notes.md` 里的条目。
- **对抗式评审** —— 七个独立 agent 做了三轮(脚本折磨测试者、外部事实核查员、领队视角的
  现实性攻击者、跨文件一致性评审员、两个端到端搭建者)。他们抓到了什么、由此产生了哪些
  规则:[`docs/verification.md`](docs/verification.md)。

## 状态与已知问题

能用的、个人自用的软件,仍在积极开发中,并且**刻意不绑定宿主**:它是一个 Agent Skill,
不是 Claude Code 的插件 —— 在 Claude Code 里端到端验证过,预期也能跑在[兼容性](#兼容性)
一节列出的另外十个 agent 里,在有人反馈之前那些都算没测过。当前代码树里每一条缺陷和硬性
限制都列在 [`docs/KNOWN-ISSUES.md`](docs/KNOWN-ISSUES.md) 里 —— 横跨导出 / 渲染器、规划
脚本、素材与范围的 30 条(29 条未修或已排期,1 条已解决),每条都有症状、绕行办法和来源
指针,外加一份简短路线图(整页导出的尺寸、journal 的 `zh` 封面修复、picker 文案、竖版
portal 链条、旅行后的相册、给托管版本准备的联盟营销通路)。

**运行要求。** Python 3.9+(macOS 自带的 Python 就行);只用标准库,除了可选的
`fast-flights`(机票扫描器)和 Pillow(素材流水线:`towebp.py`、`cutout.py`、
`split_sheet.py`、`gen.py`)。`gen.py` / `genvideo.py` 需要 `themes/.auth_header`
(一行:`Authorization: Bearer <OpenRouter key>`)—— 且只在 agent 自己没有原生生图 / 生视频
能力时才需要;两者都没有时,`stock_art.py` 加附带的素材库照样能出主题页面。导出探针需要
macOS 且 Google Chrome 装在 `/Applications` 下(路径写死)。用附带图库或素材库渲染任意
主题,以上这些一个都不需要。

**限制与非目标。**

- **个人自用定位。** 里面的浏览器和抓取步骤,就是一个旅行者会手动做的那些事。要做成给别人
  用的托管服务,得接联盟营销通路(Travelpayouts、Amadeus 生产密钥、Viator/GetYourGuide
  的 API)—— 这里用的免费数据源并没有再分发的授权。
- **不是实时的。** 它做规划;它不追踪延误,也不改签。
- **价格会变。** 每个数字都带一个「截至」日期,正是为此。
- **portal 需要视频素材**,得你自己生成或渲染;附带的那条链条属于某一趟旅行。

## 参与贡献

欢迎 issue 和 pull request。最有用的四类贡献:

- **一份兼容性报告** —— 在 Claude Code 以外的宿主里跑一跑这个 skill,告诉我们什么能用、
  什么不能用,以及那个宿主期望把 skill 放在哪里。
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
  portal 片子(`themes/assets/portal/`,19 段 mp4)和作品展示里的摩洛哥 portal 素材,都是
  在本地用 ComfyUI 跑 MiniMax-H3 渲染的;`genvideo.py` 里的云端替代方案是经 OpenRouter 的
  `google/veo-3.1-lite`(默认)或 `minimax/hailuo-3`。

## 许可证

MIT —— 见 [LICENSE](LICENSE)。© 2026 skywain。
