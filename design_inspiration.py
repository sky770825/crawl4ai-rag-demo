"""design_inspiration.py"""
import asyncio, json, os
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
OUT = os.path.expanduser("~/Desktop/crawl4ai/rag_data/design_inspiration")
os.makedirs(OUT, exist_ok=True)
P = [
    ["site_inspire", "https://www.siteinspire.com/"],
    ["awwwards", "https://www.awwwards.com/"],
    ["land_book", "https://land-book.com/"],
    ["minimal_gallery", "https://minimal.gallery/"],
    ["godly", "https://godly.website/"],
    ["mobbin", "https://mobbin.com/"],
    ["dribbble", "https://dribbble.com/shots/popular"],
]

async def main():
    results = []
    async with AsyncWebCrawler(headless=True) as crawler:
        cfg = CrawlerRunConfig(page_timeout=15000, delay_before_return_html=2.0, verbose=False)
        for label, url in P:
            try:
                r = await crawler.arun(url=url, config=cfg)
                results.append({"label": label, "url": url, "status": r.status_code, "chars": len(r.markdown.raw_markdown or ""), "md": (r.markdown.raw_markdown or "")[:3000]})
                print(f"  [{r.status_code}] {label:20s} chars={len(r.markdown.raw_markdown or ''):6d}")
            except Exception as e:
                print(f"  [EXC] {label}: {str(e)[:60]}")
    fp = os.path.join(OUT, f"design_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    open(fp, "w", encoding="utf-8").write(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\nWrote: {fp}")

asyncio.run(main())
