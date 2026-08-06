"""long_running_test.py - 30 分鐘連續爬蟲壓力
驗證記憶體 / 速度 / 錯誤率隨時間變化
"""
import asyncio, json, os, time, psutil
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

OUT_DIR = os.path.expanduser("~/Desktop/crawl4ai/benchmark")
os.makedirs(OUT_DIR, exist_ok=True)

# 友善站輪詢池
POOL = [
    "https://news.ycombinator.com/",
    "https://www.bbc.com/news",
    "https://github.com/trending/python?since=daily",
    "https://www.ettoday.net/news/news-list.htm",
    "https://www.theguardian.com/uk",
    "https://en.yna.co.kr/",
    "https://www3.nhk.or.jp/news/",
    "https://www.channelnewsasia.com/",
    "https://www.dw.com/en",
    "https://www.ndtv.com/",
]

DURATION_SEC = 600  # 10 分鐘(老蔡測試用,可改 1800=30分)

async def main():
    cfg = CrawlerRunConfig(verbose=False, magic=False)
    metrics = []
    p = psutil.Process()
    start_mem = p.memory_info().rss / 1024 / 1024
    start = time.time()
    count = 0
    err_count = 0
    bytes_total = 0
    
    async with AsyncWebCrawler(headless=True) as crawler:
        i = 0
        while time.time() - start < DURATION_SEC:
            url = POOL[i % len(POOL)]
            t0 = time.time()
            try:
                r = await crawler.arun(url=url, config=cfg)
                dt = time.time() - t0
                if r.success:
                    count += 1
                    md = r.markdown or ''
                    bytes_total += len(md)
                    mem = p.memory_info().rss / 1024 / 1024
                    elapsed = time.time() - start
                    if count % 10 == 0:
                        print(f"  [{elapsed:5.0f}s] #{count} {url[:30]:30s} md={len(md):>6} t={dt:.1f}s mem={mem:.0f}MB")
                    metrics.append({
                        'i': count, 't': elapsed, 'dt': dt,
                        'url': url, 'md': len(md), 'mem': mem, 'err': False
                    })
                else:
                    err_count += 1
                    metrics.append({'i': count, 't': time.time()-start, 'dt': dt, 'url': url, 'err': True, 'err_msg': str(r.error_message)[:100]})
            except Exception as e:
                err_count += 1
                metrics.append({'i': count, 't': time.time()-start, 'err': True, 'err_msg': str(e)[:100]})
                print(f"  [EXC] #{count} {url[:30]} {str(e)[:60]}")
            i += 1
    
    elapsed = time.time() - start
    end_mem = p.memory_info().rss / 1024 / 1024
    
    summary = {
        'duration_sec': elapsed,
        'total_requests': i,
        'success': count,
        'error': err_count,
        'pass_rate': count*100/i if i else 0,
        'avg_dt': sum(m['dt'] for m in metrics if 'dt' in m) / max(count, 1),
        'total_md_chars': bytes_total,
        'start_mem_mb': start_mem,
        'end_mem_mb': end_mem,
        'mem_growth_mb': end_mem - start_mem,
        'req_per_sec': i / elapsed if elapsed else 0,
        'metrics_first10': metrics[:10],
        'metrics_last10': metrics[-10:],
    }
    
    out = os.path.join(OUT_DIR, f"long_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 30 分鐘壓力 ===")
    print(f"  總請求: {i}")
    print(f"  成功: {count} ({summary['pass_rate']:.1f}%)")
    print(f"  失敗: {err_count}")
    print(f"  平均延遲: {summary['avg_dt']:.2f}s")
    print(f"  記憶體: {start_mem:.0f}MB → {end_mem:.0f}MB (增 {end_mem-start_mem:.0f}MB)")
    print(f"  req/s: {summary['req_per_sec']:.2f}")
    print(f"  抓取總量: {bytes_total/1024/1024:.1f}MB")
    print(f"  報告: {out}")

asyncio.run(main())
