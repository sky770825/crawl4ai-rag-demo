"""戰場 1 v2: 房市新聞知識庫 — 修正 schema
從前次測試, 通用 h2/h3 太嚴, 用 content filter 把 markdown 拆開更可靠
"""
import asyncio
import json
import os
import re
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

OUT_DIR = os.path.expanduser("~/Desktop/crawl4ai/rag_data")
os.makedirs(OUT_DIR, exist_ok=True)

# 從 markdown 直接抓 line (每行是 "時間 標題 網址")
URL_RE = re.compile(r'\((https?://[^\s)]+)\)')

TARGETS = [
    ("ETtoday 房產焦點", "https://house.ettoday.net/news-list.htm"),
    ("ETtoday 新聞總覽", "https://www.ettoday.net/news/news-list.htm"),
    ("ETtoday 財經", "https://finance.ettoday.net/news/news-list.htm"),
    ("Yahoo 房地產", "https://tw.news.yahoo.com/real-estate"),
    ("Yahoo 新聞首頁", "https://tw.news.yahoo.com/"),
]

def parse_ettoday_markdown(md):
    """ETtoday markdown 格式: '標題  網址'"""
    items = []
    for line in md.split("\n"):
        line = line.strip()
        if not line or len(line) < 10:
            continue
        m = URL_RE.search(line)
        if not m:
            continue
        url = m.group(1)
        # 過濾非新聞 URL
        if not any(x in url for x in ["news-list", "/news/"]):
            continue
        # 抓標題 = URL 前的字
        title = line[:m.start()].strip(" |[]-—·•")
        # 過濾
        if len(title) < 6 or title in ["", "即時新聞", "看更多"]:
            continue
        if title.startswith("http"):
            continue
        items.append({"title": title, "link": url})
    return items

def parse_yahoo_markdown(md):
    """Yahoo markdown: 標題在前, link 跟在後"""
    items = []
    for line in md.split("\n"):
        line = line.strip()
        if not line or len(line) < 8:
            continue
        m = URL_RE.search(line)
        if not m:
            continue
        url = m.group(1)
        # 過濾
        if "yahoo.com" not in url:
            continue
        if any(x in url for x in ["/topic/", "/tag/", "/category/"]):
            continue
        title = line[:m.start()].strip(" |[]-—·•")
        if len(title) < 8 or title in ["", "新聞"]:
            continue
        if title.startswith("http"):
            continue
        items.append({"title": title, "link": url})
    return items

async def main():
    all_items = []
    async with AsyncWebCrawler(headless=True) as crawler:
        for label, url in TARGETS:
            print(f"\n=== {label} ===")
            try:
                # 用 content filter + markdown 拆乾淨
                config = CrawlerRunConfig(
                    markdown_generator=DefaultMarkdownGenerator(
                        content_filter=PruningContentFilter(threshold=0.3)
                    ),
                    delay_before_return_html=3.0,
                )
                result = await crawler.arun(url=url, config=config)
                if not result.success:
                    print(f"  ✗ failed: {result.error_message}")
                    continue
                md = result.markdown or ""
                # 去掉 prun 過的 prefix
                if "Pruning Content" in md[:100]:
                    pass
                # 解析
                if "yahoo" in url:
                    items = parse_yahoo_markdown(md)
                else:
                    items = parse_ettoday_markdown(md)
                # 去重
                seen = set()
                unique = []
                for it in items:
                    key = it["title"]
                    if key in seen:
                        continue
                    seen.add(key)
                    unique.append(it)
                print(f"  ✓ {len(unique)} items, md={len(md)} chars")
                for it in unique[:5]:
                    print(f"    → {it['title'][:60]}")
                all_items.append({
                    "source": label,
                    "url": url,
                    "fetched_at": datetime.now().isoformat(),
                    "count": len(unique),
                    "items": unique,
                })
            except Exception as e:
                print(f"  ✗ EXC: {e}")

    # 寫 RAG-ready JSON
    fname = f"house_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out = os.path.join(OUT_DIR, fname)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    total = sum(x["count"] for x in all_items)
    print(f"\n=== 完成: {total} items → {out} ===")
    return out, total

asyncio.run(main())
