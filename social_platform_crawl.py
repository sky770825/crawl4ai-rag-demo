"""social_platform_crawl.py - 各社群平台實際抓取"""
import asyncio, json, os
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from urllib.parse import urlparse

OUT = os.path.expanduser("~/Desktop/crawl4ai/rag_data")

# 平台清單: (label, url, note)
PLATFORMS = [
    # === B站 (核心, 已知可用) ===
    ("B站 AI短劇 綜合", "https://search.bilibili.com/all?keyword=AI%E7%9F%AD%E5%8A%87"),
    ("B站 Seedance 教程", "https://search.bilibili.com/all?keyword=Seedance%202.5"),
    ("B站 可靈 教程", "https://search.bilibili.com/all?keyword=%E5%8F%AF%E9%9D%99%20%E6%95%99%E7%A8%8B"),
    ("B站 即夢 AI", "https://search.bilibili.com/all?keyword=%E5%8D%B3%E5%A4%A2%20AI%20%E6%95%99%E7%A8%8B"),
    ("B站 AI漫劇", "https://search.bilibili.com/all?keyword=AI%20%E6%BC%AB%E5%8A%87"),
    ("B站 短劇 綜合", "https://search.bilibili.com/all?keyword=%E7%9F%AD%E5%8A%87"),
    ("B站 動漫 AI", "https://search.bilibili.com/all?keyword=%E5%8A%A8%E6%BC%AB%20AI"),
    # === YouTube (英文社區強) ===
    ("YouTube AI 短劇", "https://www.youtube.com/results?search_query=AI+short+drama"),
    ("YouTube Seedance", "https://www.youtube.com/results?search_query=seedance+2.5+tutorial"),
    ("YouTube Kling", "https://www.youtube.com/results?search_query=kling+ai+3.0"),
    # === Threads (文字社群) ===
    ("Threads Crawl4AI", "https://www.threads.net/search?q=crawl4ai"),
    ("Threads AI agent", "https://www.threads.net/search?q=AI+agent"),
    # === X / Twitter (有 web 版可抓) ===
    ("X Crawl4AI", "https://x.com/search?q=crawl4ai&src=typed_query"),
    ("X Seedance", "https://x.com/search?q=seedance%202.5"),
    # === Facebook (公開 page) ===
    ("FB AI 公開", "https://www.facebook.com/search/top?q=AI%20short%20drama"),
    # === 抖音 web (會有 SPA 問題) ===
    ("抖音 web AI 短劇", "https://www.douyin.com/search/AI%E7%9F%AD%E5%8A%87"),
    # === Ptt (台灣本土) ===
    ("Ptt Gossiping", "https://www.ptt.cc/bbs/Gossiping/index.html"),
    ("Ptt 房仲版", "https://www.ptt.cc/bbs/Yangmei/index.html"),
    # === Dcard (台灣) ===
    ("Dcard 有趣", "https://www.dcard.tw/f/funny"),
    # === 微博 (中文社群) ===
    ("微博 AI 短劇", "https://s.weibo.com/weibo?q=AI%E7%9F%AD%E5%8A%87"),
    # === Reddit (英文社群) ===
    ("Reddit AIshortdrama", "https://www.reddit.com/r/AIshortdrama/"),
    ("Reddit LocalLLaMA", "https://www.reddit.com/r/LocalLLaMA/"),
    # === 知乎 (中文知識社群) ===
    ("知乎 AI 短劇", "https://www.zhihu.com/search?type=content&q=AI%20%E7%9F%AD%E5%8A%87"),
]

async def main():
    results = []
    async with AsyncWebCrawler(headless=True) as crawler:
        cfg = CrawlerRunConfig(page_timeout=20000, delay_before_return_html=2.0, verbose=False)
        for label, url in PLATFORMS:
            try:
                r = await crawler.arun(url=url, config=cfg)
                results.append({
                    "label": label, "url": url,
                    "status": r.status_code,
                    "chars": len(r.markdown.raw_markdown or ""),
                    "md": (r.markdown.raw_markdown or "")[:6000],
                })
                print(f"  [{r.status_code}] {label:30s} chars={len(r.markdown.raw_markdown or ''):6d}")
            except Exception as e:
                results.append({"label": label, "url": url, "status": "EXC", "err": str(e)[:200]})
                print(f"  [EXC] {label}: {str(e)[:60]}")
    fp = os.path.join(OUT, f"social_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    open(fp, "w", encoding="utf-8").write(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\nWrote: {fp}")

asyncio.run(main())
