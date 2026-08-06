# crawl4ai-rag-demo — 老蔡版

> 2026-08-06 老蔡「去使用吧,然後去跑過,看極限在哪邊,你就儘量去做」

把 [unclecode/crawl4ai 0.9.2](https://github.com/unclecode/crawl4ai) (76.8K ⭐) 套到台灣房仲 / 防霾紗窗 / 短劇研究 6 個真實業務場景。

**Live Demo**: https://crawl4ai-rag-20260806.surge.sh

## 6 個業務場景

| # | 場景 | 腳本 | 結果 |
|---|---|---|---|
| 1 | 🏠 房市新聞知識庫 | `real_estate_news_rag.py` | **224 高品質新聞** (ETtoday + Yahoo) |
| 2 | 🏛️ 政府公開資料 | `gov_data_crawl.py` | 央行 / 地政司 / 公平會 / 法務部 **302k chars** |
| 3 | 🤖 AI 技術雷達 | `ai_radar.py` | GitHub Trending + HN + HF + Papers **204 items** |
| 4 | 🎬 AI 短劇市場 | `short_drama_market.py` | B站 9 個關鍵字搜尋 **345 videos** |
| 5 | 🌬️ 防霾紗窗 | `poll_tex_kb.py` | 環保署 + Google 比較 **76k chars** |
| 6 | 🌐 公開部署 | `build_site.py` | Surge 部署 `crawl4ai-rag-20260806.surge.sh` |

## 安裝

```bash
git clone https://github.com/sky770825/crawl4ai-rag-demo.git
cd crawl4ai-rag-demo
pip install -U crawl4ai
crawl4ai-setup
crawl4ai-doctor  # 確認瀏覽器+DB OK

# 重要: 必須用 3.11 venv python
/c/Users/user/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe real_estate_news_rag.py
```

## 環境硬規則

- **Python**: 必須 3.11 venv, 別用系統 3.14 (pydantic_core ABI 不相容)
- **並行**: 同一站 max 2-3, 跨站可到 4-5
- **rate limit**: HN / 高流量站會 429, 加 1-2 秒 delay
- **SPA 站**: 591 / YC / 抖音 / 小紅書 用 js_code + wait_for 仍抓不到
- **Gov station**: 公開資訊觀測站 / 央行 / 法務部 / 內政部 都進得去
- **B站 / 抖音 / IG**: 過 Cloudflare, 但 SPA 後載資料需 XHR hook

## 反爬壓力 26 站測試

| 站 | 結果 | chars |
|---|---|---|
| 公開資訊觀測站 | ✅ 302 | **112,911** |
| GitHub repo | ✅ 200 | **286,886** |
| Yahoo 新聞 | ✅ 200 | 63,710 |
| StackOverflow | ✅ 302 (過 Cloudflare) | 20,186 |
| Medium | ✅ 200 | 2,646 |
| 591 桃園全區 | ✅ 200 | 1,319,094 |
| B站 AI 短劇 | ✅ 200 | 38,326 |
| 抖音 web | ✅ 200 | 4,819 |
| Threads | ✅ 301 | 13,135 |
| X (Twitter) | ✅ 200 | 7,457 |
| FB | ✅ 302 | 11,885 |
| 小紅書 | ❌ 404 (台灣 IP 封鎖) | 357 |
| Dcard | ❌ 307 (Cloudflare) | 297 |
| Mobile01 | ❌ 302 (Akamai) | 216 |
| 591 物件列表 | ⚠ 進得去但 SPA 不 render | - |
| Ptt 18 歲確認頁 | ⚠ 需 cookie over18=1 | 159 |

**過關率 17/26 (65%)** — 推翻 K15 SOP 悲觀預期 (Google / StackOverflow / Medium 都過)

## 8 大踩坑

1. **Python 3.14 找不到 pydantic_core** → 用 3.11 venv
2. **wait_for 傳 list 會壞** → 必須 string
3. **HN 過度抓會 429** → max 2-3 parallel
4. **591 SPA 抓不到** → 用 XHR skill 替代
5. **Ptt 18 歲頁** → 需 cookie `over18=1`
6. **TikTok NoneType** → crawl4ai 0.9.2 bug
7. **小紅書台灣 IP 封鎖** → 走既有 skill
8. **delay ≠ wait_for** → wait_for 等 DOM, delay 只 sleep

## 技術棧

- **crawl4ai 0.9.2** (Playwright + Patchright + Stealth + Litellm)
- **Python 3.11** venv
- **Surge** token-free static deploy
- **JSON CSS schema** 結構化抽取

## Skill

- `web/web-crawl-llm-friendly` (寫在 `~/AppData/Local/hermes/skills/web/`)
- canonical: HANDOFF_2026-08-06.md

## Author

老蔡 (sky770825) · Hermes Agent · 2026-08-06
