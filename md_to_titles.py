"""md_to_titles.py - 從 markdown 抽所有真實標題
策略: 抓 [text](url) 連結 + 跳過明顯雜訊
"""
import json, os, re
from datetime import datetime

SRC = os.path.expanduser("~/Desktop/crawl4ai/rag_data/fresh_20260806.json")
OUT = os.path.expanduser("~/Desktop/crawl4ai/rag_data/fresh_titles_20260806.json")

NOISE = {
    "Skip to content", "Sponsor", "MCP Registry", "GitHub Advanced Security",
    "Trending", "Topics", "Collections", "Marketplace", "Premium Support",
    "Forks", "Watch", "Star", "README", "License", "Issues",
    "Reloading", "You signed in", "Sign in", "Sign up", "Sign out",
    "Code security", "Secret protection", "Built by",
    "Why GitHub", "Documentation", "Changelog", "Enterprise",
    "Abkhazian", "Reload", "Loading",
    "Hugging Face's logo", "Models", "Datasets", "Spaces",
    "Posts", "Docs", "Pricing", "Blog", "Log In", "Sign Up",
    "Search code", "Repositories", "Users", "Organizations",
    "Find a repository", "Search", "Clear", "Type / to search",
    # 房仲 / 政府 nav
    "網站導覽", "回首頁", "兒童網頁", "意見信箱", "雙語詞彙", "English",
    "跳到主要內容", "跳至主要內容", "至中間內容", "至網站導覽",
    "服務信箱", "訂閱電子報", "按 Enter 到中央內容區塊", "關閉",
    "原  ", "選單  ", "公告快易查", "公司歷年變更登記", "公司總覽",
    "活動報名", "返回首頁", "聯絡我們", "網站地圖", "隱私權", "資訊安全",
    "首頁", "關於我們", "聯絡資訊", "常見問題", "FAQ", "Q&A",
    "歷史活動", "歷史專題", "會員中心", "家外媒體", "數位廣告刊登",
    "很抱歉，您使用的瀏覽器版本過低。 建議改用 Google Chrome, Firefox, Microsoft Edge 以獲得最佳瀏覽經驗！",
    "購物中心", "App 下載", "AI 事件整理", "每日Yahoo焦點",
    "past", "comments", "show", "jobs", "ask", "newest", "front", "newcomments", "submit",
    "Hacker News",
    "B站 短劇", "稍后再看", "游戏中心", "一打歌", "下载客户端",
    "GitHub Copilot", "GitHub Copilot app", "Actions", "Codespaces",
    # Pure punctuation / empty
    "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.",
}

NOISE_RE = re.compile(r"^(?:\d+\s*(?:hours?|minutes?|days?|seconds?)\s*ago|\d+\s*points?\s+by\s+\w+|GitHub\s+\d+k|Star|Fork|\d+\.)$", re.IGNORECASE)

LINK_RE = re.compile(r"\[([^\]]{4,200})\]\((https?://[^)]+)\)")
HEADING_RE = re.compile(r"^#{2,4}\s+(.+)$", re.MULTILINE)

NOISE_LIKE = re.compile(r"^(?:抽|抽!|免費抽|天天|Google News|中華電信|門票|粉絲團|好康|抽200|加碼|揪好友|達人)",
    re.IGNORECASE)

def is_noise(t):
    t = t.strip().rstrip(".,;:")
    if t in NOISE: return True
    if NOISE_RE.match(t): return True
    if t.startswith("!"): return True
    if t.startswith("(") and t.endswith(")"): return True
    if "![图" in t: return True
    if t.startswith("[") and ("BV" in t or "sm" in t or "av" in t): return True
    if "稍后再看" in t: return True
    if "稍後再看" in t: return True
    if t.startswith("【") and t.endswith("】") and len(t) < 8: return True
    if re.match(r"^[\W_]+$", t): return True
    if len(t) < 8: return True
    # 純數字/純英文 1-2 詞
    if re.match(r"^\d+\s*(comments?|points?)$", t, re.IGNORECASE): return True
    if re.match(r"^[a-z0-9_-]+$", t) and "." not in t and len(t) < 25: return True
    if re.match(r"^[a-z0-9.-]+\.(com|io|org|net|tw|cn)$", t, re.IGNORECASE): return True
    # GitHub nav
    if t.startswith("GitHub ") and len(t) < 50: return True
    # 純 1-3 字中文
    if re.match(r"^[\u4e00-\u9fff]{1,3}$", t): return True
    # 廣告 / 抽獎 / 活動 nav
    if NOISE_LIKE.match(t): return True
    if "活動新聞專區" in t: return True
    if "門票" in t and len(t) < 30: return True
    if "粉絲團" in t: return True
    if "粉絲" in t and len(t) < 25: return True
    if "IoT" in t: return True
    if "５Ｇ" in t or "5G" in t.upper(): return True
    if "金孫" in t: return True
    if "好康" in t: return True
    if "大谷翔平" in t: return True  # ETtoday 廣告常客
    if "古林" in t: return True
    return False

def extract(md, source_url):
    titles = []
    seen = set()
    # 1. markdown 連結
    for m in LINK_RE.finditer(md):
        t = m.group(1).strip()
        t = re.sub(r"\*+", "", t).strip()
        link = m.group(2)
        if is_noise(t): continue
        if t in seen: continue
        seen.add(t)
        titles.append({"title": t, "link": link})
    # 2. 2-4 級 heading
    for m in HEADING_RE.finditer(md):
        t = m.group(1).strip()
        t = re.sub(r"\*+", "", t).strip()
        if is_noise(t): continue
        if t in seen: continue
        seen.add(t)
        titles.append({"title": t, "link": "#"})
    return titles

src = json.load(open(SRC, encoding="utf-8"))
all_titles = []
per_source = {}
for s in src["sources"]:
    if s.get("status") != "ok": continue
    md = s.get("md", "")
    titles = extract(md, s["url"])
    per_source[s["label"]] = len(titles)
    for t in titles:
        t["source"] = s["label"]
        all_titles.append(t)

# 來源分組
by_source = {}
for t in all_titles:
    by_source.setdefault(t["source"], []).append(t)

result = {
    "fetched_at": datetime.now().isoformat(),
    "total_titles": len(all_titles),
    "per_source": per_source,
    "sources": [{"label": k, "count": len(v), "items": v[:50]} for k, v in by_source.items()],
}
json.dump(result, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"=== 抽取 {len(all_titles)} 真實標題 ===")
for k, v in per_source.items():
    print(f"  {k:30s} {v:4d} titles")
print(f"Wrote: {OUT}")
