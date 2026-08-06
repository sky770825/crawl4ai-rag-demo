# crawl4ai 長期累積 SOP (2026-08-06 v2)

> 老蔡:「持續運行,累積大量數據和經驗,讓你自己的整個 SOP 去優化迭代,
> 慢慢減少一些汙染和幻覺,並提升精準度與長效執行的能力」

## 3 大目標 (老蔡原話拆解)

1. **累積大量數據** — 每天自動跑,資料越來越厚
2. **減少污染幻覺** — 智慧去噪 + hash dedup
3. **提升精準度 + 長效執行** — 品質 SOP + 排程 + 監控

## 系統架構 (3 件套)

```
每天每 6 小時:
  1. auto_pipeline.sh (cron) 自動跑
     ├── cumulative_rag.py    累積 RAG (smart dedup)
     ├── build_site.py        重 build 76KB HTML
     └── surge . .            部署公開 URL
  2. Master: rag_data/master_rag.jsonl (1 file per item, append only)
  3. 公開 URL: https://crawl4ai-rag-20260806.surge.sh
```

## 6 大 SOP 模組

### SOP-A: 安裝與環境
- Python **3.11 venv**(`/c/Users/user/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe`)
- 系統 3.14 找不到 pydantic_core (ABI 不相容)
- 必跑: `pip install -e ".[all]" && crawl4ai-setup && crawl4ai-doctor`

### SOP-B: 抓取策略
- **友善站** 1 個 AsyncWebCrawler 跑多次 OK
- **HN/中型站** max 2-3 parallel (會 429)
- **跨站並行** max=4 (Semaphore 控制)
- **SPA 站** 預設不抓 XHR,要 js_code 注入
- **延遲**: 短站 3-5s, 重大站 7-10s

### SOP-C: 智慧去噪 (smart_dedup.py)
- 時間字串: "X hours ago" / "X minutes ago" 過濾
- 跨站固定: "Google News" / "Skip to content" / "Sponsor"
- 短標題 < 6 字中文 / < 8 字英文 過濾
- 已知導覽: `* [手機版]` / `* [App 下載]`
- **5 輪實測**: HN 703 → 553 (過濾 21% 時間雜訊)

### SOP-D: 累積式 Dedup (cumulative_rag.py)
- **SHA256(source::title).hexdigest()[:16]** hash 去重
- 累積 master_rag.jsonl (append only)
- 跑 1 輪 10 站 → +842 條 (第 1 次)
- 跑第 2 輪 → 預期 +50-100 (新聞更新)

### SOP-E: 長效執行 (long_running_test.py)
- **10 分鐘壓力**: 140+ 請求, 記憶體穩定 125-143MB
- 沒有 memory leak (Python GC + 每次 arun 釋放 page)
- 友善站輪詢池 10 站
- 30 分鐘版本改 DURATION_SEC=1800

### SOP-F: 結構化抽取 (llm_extract_ollama.py)
- **LLMConfig(provider="ollama/qwen2.5:7b", api_token="ollama")**
- 0 API key, 完全本地
- 慢 (CPU 7b): 1 頁 ~5 分鐘
- 替代: 用 CSS schema (快, 0 token)

## 9 大踩坑 (canonical, 寫進 skill)

1. ❌ Python 3.14 → 用 3.11 venv
2. ❌ `wait_for=[...]` 傳 list → 必須 string
3. ❌ HN 過度抓 → max 2-3 parallel
4. ❌ 591 SPA → 用 XHR skill
5. ❌ Ptt 18 歲頁 → 需 cookie over18=1
6. ❌ TikTok NoneType → crawl4ai bug
7. ❌ 小紅書台灣 IP 封鎖 → 走既有 skill
8. ❌ `provider=` deprecated → 用 `llm_config=`
9. ❌ time 字串 "X hours ago" 被當標題 → 智慧去噪

## Cron 已設 (long-running 0 token 模式)

- job_id: `65efba3a52de`
- schedule: `every 6h`
- script: `crawl4ai-auto-pipeline.sh`
- no_agent: **True** (零 LLM,純 script,符合 LONG-RUNNING SOP)

## 量化目標 (1 個月後)

- Master RAG: 842 → 30,000 條
- 去重後淨增長: ~5000 條/月
- Cron 跑: 120 次/月, 每次 +50-100
- 公開 URL 部署: 120 次/月
- 智慧去噪規則: 5 → 30 條 (新污染模式累積)

## 給老蔡的觀察

**「精準度」+「長效執行」= 三件事**:
1. 資料越多 dedup 越準(5 輪驗證的污染清單 → 永久過濾)
2. cron 持續跑 = 經驗累積
3. 每次撞牆寫進 SOP = 9 條以後只會越來越強

**這是 30 天後會看到真實效果的累積型系統**。
