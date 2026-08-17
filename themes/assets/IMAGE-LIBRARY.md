# IMAGE-LIBRARY — themes/assets/ 图片复用库索引(含九趟测试行程资产,见 §13-21)

2026-08-16 实扫:**301 个基名 = webp 444 个 26MB**(**页面只用这些**;png 母图不进 repo,重切图用的 png 留在各 trips/ 目录)。
生成累计 **≈$6.57**(manifest 求和;portal 视频另计);单条 prompt/参数/单价查 `manifest.json`(**181 条**;sheet 切出的子件不单列,查对应 `*-sheet-*` 母条目)。**通用件(§12)先查本表+manifest,已有就复用;封面/主视觉/地形带=目的地场景,必须为本行程生成(见 SKILL.md Phase 6);生成时 agent 自己有原生生图能力就直接用(不配 KEY),没有才走 gen.py/OpenRouter(见 ART-SCHEMA「生成器选择」);生成花钱须 owner 批。**
另有 **stock 通用素材包**(`stock/`,80 个基名 / 161 webp / $0.9284,索引与 manifest 独立)——**没有生图能力时**的兜底图库,见 §22;它不是「通用件」的替代,有生图能力照旧为本行程现生成。

**测试行程资产怎么进库(2026-08-16 定,别再照第 13 节以前的写法自己往 themes/ 里塞)**
- 测试员/普通用户**只写自己的行程目录**:`trips/<trip>/manifest.<trip>.json` 是那趟资产的**权威记录**(prompt/参数/单价/文件大小全在里面),png 与 webp 都留在该目录,`themes/` 一律只读——`themes/*.py`、`ART-SCHEMA.md`、本表都不许改。
- **主 agent 在一批测试跑完后统一回收**:webp(含 `.sm/.md/.lg/.cut/.band/.strip` 变体)拷进 `themes/assets/`、trip manifest 条目按本库 schema 手工并进 `manifest.json`(补 `source_job` / `trip` / `note`,`files` 只记真拷进来的 webp)、本表追加一节并把该节的通用件同步进 §12。
- ⚠️ 回收时**不要跑 `build_manifest.py`** —— 它按 job 文件扫 `themes/assets`,会把 trip 目录里的 job↔png 关系弄乱;**手工合并**,合完用 `python3 -c` 校验 JSON 有效 + 条目数 + `cost_usd` 求和。

## 使用说明
- 嵌入只走 `theme_common.data_uri(stem, size=None)`:显式 size 取 `<stem>.<size>.webp`(sm/md/lg/band/strip);不给 size 按 **md.webp → cut.webp → .webp** 链回退。输出 base64 data-URI,file:// 双击可开,页面零 fetch/外链。
- 选变体 = 按显示尺寸取最小够用档:sm(高≈128,缩略/角标)< md(≈300–480,卡片/节点)< lg(≈640)< cut.webp(原尺寸抠图,大主体)< 全幅 .webp(1536×864 背景)。同图多处引用会把 base64 翻倍(插画/玻璃两次踩雷)。
- `cut` 系 = cutout.py 真 alpha 抠图(全部 cut.webp 已 PIL 验 RGBA),其 sm/md/lg 缩放同样透明;全幅 .webp(hero/glass-*/noir-*/zine-* 等)为不透明 RGB。
- 下表「变体」列只列**可嵌入的 webp 档**(数字=KB);各基名的 .png / .cut.png 原图默认都在盘上、一律不进页面。装饰元素(印章/胶带感/污渍/彩虹/纹理)优先 CSS/SVG 手写,别拿图凑。
- 「引用」列 = live 渲染器(theme2插画 / clay2黏土 / noir2夜航 / glass2玻璃 / journal手账 / zine / splash 闪屏);`v1` = 仅退役渲染器在用,现行无人占,可自由复用。chart/board/picker 零图片。
- **封面/主视觉/标题贴纸/地形带/底片/岛屿 = 目的地场景,一律为本行程按主题风格生成**:优先目的地景区(西安城墙/长城)> 国家地标 > 中性场景,永远别空着、别拿别国的带(owner 2026-08-15:中国页开头出现纽约天际线带=缺陷);「先复用」只针对第 12 节通用道具。地形带配方=US `strip-*` 同一提示词模板(见 manifest china-strip-xian / -beijing)。
- **地域绑定件(自由女神/金门/黄石/优胜美地/钻石头/火山/盐湖圣殿/天安门……)禁止跨行程复用**——别的行程只能用第 12 节「通用件」列出的 stem,其余一律现生成(sheet 配方见 ART-SCHEMA.md「图片工具链」)。
- **「通用」只有一张表:§12。** 凡在 §13-21 的分节表里把某个 stem 的「地域」标成**通用**的,**必须同时出现在 §12 的表里**(注明来源节);只在分节里写「通用」而 §12 查不到 = 缺陷,复用方**按未列处理**(当地域绑定件,别用)。标成「**看行程**」的走 §12 末尾那条「看行程再定」名单,不是通用件;§13/§14 里的「(泛)」标记同样按「看行程再定」处理,不等于通用。
- 变体生成:`towebp.py in.png --sizes sm,md,lg` 产 `.webp` / `.cut.webp`(按有无 alpha)与 **最长边** sm 128 / md 480 / lg 640 档;`band`/`strip` 是手工形状不是尺寸档。⚠️ 库里 2026-08-15 之前的 sm/md/lg 是按**高度**≈128/300-320/640 手工缩的(所以上一条写「高≈128 / ≈300–480」),两种口径的档位都能被 data_uri 正常取用,选档只看「显示尺寸最小够用」即可。

## 1 通用插画组(gouache 插画风)— 13
v1(build_page/render_theme)也引用本组,不影响复用。

| 基名 | 变体(KB) | 透明 | 引用 | 复用建议 |
|---|---|---|---|---|
| liberty | cut61 md11 sm3 lg22 | ✓ | theme2 | 自由女神,NYC 日角标/卡片 |
| golden-gate | cut110 md32 sm10 lg58 | ✓ | theme2,zine | 金门桥,旧金山日 |
| diamond-head | cut148 md46 sm11 lg66 | ✓ | theme2,zine | 钻石头山,檀香山日 |
| kilauea | cut144 md19 sm5 lg35 | ✓ | theme2,zine | 基拉韦厄火山,大岛日 |
| prismatic | cut149 md27 sm7 lg49 | ✓ | theme2,zine | 大棱镜温泉,黄石日 |
| stadium | cut184 md31 sm7 lg59 | ✓ | theme2 | 棒球场,绿茵之夜 |
| teton | cut177 md30 sm7 lg55 | ✓ | theme2 | 大提顿群峰 |
| yosemite | cut183 md27 sm6 lg47 | ✓ | theme2,zine | 优胜美地半穹 |
| tiananmen | cut114 md32 sm8 | ✓ | theme2,zine | 天安门,返程北京端盖专用 |
| bus | cut144 md24 sm7 lg43 | ✓ | theme2,zine | 复古团巴,任何团巴日 |
| plane | cut79 md30 sm9 lg35 | ✓ | theme2,zine | 客机侧影,飞行日通用 |
| hero | webp248 | ✗ | theme2 兜底+v1 | 16:9 全幅封面(cover-hero 缺时才用) |
| cover-hero | webp101 | ✗ | theme2 | 插画版现行封面大图 |

