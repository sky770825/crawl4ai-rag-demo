"""踩坑 3: 並行 + 流量邊界
測試 1: 連續 5 頁同網站 (rate limit 邊界)
測試 2: 8 個並行
測試 3: 不同網站並行
"""
import asyncio
import time
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

# 用相對友善的網站測
HACKER_NEWS_BASE = "https://news.ycombinator.com/news?p="
GITHUB_BASE = "https://github.com/unclecode/crawl4ai/issues/"

async def test_serial(crawler, name, urls):
    """連續 N 個同一站"""
    print(f"\n--- {name}: serial {len(urls)} urls ---")
    start = time.time()
    results = []
    for i, url in enumerate(urls):
        try:
            cfg = CrawlerRunConfig(page_timeout=20000, delay_before_return_html=1.0)
            r = await crawler.arun(url=url, config=cfg)
            ms = time.time() - start
            md = len(r.markdown.raw_markdown) if r.markdown and r.markdown.raw_markdown else 0
            results.append((url, r.status_code, md, ms, r.success))
            print(f"  [{i+1}/{len(urls)}] status={r.status_code} md={md:>7} t={ms:.1f}s")
        except Exception as e:
            ms = time.time() - start
            results.append((url, "EXC", 0, ms, False))
            print(f"  [{i+1}/{len(urls)}] EXC: {str(e)[:80]}  t={ms:.1f}s")
    success_n = sum(1 for r in results if r[4] and r[2] > 500)
    total = time.time() - start
    print(f"  → {success_n}/{len(urls)} OK, total {total:.1f}s, avg {total/len(urls):.1f}s/url")
    return results

async def test_parallel(crawler, name, urls, max_concurrent=5):
    """並行 N 個"""
    print(f"\n--- {name}: parallel {len(urls)} urls, max={max_concurrent} ---")
    sem = asyncio.Semaphore(max_concurrent)
    results = []
    start = time.time()

    async def _one(url, idx):
        async with sem:
            try:
                cfg = CrawlerRunConfig(page_timeout=20000, delay_before_return_html=1.0)
                r = await crawler.arun(url=url, config=cfg)
                md = len(r.markdown.raw_markdown) if r.markdown and r.markdown.raw_markdown else 0
                return (idx, url, r.status_code, md, time.time() - start, r.success)
            except Exception as e:
                return (idx, url, "EXC", 0, time.time() - start, False)

    tasks = [_one(u, i) for i, u in enumerate(urls)]
    for coro in asyncio.as_completed(tasks):
        r = await coro
        results.append(r)
        print(f"  [{r[0]+1}/{len(urls)}] status={r[2]} md={r[3]:>7} t={r[4]:.1f}s")
    success_n = sum(1 for r in results if r[5] and r[3] > 500)
    total = time.time() - start
    print(f"  → {success_n}/{len(urls)} OK, total {total:.1f}s, avg {total/len(urls):.1f}s/url")
    return results

async def main():
    # 準備 URL
    # HN 不同頁 (p=1..5)
    hn_urls = [f"https://news.ycombinator.com/news?p={i}" for i in range(1, 6)]
    # GitHub issues (1..5)
    gh_urls = [f"https://github.com/unclecode/crawl4ai/issues/{i}" for i in range(100, 110)]
    # 跨站
    mixed = [
        "https://news.ycombinator.com/news",
        "https://www.ycombinator.com/",
        "https://github.com/unclecode/crawl4ai",
        "https://developer.mozilla.org/en-US/docs/Web",
        "https://tw.news.yahoo.com/",
        "https://www.ettoday.net/news/news-list.htm",
        "https://juejin.cn/",
        "https://so.csdn.net/",
    ]
    async with AsyncWebCrawler(headless=True) as crawler:
        await test_serial(crawler, "HN 5 頁 serial", hn_urls)
        await test_serial(crawler, "GitHub issues 10 個 serial", gh_urls)
        await test_parallel(crawler, "跨站 8 個並行", mixed, max_concurrent=4)
        await test_parallel(crawler, "HN 5 個並行", hn_urls, max_concurrent=3)

asyncio.run(main())
