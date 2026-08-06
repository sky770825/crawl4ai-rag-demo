# crawl4ai 業務衝刺全紀錄 (2026-08-06 22:00-22:15)

> 老蔡:「執行吧」+ 「你就儘量去做」 — 信心度 ≥ 90 自動衝
> 結果: **6 個業務場景 + 1 公開 demo + 1 GH repo + skill 完備**

## TL;DR

15 分鐘內從工具驗證 → 業務衝刺 → 公開部署。**產生 1193 個 RAG items / 658k chars 政府資料 / 部署公開 demo / push GH repo**。

## 6 戰場結果

| # | 戰場 | 程式 | 結果 | 用途 |
|---|---|---|---|---|
| 1 | 🏠 房市新聞 | real_estate_news_rag.py | **224 高品質新聞** | 客戶問答 RAG |
| 2 | 🏛️ 政府公開 | gov_data_crawl.py | **302k chars** (6 站) | 房仲法規/央行/實價 |
| 3 | 🤖 AI 雷達 | ai_radar.py | **204 items** | AI 新知每日 |
| 4 | 🎬 短劇市場 | short_drama_market.py | **345 B站 videos** | 短劇研究決策 |
| 5 | 🌬️ 防霾紗窗 | poll_tex_kb.py | **76k chars** | Poll-tex 副業務 |
| 6 | 🌐 公開部署 | build_site.py | Surge 上線 | 公開 demo |

## 關鍵 URL

- **Live demo**: https://crawl4ai-rag-20260806.surge.sh (Surge, 200 OK)
- **GH repo**: https://github.com/sky770825/crawl4ai-rag-demo (16 檔, 公開)
- **Skill**: ~/AppData/Local/hermes/skills/web/web-crawl-llm-friendly/SKILL.md

## RAG 資料庫內容 (1.4MB)

```
~/Desktop/crawl4ai/rag_data/
├── house_news_20260806_220429.json      82KB    ETtoday 108 + Yahoo 118 raw
├── house_news_20260806_220429_clean.json 73KB   224 高品質新聞
├── gov_data_20260806_220550.json        2KB     6 站 index
├── 公開資訊觀測站.md                    154KB   上市公司公告
├── 央行_利率政策.md                     44KB
├── 央行_本行業務.md                     44KB
├── 內政部地政司.md                      56KB
├── 平均地權條例.md                      33KB
├── 租賃住宅市場發展條例.md              28KB
├── 公平交易委員會.md                    65KB
├── ai_radar_20260806_220636.json        26KB    GitHub Trending + HN + HF
├── short_drama_market_20260806_220757.json 57KB  B站 AI 短劇 345 videos
├── poll_tex_kb_20260806_220845.json     5KB
├── poll_tex_環保署_空氣品質.md          40KB
├── poll_tex_N95_vs_防霾紗窗.md          33KB
└── poll_tex_空氣清淨機_比較.md          24KB
```

## 全自動衝的 5 個老蔡紅線

1. **「完成 ≠ 部署好」** — Surge 部署 ✅
2. **「不主動問下一步」** — 全程不問,連續做完
3. **「信心度 ≥ 90 自動執行」** — 7/7 todo 自動衝
4. **「不做完不等」** — 撞牆自己換路(591 SPA → 改抓 XHR; 房仲 URL 失效 → 改抓政府)
5. **「HANDOFF 寫檔」** — 本檔 + HANDOFF_2026-08-06.md 雙備份

## 房仲客戶可即時問

- 「央行最新利率」→ 央行 利率政策.md (44k chars)
- 「平均地權條例最新規定」→ 平均地權條例.md
- 「實價登錄怎麼查」→ 內政部地政司.md + lvr.land.moi.gov.tw (但 404, 需查新 URL)
- 「今天房市新聞」→ house_news clean 224 條
- 「N95 vs 防霾紗窗」→ poll_tex N95 vs 防霾紗窗.md

## 短劇研究決策

- B站 9 關鍵字搜尋 345 videos 抓出來
- 涵蓋: AI 短劇 / 短劇 / AI 生成視頻 / 動漫 AI / Seedance / 即夢 / 可靈 / AI 角色
- 看到「萬相Wan3.0即將發布」「可靈 3.0 教程」「Seedance 2.5 完整教程」
- 趨勢: 純享版 + 多集連載 + 同人改編為主

## 8 大踩坑再次總結

1. **Python 3.14 找不到 pydantic_core** → 用 3.11 venv
2. **wait_for 傳 list 會壞** → 必須 string
3. **HN 過度抓會 429** → max 2-3 parallel
4. **591 SPA 抓不到** → 用 XHR skill 替代
5. **Ptt 18 歲頁** → 需 cookie `over18=1`
6. **TikTok NoneType** → crawl4ai 0.9.2 bug
7. **小紅書台灣 IP 封鎖** → 走既有 skill
8. **delay ≠ wait_for** → wait_for 等 DOM, delay 只 sleep

## 下次機會

- 加 LLM extraction 模式 (有 OpenAI/Groq key 可開)
- 591 改打 XHR API (api.591.com.tw/house/list)
- 排程每日早上 8 點跑 RAG 抓取 → 進 Hugo/Notion
- 把 Skill 整合進房仲 LINE bot (`~/Desktop/line-oa-bot`)

## 完整檔案清單

```
~/Desktop/crawl4ai/  (clone 的 upstream, 不 push)
├── *.py (16 個範本)
├── HANDOFF_2026-08-06.md (6.2KB 極限測試報告)
└── rag_data/ (1.4MB RAG 原始資料)

~/Desktop/crawl4ai-rag-demo/  (老蔡自己的 GH repo, public)
├── README.md (3.4KB)
├── HANDOFF_2026-08-06.md
├── real_estate_news_rag.py
├── real_search_demo.py
├── gov_data_crawl.py
├── ai_radar.py
├── short_drama_market.py
├── poll_tex_kb.py
├── build_site.py
├── clean_rag_data.py
├── quick_search_demo.py
├── spa_render_test_v3.py
├── concurrency_test.py
├── llm_extraction_test.py
├── css_schema_test_v2.py
├── anti_bypass_stress_test.py
└── deep_crawl_test.py

~/AppData/Local/hermes/skills/web/web-crawl-llm-friendly/SKILL.md (6.2KB skill)
```

## 結論

**crawl4ai 從「能跑通」到「能用在 6 個業務場景」,15 分鐘跑完。**

老蔡的房仲/防霾業務明天就能用這個 demo 給客戶展示「即時新聞 + 法規 + AI 雷達」。

下一步如果老蔡要,可以排程每日跑 → 推 LINE bot,或開 LLM extraction 進階版。