## 2 黏土组 — 27
| 基名 | 变体(KB) | 透明 | 引用 | 复用建议 |
|---|---|---|---|---|
| clay-liberty | cut58 md18 sm5 | ✓ | clay,clay2 | 黏土地标 10 件套:里程碑石头旁 |
| clay-goldengate | cut87 md27 sm8 | ✓ | clay,clay2 | 〃 |
| clay-diamondhead | cut101 md35 sm9 | ✓ | clay,clay2 | 〃 |
| clay-prismatic | cut87 md23 sm6 | ✓ | clay,clay2 | 〃 |
| clay-stadium | cut69 md24 sm7 | ✓ | clay,clay2 | 〃 |
| clay-yosemite | cut87 md19 sm5 | ✓ | clay,clay2 | 〃 |
| clay-teton | cut31 md27 sm7 | ✓ | clay2 | 〃 |
| clay-saltlake | cut22 md17 sm7 | ✓ | clay2 | 盐湖城摩门圣殿 |
| clay-volcano | cut29 md20 sm5 | ✓ | clay2 | 火山冒烟 |
| clay-island | cut37 md34 sm10 | ✓ | clay2 | 夏威夷小岛+椰树 |
| clay-plane | cut19 md16 sm8 | ✓ | clay2 | 黏土小飞机,飞行日 |
| clay-bus-solo | cut57 md21 | ✓ | clay2 | 黏土团巴(贴在路上那辆) |
| clay-luggage | cut19 md16 sm6 | ✓ | 无 | 行李箱,**空闲**可当收尾/打包位装饰 |
| clay-balloon | cut14 | ✓ | clay2 | 热气球,天空装饰 |
| clay-cactus | cut16 | ✓ | clay2 | 仙人掌(沙漠段) |
| clay-palm | cut18 | ✓ | clay2 | 棕榈树(海岛段) |
| clay-pines | cut22 | ✓ | clay2 | 松树丛(山地段) |
| clay-signpost | cut15 | ✓ | clay2 | 路牌 |
| clay-cloud-a/b/c | cut11/6/4 | ✓ | clay2 | 云朵三件,页缘天空装饰 |
| strip-desert | band77 cut105 | ✓ | clay2 | 地形带:沙漠(1400×380,负边距咬合) |
| strip-geyser | band86 cut123 | ✓ | clay2 | 地形带:间歇泉 |
| strip-mountains | band62 cut90 | ✓ | clay2 | 地形带:雪山 |
| strip-ocean | band76 cut99 | ✓ | clay2 | 地形带:海岸 |
| clay-title | cut132 md83 | ✓ | clay2 | 黏土立体标题字「美国行」 |
| clay-hero | webp85 | ✗ | 仅v1 | v1 全幅封面,弃用;可当风格锚参考 |

## 3 玻璃组(16:9 全幅影像,当固定背景层)— 6
| 基名 | 变体(KB) | 透明 | 引用 | 复用建议 |
|---|---|---|---|---|
| glass-hero | webp135 strip22 | ✗ | glass2 | 封面影像;.strip 窄条(800×300)仅 v1 用 |
| glass-city | webp150 strip23 | ✗ | glass2 | 城市段背景(NYC) |
| glass-park | webp152 strip29 | ✗ | glass2 | 国家公园段背景 |
| glass-island | webp154 strip29 | ✗ | glass2 | 海岛段背景 |
| glass-west | webp131 | ✗ | glass2 | 西部段背景 |
| glass-dawn | webp33 | ✗ | glass2 | 黎明收官段背景 |

## 4 夜航组(16:9 夜景画,底片层)— 7
| 基名 | 变体(KB) | 透明 | 引用 | 复用建议 |
|---|---|---|---|---|
| noir-hero | webp59 | ✗ | noir2 | 序幕底片 |
| noir-nyc | webp93 | ✗ | noir2 | 纽约夜景 |
| noir-stadium | webp68 | ✗ | noir2 | 球场夜景(zine 已换 zine-stadium+journal-ph-soccer,棒球素材退出足球日) |
| noir-yellowstone | webp64 | ✗ | noir2 | 黄石夜泉 |
| noir-yosemite | webp52 | ✗ | noir2 | 优胜美地星夜 |
| noir-volcano | webp47 | ✗ | noir2 | 火山熔岩夜 |
| noir-sunrise | webp50 | ✗ | noir2 | 日出收官(暖色出口) |

## 5 Zine 组(riso 海报大图)— 4
| 基名 | 变体(KB) | 透明 | 引用 | 复用建议 |
|---|---|---|---|---|
| zine-nyc | webp324 | ✗ | zine | 竖版 1024×1536 章头海报 |
| zine-geyser | webp179 | ✗ | zine | 〃 黄石 |
| zine-elcap | webp158 | ✗ | zine | 〃 优胜美地 |
| zine-hawaii | webp301 | ✗ | zine | 〃 夏威夷 |

## 6 手账组 — 25
| 基名 | 变体(KB) | 透明 | 引用 | 复用建议 |
|---|---|---|---|---|
| journal-ph-*(12 张拍立得) | cut:beach58 diamondhead50 geyser40 goldengate28 lava28 liberty38 nyc36 saltlake42 stadium36(⚠️棒球,已无人用,自由复用) teton35 wing33 yosemite68 | ✓ | journal,zine | 白框拍立得照片,配 CSS 胶带角贴 |
| journal-boarding | cut24 | ✓ | journal,zine | 登机牌道具 |
| journal-ticket | cut21 | ✓ | journal,zine | 复古门票票根 |
| journal-tag | cut21 | ✓ | journal,zine | 行李吊牌 |
| journal-seal | cut21 | ✓ | journal | 火漆封蜡 |
| journal-stamp-bison/goldengate/liberty | cut36/33/35 | ✓ | journal | 邮票三枚(邮戳用 CSS 画) |
| journal-tape-a/b/c/d | cut17/16/17/13 | ✓ | journal | 和纸胶带四条 |
| journal-flower-a/b | cut12/10 | ✓ | journal | 压花两枝,页角装饰 |

## 7 闪屏组(Brawl Stars 厚涂)— 10
| 基名 | 变体(KB) | 透明 | 引用 | 复用建议 |
|---|---|---|---|---|
| splash-title | cut134 md76 | ✓ | splash | 厚涂标题图(用 md) |
| splash-hero | cut292 md156 | ✓ | splash | 主视觉人物群像(用 md,cut 很重慎用) |
| splash-geyser | cut130 md108 sm60 | ✓ | splash | 间歇泉大图 |
| splash-volcano | cut101 md83 sm40 | ✓ | splash | 火山大图 |
| splash-{baseball,cliff,ggate,surf,taxi,teton} | cut39–48 sm31–40 | ✓ | splash | 浮岛节点六件(用 sm),缎带路章头 |

