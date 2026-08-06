"""踩坑 4: Deep crawl — 從主頁出發抓內頁
測試 1: GitHub repo 內 page (從 issues list 進單個 issue)
測試 2: Hacker News 從首頁抓每個 story 內頁
測試 3: 591 楊梅 用 BFS deep crawl 內頁
"""
import asyncio
import re
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from urllib.parse import urljoin, urlparse

async def main():
    async with AsyncWebCrawler(headless=True) as crawler:
        # 測試 1: 抓 HN 首頁 + 進 3 個 story 內頁
        print(f"\n=== HN deep: 從首頁進 3 個 story ===")
        cfg = CrawlerRunConfig(page_timeout=20000, delay_before_return_html=2.0)
        r = await crawler.arun(url="https://news.ycombinator.com/news", config=cfg)
        md = r.markdown.raw_markdown
        # 抓 item?id=xxx
        item_links = re.findall(r'https://news\.ycombinator\.com/item\?id=\d+', md)
        item_links = list(dict.fromkeys(item_links))[:3]
        print(f"  found {len(item_links)} unique item links")
        for il in item_links:
            print(f"    → {il}")
        for i, link in enumerate(item_links):
            r2 = await crawler.arun(url=link, config=cfg)
            md2 = r2.markdown.raw_markdown if r2.markdown else ""
            # 抓 title (H1 / h2 標籤)
            title_match = re.search(r'^#\s+(.+)$', md2, re.MULTILINE) if md2 else None
            title = title_match.group(1) if title_match else '?'
            print(f"  [{i+1}] {link[:60]} status={r2.status_code} md={len(md2)} title={title[:60]}")

        # 測試 2: GitHub issues deep — 從 1 個 issue 抓 comment 結構
        print(f"\n=== GitHub issues deep: 1 個 issue 內頁 ===")
        for issue_num in [100, 200, 300]:
            url = f"https://github.com/unclecode/crawl4ai/issues/{issue_num}"
            r = await crawler.arun(url=url, config=cfg)
            md = r.markdown.raw_markdown if r.markdown else ""
            # 看 comment count
            comments = re.findall(r'(\d+)\s*(?:comment|回覆|回應)', md.lower() if md else "")
            print(f"  #{issue_num}: status={r.status_code} md={len(md)} comments-mentioned={comments[:3]}")

        # 測試 3: Ptt Gossiping 內頁 (雖然 18 歲確認頁卡住, 試 article 內頁)
        print(f"\n=== Ptt 內頁 deep ===")
        # Ptt Gossiping 的 article URL 模式
        # 先抓看板首頁
        r = await crawler.arun(url="https://www.ptt.cc/bbs/Gossiping/index.html", config=cfg)
        print(f"  Ptt board: status={r.status_code} md={len(r.markdown.raw_markdown) if r.markdown else 0}")
        # 抓 article 連結
        md = r.markdown.raw_markdown if r.markdown else ""
        articles = re.findall(r'/bbs/Gossiping/M\.\d+\.A\.[A-Z0-9]+\.html', md)
        articles = list(dict.fromkeys(articles))[:3]
        print(f"  found {len(articles)} article links")
        for a in articles:
            full = urljoin("https://www.ptt.cc", a)
            # Ptt 18 歲同意 cookie
            r2 = await crawler.arun(
                url=full,
                config=cfg,
                # cookies 設定
            )
            md2 = r2.markdown.raw_markdown if r2.markdown else ""
            print(f"    {a[:60]}: status={r2.status_code} md={len(md2)}")

asyncio.run(main())
