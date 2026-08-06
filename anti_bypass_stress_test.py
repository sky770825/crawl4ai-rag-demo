"""踩坑 2: 反爬壓力測試 — crawl4ai 對各家反爬機制
平台清單: 抖音/小紅書/微博/IG/FB/Threads/X/TikTok/Ptt/Dcard/Mobile01
"""
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

BATCH = "a"  # 改這個: a=第一輪, b=第二輪
BATCH_A = [
    # === 反爬強站 ===
    ("抖音 web 用戶頁", "https://www.douyin.com/user/MS4wLjABAAAAxxxxx"),
    ("小紅書 搜尋", "https://www.xiaohongshu.com/search_result?keyword=AI"),
    ("微博 搜尋", "https://s.weibo.com/weibo?q=AI"),
    ("IG public", "https://www.instagram.com/crawl4ai/"),
    ("TikTok 個人", "https://www.tiktok.com/@crawl4ai"),
    ("Threads", "https://www.threads.net/@zuck"),
    ("X (Twitter)", "https://x.com/UNclecode"),
    ("FB public page", "https://www.facebook.com/UNclecode/"),
    # === 台灣 ===
    ("Ptt Gossiping", "https://www.ptt.cc/bbs/Gossiping/index.html"),
    ("Ptt Yangmei", "https://www.ptt.cc/bbs/Yangmei/index.html"),
    ("Dcard funny", "https://www.dcard.tw/f/funny"),
    ("Mobile01", "https://www.mobile01.com/topicdetail.php?f=18&t=7000000"),
]
BATCH_B = [
    # === 政府 / 法務 ===
    ("司法院法學", "https://law.judicial.gov.tw/FJUD/default.aspx"),
    ("MOEA 公司登記", "https://findbiz.nat.gov.tw/fts/query/advanceSearch/queryResult"),
    ("公開資訊觀測站", "https://mops.twse.com.tw/mops/web/index"),
    # === 新聞 / 知識庫 ===
    ("Yahoo 新聞", "https://tw.news.yahoo.com/"),
    ("ETtoday", "https://www.ettoday.net/news/news-list.htm"),
    ("Medium", "https://medium.com/search?q=crawl4ai"),
    ("StackOverflow", "https://stackoverflow.com/search?q=python+async+web+scraping"),
    ("MDN", "https://developer.mozilla.org/en-US/docs/Web"),
    # === 中文 ===
    ("知乎", "https://www.zhihu.com/"),
    ("CSDN 搜尋", "https://so.csdn.net/so/search?q=crawl4ai"),
    ("掘金", "https://juejin.cn/search?query=crawl4ai"),
    # === GitHub / 工具 ===
    ("GitHub repo", "https://github.com/unclecode/crawl4ai"),
    ("GitHub user", "https://github.com/sky770825"),
    ("RegExr", "https://regexr.com/"),
]
TARGETS = BATCH_A if BATCH == "a" else BATCH_B

async def main():
    async with AsyncWebCrawler(headless=True) as crawler:
        results = []
        for name, url in TARGETS:
            try:
                cfg = CrawlerRunConfig(
                    page_timeout=20000,
                    delay_before_return_html=2.0,
                )
                r = await crawler.arun(url=url, config=cfg)
                status = r.status_code
                md_len = len(r.markdown.raw_markdown) if r.markdown and r.markdown.raw_markdown else 0
                title = (r.metadata or {}).get('title', '?')[:50]
                success = r.success
                # 抓 CAPTCHA / 403 訊號
                captcha = "captcha" in (r.html or "").lower()[:5000] or "驗證" in (r.html or "")[:5000]
                results.append((name, success, status, md_len, title, captcha))
                print(f"  [{'✓' if success and md_len > 500 else ('✗' if not success or md_len < 200 else '⚠')}] {name:35s} status={status} md={md_len:>8} title={title}")
            except Exception as e:
                results.append((name, False, "EXC", 0, str(e)[:50], False))
                print(f"  [E] {name:35s} EXC: {str(e)[:80]}")
        # 統計
        print(f"\n{'='*70}\n總計 {len(results)} 個目標")
        ok = sum(1 for r in results if r[1] and r[3] > 500)
        fail = sum(1 for r in results if not r[1] or r[3] < 200)
        warn = sum(1 for r in results if r[1] and 200 <= r[3] <= 500)
        captcha_n = sum(1 for r in results if r[5])
        print(f"  ✓ 過: {ok}  ⚠ 邊界: {warn}  ✗ 失敗: {fail}  🔒 CAPTCHA 觸發: {captcha_n}")

asyncio.run(main())
