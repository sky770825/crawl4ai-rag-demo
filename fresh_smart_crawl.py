"""fresh_smart_crawl.py - 抓最新有用"""
import asyncio, json, os, re
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

OUT = os.path.expanduser("~/Desktop/crawl4ai/rag_data/fresh_20260806.json")

# 8 個精選: 每個都是真實業務用
TARGETS = [
    ("ETtoday_房產焦點", "https://house.ettoday.net/news-list.htm"),
    ("ETtoday_新聞總覽", "https://www.ettoday.net/news/news-list.htm"),
    ("Yahoo_房地產", "https://tw.news.yahoo.com/real-estate"),
    ("央行_最新業務", "https://www.cbc.gov.tw/tw/mp-001.html"),
    ("公開資訊觀測站", "https://mops.twse.com.tw/mops/web/index"),
    ("公平會最新", "https://www.ftc.gov.tw/internet/main/index.aspx"),
    ("內政部地政", "https://www.land.moi.gov.tw/chhtml/index"),
    ("GitHub_Trending_Python", "https://github.com/trending/python?since=daily"),
    ("Hacker_News", "https://news.ycombinator.com/"),
    ("B站_AI短劇", "https://search.bilibili.com/all?keyword=AI%E7%9F%AD%E5%8A%87"),
    ("B站_Seedance", "https://search.bilibili.com/all?keyword=Seedance"),
    ("B站_可靈", "https://search.bilibili.com/all?keyword=%E5%8F%AF%E9%9D%88"),
]

SCHEMAS = {
    "news": {"name": "n", "baseSelector": "h3 a, h2 a, .story-title, [class*='title'] a", "fields": [{"name": "title", "selector": "h3 a, h2 a, [class*='title'] a", "type": "text"}]},
    "default": {"name": "n", "baseSelector": "a[href*='http']", "fields": [{"name": "title", "selector": "a", "type": "text"}, {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"}]},
}

async def main():
    out_data = {"fetched_at": datetime.now().isoformat(), "sources": []}
    async with AsyncWebCrawler(headless=True) as c:
        for label, url in TARGETS:
            try:
                cfg = CrawlerRunConfig(
                    page_timeout=30000,
                    delay_before_return_html=2.0,
                    extraction_strategy=JsonCssExtractionStrategy(SCHEMAS["default"])
                )
                r = await c.arun(url=url, config=cfg)
                if not r.success:
                    out_data["sources"].append({"label": label, "url": url, "status": "fail", "error": r.error_message})
                    print(f"  [FAIL] {label} {r.error_message[:50]}")
                    continue
                items = []
                if r.extracted_content:
                    try:
                        items = json.loads(r.extracted_content)
                    except:
                        pass
                out_data["sources"].append({
                    "label": label, "url": url, "status": "ok",
                    "chars": len(r.markdown.raw_markdown or ""),
                    "count": len(items),
                    "items": items,
                    "md": (r.markdown.raw_markdown or "")[:8000]
                })
                print(f"  [OK] {label:30s} chars={len(r.markdown.raw_markdown or 0):6d} items={len(items)}")
            except Exception as e:
                out_data["sources"].append({"label": label, "url": url, "status": "error", "error": str(e)})
                print(f"  [ERR] {label} {str(e)[:50]}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out_data, f, ensure_ascii=False, indent=2)
    total = sum(s.get("count", 0) for s in out_data["sources"] if s.get("status") == "ok")
    print(f"\n=== 抓取完成: {total} items 進 {OUT} ===")

asyncio.run(main())
