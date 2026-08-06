"""dedup_benchmark.py
跑 5 輪同一站,看哪些是穩定新聞 vs 雜訊
建立 benchmark set,給未來 dedup 演算法用
"""
import asyncio
import hashlib
import json
import os
import re
from datetime import datetime
from collections import Counter
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

SITES = [
    ("ETtoday_房產", "https://house.ettoday.net/news-list.htm"),
    ("ETtoday_新聞總覽", "https://www.ettoday.net/news/news-list.htm"),
    ("Yahoo_房地產", "https://tw.news.yahoo.com/real-estate"),
    ("HN_top", "https://news.ycombinator.com/"),
    ("B站_AI短劇", "https://search.bilibili.com/all?keyword=AI%E7%9F%AD%E5%8A%87"),
    ("GITHUB_trending_python", "https://github.com/trending/python?since=daily"),
]

OUT_DIR = os.path.expanduser("~/Desktop/crawl4ai/benchmark")
os.makedirs(OUT_DIR, exist_ok=True)

def title_hash(title):
    """去標題變體: 小寫 + 移除空白 + 移除標點"""
    t = re.sub(r'[\s\W_]+', '', title.lower())
    return hashlib.md5(t.encode('utf-8')).hexdigest()[:12]

async def fetch_titles(site_name, url, run_idx):
    """抓一次,回傳 titles 列表 + metadata"""
    async with AsyncWebCrawler(headless=True) as crawler:
        config = CrawlerRunConfig(
            word_count_threshold=20,
            exclude_external_links=False,
            excluded_tags=['script', 'style', 'noscript', 'iframe', 'header', 'footer', 'nav'],
        )
        result = await crawler.arun(url=url, config=config)
        if not result.success:
            return None
        # 從 markdown 提取標題
        md = result.markdown or ""
        titles = []
        # 找 markdown link
        for m in re.finditer(r'\[([^\[\]]{8,200}?)\]\(([^)]+)\)', md):
            title, link = m.group(1).strip(), m.group(2).strip()
            # 過濾 nav/廣告
            skip = ['登入', '註冊', 'APP', '下載', 'English', '首頁', 'App Store', 'Google Play',
                    'Skip to', '更多', '熱門', '發送', '取消', '送出', '使用條款', '隱私權',
                    'cookie', 'Cookie', '追蹤', '關於', '聯絡', '廣告', '服務', '說明', '客服']
            if any(s in title for s in skip) and len(title) < 30:
                continue
            if 'javascript:' in link or '#' == link[:1] or 'mailto:' in link:
                continue
            if not re.search(r'http', link):
                continue
            titles.append({'title': title, 'link': link, 'h': title_hash(title)})
        return {
            'site': site_name,
            'url': url,
            'run': run_idx,
            'ts': datetime.now().isoformat(timespec='seconds'),
            'n_titles': len(titles),
            'titles': titles,
        }

async def main():
    runs = 5
    all_data = {site[0]: [] for site in SITES}
    print(f"=== 跑 {runs} 輪, 每輪 {len(SITES)} 站 ===\n")
    for r in range(1, runs+1):
        print(f"--- 輪 {r}/{runs} ---")
        for site_name, url in SITES:
            data = await fetch_titles(site_name, url, r)
            if data is None:
                print(f"  ✗ {site_name}: FAILED")
                continue
            all_data[site_name].append(data)
            print(f"  ✓ {site_name}: {data['n_titles']} titles")
        # 每輪間留 1s 避免 429
        await asyncio.sleep(1)
    # 存原始
    out_raw = os.path.join(OUT_DIR, f"benchmark_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(out_raw, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"\n=== 儲存 {out_raw} ===\n")
    # 分析
    report_lines = ["# Dedup Benchmark Report\n", f"Date: {datetime.now().isoformat()}\n", f"Runs: {runs}\n", f"Sites: {len(SITES)}\n\n"]
    for site_name, runs_data in all_data.items():
        if not runs_data:
            continue
        # 累計每個 h 出現幾次
        h_counter = Counter()
        all_titles = []
        for run in runs_data:
            for t in run['titles']:
                h_counter[t['h']] += 1
                all_titles.append(t)
        n_unique = len(h_counter)
        n_total = sum(run['n_titles'] for run in runs_data)
        # 穩定: 出現 >= 3 輪的標題
        stable = [(h, c) for h, c in h_counter.most_common() if c >= 3]
        # 一次性: 只出現 1 次
        one_off = [h for h, c in h_counter.items() if c == 1]
        # 算噪音率 (標題 < 8 字)
        short = sum(1 for t in all_titles if len(t['title']) < 8)
        report_lines.append(f"## {site_name}\n")
        report_lines.append(f"- URL: {runs_data[0]['url']}\n")
        report_lines.append(f"- 總抓取: {n_total} titles\n")
        report_lines.append(f"- unique: {n_unique} ({n_unique*100/max(n_total,1):.1f}%)\n")
        report_lines.append(f"- 穩定 (>=3 輪): {len(stable)} 個\n")
        report_lines.append(f"- 一次性 (只 1 輪): {len(one_off)} 個\n")
        report_lines.append(f"- 短標題 (<8字, 可能是雜訊): {short} 個 ({short*100/max(n_total,1):.1f}%)\n")
        if stable:
            report_lines.append(f"- Top 5 穩定標題:\n")
            for h, c in stable[:5]:
                # 找原始 title
                orig = next((t['title'] for t in all_titles if t['h'] == h), '?')
                report_lines.append(f"  - [{c}次] {orig}\n")
        report_lines.append("\n")
    out_report = os.path.join(OUT_DIR, f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(out_report, 'w', encoding='utf-8') as f:
        f.writelines(report_lines)
    print(f"=== 報告 {out_report} ===\n")
    # 印摘要
    for line in report_lines:
        print(line.rstrip())

asyncio.run(main())
