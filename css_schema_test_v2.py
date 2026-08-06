"""踩坑 5 v2: 寫專用 CSS schema 對各站
ETtoday: .block, .piece, h3 a...
591: .vue-list, .item
"""
import asyncio
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

# ETtoday 試
ETTODAY_SCHEMAS = [
    ("block-list", {
        "name": "ETNews",
        "baseSelector": ".block_list, .piece, .list_news, .news-list, .item",
        "fields": [
            {"name": "title", "selector": "h3, h2, .title, a", "type": "text"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
        ]
    }),
    ("h3-only", {
        "name": "ETNews",
        "baseSelector": "h3",
        "fields": [
            {"name": "title", "selector": "a, em, span", "type": "text"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
        ]
    }),
    ("a-with-news", {
        "name": "ETNews",
        "baseSelector": "a[href*='news']",
        "fields": [
            {"name": "title", "selector": "a", "type": "text"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
        ]
    }),
]

YAHOO_NEWS_SCHEMA = {
    "name": "YahooNews",
    "baseSelector": "h3, h2, .story-title, [class*='title']",
    "fields": [
        {"name": "title", "selector": "a", "type": "text"},
        {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
    ]
}

# B 站 搜尋卡片
BILIBILI_SCHEMA = {
    "name": "BVid",
    "baseSelector": "a[href*='/video/BV']",
    "fields": [
        {"name": "title", "selector": "a", "type": "text"},
        {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
    ]
}

async def main():
    async with AsyncWebCrawler(headless=True) as crawler:
        for name, schema in ETTODAY_SCHEMAS:
            print(f"\n=== ETtoday schema: {name} ===")
            cfg = CrawlerRunConfig(
                page_timeout=20000,
                delay_before_return_html=3.0,
                extraction_strategy=JsonCssExtractionStrategy(schema),
            )
            r = await crawler.arun(url="https://www.ettoday.net/news/news-list.htm", config=cfg)
            if r.extracted_content:
                data = json.loads(r.extracted_content)
                print(f"  {len(data)} items, 範例:")
                for d in data[:3]:
                    print(f"    → {d.get('title', '?')[:60]} | {d.get('link', '?')[:60]}")
            else:
                print(f"  no extracted_content")

        print(f"\n=== Yahoo 新聞 ===")
        cfg = CrawlerRunConfig(
            page_timeout=20000,
            delay_before_return_html=3.0,
            extraction_strategy=JsonCssExtractionStrategy(YAHOO_NEWS_SCHEMA),
        )
        r = await crawler.arun(url="https://tw.news.yahoo.com/", config=cfg)
        if r.extracted_content:
            data = json.loads(r.extracted_content)
            print(f"  {len(data)} items, 範例:")
            for d in data[:5]:
                print(f"    → {d.get('title', '?')[:60]}")

        print(f"\n=== B站 搜尋 AI 短劇 ===")
        cfg = CrawlerRunConfig(
            page_timeout=20000,
            delay_before_return_html=3.0,
            extraction_strategy=JsonCssExtractionStrategy(BILIBILI_SCHEMA),
        )
        r = await crawler.arun(url="https://search.bilibili.com/all?keyword=AI%E7%9F%AD%E5%8A%87", config=cfg)
        if r.extracted_content:
            data = json.loads(r.extracted_content)
            print(f"  {len(data)} items, 範例:")
            for d in data[:5]:
                title = d.get('title', '?')[:60]
                link = d.get('link', '?')[:80]
                print(f"    → {title}")
                print(f"      {link}")

asyncio.run(main())
