"""build_v3_site.py - 用所有 sources 重新 build"""
import json, os, shutil, glob
from datetime import datetime

OUT = os.path.expanduser("~/Desktop/crawl4ai/rag_data")
SITE = os.path.expanduser("~/Desktop/crawl4ai/site")
HTML = os.path.join(SITE, "index.html")
CSS_SRC = os.path.expanduser("~/Desktop/crawl4ai/site_v2.css")
CSS_DST = os.path.join(SITE, "site_v2.css")

# 載入所有 sources: fresh + social + social_v2
ALL_SOURCES = []
for pattern in ["fresh_titles_*.json", "social_titles_*.json", "social_v2_titles_*.json"]:
    for fp in sorted(glob.glob(os.path.join(OUT, pattern))):
        try:
            d = json.load(open(fp, encoding="utf-8"))
            if "sources" in d:
                for s in d["sources"]:
                    if s.get("items"):
                        s["_file"] = os.path.basename(fp)
                        ALL_SOURCES.append(s)
        except Exception as e:
            print(f"  ! {fp}: {e}")

print(f"Loaded {len(ALL_SOURCES)} sources, {sum(len(s['items']) for s in ALL_SOURCES)} titles")

# 分類
SECTIONS_DEF = [
    ("news", "🏠 房市新聞", "#8B2845", ["ettoday", "yahoo", "新聞", "news", "ptt", "房市", "real+estate", "realestate", "杨梅", "楊梅", "楊梅"]),
    ("gov", "🏛️ 政府公開", "#1E3A8A", ["央行", "cbc", "mops", "moi", "moj", "moea", "ftc", "land", "公平", "公報", "財政", "法規"]),
    ("ai", "🤖 AI 雷達", "#0E7490", ["github", "huggingface", "papers", "trend", "ai", "radar", "ollama", "llama", "stable", "unsloth"]),
    ("drama", "🎬 短劇市場", "#B45309", ["b站", "bilibili", "短劇", "drama", "douyin", "抖音", "seedance", "可靈", "即夢", "kling", "short", "yt"]),
    ("social", "💬 社群平台", "#7C3AED", ["x", "twitter", "reddit", "threads", "微博", "知乎", "掘金", "csdn", "weibo", "hn", "hacker"]),
    ("other", "✨ 其他", "#6B21A8", []),
]
buckets = {k: [] for k, _, _, _ in SECTIONS_DEF}

def categorize(label):
    s = (label or "").lower()
    for k, _, _, kws in SECTIONS_DEF:
        if any(kw in s for kw in kws):
            return k
    return "other"

for src in ALL_SOURCES:
    cat = categorize(src["label"])
    buckets[cat].append(src)

for k in buckets:
    buckets[k] = sorted(buckets[k], key=lambda x: -len(x["items"]))

print("\n=== Sections ===")
total = 0
for k, label, color, _ in SECTIONS_DEF:
    if buckets[k]:
        c = sum(len(s["items"]) for s in buckets[k])
        total += c
        print(f"  {k:10s} {label}  {c} titles in {len(buckets[k])} sources")
print(f"Total: {total} titles")

# 即時精選
featured = []
for k, label, color, _ in SECTIONS_DEF:
    for src in buckets[k][:1]:
        for it in src["items"][:2]:
            featured.append({**it, "section": label, "color": color, "src": src["label"]})
            if len(featured) >= 8: break
    if len(featured) >= 8: break

