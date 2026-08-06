"""build_v4.py - 設計感 v3 + 圖卡化分類
"""
import json, os, shutil, glob
from datetime import datetime
OUT = os.path.expanduser("~/Desktop/crawl4ai/rag_data")
SITE = os.path.expanduser("~/Desktop/crawl4ai/site")
HTML = os.path.join(SITE, "index.html")
CSS_SRC = os.path.expanduser("~/Desktop/crawl4ai/site_v3.css")
CSS_DST = os.path.join(SITE, "site_v3.css")

SOURCES = []
fp = sorted(glob.glob(os.path.join(OUT, "tw_titles_*.json")))[-1]
print(f"Using: {fp}")
d = json.load(open(fp, encoding="utf-8"))
for s in d["sources"]:
    if s.get("items"):
        SOURCES.append(s)
print(f"Loaded {len(SOURCES)} sources, {sum(len(s['items']) for s in SOURCES)} titles")

# 4 大圖卡分類
CATS = [
    {"key": "news", "name": "房仲新聞", "desc": "即時臺灣房仲 / 房市新聞,客戶問房即時有答案", "icon": "🏠", "color": "#8B2845",
     "kw": ["ettoday", "yahoo", "自由", "中央社", "cna", "lifetime", "591", "桃園", "中壢", "楊梅", "news"]},
    {"key": "gov", "name": "政府公開", "desc": "央行 / 公平會 / 內政部即時公告", "icon": "🏛️", "color": "#1E3A8A",
     "kw": ["央行", "cbc", "公平會", "ftc", "mops", "公開資訊", "內政部", "moi"]},
    {"key": "prod", "name": "生產力科技", "desc": "iThome / INSIDE / 數位時代 — AI 與科技新知", "icon": "💼", "color": "#0E7490",
     "kw": ["inside", "ithome", "數位時代", "科技新報", "經理人", "cheers", "方格子", "bnext", "pixnet", "大紀元"]},
    {"key": "life", "name": "生活環保", "desc": "Mobile01 / Ptt / 環保署 / Cheers — 在地生活", "icon": "🌿", "color": "#15803D",
     "kw": ["mobile01", "ptt", "lifeismoney", "taichung", "環保", "poll-tex", "痞客邦"]},
]

# 分組
buckets = {c["key"]: [] for c in CATS}
for src in SOURCES:
    s = (src["label"] or "").lower()
    matched = False
    for c in CATS:
        if any(kw in s for kw in c["kw"]):
            buckets[c["key"]].append(src)
            matched = True
            break
    if not matched:
        buckets["news"].append(src)

for k in buckets: buckets[k] = sorted(buckets[k], key=lambda x: -len(x["items"]))

print("\n=== 分類結果 ===")
total = 0
for c in CATS:
    cnt = sum(len(s["items"]) for s in buckets[c["key"]])
    total += cnt
    print(f"  {c['icon']} {c['name']:10s}  {cnt:3d} titles in {len(buckets[c['key']])} sources")
print(f"Total: {total} titles")

# Featured (即時精選) - 每分類前 2 條
featured = []
for c in CATS:
    for src in buckets[c["key"]][:2]:
        for it in src["items"][:1]:
            featured.append({**it, "section": c["name"], "color": c["color"], "src": src["label"], "icon": c["icon"]})
            if len(featured) >= 4: break

# Featured HTML
featured_html = ""
for f in featured:
    title = (f.get("title") or "").replace("<", "&lt;").replace(">", "&gt;")[:140]
    featured_html += f'<a class="featured-card" href="{f.get("link","#")}" target="_blank" style="--c:{f["color"]};">'
    featured_html += f'<span class="card-tag" style="background:{f["color"]};">{f["icon"]} {f["section"]}</span>'
    featured_html += f'<h3 class="card-title">{title}</h3>'
    featured_html += f'<span class="card-src">{f.get("src","")}</span>'
    featured_html += '</a>'

# 4 大圖卡
cat_html = ""
for c in CATS:
    cnt = sum(len(s["items"]) for s in buckets[c["key"]])
    src_count = len(buckets[c["key"]])
    cat_html += f'<a class="cat-card" href="#{c["key"]}" style="--c:{c["color"]};">'
    cat_html += f'<div class="cat-icon">{c["icon"]}</div>'
    cat_html += f'<div class="cat-name">{c["name"]}</div>'
    cat_html += f'<div class="cat-desc">{c["desc"]}</div>'
    cat_html += f'<div class="cat-count">{cnt}</div>'
    cat_html += f'<div class="cat-count-label">{src_count} 個來源</div>'
    cat_html += '</a>'

