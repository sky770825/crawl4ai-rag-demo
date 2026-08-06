"""踩坑 5: LLM 結構化抽取 (schema 從新聞頁抽 title/date/author/price)
crawl4ai 內建 LLMExtractionStrategy, 但需要 LLM API key
測試兩種: 1) cs-extraction 模式 (純 CSS selector) 2) LLM 模式
"""
import asyncio
import json
import os
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy, LLMExtractionStrategy

# 定義 schema
NEWS_SCHEMA = {
    "name": "NewsArticle",
    "baseSelector": "article, .article, .news-item, .post, .story, body",
    "fields": [
        {"name": "title", "selector": "h1, h2, h3, .title, .headline", "type": "text"},
        {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
    ]
}

HN_SCHEMA = {
    "name": "HNStory",
    "baseSelector": "tr.athing",
    "fields": [
        {"name": "title", "selector": ".titleline a", "type": "text"},
        {"name": "link", "selector": ".titleline a", "type": "attribute", "attribute": "href"},
        {"name": "rank", "selector": ".rank", "type": "text"},
    ]
}

async def test_css_extraction():
    """CSS 抽取 — 不需 LLM"""
    print(f"\n=== CSS extraction (no LLM) ===")
    async with AsyncWebCrawler(headless=True) as crawler:
        # 1. HN — 有明確的 tr.athing 結構
        cfg = CrawlerRunConfig(
            page_timeout=20000,
            delay_before_return_html=2.0,
            extraction_strategy=JsonCssExtractionStrategy(HN_SCHEMA),
        )
        r = await crawler.arun(url="https://news.ycombinator.com/news?p=2", config=cfg)
        print(f"  HN: status={r.status_code} extracted_content={len(r.extracted_content or '')} chars")
        if r.extracted_content:
            try:
                data = json.loads(r.extracted_content)
                print(f"  HN: extracted {len(data)} items")
                for d in data[:3]:
                    print(f"    → rank={d.get('rank', '?')[:5]} title={d.get('title', '?')[:50]}")
            except Exception as e:
                print(f"  parse err: {e}")

        # 2. ETtoday
        cfg2 = CrawlerRunConfig(
            page_timeout=20000,
            delay_before_return_html=3.0,
            extraction_strategy=JsonCssExtractionStrategy(NEWS_SCHEMA),
        )
        r2 = await crawler.arun(url="https://www.ettoday.net/news/news-list.htm", config=cfg2)
        print(f"\n  ETtoday: status={r2.status_code} extracted_content={len(r2.extracted_content or '')} chars")
        if r2.extracted_content:
            try:
                data = json.loads(r2.extracted_content)
                print(f"  ETtoday: extracted {len(data)} items")
                for d in data[:5]:
                    print(f"    → title={d.get('title', '?')[:60]}")
                    if d.get('link'):
                        print(f"      link={d.get('link')[:80]}")
            except Exception as e:
                print(f"  parse err: {e}")
                print(f"  raw: {r2.extracted_content[:500]}")

        # 3. 591 楊梅 (雖然 SPA 不 render, 試試)
        r3 = await crawler.arun(
            url="https://rent.591.com.tw/list?region=5&section=49&kind=0",
            config=cfg2,
        )
        print(f"\n  591: status={r3.status_code} extracted_content={len(r3.extracted_content or '')} chars")
        if r3.extracted_content:
            data = json.loads(r3.extracted_content)
            print(f"  591: extracted {len(data)} items")
            for d in data[:3]:
                print(f"    → {d}")


async def test_llm_extraction():
    """LLM 抽取 — 需 LLM key,看能否 fallback"""
    print(f"\n=== LLM extraction ===")
    # 檢查環境有沒有 LLM key
    keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GROQ_API_KEY", "MINIMAX_API_KEY", "MISTRAL_API_KEY"]
    has_key = any(os.environ.get(k) for k in keys)
    print(f"  環境 LLM keys: {[(k, bool(os.environ.get(k))) for k in keys]}")
    if not has_key:
        print(f"  → 跳過 LLM extraction (無 key)")
        return
    # 試 Groq (便宜 + 快)
    if os.environ.get("GROQ_API_KEY"):
        llm_cfg = {
            "provider": "groq/llama-3.1-70b-versatile",
            "api_token": os.environ["GROQ_API_KEY"],
        }
    elif os.environ.get("OPENAI_API_KEY"):
        llm_cfg = {"provider": "openai/gpt-4o-mini", "api_token": os.environ["OPENAI_API_KEY"]}
    else:
        llm_cfg = None
    if not llm_cfg:
        return
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "新聞標題"},
            "author": {"type": "string", "description": "作者"},
            "date": {"type": "string", "description": "發布日期"},
            "summary": {"type": "string", "description": "一句話摘要"},
        }
    }
    async with AsyncWebCrawler(headless=True) as crawler:
        cfg = CrawlerRunConfig(
            page_timeout=20000,
            delay_before_return_html=2.0,
            extraction_strategy=LLMExtractionStrategy(
                llm_config=llm_cfg,
                schema=schema,
                extraction_type="schema",
            ),
        )
        try:
            r = await crawler.arun(
                url="https://news.ycombinator.com/item?id=49195231",
                config=cfg,
            )
            print(f"  HN story: status={r.status_code} extracted_content={len(r.extracted_content or '')} chars")
            print(f"  → {r.extracted_content[:500] if r.extracted_content else '(empty)'}")
        except Exception as e:
            print(f"  ❌ FAILED: {type(e).__name__}: {str(e)[:200]}")


async def main():
    await test_css_extraction()
    await test_llm_extraction()

asyncio.run(main())