# Sections
sections_html = ""
section_idx = 1
roman = ["I", "II", "III", "IV", "V", "VI"]
for k, label, color, _ in SECTIONS_DEF:
    if not buckets[k]: continue
    all_items = []
    for src in buckets[k]:
        for it in src["items"][:30]:
            it["_src"] = src["label"]
            all_items.append(it)
    cards = ""
    for it in all_items[:60]:
        title = it.get("title", "").replace("<", "&lt;").replace(">", "&gt;")[:120]
        link = it.get("link", "#")
        src_label = it.get("_src", "")[:25]
        cards += f'<a class="card" href="{link}" target="_blank" rel="noopener" style="--c:{color};">'
        cards += f'<span class="card-dot" style="background:{color};"></span>'
        cards += f'<h3 class="card-title">{title}</h3>'
        cards += f'<span class="card-src">{src_label}</span>'
        cards += '</a>'
    sections_html += f'''<section class="section" id="{k}">
  <div class="wrap">
    <div class="section-head">
      <span class="section-num">{roman[section_idx-1] if section_idx <= 6 else section_idx}</span>
      <div>
        <h2 class="section-title">{label}</h2>
        <p class="section-sub">{len(all_items)} 條即時內容</p>
      </div>
    </div>
    <div class="grid">{cards}</div>
  </div>
</section>'''
    section_idx += 1

# Featured HTML
featured_html = ""
for f in featured:
    title = f.get("title", "").replace("<", "&lt;").replace(">", "&gt;")[:140]
    featured_html += f'<a class="card featured-card" href="{f.get("link","#")}" target="_blank" rel="noopener" style="--c:{f["color"]};">'
    featured_html += f'<span class="card-tag" style="background:{f["color"]};">{f["section"]}</span>'
    featured_html += f'<h3 class="card-title">{title}</h3>'
    featured_html += f'<span class="card-src">{f.get("src","")}</span>'
    featured_html += '</a>'

CSS = open(CSS_SRC, encoding="utf-8").read()
now = datetime.now()

html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>老蔡的 RAG 知識庫 — crawl4ai 即時累積</title>
  <meta name="description" content="crawl4ai 0.9.2 + patchright 自動抓 35+ 站業務內容">
  <link rel="stylesheet" href="site_v2.css">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📡</text></svg>\">
</head>
<body>
  <header class="hero">
    <div class="wrap">
      <div class="hero-eyebrow">
        <span class="live-pill"><span class="live-dot"></span> LIVE</span>
        <span>Issue №{now.strftime("%Y%m%d.%H%M")}</span>
      </div>
      <h1>讓 web <em>變得</em> 可讀。<br>把整個網路變成你的 RAG。</h1>
      <p class="hero-lede">crawl4ai 0.9.2 + <b>patchright</b> 自動從 <b>{len(ALL_SOURCES)} 個來源站</b>抓資料。智慧去噪、每 6 小時自動累積、即時更新。</p>
      <div class="hero-meta">
        <span>📦 <b>{total:,}</b> 條 items</span>
        <span>🌐 <b>{len(ALL_SOURCES)}</b> 來源站</span>
        <span>💬 <b>{len(buckets['social'])}</b> 社群</span>
        <span>⏰ 更新於 {now.strftime("%Y-%m-%d %H:%M")}</span>
      </div>
    </div>
  </header>
  <section class="featured">
    <div class="wrap">
      <div class="section-head">
        <span class="section-num">★</span>
        <div>
          <h2 class="section-title">即時精選</h2>
          <p class="section-sub">最新業務相關的真實內容</p>
        </div>
      </div>
      <div class="grid featured-grid">{featured_html}</div>
    </div>
  </section>
  {sections_html}
  <footer class="foot">
    <div class="wrap">
      <div class="foot-meta">Crawl4AI 0.9.2 · patchright stealth · chromium-headless-shell · Python 3.11</div>
      <div class="foot-credit">Built by <a href="https://github.com/sky770825" target="_blank">老蔡</a> · 達爾 Q / MiniMax-M3</div>
      <div class="foot-meta" style="margin-top:12px;">Auto-rebuild every 6h · cron job 65efba3a52de</div>
    </div>
  </footer>
</body>
</html>"""

os.makedirs(SITE, exist_ok=True)
open(HTML, "w", encoding="utf-8").write(html)
shutil.copy(CSS_SRC, CSS_DST)
print(f"\n=== Done ===")
print(f"Total: {total} titles in {len(ALL_SOURCES)} sources")
print(f"HTML: {HTML} ({len(html)} chars)")
