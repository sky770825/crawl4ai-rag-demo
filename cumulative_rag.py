"""cumulative_rag.py - 累積式 RAG 知識庫
- 跑一輪 → hash dedup 加進 master
- 不重複存
- 統計: 今日新增 / 累計 / 站點分佈
"""
import asyncio, json, os, hashlib
from datetime import datetime
from collections import Counter
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

OUT_DIR = os.path.expanduser("~/Desktop/crawl4ai/rag_data")
MASTER = os.path.join(OUT_DIR, "master_rag.jsonl")
os.makedirs(OUT_DIR, exist_ok=True)

# 載入既有
existing_hashes = set()
if os.path.exists(MASTER):
    with open(MASTER, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                d = json.loads(line)
                existing_hashes.add(d.get('h', ''))
            except: pass

print(f"現有: {len(existing_hashes)} 條")

# 目標: 老蔡核心業務
SOURCES = [
    ("ETtoday 房產", "https://house.ettoday.net/news-list.htm"),
    ("ETtoday 新聞總覽", "https://www.ettoday.net/news/news-list.htm"),
    ("Yahoo 房地產", "https://tw.news.yahoo.com/real-estate"),
    ("央行 利率", "https://www.cbc.gov.tw/tw/mp-002.html"),
    ("內政部 地政", "https://www.land.moi.gov.tw/chhtml/index"),
    ("平均地權", "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=D0060066"),
    ("租賃條例", "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=D0060104"),
    ("公開資訊觀測站", "https://mops.twse.com.tw/mops/web/index"),
    ("公平會", "https://www.ftc.gov.tw/internet/main/index.aspx"),
    ("環保署", "https://airtw.moenv.gov.tw/"),
]

def is_noise(title):
    """去噪"""
    if not title: return True
    if len(title) < 6: return True
    # 時間字串
    if re.match(r'^\d+\s*(hours?|minutes?|days?|seconds?)\s+ago$', title, re.I): return True
    # 跨站固定雜訊
    if title in {'Google News', 'Skip to content', 'Sponsor', 'App 下載'}: return True
    return False

import re

def extract_titles(md, source):
    """通用抽取"""
    titles = []
    # 抓 ### 或 [text](url) 模式
    for line in md.split('\n'):
        line = line.strip()
        if not line: continue
        # markdown 標題
        if line.startswith('###') or line.startswith('##'):
            t = re.sub(r'^#+\s*', '', line).strip()
            if 6 < len(t) < 200:
                titles.append((t, source))
        # markdown link [text](url) 排除 nav
        elif line.startswith('* [') or line.startswith('- ['):
            m = re.match(r'^\*?\s*-?\s*\[([^\]]+)\]\(([^\)]+)\)', line)
            if m:
                t = m.group(1).strip()
                if 6 < len(t) < 200:
                    titles.append((t, source))
    # 去重
    seen = set()
    out = []
    for t, s in titles:
        if t in seen: continue
        if is_noise(t): continue
        seen.add(t)
        out.append((t, s))
    return out

async def main():
    cfg = CrawlerRunConfig(verbose=False, magic=False)
    new_count = 0
    site_count = Counter()
    async with AsyncWebCrawler(headless=True) as crawler:
        for name, url in SOURCES:
            try:
                r = await crawler.arun(url=url, config=cfg)
                if not r.success: 
                    print(f"  [FAIL] {name}")
                    continue
                titles = extract_titles(r.markdown or '', name)
                added = 0
                with open(MASTER, 'a', encoding='utf-8') as f:
                    for t, s in titles:
                        h = hashlib.sha256(f"{s}::{t}".encode()).hexdigest()[:16]
                        if h in existing_hashes: continue
                        existing_hashes.add(h)
                        d = {'h': h, 'source': s, 'title': t, 'crawled': datetime.now().isoformat(), 'url': url}
                        f.write(json.dumps(d, ensure_ascii=False) + '\n')
                        added += 1
                new_count += added
                site_count[name] = added
                print(f"  [{r.status_code}] {name:20s} +{added} (total now: {len(existing_hashes)})")
            except Exception as e:
                print(f"  [ERR] {name}: {str(e)[:80]}")
    
    print(f"\n=== 累積 RAG ===")
    print(f"  今日新增: {new_count}")
    print(f"  累計總數: {len(existing_hashes)}")
    print(f"  站點分佈:")
    for k, v in site_count.most_common():
        print(f"    {k:20s} {v}")
    print(f"\nMaster: {MASTER}")

asyncio.run(main())
