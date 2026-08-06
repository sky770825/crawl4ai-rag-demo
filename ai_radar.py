"""戰場 3: AI 技術雷達 — 自動監控 AI 新知
- GitHub trending AI/ML/Python
- Hacker News 頂級 AI 文章
- Hugging Face trending
- Papers with Code
"""
import asyncio
import json
import os
import re
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

OUT_DIR = os.path.expanduser("~/Desktop/crawl4ai/rag_data")
os.makedirs(OUT_DIR, exist_ok=True)

TARGETS = [
    ("GitHub Trending Python", "https://github.com/trending/python?since=daily"),
    ("GitHub Trending TypeScript", "https://github.com/trending/typescript?since=daily"),
    ("Hacker News Top", "https://news.ycombinator.com/"),
    ("Hugging Face Models", "https://huggingface.co/models?sort=downloads"),
    ("Papers with Code Trending", "https://paperswithcode.com/"),
]

URL_RE = re.compile(r'\((https?://[^\s)]+)\)')

async def crawl_one(crawler, label, url):
    print(f"\n=== {label} | {url} ===")
    try:
        config = CrawlerRunConfig(delay_before_return_html=2.5)
        result = await crawler.arun(url=url, config=config)
        if not result.success:
            print(f"  ✗ failed")
            return {"label": label, "url": url, "status": "FAIL", "error": result.error_message}
        md = result.markdown or ""
        # 解析 item (每行標題 + link)
        items = []
        for line in md.split("\n"):
            line = line.strip()
            m = URL_RE.search(line)
            if not m:
                continue
            link = m.group(1)
            # 過濾 nav
            if any(x in link for x in ["/login", "/signup", "/pricing", "/about", "/features"]):
                continue
            title = line[:m.start()].strip(" |[]-—·•*")
            if len(title) < 6 or title.startswith("http"):
                continue
            items.append({"title": title[:120], "link": link})
        # 去重
        seen = set()
        unique = []
        for it in items:
            if it["link"] in seen:
                continue
            seen.add(it["link"])
            unique.append(it)
        print(f"  ✓ {len(unique)} items, md={len(md)} chars")
        return {
            "label": label,
            "url": url,
            "status": "OK",
            "items": unique[:50],  # 上限 50
            "fetched_at": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"  ✗ EXC: {e}")
        return {"label": label, "url": url, "status": "EXC", "error": str(e)}

async def main():
    results = []
    async with AsyncWebCrawler(headless=True) as crawler:
        for label, url in TARGETS:
            r = await crawl_one(crawler, label, url)
            results.append(r)
            for it in r.get("items", [])[:3]:
                print(f"    → {it['title'][:60]}")
    out = os.path.join(OUT_DIR, f"ai_radar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    total = sum(len(r.get("items", [])) for r in results)
    print(f"\n=== 完成: {total} items → {out} ===")

asyncio.run(main())
