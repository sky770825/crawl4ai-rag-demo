"""戰場 4: AI 短劇 / 視頻市場 — 老蔡短劇研究決策依據
- B站 AI 短劇搜尋
- YouTube AI 短劇搜尋
- 抖音 web 搜尋
- B站 AI 短劇 (純中文)
"""
import asyncio
import json
import os
import re
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

OUT_DIR = os.path.expanduser("~/Desktop/crawl4ai/rag_data")
os.makedirs(OUT_DIR, exist_ok=True)

BV_RE = re.compile(r'BV([A-Za-z0-9]+)')

TARGETS = [
    ("B站 搜尋 AI 短劇", "https://search.bilibili.com/all?keyword=AI%E7%9F%AD%E5%8A%87"),
    ("B站 搜尋 AI 短劇 中文", "https://search.bilibili.com/all?keyword=AI短劇"),
    ("B站 搜尋 短劇", "https://search.bilibili.com/all?keyword=短劇"),
    ("B站 搜尋 AI 生成 視頻", "https://search.bilibili.com/all?keyword=AI%E7%94%9F%E6%88%90%E8%A7%86%E9%A2%91"),
    ("B站 搜尋 動漫 AI", "https://search.bilibili.com/all?keyword=AI动漫"),
    ("B站 搜尋 Seedance", "https://search.bilibili.com/all?keyword=Seedance"),
    ("B站 搜尋 即夢AI", "https://search.bilibili.com/all?keyword=即梦AI"),
    ("B站 搜尋 可靈", "https://search.bilibili.com/all?keyword=可灵"),
    ("B站 搜尋 AI 角色", "https://search.bilibili.com/all?keyword=AI%E8%A7%92%E8%89%B2"),
    ("抖音 web 搜尋 AI 短劇", "https://www.douyin.com/search/AI%E7%9F%AD%E5%8A%87"),
]

async def main():
    results = []
    async with AsyncWebCrawler(headless=True) as crawler:
        for label, url in TARGETS:
            print(f"\n=== {label} ===")
            try:
                config = CrawlerRunConfig(
                    delay_before_return_html=3.5,
                    page_timeout=30000,
                )
                result = await crawler.arun(url=url, config=config)
                if not result.success:
                    print(f"  ✗ failed: {result.error_message[:100]}")
                    results.append({"label": label, "url": url, "status": "FAIL"})
                    continue
                md = result.markdown or ""
                # B站特別處理: 找 BV id
                bv_ids = list(set(BV_RE.findall(md)))
                bv_full = [f"BV{x}" for x in bv_ids]
                # 找標題 (含 video/BV 的行)
                items = []
                for line in md.split("\n"):
                    line = line.strip()
                    if "video/BV" in line:
                        m = re.search(r'\[(.*?)\]\(https?://www\.bilibili\.com/video/(BV[A-Za-z0-9]+)', line)
                        if m:
                            title = m.group(1).strip()
                            if 4 < len(title) < 100:
                                items.append({"title": title, "bv": m.group(2)})
                # 去重
                seen = set()
                unique = []
                for it in items:
                    if it["bv"] in seen:
                        continue
                    seen.add(it["bv"])
                    unique.append(it)
                print(f"  ✓ {len(unique)} items, BV={len(bv_full)}, md={len(md)} chars")
                for it in unique[:5]:
                    print(f"    → [{it['bv']}] {it['title'][:50]}")
                results.append({
                    "label": label,
                    "url": url,
                    "status": "OK",
                    "count": len(unique),
                    "items": unique,
                    "fetched_at": datetime.now().isoformat(),
                })
            except Exception as e:
                print(f"  ✗ EXC: {e}")
                results.append({"label": label, "url": url, "status": "EXC", "error": str(e)})

    out = os.path.join(OUT_DIR, f"short_drama_market_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    total = sum(r.get("count", 0) for r in results)
    print(f"\n=== 完成: {total} 短劇 videos → {out} ===")

asyncio.run(main())