## 8 Portal 视频底图(i2v 种子帧,**不嵌页面**)— 13
portal-nyc / portal-yellowstone(旧 1:1)+ portal-{nyc,stadium,saltlake,yellowstone,teton,goldengate,yosemite,waikiki,volcano,diamondhead}-w + portal-nyc-w2(16:9 宽版,各 1.5–2.0MB png)。
仅被 `build_portal_jobs.py` 当生视频输入;页面用的是 `themes/assets/portal/*.mp4`(19 条 37MB),详见 portal-theme 记忆。

## 9 wishlist 增补(2026-08-13,owner「全补上」;引用列由接入方更新)

| 基名 | 变体(KB) | 透明 | 引用 | 复用建议 |
|---|---|---|---|---|
| zine-goldengate / -teton / -volcano / -stadium | webp142/183/66/195(1024×1536) | ✗ | zine | zine 竖版胶片照 4 张,补齐金门/提顿/火山/足球夜,与 zine-nyc 同族(D7/D6/D10/D3 章节主图) |
| journal-ph-soccer/slctemple/sequoia/tunnelview/canyonfalls/elkarch | cut38-70 | ✓ | journal,zine | 柯达 70s 照片 6 张:足球夜(替棒球)/盐湖圣殿/巨杉/隧道观景/黄石大峡谷瀑布/鹿角拱门(D3/D4/D8/D8/D6/D6) |
| journal-flora-daisy/fern/maple | cut19/36/24 | ✓ | journal | 压花三件:雏菊/蕨叶/枫叶;与 flower-a/b 同池种子散布 |
| journal-washi-floral/ticking/gingham | cut32/30/33 | ✓ | journal | 织物纹理胶带三条:碎花/条纹/格子;入 tape() 七纹轮换 |
| journal-poster-yosemite | webp298 md77 | ✗ | journal | WPA 复古国家公园海报(D8 钉挂,留白带排 Caveat 字) |
| journal-postcard-hula | webp345 md73 | ✗ | journal | 1950s 亚麻纹 hula 明信片(D11 收官,配邮票+邮戳) |
| splash-strip-city / splash-strip-goldengate | cut56/63(1433/1431 宽横条) | ✓ | splash | 闪屏剪影横条:紫夜城市天际线/金门日落,端头自带渐隐 |
| splash-plane / splash-bus | cut24/33 | ✓ | splash | 闪屏画风飞机(d4/d9 飞行日)/行李顶架团巴 |
| splash-cloud-a/b/c/d + splash-star | cut14/7/4/2/5 | ✓ | splash | 闪屏同画风云四朵+四角星光,已替换黏土云 |
| splash-baseball/cliff/ggate/surf/taxi/teton | cut40/48/39/42/41/48 | ✓ | splash | 闪屏浮岛节点第一批切件(棒球场/峭壁/金门/浪花/出租车/提顿),已被 nodes2 二批部分取代——棒球件因赛事实为足球已停用,其余仍在页面上 |
| caveat-vf.woff2 | 74KB(woff2 变量字重 400-700) | 字体 | journal | 英文手写体 Caveat(OFL 开源),base64 进页嵌 @font-face,--curs 栈打头 |

## 10a 稿图 mock-*(**风格草稿,勿嵌入页面**)— 19
mock-{bento,bento2,bento3,candy,candy2,cover,day,flow,game2,journal,odyssey,splash,splash2,splash3,splash4,zelda,zine} + clay-mock-{flow,world}。
全是 png(1.5–3.5MB),是画给 owner 选型的版式示意/AI 稿,**不是素材**:无变体、无抠图,任何 render_*.py 不得引用;新主题开工前当风格参考看即可。

## 11 sheet 母图与中间产物(**勿嵌入**)— 9
clay-sheet-{deco,props} / journal-sheet-{photo-a,photo-b,props} / splash-sheet-nodes(切格母图,子件已入上表)+ contact-sheet / contact-sheet2 / world-check(早期拼样/QA 检查图)。全 png,只在重切图(split_sheet.py)时用。

## 10b 闪屏专属件二批(2026-08-14,sheet×2 ≈$0.09,style=Brawl Stars splash)
| 基名 | 变体(KB) | 透明 | 引用 | 复用建议 |
|---|---|---|---|---|
| splash-nightflight | cut29 sm26 | ✓ | splash | 夜航机趴星云岛,D1 章头 |
| splash-temple | cut31 sm29 | ✓ | splash | 盐湖圣殿盐镜岛,D4 章头 |
| splash-soccer | cut36 sm33 | ✓ | splash | 足球+泛光灯岛,D3 章头(替换 baseball) |
| splash-sunrise | cut47 sm44 | ✓ | splash | 钻石头日出岛,D11 收官章头 |
| splash-sequoia | cut48 sm44 | ✓ | splash | 巨杉隧道,D8 伴岛(veh-sequoia) |
| splash-balloon | cut31 sm28 | ✓ | splash | 条纹热气球+云座,sc-bal(替换 clay-balloon) |
| splash-m-*(6 只吉祥物) | cut26-35 sm26-33 | ✓ | splash | hotdog/whistle/bison/moose/cablecar/ukulele,MASCOT 贴场景缘 |

## 12 通用件(任何行程可直接复用,零地域绑定)— 2026-08-15 逐件目检,2026-08-16 补第三批
「地域绑定」= 画面里有一个能认出来的地方(地标/特定地貌/城市专属物件)。下面这些没有,写进任何 art.json 都不会「把别人的旅行贴到自己页上」;其余所有 stem(尤其 `*-liberty / -goldengate / -yellowstone / -yosemite / -diamondhead / -volcano / -kilauea / -prismatic / -teton / -saltlake / -stadium / -tiananmen / zine-* / noir-* / glass-*` 与九趟测试行程的 `au-* / nordic-* / japan-* / china-* / italy-* / mexico-* / morocco-* / turkey-* / vietnam-*`)默认视为绑定件。**本表是「通用」的唯一权威**:§13-21 分节里标通用的都在这儿,标了而这儿没有的按绑定件处理(见顶部规则)。

