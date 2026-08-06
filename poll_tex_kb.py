"""戰場 5: 防霾紗窗 / 空氣品質 / 過濾知識 — Poll-tex 副業務"""
import asyncio
import json
import os
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

OUT_DIR = os.path.expanduser("~/Desktop/crawl4ai/rag_data")
os.makedirs(OUT_DIR, exist_ok=True)

TARGETS = [
    ("環保署 空氣品質", "https://airtw.moenv.gov.tw/"),
    ("環保署 PM2.5", "https://airtw.moenv.gov.tw/Information/Central/Central"),
    ("Poll-tex 官網", "https://www.poll-tex.com/"),
    ("Poll-tex 產品", "https://www.poll-tex.com/products"),
    ("Poll-tex 關於我們", "https://www.poll-tex.com/about"),
    ("N95 vs 防霾紗窗", "https://www.google.com/search?q=Poll-tex+%E9%98%B2%E9%9C%89%E7%B4%99%E7%AA%97+vs+N95"),
    ("空氣清淨機 比較", "https://www.google.com/search?q=%E7%A9%BA%E6%B0%A3%E6%B8%85%E6%B7%A8%E6%A9%9F+vs+%E9%98%B2%E9%9C%89%E7%B4%99%E7%AA%97+2026"),
]

async def main():
    results = []
    async with AsyncWebCrawler(headless=True) as crawler:
        for label, url in TARGETS:
            print(f"\n=== {label} | {url} ===")
            try:
                config = CrawlerRunConfig(delay_before_return_html=3.0, page_timeout=30000)
                result = await crawler.arun(url=url, config=config)
                if not result.success:
                    print(f"  ✗ failed: {result.error_message[:80]}")
                    results.append({"label": label, "url": url, "status": "FAIL", "error": result.error_message})
                    continue
                md = result.markdown or ""
                print(f"  ✓ status={result.status_code} md={len(md)} chars")
                # 印前 200 chars
                preview = md[:300].replace("\n", " | ")
                print(f"  preview: {preview[:200]}")
                # 存 md
                fname = f"poll_tex_{label.replace(' ', '_').replace('|', '_')}.md"
                fname = "".join(c if c.isalnum() or c in "._-" else "_" for c in fname)
                out = os.path.join(OUT_DIR, fname)
                with open(out, "w", encoding="utf-8") as f:
                    f.write(f"# {label}\nURL: {url}\nfetched: {datetime.now().isoformat()}\n\n{md}")
                results.append({"label": label, "url": url, "status": "OK", "chars": len(md), "file": out})
            except Exception as e:
                print(f"  ✗ EXC: {e}")
                results.append({"label": label, "url": url, "status": "EXC", "error": str(e)})
    # 寫 index
    out = os.path.join(OUT_DIR, f"poll_tex_kb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n=== 完成 → {out} ===")

asyncio.run(main())
