"""老蔡實戰場景: 房仲 / 防霾紗窗 / 業務知識爬取"""
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

TARGETS = [
    ("591 楊梅租房", "https://rent.591.com.tw/list?region=5&section=49&kind=0"),
    ("Google 搜尋: 楊梅房價 2026", "https://www.google.com/search?q=%E6%A5%8A%E6%A2%9D%E6%88%BF%E5%83%B9+2026&hl=zh-TW"),
    ("MOEA 公司登記: Poll-tex", "https://findbiz.nat.gov.tw/fts/query/advanceSearch/queryResult?banNo=&brName=Poll-tex&brdCode=&queryType=advanceSearch&infoType=brCmpy&jessionId="),
    ("YCombinator: AI crawler news", "https://www.ycombinator.com/companies?industry=AI&regions=NA"),
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
            print(f"\n{'='*70}\n[{name}]\n  URL: {url}\n{'='*70}")
            try:
                r = await crawler.arun(url=url, config=cfg)
                md = r.markdown.fit_markdown if r.markdown and hasattr(r.markdown, "fit_markdown") else (
                    r.markdown.raw_markdown if r.markdown else "(no markdown)"
                )
                print(f"  success={r.success} status={r.status_code}  md={len(md) if md else 0} chars")
                print(f"  title: {(r.metadata or {}).get('title','?')[:80]}")
                # 取前 800 字 preview
                if md:
                    preview = md[:800].replace("\n\n", "\n")
                    print(f"  --- preview (前 800 chars) ---")
                    print(f"  {preview}")
                    print(f"  --- end ---")
            except Exception as e:
                print(f"  ❌ FAILED: {type(e).__name__}: {e}")

asyncio.run(main())