| 基名 | 变体(KB) | 用途 | 主题 |
|---|---|---|---|
| journal-ph-wing | cut33 | 舷窗机翼拍立得——去程/回程日的 `photo`/`photos2` | journal |
| journal-ph-beach | cut58 | 椰林沙滩拍立得(热带海滩通用;北欧/内陆行程别用) | journal |
| nordic-journal-flora-fern | cut45 | 蕨类压花(props flora stem) | journal |
| nordic-journal-flora-heather | cut37 | 石楠压花(props flora stem) | journal |
| journal-boarding | cut24 | 空白登机牌道具(`props kind:img`) | journal |
| journal-ticket | cut21 | ADMIT ONE 复古票根 | journal |
| journal-tag | cut21 | 牛皮纸行李吊牌 | journal |
| journal-seal | cut21 | 罗盘火漆(`seal` kit 用的就是它) | journal |
| journal-tape-a/b/c/d | cut17/16/17/13 | 和纸胶带(主题 `tape()` 轮换,art 不必点名) | journal |
| journal-washi-floral/ticking/gingham | cut32/30/33 | 织物纹理胶带(同上) | journal |
| journal-flower-a/b · journal-flora-daisy/fern/maple | cut12/10 · 19/36/24 | 压花(`flora` kit 池) | journal |
| plane | cut79 md30 sm9 lg35 | 水粉客机侧影,飞行日 | 插画 / zine |
| bus | cut144 md24 sm7 lg43 | 水粉复古团巴,任何团巴日 | 插画 / zine |
| clay-plane · clay-bus-solo | cut19 md16 sm8 · cut57 md21 | 黏土小飞机 / 团巴 | clay |
| clay-luggage | cut19 md16 sm6 | 行李箱+相机,收尾/打包位 | clay |
| clay-balloon · clay-cloud-a/b/c · clay-signpost | cut14 · 11/6/4 · 15 | 天空/页缘装饰、路牌 | clay |
| clay-cactus · clay-palm · clay-pines | cut16/18/22 | 地貌植被(沙漠/海岛/山地),按行程地貌挑 | clay |
| splash-plane · splash-bus · splash-nightflight | cut24/33 · cut29 sm26 | 厚涂飞机 / 团巴 / 夜航机趴星云 | splash |
| splash-cloud-a/b/c/d · splash-star · splash-balloon | cut14/7/4/2 · 5 · 31 sm28 | 云、星光、热气球 | splash |
| splash-surf · splash-cliff | cut42 sm40 · cut48 sm44 | 浪花冲浪板浮岛 / 瀑布断崖浮岛(无地标) | splash |
| splash-m-whistle | cut29 sm27 | 哨子吉祥物(裁判/球赛日) | splash |
| caveat-vf.woff2 | 74 | 英文手写字体 | journal |
| **↓ 2026-08-16 补:分节标了通用但本表漏收的(规则冲突修复)** | | | |
| japan-train | cut27 sm4 | 白蓝新干线车头三四分之一视角,无地标——任何高铁/城际日 | 插画 / zine(来源 §15) |
| china-clay-train | cut21 | 黏土高铁头车(白身红条纹)+ 一小截灰轨 | clay(来源 §16) |
| china-splash-train | cut42 sm7 | 厚涂高铁头车贴纸(圆车灯眼睛),交通位 | splash(来源 §16) |
| china-splash-veh-train | cut27 | 厚涂高铁行驶浮岛,`vehicle` 位 | splash(来源 §16) |
| **↓ 2026-08-16 第三批测试行程新增(§18-21,已逐件开图目检)** | | | |
| mexico-journal-ticket-ado | cut35 | 长途巴士票根:巴士线描 + 序列号 48167,**画面零文字零地标**(名字带 ADO 但图上没有),任何长途巴士/城际日 | journal(来源 §18) |
| morocco-glass-dawn | webp53 | 海滨黎明 16:9 底片:平静海面 + 沙滩弧线 + 远处一排白色低屋剪影,粉桃色天,无地标——**§12 第一件 16:9 摄影底片**,玻璃/夜航版收官段可直接用 | glass(来源 §19) |
| turkey-balloon | cut27 sm8 | 四只条纹热气球升空(水粉),无地标——天空装饰/热气球日 | 插画 / zine(来源 §20) |
| vietnam-splash-i-train | cut32 sm7 | 绿皮卧铺车厢浮岛 + 月牙,无地标——夜车日章头 | splash(来源 §21) |
| vietnam-ph-train | webp23 | 卧铺车窗外的海岸晨光照片(铺位+车窗框),无地标;**海岸线偏热带/亚热带**,内陆或北欧行程别用 | zine / journal(来源 §21) |

**看行程再定(有地域味但不是地标)**:`splash-taxi`(黄色出租车=纽约)、`splash-m-hotdog`(纽约热狗车)、`splash-m-cablecar`(旧金山缆车)、`splash-m-ukulele`(夏威夷)、`splash-m-bison/-moose`(北美动物)、`strip-desert`(西南沙漠拱门+仙人掌)、`strip-ocean`(火山岛)、`strip-mountains/-geyser`;**2026-08-16 补入**:`china-clay-food` / `china-splash-m-dumpling`(竹蒸笼+包子=中华菜系,原 §16 误标通用)、`au-noir-hero`/`au-noir-dawn`(南天银河/黎明归航,南半球或海岛行程可借)、`nordic-noir-aurora`(极光,北极圈行程可借)——只有行程真去了对应的地方/菜系才复用。

## 13 澳大利亚 2026 测试行程资产(2026-08-15,Opus 测试员生成,$0.31;sheet 母图 au-journal-sheet-photo / -props 见 manifest)— 19
地域绑定件只在澳洲行程复用;`au-noir-hero`(客机+南天银河)与 `au-noir-dawn`(黎明归航)偏泛,南半球/海岛行程可借。

| 基名 | 变体(KB) | 内容 | 地域 | 用法 |
|---|---|---|---|---|
| au-journal-ph-opera | cut54 | 悉尼歌剧院+海港大桥黄昏拍立得 | 🇦🇺 悉尼 | journal photo |
| au-journal-ph-bondi | cut64 | 邦迪海滩拍立得 | 🇦🇺 悉尼 | journal photo |
| au-journal-ph-bluemtn | cut60 | 蓝山三姐妹峰拍立得 | 🇦🇺 蓝山 | journal photo |
| au-journal-ph-reef | cut88 | 大堡礁浮潜/珊瑚拍立得 | 🇦🇺 凯恩斯 | journal photo |
| au-journal-ph-daintree | cut78 | 戴恩树雨林木栈道到海拍立得 | 🇦🇺 凯恩斯 | journal photo |
| au-journal-ph-cairns | cut68 | 凯恩斯泻湖/滨海拍立得 | 🇦🇺 凯恩斯 | journal photo |
| au-journal-stamp-opera | cut87 | 歌剧院邮票(竖) | 🇦🇺 | journal stamp st-a/st-b |
| au-journal-stamp-kangaroo | cut80 | 袋鼠邮票(竖) | 🇦🇺 | journal stamp st-a/st-b |
| au-journal-stamp-reef | cut71 | 大堡礁邮票(横) | 🇦🇺 | journal stamp st-wide |
| au-journal-stamp-cliff | cut81 | 砂岩峰邮票(竖) | 🇦🇺 蓝山 | journal stamp |
| au-journal-card-opal | cut10 | Opal 交通卡 | 🇦🇺 悉尼 | journal img prop |
| au-journal-ticket-cable | cut24 | 缆车票根 | 🇦🇺 凯恩斯 | journal img prop |
| au-noir-hero | webp110 | 南天银河下的客机(封面底片) | 🇦🇺(泛) | noir plate 0 |
| au-noir-sydney | webp136 | 悉尼港夜景底片 | 🇦🇺 悉尼 | noir plate |
| au-noir-coast | webp117 | 东海岸崖边夜景 | 🇦🇺 悉尼 | noir plate |
| au-noir-bluemtn | webp98 | 蓝山夜色 | 🇦🇺 蓝山 | noir plate |
| au-noir-reef | webp85 | 大堡礁夜航 | 🇦🇺 凯恩斯 | noir plate |
| au-noir-rainforest | webp131 | 雨林夜 | 🇦🇺 凯恩斯 | noir plate |
| au-noir-dawn | webp72 | 黎明归航 | 🇦🇺(泛) | noir plate |

