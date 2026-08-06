"""llm_extract_ollama.py v2 - 用 LLMConfig"""
import asyncio, json, os
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai import LLMConfig

OUT_DIR = os.path.expanduser("~/Desktop/crawl4ai/rag_data")
os.makedirs(OUT_DIR, exist_ok=True)

SCHEMA = """
{
  "title": "string - 物件或新聞標題",
  "type": "string - 類型 (新聞/物件/法規/教學)",
  "key_points": ["string - 3-5 個重點"],
  "numbers": ["string - 提到的關鍵數字 (價格/坪數/利率)"],
  "source_credibility": "high|medium|low"
}
"""

URLS = [
    ("ETtoday 房產焦點", "https://house.ettoday.net/news-list.htm"),
    ("央行 利率", "https://www.cbc.gov.tw/tw/mp-002.html"),
    ("平均地權", "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=D0060066"),
]

async def main():
    llm_cfg = LLMConfig(provider="ollama/qwen2.5:7b", api_token="ollama")
    cfg = CrawlerRunConfig(
        verbose=False,
        extraction_strategy=LLMExtractionStrategy(
            llm_config=llm_cfg,
            schema=SCHEMA,
            instruction="從這個網頁抽取 JSON"
        )
    )
    results = []
    async with AsyncWebCrawler(headless=True) as crawler:
        for name, url in URLS:
            print(f"  >> {name}")
            try:
                r = await crawler.arun(url=url, config=cfg)
                results.append({
                    'name': name, 'url': url,
                    'success': r.success,
                    'extracted': (r.extracted_content or '')[:500],
                    'md_chars': len(r.markdown or '')
                })
                print(f"     status={r.status_code} extracted_len={len(r.extracted_content or '')}")
            except Exception as e:
                print(f"     EXC: {str(e)[:200]}")
                results.append({'name': name, 'url': url, 'error': str(e)[:200]})
    
    out = os.path.join(OUT_DIR, f"llm_extract_ollama_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nDone: {out}")

asyncio.run(main())
