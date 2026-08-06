"""戰場 2: 公開資訊觀測站 / 政府法規 — 房仲業務必查
1. 公開資訊觀測站 — 上市公司公告
2. 法務部 — 法規更新
3. 內政部地政司 — 實價登錄 + 平均地權
4. 央行 — 利率政策
5. 租賃專法
"""
import asyncio
import json
import os
import re
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

OUT_DIR = os.path.expanduser("~/Desktop/crawl4ai/rag_data")
os.makedirs(OUT_DIR, exist_ok=True)

TARGETS = [
    ("公開資訊觀測站", "https://mops.twse.com.tw/mops/web/index"),
    ("央行 本行業務", "https://www.cbc.gov.tw/tw/mp-001.html"),
    ("央行 利率政策", "https://www.cbc.gov.tw/tw/mp-002.html"),
    ("內政部地政司", "https://www.land.moi.gov.tw/chhtml/index"),
    ("平均地權條例", "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=D0060066"),
    ("租賃住宅市場發展條例", "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=D0060104"),
    ("實價登錄專區", "https://lvr.land.moi.gov.tw/homePage"),
    ("公平交易委員會", "https://www.ftc.gov.tw/internet/main/index.aspx"),
]

async def main():
    results = []
    async with AsyncWebCrawler(headless=True) as crawler:
        for label, url in TARGETS:
            print(f"\n=== {label} | {url} ===")
            try:
                config = CrawlerRunConfig(
                    delay_before_return_html=3.0,
                    page_timeout=30000,
                )
                result = await crawler.arun(url=url, config=config)
                status = "OK" if result.success else "FAIL"
                md = result.markdown or ""
                print(f"  [{status}] status={result.status_code} md={len(md)} chars")
                # 印前 300 chars 看內容
                preview = md[:300].replace("\n", " ")
                print(f"  preview: {preview[:200]}")
                # 寫 raw
                fname = re.sub(r"[^\w]", "_", label) + ".md"
                out = os.path.join(OUT_DIR, fname)
                with open(out, "w", encoding="utf-8") as f:
                    f.write(f"# {label}\nURL: {url}\nfetched: {datetime.now().isoformat()}\n\n")
                    f.write(md)
                results.append({
                    "label": label,
                    "url": url,
                    "status": status,
                    "code": result.status_code,
                    "chars": len(md),
                    "file": out,
                })
            except Exception as e:
                print(f"  ✗ EXC: {e}")
                results.append({"label": label, "url": url, "status": "EXC", "error": str(e)})

    # 寫 index
    out = os.path.join(OUT_DIR, f"gov_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n=== 完成 → {out} ===")

asyncio.run(main())