## 14 北欧/挪威 2026 测试行程资产(2026-08-15,Opus 测试员生成,$0.25;sheet 母图 nordic-journal-sheet-photo / -props 见 manifest)— 17
两枚压花(fern/heather)零地域,已同时列入第 12 节通用件;`nordic-noir-aurora` 极光可供任何北极圈行程复用。

| 基名 | 变体(KB) | 内容 | 地域 | 用法 |
|---|---|---|---|---|
| nordic-journal-ph-opera | cut39 | 奥斯陆歌剧院白色斜坡拍立得 | 🇳🇴 奥斯陆 | journal photo |
| nordic-journal-ph-flamtrain | cut57 | 弗洛姆铁路观景火车拍立得 | 🇳🇴 弗洛姆 | journal photo |
| nordic-journal-ph-fjordferry | cut40 | 纳柔伊峡湾渡轮船头拍立得 | 🇳🇴 峡湾 | journal photo |
| nordic-journal-ph-stegastein | cut45 | 斯泰加斯坦观景台拍立得 | 🇳🇴 峡湾 | journal photo |
| nordic-journal-ph-bryggen | cut50 | 卑尔根布吕根木屋拍立得 | 🇳🇴 卑尔根 | journal photo |
| nordic-journal-ph-floyen | cut31 | 弗洛伊恩山俯瞰卑尔根拍立得 | 🇳🇴 卑尔根 | journal photo |
| nordic-journal-stamp-fjord | cut73 | 峡湾邮票 NORGE(竖) | 🇳🇴 | journal stamp st-a/st-b |
| nordic-journal-stamp-stave | cut68 | 木板教堂邮票(竖) | 🇳🇴 | journal stamp st-a/st-b |
| nordic-journal-stamp-aurora | cut67 | 极光邮票(横) | 🇳🇴 | journal stamp st-wide |
| nordic-journal-ticket-ferry | cut34 | 渡轮票根 | 🇳🇴 | journal img prop |
| nordic-journal-flora-fern | cut45 | 北欧蕨类压花 | 通用(压花无地域) | journal flora stem |
| nordic-journal-flora-heather | cut37 | 石楠压花 | 通用(压花无地域) | journal flora stem |
| nordic-noir-hero | webp36 | 峡湾夜航封面底片 | 🇳🇴(泛) | noir plate 0 |
| nordic-noir-oslo | webp101 | 奥斯陆夜景 | 🇳🇴 奥斯陆 | noir plate |
| nordic-noir-fjord | webp49 | 峡湾夜色 | 🇳🇴 峡湾 | noir plate |
| nordic-noir-bergen | webp167 | 卑尔根夜景 | 🇳🇴 卑尔根 | noir plate |
| nordic-noir-aurora | webp75 | 极光(泛北极圈通用) | 🇳🇴/北极圈通用 | noir plate |

## 15 日本 2026(伦敦出发,英文) 测试行程资产(2026-08-15,插画+Zine,$0.41;sheet 母图见 manifest)— 25
地域绑定件只在同国行程复用;标「通用」的可跨行程。行内容按 stem 推断,复用前打开图核一眼。

| 基名 | 变体(KB) | 内容(按 stem 推断,复用前打开看) | 地域 | 用法 |
|---|---|---|---|---|
| japan-bamboo | cut56 sm11 | bamboo | 🇯🇵 | illustrated/zine |
| japan-cover-hero | webp112 | cover hero | 🇯🇵 | illustrated |
| japan-gate | cut57 md53 sm7 | gate | 🇯🇵 | illustrated/zine |
| japan-lantern | cut32 sm7 | lantern | 🇯🇵 | illustrated/zine |
| japan-maple | cut68 md73 sm9 | maple | 🇯🇵 | illustrated/zine |
| japan-onsen | cut36 sm7 | onsen | 🇯🇵 | illustrated/zine |
| japan-pagoda | cut34 sm6 | pagoda | 🇯🇵 | illustrated/zine |
| japan-ph-fushimi | cut52 | ph fushimi | 🇯🇵 | illustrated/zine |
| japan-ph-hamarikyu | cut52 | ph hamarikyu | 🇯🇵 | illustrated/zine |
| japan-ph-kiyomizu | cut48 | ph kiyomizu | 🇯🇵 | illustrated/zine |
| japan-ph-meiji | cut54 | ph meiji | 🇯🇵 | illustrated/zine |
| japan-ph-owakudani | cut51 | ph owakudani | 🇯🇵 | illustrated/zine |
| japan-ph-tsukiji | cut47 | ph tsukiji | 🇯🇵 | illustrated/zine |
| japan-ropeway | cut50 sm9 | ropeway | 🇯🇵 | illustrated/zine |
| japan-stage | cut75 md63 sm7 | stage | 🇯🇵 | illustrated/zine |
| japan-stall | cut43 sm7 | stall | 🇯🇵 | illustrated/zine |
| japan-teahouse | cut53 sm8 | teahouse | 🇯🇵 | illustrated/zine |
| japan-torii | cut33 sm7 | torii | 🇯🇵 | illustrated/zine |
| japan-train | cut27 sm4 | 白蓝新干线车头(三四分之一角) | 通用(已入 §12)| illustrated/zine |
| japan-zine-arashiyama | webp460 | zine arashiyama | 🇯🇵 | zine |
| japan-zine-cover | webp298 | zine cover | 🇯🇵 | zine |
| japan-zine-hakone | webp108 | zine hakone | 🇯🇵 | zine |
| japan-zine-momiji | webp216 | zine momiji | 🇯🇵 | zine |
| japan-zine-toji | webp90 | zine toji | 🇯🇵 | zine |
| japan-zine-tokyo | webp111 | zine tokyo | 🇯🇵 | zine |

## 16 中国大陆 2026(纽约出发,英文) 测试行程资产(2026-08-15,黏土+闪屏,$0.30;sheet 母图见 manifest)— 23
地域绑定件只在同国行程复用;标「通用」的可跨行程。行内容按 stem 推断,复用前打开图核一眼。

