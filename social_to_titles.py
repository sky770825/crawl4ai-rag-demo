"""social_to_titles.py - 從 social_20260807 抽真實社群內容
"""
import json, os, re
from datetime import datetime
from urllib.parse import urlparse

OUT = os.path.expanduser("~/Desktop/crawl4ai/rag_data")
RAW = [f for f in os.listdir(OUT) if f.startswith("social_") and f.endswith(".json")][-1]
src = json.load(open(os.path.join(OUT, RAW), encoding="utf-8"))

NOISE = {
    "Skip to content", "Sponsor", "MCP Registry", "GitHub Advanced Security",
    "首頁", "Shorts", "訂閱內容", "說明中心", "上傳", "應用程式", "更多", "更多項目",
    "登入", "搜尋", "篩選器", "動態消息", "探索", "Reels", "商店", "通知", "建立", "建立新...",
    "Sign Up", "Log In", "Sign up for Reddit", "Log in to Reddit",
    "past", "comments", "show", "jobs", "ask", "newest", "front", "newcomments", "submit",
    "Best", "Hot", "New", "Top", "Rising", "Card", "Compact",
    "Open menu", "Open navigation", "Go to Reddit Home",
}

NOISE_RE = re.compile(r"^(?:\d+\s*(hours?|minutes?|days?|seconds?|hr|min)\.?\s*ago|\d+\s*points?\s+by\s+\w+|\d+\s*comments?$|u/\w+|r/\w+)$", re.IGNORECASE)

LINK_RE = re.compile(r"\[([^\]]{4,300})\]\((https?://[^)]+)\)")

def is_noise(t):
    t = t.strip().rstrip(".,;:")
    if not t: return True
    if t in NOISE: return True
    if NOISE_RE.match(t): return True
    if t.startswith("!") or t.startswith("(") and t.endswith(")"): return True
    if "![图片" in t: return True
    if "稍后再看" in t or "稍後再看" in t: return True
    # X / Twitter nav
    if t in ["Terms of Service", "Privacy Policy", "Cookie Use", "Ads & Business", "Developers", "Accessibility"]:
        return True
    if t.startswith("blog.") or t.startswith("github.com/") or t.startswith("x.com/"):
        return True
    if re.match(r"^[\W_]+$", t): return True
    if len(t) < 8: return True
    # 純數字
    if re.match(r"^[\d.,]+\s*\w*$", t) and len(t) < 15: return True
    if t.startswith("u/") or t.startswith("r/"): return True
    if re.match(r"^[\d.]+[KMB]?\s*$", t): return True
    return False

out_sources = []
for entry in src:
    if entry.get("status") != 200: continue
    md = entry.get("md", "")
    if not md: continue
    titles = []
    seen = set()
    for m in LINK_RE.finditer(md):
        title = m.group(1).strip()
        if is_noise(title): continue
        if title in seen: continue
        seen.add(title)
        titles.append({"title": title, "link": m.group(2)})
    # 同時抓 YouTube / Reddit 文章 (用時間標記當分隔)
    if titles:
        out_sources.append({
            "label": entry["label"], "url": entry["url"],
            "count": len(titles), "items": titles[:60]
        })
        print(f"  {entry['label']:30s} {len(titles):3d} titles")

out = {"sources": out_sources, "total": sum(s["count"] for s in out_sources)}
fp = os.path.join(OUT, f"social_titles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
open(fp, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=2))
print(f"\nTotal: {out['total']} titles in {len(out_sources)} sources")
print(f"Wrote: {fp}")
