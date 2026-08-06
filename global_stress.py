"""global_stress.py - 24 國跨語言壓力測試
累積國際經驗 + 找語系陷阱
"""
import asyncio, json, os
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

OUT_DIR = os.path.expanduser("~/Desktop/crawl4ai/benchmark")
os.makedirs(OUT_DIR, exist_ok=True)

TARGETS = [
    # 西歐
    ("英國 BBC", "https://www.bbc.com/news"),
    ("英國 The Guardian", "https://www.theguardian.com/uk"),
    ("法國 Le Monde", "https://www.lemonde.fr/"),
    ("德國 DW", "https://www.dw.com/en"),
    ("西班牙 El País", "https://english.elpais.com/"),
    ("義大利 ANSA", "https://www.ansa.it/english/"),
    # 北歐
    ("芬蘭 Yle", "https://yle.fi/news"),
    ("瑞典 SvD", "https://www.svd.se/"),
    ("挪威 NRK", "https://www.nrk.no/"),
    ("丹麥 DR", "https://www.dr.dk/nyheder"),
    # 東歐
    ("波蘭 TVN24", "https://tvn24.pl/"),
    ("俄羅斯 RT", "https://www.rt.com/"),
    ("土耳其 TRT", "https://www.trtworld.com/"),
    # 亞洲
    ("日本 NHK", "https://www3.nhk.or.jp/news/"),
    ("日本 Asahi", "https://www.asahi.com/ajw/"),
    ("韓國 Yonhap", "https://en.yna.co.kr/"),
    ("新加坡 CNA", "https://www.channelnewsasia.com/"),
    ("馬來西亞 TheStar", "https://www.thestar.com.my/"),
    ("泰國 BangkokPost", "https://www.bangkokpost.com/"),
    ("越南 VNExpress", "https://vnexpress.net/"),
    ("印尼 Kompas", "https://www.kompas.com/"),
    ("印度 NDTV", "https://www.ndtv.com/"),
    ("菲律賓 Inquirer", "https://www.inquirer.net/"),
    # 中東
    ("以色列 TimesOfIsrael", "https://www.timesofisrael.com/"),
    ("UAE TheNational", "https://www.thenationalnews.com/"),
    # 非洲
    ("南非 News24", "https://www.news24.com/"),
    ("肯亞 Nation", "https://nation.africa/"),
    # 南美
    ("巴西 Folha", "https://www1.folha.uol.com.br/internacional/en/"),
    ("阿根廷 Clarín", "https://www.clarin.com/"),
    # 大洋洲
    ("澳洲 ABC", "https://www.abc.net.au/news"),
    ("紐西蘭 NZHerald", "https://www.nzherald.co.nz/"),
]

async def main():
    cfg = CrawlerRunConfig(verbose=False, magic=False)
    results = []
    async with AsyncWebCrawler(headless=True) as crawler:
        sem = asyncio.Semaphore(4)  # max 4 parallel
        async def one(name, url):
            async with sem:
                try:
                    r = await crawler.arun(url=url, config=cfg)
                    results.append({
                        'name': name, 'url': url,
                        'status': r.status_code,
                        'success': r.success,
                        'md_chars': len(r.markdown or ''),
                        'title': (r.metadata or {}).get('title', '?')[:60]
                    })
                    print(f"  [{r.status_code}] {name:30s} md={len(r.markdown or ''):>6} t={r.success}")
                except Exception as e:
                    results.append({'name': name, 'url': url, 'error': str(e)[:100]})
                    print(f"  [ERR] {name:30s} {str(e)[:60]}")
        await asyncio.gather(*[one(n, u) for n, u in TARGETS])
    
    out = os.path.join(OUT_DIR, f"global_stress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({'targets': len(TARGETS), 'results': results}, f, ensure_ascii=False, indent=2)
    
    ok = sum(1 for r in results if r.get('success'))
    err = sum(1 for r in results if 'error' in r)
    fail = sum(1 for r in results if r.get('success') is False and 'error' not in r)
    print(f"\n=== 24 國 30 站 ===\nOK {ok} / FAIL {fail} / ERR {err} / Total {len(TARGETS)}")
    print(f"Pass rate: {ok*100/len(TARGETS):.1f}%")
    print(f"Report: {out}")

asyncio.run(main())
