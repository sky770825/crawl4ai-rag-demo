"""social_v2.py"""
import asyncio, json, os
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
OUT = os.path.expanduser("~/Desktop/crawl4ai/rag_data")
P = []
P.append(("B站 開箱", "https://search.bilibili.com/all?keyword=開箱"))
P.append(("B站 美食", "https://search.bilibili.com/all?keyword=美食"))
P.append(("B站 旅遊", "https://search.bilibili.com/all?keyword=旅遊"))
P.append(("B站 投資理財", "https://search.bilibili.com/all?keyword=投資理財"))
P.append(("B站 房市", "https://search.bilibili.com/all?keyword=房市"))
P.append(("B站 楊梅", "https://search.bilibili.com/all?keyword=楊梅"))
# YouTube
P.append(("YT AI tools", "https://www.youtube.com/results?search_query=AI+tools+2026"))
P.append(("YT agent", "https://www.youtube.com/results?search_query=AI+agent"))
P.append(("YT Llama", "https://www.youtube.com/results?search_query=llama+3.3"))
P.append(("YT realestate", "https://www.youtube.com/results?search_query=taiwan+real+estate"))
# Reddit
P.append(("Reddit LocalLLaMA", "https://www.reddit.com/r/LocalLLaMA/"))
P.append(("Reddit AIart", "https://www.reddit.com/r/AIart/"))
P.append(("Reddit StableDiffusion", "https://www.reddit.com/r/StableDiffusion/"))
# X / Twitter
P.append(("X Crawl4AI", "https://x.com/search?q=crawl4ai"))
P.append(("X Seedance", "https://x.com/search?q=seedance"))
P.append(("X unsloth", "https://x.com/search?q=unsloth"))
P.append(("X eldelt", "https://x.com/search?q=AI+dram+a"))
# 中文社群
P.append(("知乎 Seedance", "https://www.zhihu.com/search?type=content&q=Seedance"))
P.append(("掘金 crawl4ai", "https://juejin.cn/search?query=crawl4ai"))
P.append(("CSDN crawl4ai", "https://so.csdn.net/so/search?q=crawl4ai"))
P.append(("抖音 web Seedance", "https://www.douyin.com/search/Seedance"))
P.append(("B站 Seedance 2.5", "https://search.bilibili.com/all?keyword=Seedance%202.5"))
P.append(("Threads crawl4ai", "https://www.threads.net/search?q=crawl4ai"))
P.append(("Threads AI", "https://www.threads.net/search?q=AI+agent"))
P.append(("Threads seedance", "https://www.threads.net/search?q=seedance"))
P.append(("微博 Seedance", "https://s.weibo.com/weibo?q=Seedance"))
P.append(("Threads unsloth", "https://www.threads.net/search?q=unsloth"))
P.append(("Threads ollama", "https://www.threads.net/search?q=ollama"))
P.append(("Threads llama", "https://www.threads.net/search?q=llama"))
P.append(("Threads stable diffusion", "https://www.threads.net/search?q=stable+diffusion"))
# Hacker News
P.append(("HN Crawl4AI", "https://hn.algolia.com/?q=crawl4ai"))
P.append(("HN Seedance", "https://hn.algolia.com/?q=seedance"))
P.append(("HN unsloth", "https://hn.algolia.com/?q=unsloth"))
P.append(("HN llama 3.3", "https://hn.algolia.com/?q=llama+3.3"))
P.append(("HN ollama", "https://hn.algolia.com/?q=ollama"))

async def main():
    results = []
    async with AsyncWebCrawler(headless=True) as crawler:
        cfg = CrawlerRunConfig(page_timeout=15000, delay_before_return_html=1.5, verbose=False)
        for label, url in P:
            try:
                r = await crawler.arun(url=url, config=cfg)
                results.append({
                    "label": label, "url": url,
                    "status": r.status_code,
                    "chars": len(r.markdown.raw_markdown or ""),
                    "md": (r.markdown.raw_markdown or "")[:5000],
                })
                print(f"  [{r.status_code}] {label:30s} chars={len(r.markdown.raw_markdown or ''):6d}")
            except Exception as e:
                results.append({"label": label, "url": url, "status": "EXC", "err": str(e)[:200]})
                print(f"  [EXC] {label}: {str(e)[:60]}")
    fp = os.path.join(OUT, f"social_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    open(fp, "w", encoding="utf-8").write(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\nWrote: {fp}")

asyncio.run(main())
