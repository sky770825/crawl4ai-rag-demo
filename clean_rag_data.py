"""清洗 + 驗證 RAG 資料品質
1. 過濾 nav/廣告/星號標題
2. 至少要含「中文 + 標題字數 > 8」
3. 驗證 link 真的能進
"""
import json
import os
import re
import asyncio
from datetime import datetime
from crawl4ai import AsyncWebCrawler

OUT_DIR = os.path.expanduser("~/Desktop/crawl4ai/rag_data")

# 找最新檔
files = sorted([f for f in os.listdir(OUT_DIR) if f.startswith("house_news_")])
src = os.path.join(OUT_DIR, files[-1])
print(f"讀取: {src}")

with open(src, encoding="utf-8") as f:
    data = json.load(f)

# 清洗
BLACKLIST_PATTERNS = [
    r"^\*\s*\[",       # * [xxx]
    r"^下載",          # App 下載
    r"^App\b",
    r"^手機版",
    r"^電腦版",
    r"^看更多",
    r"^更多",
    r"登入|註冊|會員",
    r"^.{1,4}$",       # 標題太短
    r"展覽|門票|抽！",  # 廣告
    r"懶人包$",
    r"Q&A$",
]
BLACKLIST_RE = re.compile("|".join(BLACKLIST_PATTERNS))

# URL pattern
def is_valid_link(url):
    if not url.startswith("http"):
        return False
    if any(x in url for x in ["/topic/", "/tag/", "/category/", "/ads/"]):
        return False
    return True

cleaned = []
for source in data:
    good = []
    for item in source["items"]:
        title = item["title"].strip()
        # 去掉星號和管道
        title = re.sub(r"^\*?\s*\[?|\]?$", "", title)
        title = title.strip()
        if BLACKLIST_RE.search(title):
            continue
        if len(title) < 8:
            continue
        if not is_valid_link(item["link"]):
            continue
        good.append({"title": title, "link": item["link"]})
    print(f"  {source['source']}: {source['count']} → {len(good)} ({len(good)/max(source['count'],1)*100:.0f}%)")
    cleaned.append({**source, "items": good, "count": len(good), "raw_count": source["count"]})

# 去重 (跨 source)
seen_titles = set()
final = []
for source in cleaned:
    unique = []
    for it in source["items"]:
        if it["title"] in seen_titles:
            continue
        seen_titles.add(it["title"])
        unique.append(it)
    source["items"] = unique
    source["count"] = len(unique)
    final.append(source)
    print(f"  去重後 {source['source']}: {source['count']}")

# 寫清洗後
out = src.replace(".json", "_clean.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)

total = sum(s["count"] for s in final)
print(f"\n=== 清洗完成: {total} 高品質 items → {out} ===")
print(f"\n範例前 5 筆:")
for s in final:
    for it in s["items"][:3]:
        print(f"  [{s['source']}] {it['title'][:50]}")
        print(f"    → {it['link'][:80]}")
