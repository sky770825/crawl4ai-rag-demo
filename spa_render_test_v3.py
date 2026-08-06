"""踩坑 1 v3: 放棄 wait_for,改用 js_code 注入 + scroll
1. 591 楊梅 — 用 regionid 對照表找正確
2. 591 整層 — 看能否拿到物件列表
3. YC AI — scroll 觸發 infinite scroll
"""
import asyncio
import re
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

# 591 region 對照 (從官方): 台北 1, 新北 3, 桃園 5
# 桃園 section 對照: 楊梅沒有獨立 section! 桃園下分: 中壢 33 平鎮 32 楊梅 49 ?
# 直接給 591 桃園總
TARGETS = [
    ("591 桃園全區 + scroll", "https://rent.591.com.tw/list?region=5&kind=1",
     "window.scrollTo(0, 2000); new Promise(r => setTimeout(r, 3000));"),
    ("591 桃園中壢 + scroll", "https://rent.591.com.tw/list?region=5&section=33&kind=0",
     "window.scrollTo(0, 2000); new Promise(r => setTimeout(r, 3000));"),
    ("591 桃園楊梅 + scroll", "https://rent.591.com.tw/list?region=5&section=49&kind=0",
     "window.scrollTo(0, 2000); new Promise(r => setTimeout(r, 3000));"),
    ("591 桃園平鎮 + scroll", "https://rent.591.com.tw/list?region=5&section=32&kind=0",
     "window.scrollTo(0, 2000); new Promise(r => setTimeout(r, 3000));"),
    ("591 桃園蘆竹 + scroll", "https://rent.591.com.tw/list?region=5&section=34&kind=0",
     "window.scrollTo(0, 2000); new Promise(r => setTimeout(r, 3000));"),
    ("591 桃園八德 + scroll", "https://rent.591.com.tw/list?region=5&section=35&kind=0",
     "window.scrollTo(0, 2000); new Promise(r => setTimeout(r, 3000));"),
    ("591 桃園龜山 + scroll", "https://rent.591.com.tw/list?region=5&section=36&kind=0",
     "window.scrollTo(0, 2000); new Promise(r => setTimeout(r, 3000));"),
    ("591 桃園龍潭 + scroll", "https://rent.591.com.tw/list?region=5&section=37&kind=0",
     "window.scrollTo(0, 2000); new Promise(r => setTimeout(r, 3000));"),
    # YC — 用真實 JS scroll
    ("YC AI + infinite scroll", "https://www.ycombinator.com/companies?industry=AI",
     """for(let i=0;i<3;i++){window.scrollTo(0, document.body.scrollHeight); await new Promise(r => setTimeout(r, 2000))};"""),
    # 591 楊梅 — 試 kind=2 (雅房), kind=3 (分租), kind=4 (其他)
    ("591 楊梅 kind=2 雅房", "https://rent.591.com.tw/list?region=5&section=49&kind=2",
     "window.scrollTo(0, 2000); new Promise(r => setTimeout(r, 3000));"),
    # 591 不分頁: kind=5 整層; section=null 用 'all'
    ("591 桃園 section=0 (全區) + scroll", "https://rent.591.com.tw/list?region=5&section=0&kind=0",
     "window.scrollTo(0, 2000); new Promise(r => setTimeout(r, 3000));"),
]

async def main():
    async with AsyncWebCrawler(headless=True) as crawler:
        for name, url, js in TARGETS:
            print(f"\n{'='*70}\n[{name}]")
            try:
                cfg = CrawlerRunConfig(
                    page_timeout=30000,
                    js_code=js,
                    delay_before_return_html=3.0,
                )
                r = await crawler.arun(url=url, config=cfg)
                md = r.markdown.fit_markdown if r.markdown and r.markdown.fit_markdown else (
                    r.markdown.raw_markdown if r.markdown else ""
                )
                title = (r.metadata or {}).get('title', '?')[:80]
                print(f"  status={r.status_code}  md={len(md) if md else 0} chars  title={title}")
                # 抓價格 (591 顯示 $X,XXX 元/月) 跟 地址 (中壢區/楊梅區/...)
                if "591" in url and md:
                    prices = re.findall(r'\$[\d,]+(?:\s*元)?', md)
                    sections = re.findall(r'(中壢|楊梅|平鎮|蘆竹|八德|龜山|龍潭|大溪|復興)區', md)
                    print(f"  prices found: {len(prices)} (e.g. {prices[:3]})")
                    print(f"  sections mentioned: {len(sections)} (e.g. {sections[:3]})")
                    if not prices and not sections:
                        # 抓任何 link 帶 /rent/xxx
                        rent_links = re.findall(r'/rent/[\w-]+', md)
                        print(f"  /rent/ links: {len(rent_links)} (e.g. {rent_links[:3]})")
            except Exception as e:
                print(f"  ❌ FAILED: {type(e).__name__}: {str(e)[:200]}")

asyncio.run(main())
