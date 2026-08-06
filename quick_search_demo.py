"""Quick search demo using crawl4ai — 3 targets:
1. Hacker News front page (real search/discussion content)
2. Ptt 楊梅 board (本地,中文,實戰)
3. B站 search results (中文搜尋實戰)
"""
import asyncio
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

TARGETS = [
    ("Hacker News", "https://news.ycombinator.com/"),
    ("Ptt Yangmei", "https://www.ptt.cc/bbs/Yangmei/index.html"),
    ("B站 search: AI 短劇", "https://search.bilibili.com/all?keyword=AI%E7%9F%AD%E5%8A%87"),
]

async def main():
    cfg = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(threshold=0.4, threshold_type="fixed")
        ),
        page_timeout=30000,
    )
    async with AsyncWebCrawler() as crawler:
        for name, url in TARGETS:
            print(f"\n{'='*60}\n[{name}] {url}\n{'='*60}")
            try:
                r = await crawler.arun(url=url, config=cfg)
                md = r.markdown.fit_markdown if r.markdown and hasattr(r.markdown, "fit_markdown") else (
                    r.markdown.raw_markdown if r.markdown else "(no markdown)"
                )
                print(f"  status: success={r.success} status_code={r.status_code}")
                print(f"  title: {(r.metadata or {}).get('title','?')}")
                print(f"  md length: {len(md) if md else 0} chars")
                # 印前 1500 字當 preview
                print(f"  --- preview ---")
                print(md[:1500] if md else "(empty)")
                print(f"  --- end ---")
            except Exception as e:
                print(f"  ❌ FAILED: {type(e).__name__}: {e}")

asyncio.run(main())