| 基名 | 变体(KB) | 内容(按 stem 推断,复用前打开看) | 地域 | 用法 |
|---|---|---|---|---|
| china-clay-food | cut26 | 黏土竹蒸笼开盖露四只包子 + 一缕蒸汽 | 看行程(中华菜系,非地标)| clay |
| china-clay-pagoda | cut26 | clay pagoda | 🇨🇳 | clay |
| china-clay-palace | cut36 | clay palace | 🇨🇳 | clay |
| china-clay-title | cut100 md30 | clay title | 🇨🇳 | clay |
| china-clay-train | cut21 | 黏土高铁头车(白身红条)+ 灰轨 | 通用(已入 §12)| clay |
| china-clay-wall | cut28 | clay wall | 🇨🇳 | clay |
| china-clay-warriors | cut40 | clay warriors | 🇨🇳 | clay |
| china-splash-hero | cut134 md56 | splash hero | 🇨🇳 | splash |
| china-splash-m-dumpling | cut34 | 厚涂竹蒸笼吉祥物(带眼睛)开盖露包子 | 看行程(中华菜系,非地标)| splash |
| china-splash-m-lantern | cut30 | splash m lantern | 🇨🇳 | splash |
| china-splash-m-panda | cut34 | splash m panda | 🇨🇳 | splash |
| china-splash-m-tea | cut19 | splash m tea | 🇨🇳 | splash |
| china-splash-m-warrior | cut32 | splash m warrior | 🇨🇳 | splash |
| china-splash-pagoda | cut49 sm8 | splash pagoda | 🇨🇳 | splash |
| china-splash-palace | cut60 sm8 | splash palace | 🇨🇳 | splash |
| china-splash-strip-beijing | cut54 | splash strip beijing | 🇨🇳 | splash |
| china-splash-strip-xian | cut48 | splash strip xian | 🇨🇳 | splash |
| china-splash-tiantan | cut54 sm8 | splash tiantan | 🇨🇳 | splash |
| china-splash-title | cut238 md56 | splash title | 🇨🇳 | splash |
| china-splash-train | cut42 sm7 | 厚涂高铁头车贴纸(圆车灯眼睛) | 通用(已入 §12)| splash |
| china-splash-veh-train | cut27 | 厚涂高铁行驶浮岛(`vehicle` 位) | 通用(已入 §12)| splash |
| china-splash-wall | cut51 sm8 | splash wall | 🇨🇳 | splash |
| china-splash-warriors | cut51 sm9 | splash warriors | 🇨🇳 | splash |

## 17 意大利 2026(新加坡出发,中文) 测试行程资产(2026-08-15,玻璃+穿越,$0.36;sheet 母图见 manifest)— 6
地域绑定件只在同国行程复用;标「通用」的可跨行程。行内容按 stem 推断,复用前打开图核一眼。

| 基名 | 变体(KB) | 内容(按 stem 推断,复用前打开看) | 地域 | 用法 |
|---|---|---|---|---|
| italy-glass-arno | webp210 | glass arno | 🇮🇹 | glass |
| italy-glass-dawn | webp32 | glass dawn | 🇮🇹 | glass |
| italy-glass-hero | webp168 | glass hero | 🇮🇹 | glass |
| italy-glass-laguna | webp111 | glass laguna | 🇮🇹 | glass |
| italy-glass-roma | webp238 | glass roma | 🇮🇹 | glass |
| italy-glass-sky | webp31 | glass sky | 🇮🇹 | glass |

## 18 墨西哥 2026(柏林出发,英文) 测试行程资产(2026-08-15,手账+夜航,$0.2820;sheet 母图 mexico-journal-sheet-photo / -props 见 manifest)— 18
地域绑定件只在墨西哥行程复用;`mexico-journal-ticket-ado` 画面零文字零地标,已同时列入 §12 通用件。夜航六张全部实景,`mexico-noir-hero` 是机翼+高原灯海,偏泛但仍带墨西哥城地貌。

| 基名 | 变体(KB) | 内容与用途 | 地域 | 主题 |
|---|---|---|---|---|
| mexico-journal-ph-bellasartes | cut58 | 美术宫彩色玻璃穹顶+橙瓦俯瞰(金色时刻) | 🇲🇽 墨西哥城 | journal photo |
| mexico-journal-ph-teotihuacan | cut50 | 亡灵大道尽头的阶梯金字塔 | 🇲🇽 特奥蒂瓦坎 | journal photo |
| mexico-journal-ph-casaazul | cut71 | 钴蓝院墙+绿仙人掌盆栽(蓝屋) | 🇲🇽 科约阿坎 | journal photo |
| mexico-journal-ph-marigold | cut87 | 整墙万寿菊花市摊(手账封面用) | 🇲🇽 | journal photo |
| mexico-journal-ph-panteon | cut64 | 亡灵节烛光墓园 | 🇲🇽 瓦哈卡 | journal photo |
| mexico-journal-ph-montealban | cut78 | 削平山顶石台广场俯瞰谷地 | 🇲🇽 阿尔班山 | journal photo |
| mexico-journal-ph-loom | cut65 | 脚踏织机+半织几何毯+染色毛线 | 🇲🇽 瓦哈卡(工艺) | journal photo |
| mexico-journal-ph-jalatlaco | cut57 | 鹅卵石窄巷+整面彩绘壁画 | 🇲🇽 瓦哈卡 | journal photo |
| mexico-journal-stamp-catrina | cut87 | 骷髅贵妇羽帽侧影邮票(墨紫,竖) | 🇲🇽 | journal stamp st-a/st-b |
| mexico-journal-stamp-pyramid | cut83 | 阶梯金字塔邮票(赭红,竖) | 🇲🇽 | journal stamp st-a/st-b |
| mexico-journal-stamp-alebrije | cut83 | 彩绘木雕神兽邮票(青+橙,横) | 🇲🇽 | journal stamp st-wide |
| mexico-journal-ticket-ado | cut35 | 长途巴士票根:巴士线描+序列号,画面无字无地标 | **通用**(见 §12) | journal img prop |
| mexico-noir-hero | webp161 | 凌晨两点高原盆地城市灯海+左下机翼剪影 | 🇲🇽 墨西哥城(泛) | noir plate 0 |
| mexico-noir-centro | webp138 | 雨夜大道尽头泛光的白色大理石剧院 | 🇲🇽 墨西哥城 | noir plate |
| mexico-noir-piramides | webp165 | 星空下两座金字塔夹住笔直的亡灵大道 | 🇲🇽 特奥蒂瓦坎 | noir plate |
| mexico-noir-panteon | webp137 | 亡灵节墓园:数百烛火+万寿菊拱+铜管乐队剪影 | 🇲🇽 瓦哈卡 | noir plate |
| mexico-noir-oaxaca | webp147 | 双塔巴洛克教堂+剪纸旗+提灯面具游行 | 🇲🇽 瓦哈卡 | noir plate |
| mexico-noir-montealban | webp112 | 山顶石台夜色+谷地灯火+前景龙舌兰 | 🇲🇽 阿尔班山 | noir plate |

## 19 摩洛哥 2026(伦敦出发,英文) 测试行程资产(2026-08-15,玻璃+穿越,$0.3624;5 张 portal 种子帧只有 png,见 manifest)— 6
玻璃/夜航/穿越三个主题**结构上没有可复用件**(只吃 16:9 底片和 i2v 种子帧,而当时 §12 一张 16:9 都没有,测试员通读 §12 白跑一趟)——本节的 `morocco-glass-dawn` 已补进 §12,成为第一件通用 16:9 底片。