# Sections
sections_html = ""
section_idx = 1
roman = ["I", "II", "III", "IV", "V", "VI"]
for c in CATS:
    if not buckets[c["key"]]: continue
    all_items = []
    for src in buckets[c["key"]]:
        for it in src["items"][:30]:
            it["_src"] = src["label"]
            all_items.append(it)
    cards = ""
    for it in all_items[:60]:
        title = (it.get("title") or "").replace("<", "&lt;").replace(">", "&gt;")[:120]
        link = it.get("link", "#")
        src_label = (it.get("_src") or "")[:25]
        cards += f'<a class="card" href="{link}" target="_blank" style="--c:{c["color"]};">'
        cards += f'<span class="card-tag" style="background:{c["color"]};">{c["icon"]}</span>'
        cards += f'<h3 class="card-title">{title}</h3>'
        cards += f'<span class="card-src">{src_label}</span>'
        cards += '</a>'
    sections_html += f'<section class="section" id="{c["key"]}"><div class="wrap"><div class="section-head"><span class="section-num">{roman[section_idx-1]}</span><div><h2 class="section-title">{c["name"]}</h2><p class="section-sub">{len(all_items)} 條即時內容</p></div></div><div class="grid">{cards}</div></div></section>'
    section_idx += 1

# Ticker
ticker_items = []
for src in SOURCES:
    if src.get("items"):
        for it in src["items"][:2]:
            ticker_items.append(it["title"][:60])
ticker_inner = ""
for _ in range(3):
    for t in ticker_items[:20]:
        ticker_inner += f"<span>{t}</span>"
ticker_html = f'<div class="ticker"><div class="wrap ticker-inner">{ticker_inner}</div></div>'

CSS = open(CSS_SRC, encoding="utf-8").read()
now = datetime.now()
html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>老蔡的臺灣 RAG 知識庫 — crawl4ai 即時累積</title>
<link rel="stylesheet" href="site_v3.css">
</head>
<body>
<header class="hero">
  <div class="wrap">
    <div class="hero-eyebrow">
      <span class="live-pill"><span class="live-dot"></span> LIVE</span>
      <span>臺灣 №{now.strftime("%Y%m%d.%H%M")}</span>
    </div>
    <h1>讓臺灣 web <em>變得</em> 可讀。<br>把臺灣房仲知識變成你的 RAG。</h1>
    <p class="hero-lede">crawl4ai 0.9.2 自動從 <b>{len(SOURCES)} 個臺灣來源站</b>抓資料。簡轉繁、智慧去噪、每 6 小時累積。</p>
    <div class="hero-meta">
      <span><b>{total:,}</b> 條即時資料</span>
      <span><b>{len(SOURCES)}</b> 臺灣來源</span>
      <span><b>4</b> 大主題分類</span>
      <span>更新於 {now.strftime("%Y-%m-%d %H:%M")}</span>
    </div>
  </div>
</header>
{ticker_html}
<section class="section" style="background: white; padding: 64px 0;">
  <div class="wrap">
    <div class="section-head">
      <span class="section-num">★</span>
      <div>
        <h2 class="section-title">主題分類</h2>
        <p class="section-sub">點擊跳到該分類</p>
      </div>
    </div>
    <div class="cat-grid">{cat_html}</div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="section-num">▶</span>
      <div>
        <h2 class="section-title">即時精選</h2>
        <p class="section-sub">最新臺灣業務相關的真實內容</p>
      </div>
    </div>
    <div class="featured-grid">{featured_html}</div>
  </div>
</section>
{sections_html}
<footer class="foot">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <div class="foot-tagline">讓臺灣 web<br><em>變得可讀</em>。</div>
      </div>
      <div class="foot-col">
        <h4>主題分類</h4>
        <a href="#news">房仲新聞</a>
        <a href="#gov">政府公開</a>
        <a href="#prod">生產力科技</a>
        <a href="#life">生活環保</a>
      </div>
      <div class="foot-col">
        <h4>連結</h4>
        <a href="https://github.com/sky770825/crawl4ai-rag-demo" target="_blank">GitHub</a>
        <a href="https://crawl4ai.com" target="_blank">crawl4ai</a>
      </div>
    </div>
    <div class="foot-meta">Crawl4AI 0.9.2 · patchright stealth · Python 3.11 · 純臺灣源</div>
    <div class="foot-credit" style="margin-top: 12px;">Built by <a href="https://github.com/sky770825" target="_blank">老蔡</a> · 達爾 Q / MiniMax-M3</div>
    <div class="foot-meta" style="margin-top: 12px;">Auto-rebuild every 6h · cron job 65efba3a52de</div>
  </div>
</footer>
</body>
</html>"""
os.makedirs(SITE, exist_ok=True)
open(HTML, "w", encoding="utf-8").write(html)
shutil.copy(CSS_SRC, CSS_DST)
print(f"\n=== Done ===")
print(f"Total: {total} titles in {len(SOURCES)} sources")
print(f"HTML: {HTML} ({len(html)} chars)")