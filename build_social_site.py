"""build_social_site.py - 全站重建, 用 social + fresh 一起"""
import json, os, shutil
from datetime import datetime

OUT = os.path.expanduser("~/Desktop/crawl4ai/rag_data")
SITE = os.path.expanduser("~/Desktop/crawl4ai/site")
HTML = os.path.join(SITE, "index.html")
CSS_SRC = os.path.expanduser("~/Desktop/crawl4ai/site_v2.css")
CSS_DST = os.path.join(SITE, "site_v2.css")

all_sources = []
for prefix in ["social_titles_", "fresh_titles_"]:
    matches = [f for f in sorted(os.listdir(OUT)) if f.startswith(prefix) and f.endswith(".json")]
    if matches:
        d = json.load(open(os.path.join(OUT, matches[-1]), encoding="utf-8"))
        for s in d.get("sources", []):
            all_sources.append(s)

buckets = {
    "news":     {"label": "房市新聞",   "emoji": "📰", "color": "#8B2845", "items": []},
    "gov":      {"label": "政府公開",   "emoji": "🏛️", "color": "#1E3A8A", "items": []},
    "ai":       {"label": "AI 雷達",   "emoji": "🤖", "color": "#0E7490", "items": []},
    "drama":    {"label": "短劇市場",   "emoji": "🎬", "color": "#B45309", "items": []},
    "social":   {"label": "社群平台",   "emoji": "💬", "color": "#7C3AED", "items": []},
    "global":   {"label": "國際視野",   "emoji": "🌏", "color": "#166534", "items": []},
    "poll_tex": {"label": "防霾紗窗",   "emoji": "🌬️", "color": "#065F46", "items": []},
    "other":    {"label": "其他",     "emoji": "✨", "color": "#6B21A8", "items": []},
}

for src in all_sources:
    label = src["label"].lower()
    items = src.get("items", [])
    if not items: continue
    if any(k in label for k in ["b站", "bilibili", "短劇", "seedance", "可靈", "即夢", "動漫", "ai漫"]):
        cat = "drama"
    elif any(k in label for k in ["reddit", "threads", " x ", "youtube", "微博", "抖音", "facebook", "fb "]):
        cat = "social"
    elif any(k in label for k in ["ettoday", "yahoo", "新聞", "news", "hn", "hacker"]):
        cat = "news"
    elif any(k in label for k in ["央行", "cbc", "mops", "moi", "moj", "moea", "ftc", "公平", "內政", "地政"]):
        cat = "gov"
    elif any(k in label for k in ["github", "huggingface", "papers", "trend", "ai", "radar"]):
        cat = "ai"
    elif any(k in label for k in ["poll", "n95", "pm2.5", "moenv", "airtw", "防霾", "環保"]):
        cat = "poll_tex"
    else:
        cat = "other"
    buckets[cat]["items"].extend(items)
    if len(buckets[cat]["items"]) > 60:
        buckets[cat]["items"] = buckets[cat]["items"][:60]

total = sum(len(b["items"]) for b in buckets.values())
print(f"Total: {total} titles")
for k, b in buckets.items():
    if b["items"]:
        print(f"  {k:10s} {len(b['items']):3d} items")

CSS = open(CSS_SRC, encoding="utf-8").read()
now = datetime.now()

# 即時精選
featured = []
for k in ["news", "drama", "ai", "social", "gov"]:
    if buckets[k]["items"]:
        for it in buckets[k]["items"][:2]:
            featured.append({**it, "section": buckets[k]["label"], "color": buckets[k]["color"]})
            if len(featured) >= 6: break
    if len(featured) >= 6: break

featured_html = ""
for f in featured:
    title = f["title"].replace("<", "&lt;").replace(">", "&gt;")[:120]
    featured_html += f'''<a class="card" href="{f.get("link","#")}" target="_blank" rel="noopener" style="--c:{f['color']};">
    <span class="card-tag" style="background:{f['color']};">{f['section']}</span>
    <h3 class="card-title">{title}</h3>
  </a>'''

sections_html = ""
section_idx = 1
for key in ["news", "gov", "ai", "drama", "social", "poll_tex"]:
    b = buckets[key]
    if not b["items"]: continue
    roman = ["I", "II", "III", "IV", "V", "VI", "VII"][section_idx - 1]
    items = b["items"]
    cards = ""
    for it in items[:60]:
        title = it["title"].replace("<", "&lt;").replace(">", "&gt;")[:140]
        link = it.get("link", "#")
        cards += f'''<a class="card" href="{link}" target="_blank" rel="noopener" style="--c:{b['color']};">
        <span class="card-dot" style="background:{b['color']};"></span>
        <h3 class="card-title">{title}</h3>
      </a>'''
    sections_html += f'''<section class="section" id="{key}">
    <div class="wrap">
      <div class="section-head">
        <span class="section-num">{roman}</span>
        <div>
          <h2 class="section-title"><span class="emoji">{b['emoji']}</span> {b['label']}</h2>
          <p class="section-sub">{len(items)} 條即時內容</p>
        </div>
      </div>
      <div class="grid">{cards}</div>
    </div>
  </section>'''
    section_idx += 1

html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>老蔡的 RAG 知識庫 — crawl4ai 即時累積</title>
  <meta name="description" content="crawl4ai 0.9.2 + patchright 自動抓 23 站業務內容">
  <link rel="stylesheet" href="site_v2.css">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📡</text></svg>">
</head>
<body>
  <header class="hero">
    <div class="wrap">
      <div class="hero-eyebrow">
        <span class="live-pill"><span class="live-dot"></span> LIVE</span>
        <span>Issue №{now.strftime("%Y%m%d.%H%M")}</span>
      </div>
      <h1>讓 web <em>變得</em> 可讀。<br>把整個網路變成你的 RAG。</h1>
      <p class="hero-lede">crawl4ai 0.9.2 + <b>patchright</b> 自動從 <b>{len(all_sources)} 個來源站</b>抓資料。智慧去噪、每 6 小時自動累積、即時更新。</p>
      <div class="hero-meta">
        <span>📦 <b>{total:,}</b> 條 items</span>
        <span>🌐 <b>{len(all_sources)}</b> 來源站</span>
        <span>💬 <b>{len(buckets['social']['items'])}</b> 社群</span>
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
print(f"\n=== 重新生成 ===")
print(f"Total: {total} titles in {len(all_sources)} sources")
print(f"HTML: {HTML} ({len(html)} chars)")