| 基名 | 变体(KB) | 内容与用途 | 地域 | 主题 |
|---|---|---|---|---|
| morocco-glass-hero | webp117 | 赭玫瑰土屋顶海+方形宣礼塔+远处阿特拉斯雪线(封面) | 🇲🇦 马拉喀什 | glass 背景层 |
| morocco-glass-atlas | webp209 | 土坯堡垒村落俯瞰+棕榈绿带+红褐山脊 | 🇲🇦 艾特本哈杜 | glass 背景层 |
| morocco-glass-fes | webp212 | 极密麦地那平屋顶+绿瓦锥顶+方宣礼塔 | 🇲🇦 非斯 | glass 背景层 |
| morocco-glass-blue | webp275 | 整城粉蓝白房+阶梯巷+背后灰岩峰 | 🇲🇦 舍夫沙万 | glass 背景层 |
| morocco-glass-dunes | webp43 | 沙丘脊线+三只骆驼商队剪影 | 🇲🇦 梅尔祖卡 | glass 背景层 |
| morocco-glass-dawn | webp53 | 海滨黎明:平静海面+沙滩弧线+远处白屋剪影,无地标 | **通用**(见 §12) | glass 收官段 |

**穿越版视频不进 repo**:5 张 i2v 种子帧 `morocco-portal-{marrakech,ait,merzouga,fes,chefchaouen}-w`(1536×864 png,**不嵌页面**,manifest 有条目、文件留在 trips/)生成 **9 条 mp4** —— 5 条 dive(`ma01`-`ma05`)+ 4 条 link(`ma01-ma02` … `ma04-ma05`),存放在 **`trips/test-morocco-2026/portal/`**,mp4 合计 ≈16MB,整个 `portal/` 目录(含 `chain-frames/` 帧链 QA 图)**23MB**,体积原因不并入 `themes/assets/`。5 个世界 = 马拉喀什 / 艾特本哈杜 / 梅尔祖卡沙丘 / 非斯 / 舍夫沙万(逐条 scene/motion/ambience 见 `trips/test-morocco-2026/portal-worlds.json`)。

## 20 土耳其 2026(上海出发,中文) 测试行程资产(2026-08-15,插画+黏土,$0.2594;sheet 母图 turkey-sheet-illus / turkey-clay-sheet-figs 见 manifest)— 19
`turkey-balloon` 无地标已入 §12;`turkey-shanghai` 是**出发地**上海(塞进插画 sheet 第 8 格生成的 `end.hero`,成本为零),别当土耳其件用;`turkey-clay-title` 带中文字「九万里风」,**本行程专用**,任何别的行程都不能复用。

| 基名 | 变体(KB) | 内容与用途 | 地域 | 主题 |
|---|---|---|---|---|
| turkey-cover-hero | webp102 | 插画全幅封面(上 2/3 留白托标题) | 🇹🇷 | 插画 |
| turkey-hagia | cut35 sm9 | 灰粉大穹顶+四座细宣礼塔 | 🇹🇷 伊斯坦布尔 | 插画 / zine |
| turkey-bazaar | cut56 sm8 | 条纹拱券有顶市集廊+吊灯+叠毯 | 🇹🇷 伊斯坦布尔 | 插画 / zine |
| turkey-chimney | cut38 sm8 | 锥形仙人烟囱群+洞窟小窗 | 🇹🇷 卡帕多西亚 | 插画 / zine |
| turkey-balloon | cut27 sm8 | 四只条纹热气球升空,无地标 | **通用**(见 §12) | 插画 / zine |
| turkey-pamukkale | cut31 sm7 | 白色钙华梯池+浅青池水 | 🇹🇷 棉花堡 | 插画 / zine |
| turkey-ferry | cut32 sm6 | 白色渡轮+圆顶石塔(少女塔) | 🇹🇷 伊斯坦布尔 | 插画 / zine |
| turkey-underground | cut45 sm8 | 地下石城通道+圆石门+提灯 | 🇹🇷 卡帕多西亚 | 插画 / zine |
| turkey-shanghai | cut33 sm8 | 上海外滩天际线(尖塔+开瓶器) | 🇨🇳 上海(**出发地**) | 插画 `end.hero` |
| turkey-clay-hagia | cut26 | 黏土灰粉穹顶清真寺+四塔 | 🇹🇷 伊斯坦布尔 | clay |
| turkey-clay-bazaar | cut36 | 黏土集市摊:条纹雨棚+卷毯+香料锥 | 🇹🇷 伊斯坦布尔 | clay |
| turkey-clay-chimney | cut25 | 黏土仙人烟囱三锥+洞窗 | 🇹🇷 卡帕多西亚 | clay |
| turkey-clay-pamukkale | cut26 | 黏土钙华梯池(浅青水) | 🇹🇷 棉花堡 | clay |
| turkey-clay-mosque | cut29 | 黏土奥斯曼清真寺庭院+双塔拱门 | 🇹🇷 | clay |
| turkey-clay-tea | cut36 | 黏土郁金香茶杯×2+铜托盘+粉方糖 | 🇹🇷(土耳其茶具) | clay |
| turkey-clay-title | cut91 lg75 md53 sm10 | 黏土 3D 中文标题「九万里风」 | **本行程专用**(带字) | clay 标题贴纸 |
| turkey-strip-istanbul | cut157 | 地形带:圣索菲亚+蓝寺+塔+渡轮+柏树 | 🇹🇷 伊斯坦布尔 | clay band(`to:#bfe0e6`)|
| turkey-strip-cappadocia | cut142 | 地形带:仙人烟囱+洞穴屋+三只气球 | 🇹🇷 卡帕多西亚 | clay band(`to:#f0cba4`)|
| turkey-strip-pamukkale | cut151 | 地形带:钙华梯池+希拉波利斯剧场断柱 | 🇹🇷 棉花堡 | clay band(`to:#cfe7ea`)|

## 21 越南 2026(深圳出发,中文) 测试行程资产(2026-08-15/16,Zine+闪屏,$0.4566;sheet 母图 vietnam-zine-sheet-photo/-props、vietnam-splash-sheet-islands/-props/-strips 见 manifest)— 34
本库单趟最大的一节(11 次调用切出 34 个基名 / 49 个 webp)。`vietnam-ph-train` 与 `vietnam-splash-i-train` 无地标,已同时列入 §12;其余斗笠/灯笼/粉碗/滴滤咖啡/簸箕船一类**是越南专属物件,不是地标但同样禁跨行程**。

| 基名 | 变体(KB) | 内容与用途 | 地域 | 主题 |
|---|---|---|---|---|
| vietnam-zine-cover | webp230 | 晨雾中喀斯特岛柱+木帆船(竖版封面) | 🇻🇳 下龙湾 | zine |
| vietnam-zine-hanoi | webp364 | 黑白:窄巷单轨火车街+斗笠挑担(竖) | 🇻🇳 河内 | zine 章头 |
| vietnam-zine-hoian | webp206 | 河边老街夜:成百丝绸灯笼+湿街反光(竖) | 🇻🇳 会安 | zine 章头 |
| vietnam-zine-saigon | webp262 | 芥黄殖民邮局+摩托车流长曝(竖) | 🇻🇳 西贡 | zine 章头 |
| vietnam-zine-mekong | webp186 | 舢板内视角:水椰拱顶运河+斗笠船娘(横,收尾带) | 🇻🇳 湄公三角洲 | zine 收尾 |
| vietnam-ph-pho | webp26 | 夜市塑料矮凳上的牛肉粉 | 🇻🇳 | zine photo |
| vietnam-ph-temple | webp55 | 红漆门+苔瓦庭院+驮碑石龟 | 🇻🇳 河内文庙 | zine photo |
| vietnam-ph-train | webp23 | 卧铺车窗外的海岸晨光(无地标,海岸偏热带) | **通用**(见 §12) | zine photo |
| vietnam-ph-market | webp50 | 有顶市场摊:干香料/辣椒/叠放斗笠 | 🇻🇳 | zine photo |
| vietnam-ph-cave | webp32 | 洞顶天光落在石佛上 | 🇻🇳 岘港五行山 | zine photo |
| vietnam-ph-motos | webp32 | 黄昏殖民市场前的摩托车河(慢门) | 🇻🇳 西贡 | zine photo |
| vietnam-hat | cut31 sm5 | 水粉斗笠(带系带) | 🇻🇳 | zine prop |
| vietnam-lantern | cut28 sm5 | 水粉圆丝绸灯笼+流苏 | 🇻🇳 会安 | zine prop |
| vietnam-pho | cut40 sm7 | 水粉粉碗+架在碗上的筷子 | 🇻🇳 | zine prop |
| vietnam-coffee | cut26 sm5 | 水粉滴滤壶+冰咖啡杯 | 🇻🇳 | zine prop |
| vietnam-basketboat | cut43 sm6 | 水粉圆簸箕船+桨 | 🇻🇳 | zine prop |
| vietnam-scooter | cut54 sm7 | 水粉侧面摩托+后座香草筐 | 🇻🇳 | zine prop |
| vietnam-splash-hero | cut158 md66 | 三根石灰岩柱+帆船+两只簸箕船浮岛(主视觉,**用 md**) | 🇻🇳 下龙湾 | splash |
| vietnam-splash-i-hoankiem | cut35 sm7 | 红拱桥+三层塔小岛 | 🇻🇳 河内还剑湖 | splash 日岛 |
| vietnam-splash-i-karst | cut41 sm6 | 石灰岩柱+盘山道观景亭+小船 | 🇻🇳 下龙湾 | splash 日岛 |
| vietnam-splash-i-train | cut32 sm7 | 绿皮卧铺车厢+亮黄窗+月牙,无地标 | **通用**(见 §12) | splash 日岛 |
| vietnam-splash-i-bridge | cut36 sm9 | 挂满圆灯笼的瓦顶廊桥 | 🇻🇳 会安来远桥 | splash 日岛 |
| vietnam-splash-i-basket | cut45 sm10 | 簸箕船在水椰塘里打转+斗笠船夫 | 🇻🇳 | splash 日岛 |
| vietnam-splash-i-marble | cut36 sm7 | 大理石山洞窟拱+山顶层塔 | 🇻🇳 岘港五行山 | splash 日岛 |
| vietnam-splash-i-postoffice | cut42 sm8 | 芥黄殖民邮局+圆钟+两辆摩托 | 🇻🇳 西贡 | splash 日岛 |
| vietnam-splash-i-sampan | cut49 sm10 | 窄木舢板在运河里 | 🇻🇳 湄公三角洲 | splash 日岛 |
| vietnam-splash-moto | cut44 | 厚涂摩托(圆车灯眼)+香草筐 | 🇻🇳 | splash vehicle |
| vietnam-splash-junk | cut43 | 厚涂锈红蝠翼帆木帆船 | 🇻🇳 下龙湾 | splash vehicle |
| vietnam-splash-hat | cut31 | 厚涂斗笠(笠下小笑脸) | 🇻🇳 | splash mascot |
| vietnam-splash-pho | cut38 | 厚涂粉碗+筷子+青柠 | 🇻🇳 | splash mascot |
| vietnam-splash-lantern | cut29 | 厚涂暖橙丝绸灯笼 | 🇻🇳 会安 | splash mascot |
| vietnam-splash-coffee | cut31 | 厚涂滴滤壶+冰奶咖 | 🇻🇳 | splash mascot |
| vietnam-splash-strip-hanoi | cut70 | 靛紫老城筒子楼天际线剪影+琥珀灯点(两端渐隐) | 🇻🇳 河内 | splash strip |
| vietnam-splash-strip-saigon | cut93 | 深青三角洲水岸+棕榈+钟楼+成排舢板(洋红霞) | 🇻🇳 西贡 | splash strip |

## 22 stock 通用素材包(`stock/`,2026-08-17,$0.9284)— 80 个基名 / 161 webp / 5.2 MB

**这一节是索引入口,细节在 `stock/README.md` 与 `stock/index.json`,别把 stock 件混进上面各节的表。**
用途:agent **既没有原生生图能力、也没有 KEY** 时(`prefs.pictures: "stock"`),仍然交付插画版主题页面——
本包=预生成的插画风(gouache)通用图库。**有生图能力时不用它**:封面/主视觉照旧为本行程现生成(顶部规则不变)。

| 内容 | 数量 | 文件 | 用途 |
|---|---|---|---|
| 地区封面画(16:9 不透明,上 2/3 留白托标题) | 14 | `stock-cover-<archetype>.webp`(55–124 KB) | `cover.hero`,按国家 → archetype 选 |
| 通用场景抠图件 | 30 | `stock-<scene>.cut.webp` + `.sm`(部分 `.md`) | 日章头 `days[date].hero` |
| 世界地标抠图件 | 36 | `stock-<landmark>.cut.webp` + `.sm`(部分 `.md`) | 同上,命中地标关键词时优先 |

- 14 个 archetype:european-old-town / mediterranean-coast / east-asian-temple / southeast-asia /
  tropical-beach / desert-medina / alpine-lake / nordic-fjord / modern-skyline / savanna / rainforest /
  andes-colonial / castle-highlands / north-america-roadtrip。
- `stock/index.json` = 查找表:archetype 关键词、**225 个 ISO2 → archetype**、多语言国名(en/本地/中文 702 条)、
  每个抠图件的多语言关键词、本库已有插画件的国别索引(JP/TR/US/CN)、通用交通件(plane/bus/japan-train/turkey-balloon)。
- 生成记录在 `stock/manifest.stock.json`(25 次调用:14 张封面 + 11 张 3×2 sheet 切 66 件;prompt 骨架照抄
  `japan-cover-hero` / `japan-sheet-cutouts-a`,`style_anchor` 同本库)。PNG 母图按 `themes/**/*.png` 不进 repo。
- ⚠️ **渲染时要加 `--assets themes/assets/stock`**:`data_uri` 只搜 `themes/assets/` 与 plan 所在目录,不递归子目录。
- ⚠️ **图片来源必须写在页面上**(`end.fine` + `cover.credit`,两语版本在 `index.json.notice`)——
  不写就等于把兜底图当定制图交付。
