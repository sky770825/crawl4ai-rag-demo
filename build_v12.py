"""build_v12.py - v9 base + 修 JS 漢堡 toggle + 跨 src dedup + 引號污染清理 + viewport-fit/OG/manifest
v13: 5 桶分類(加 intl 國際新聞)
"""
import json, os, shutil, glob, re
from datetime import datetime
OUT = os.path.expanduser("~/Desktop/crawl4ai/rag_data")
SITE = os.path.expanduser("~/Desktop/crawl4ai/site")
HTML = os.path.join(SITE, "index.html")
CSS_SRC = os.path.expanduser("~/Desktop/crawl4ai/site_v5.css")  # v11 最終源 (427 行 mobile-first dark v5)
CSS_DST = os.path.join(SITE, "site_v3.css")
fp = sorted(glob.glob(os.path.join(OUT, "tw_titles_*.json")))[-1]
print(f"Using: {fp}")
raw = json.load(open(fp, encoding="utf-8"))
SOURCES = raw["sources"] if isinstance(raw, dict) and "sources" in raw else raw
if "items" in SOURCES[0]:
    SOURCES = [{"label": f["label"], "count": len(f["items"]), "items": f["items"]} for f in SOURCES]
print(f"Loaded {len(SOURCES)} sources")

# === v13: 跨 src dedup（標題級 dedup，第一個 src 贏）===
seen_titles = set()
for s in SOURCES:
    new_items = []
    for it in s["items"]:
        t = it.get("title", "").strip()
        if not t or t in seen_titles:
            continue
        seen_titles.add(t)
        new_items.append(it)
    s["items"] = new_items
    s["count"] = len(new_items)
print(f"After dedup: {sum(s['count'] for s in SOURCES)} titles")

# === v13: 5 桶分類（CATS）===
CATS = [
    {"key": "news", "name": "房仲新聞", "desc": "即時臺灣房仲 / 房市新聞,客戶問房即時有答案", "icon": "🏠", "color": "#8B2845",
     "svg": '<svg viewBox="0 0 24 24"><path d="M12 3L2 12h3v8h6v-6h2v6h6v-8h3L12 3z"/></svg>',
     "kw": ["ettoday", "yahoo", "新聞", "房市", "住展", "591", "自由時報"]},  # v13 自由時報 → news (新聞源非政府)
    {"key": "gov", "name": "政府公開", "desc": "央行 / 公平會 / 內政部 — 政策法規即時查詢", "icon": "🏛️", "color": "#1E3A8A",
     "svg": '<svg viewBox="0 0 24 24"><path d="M12 2L2 7v2h20V7l-10-5zm0 4.7l6 3v.3H6v-.3l6-3zM4 11v8H2v2h20v-2h-2v-8h-2v8h-4v-8h-2v8H8v-8H4z"/></svg>',
     "kw": ["央行", "公平會", "內政部", "環保署", "公開資訊觀測站"]},
    {"key": "ai", "name": "生產力科技", "desc": "iThome / INSIDE / 數位時代 — AI 與職場新知", "icon": "💼", "color": "#0E7490",
     "svg": '<svg viewBox="0 0 24 24"><path d="M20 6h-4V4c0-1.1-.9-2-2-2h-4c-1.1 0-2 .9-2 2v2H4c-1.1 0-2 .9-2 2v11c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm-6 0h-4V4h4v2z"/></svg>',
     "kw": ["ithome", "inside", "數位時代", "科技新報", "經理人", "cheers", "大紀元"]},  # v13 大紀元 → ai (科技/職場新聞)
    {"key": "life", "name": "生活環保", "desc": "Mobile01 / Ptt / Cheers — 在地生活", "icon": "🌿", "color": "#15803D",
     "svg": '<svg viewBox="0 0 24 24"><path d="M17 8C8 10 5.9 16.17 3.82 21.34l1.89.66.95-2.3c.48.17.98.3 1.34.3C19 20 22 3 22 3c-1 2-8 2.25-13 3.25S2 11.5 2 13.5s1.75 3.75 1.75 3.75C7 8 17 8 17 8z"/></svg>',
     "kw": ["mobile01", "ptt", "lifeismoney", "taichung", "環保", "poll-tex", "痞客邦", "方格子"]},
    {"key": "intl", "name": "國際新聞", "desc": "中央社 / Yahoo 國際 / 大紀元 — 海內外即時", "icon": "🌐", "color": "#B45309",  # v13 amber-700
     "svg": '<svg viewBox="0 0 24 24"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm-1 17.9c-1.7-.2-3.2-1-4.4-2.2l1.5-1.5c.9.9 2 1.4 3.3 1.6v2.1zM4.2 13c-.1-.3-.1-.7-.1-1s0-.7.1-1h2.1c-.1.3-.1.7-.1 1s0 .7.1 1H4.2zm9 6.9v-2.1c1.2-.2 2.4-.7 3.3-1.6l1.5 1.5c-1.2 1.2-2.8 2-4.8 2.2zm5.3-7.4h2.1c.1.3.1.7.1 1s0 .7-.1 1h-2.1c.1-.3.1-.7.1-1s0-.7-.1-1z"/></svg>',
     "kw": ["中央社", "yahoo 台灣 國際", "大紀元"]},  # v13 新增:中央社 國際新聞 → intl
]
buckets = {c["key"]: [] for c in CATS}
others = []
for s in SOURCES:
    label = s["label"].lower()
    matched = False
    for c in CATS:
        if any(kw in label for kw in c["kw"]):
            buckets[c["key"]].append(s)
            matched = True
            break
    if not matched:
        others.append(s)
# 防止 buckets 順序重複:已 matched 的 src 不會再進 others
total = sum(sum(s["count"] for s in buckets[k]) for k in buckets)
print(f"Total: {total} titles")
for c in CATS:
    cnt = sum(s["count"] for s in buckets[c["key"]])
    nsrc = len(buckets[c["key"]])
    print(f"  {c['name']}: {cnt} titles / {nsrc} src")

# Featured
featured = []
roman = ["I", "II", "III", "IV", "V"]
section_idx = 0
FEAT_DENY = {"搜尋看板", "搜尋", "INSIDE 硬塞的網路趨勢觀察", "Sony / SE", "Sony Ericsson",
              "Windows Phone", "電動車／交通科技", "半導體與電子產業", "行銷與MARTECH",
              "加入LINE好友", "推薦課程", "vocus 官方沙龍", "搬家到 vocus"}
for c in CATS:
    for src in buckets[c["key"]][:2]:
        for it in src["items"][:1]:
            t = it.get("title", "")
            if any(d in t for d in FEAT_DENY): continue
            if t.startswith("搜尋") or t.startswith("找尋") or t.startswith("Sony"): continue
            featured.append({**it, "section": c["name"], "sec_color": c["color"]})
            if len(featured) >= 8: break
        if len(featured) >= 8: break
    if len(featured) >= 8: break

featured_html = ""
for f in featured[:8]:
    title = (f.get("title") or "").replace("<", "&lt;").replace(">", "&gt;")[:120]
    src = f.get("src_label") or f.get("label") or ""
    featured_html += f'<a class="featured-card fade-up" href="{f.get("link", "#")}" style="border-top:3px solid {f["sec_color"]};">'
    featured_html += f'<span class="card-tag" style="color:{f["sec_color"]};">{f["section"]}</span>'
    featured_html += f'<h3 class="card-title">{title}</h3>'
    featured_html += f'<span class="card-src">{src}</span></a>'

# Cat cards (5 桶) — v13
cat_html = ""
for c in CATS:
    cnt = sum(s["count"] for s in buckets[c["key"]])
    nsrc = len(buckets[c["key"]])
    cat_html += f'<a class="cat-card" href="#{c["key"]}" style="--card-color:{c["color"]};">'
    cat_html += f'<div class="cat-icon" style="background:{c["color"]};">{c["icon"]}</div>'
    cat_html += f'<div class="cat-name">{c["name"]}</div>'
    cat_html += f'<div class="cat-num">{cnt}</div>'
    cat_html += f'<div class="cat-src">{nsrc} 個來源</div>'
    cat_html += f'<div class="cat-desc">{c["desc"]}</div>'
    cat_html += '</a>'

# Sections (5 桶) — v13
sections_html = ""
for c in CATS:
    src_list = buckets[c["key"]]
    if not src_list:
        continue
    sec_html = f'<section id="{c["key"]}" class="sec"><div class="wrap">'
    sec_html += f'<div class="section-head"><span class="section-num" style="background:{c["color"]};">{c["icon"]}</span>'
    sec_html += f'<h2 class="section-title">{c["name"]}</h2>'
    sec_html += f'<span class="section-meta">{sum(s["count"] for s in src_list)} 條 / {len(src_list)} 個來源</span>'
    sec_html += '</div>'
    for src in src_list:
        sec_html += f'<div class="src-section"><h3 class="src-name">{src["label"]}</h3>'
        sec_html += f'<span class="src-count">{src["count"]}</span>'
        sec_html += '<div class="src-grid">'
        for it in src["items"][:12]:
            title = (it.get("title") or "").replace("<", "&lt;").replace(">", "&gt;")[:80]
            link = (it.get("link") or "#").split('"')[0].split("%22")[0].strip()
            sec_html += f'<a class="src-card fade-up" href="{link}" target="_blank" rel="noopener">'
            sec_html += f'<span class="src-card-title">{title}</span></a>'
        sec_html += '</div></div>'
    sec_html += '</div></section>'
    sections_html += sec_html

# Inspiration Wall (v6 留下)
INSPIR = os.path.join(OUT, "design_inspiration/inspirations_v2.json")
inspiration_html = ""
if os.path.exists(INSPIR):
    try:
        insps = json.load(open(INSPIR, encoding="utf-8"))
        items_html = ""
        for i, ins in enumerate(insps[:12]):
            title = ins.get("title", "").replace("<", "&lt;").replace(">", "&gt;")[:60]
            alt = ins.get("alt", "").replace("<", "&lt;").replace(">", "&gt;")[:80]
            items_html += f'<a class="insp-card" href="{ins.get("url", "#")}" target="_blank" rel="noopener">'
            items_html += f'<img loading="lazy" src="{ins.get("img", "")}" alt="{alt}">'
            items_html += f'<span class="insp-title">{title}</span></a>'
        inspiration_html = f'<section class="insp"><div class="wrap"><div class="section-head"><span class="section-num">✦</span><h2 class="section-title">Inspiration Wall</h2></div><div class="insp-grid">{items_html}</div></div></section>'
    except Exception as e:
        print(f"Inspiration skip: {e}")

# === v13: 5 桶 hero stats ===
hero_stats = ""
for c in CATS:
    hero_stats += f'<span><strong data-stat="{c["key"]}">{sum(s["count"] for s in buckets[c["key"]])}</strong> {c["name"]}</span>'

# === v13: 5 桶 sticky nav ===
nav_links = ""
for c in CATS:
    nav_links += f'<a href="#{c["key"]}">{c["name"]}</a>'

sticky_nav = f'<a class="skip-link" href="#main">跳至主要內容</a><nav class="sticky-nav"><div class="wrap"><span class="brand">臺灣 RAG</span><button class="nav-toggle" aria-expanded="false" aria-controls="primary-nav" aria-label="切換導航">☰</button><div class="nav-links" id="primary-nav">{nav_links}</div></div></nav>'

# === HTML ===
html = f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#8B2845">
<meta name="description" content="讓臺灣 web 變得可讀,把房仲知識變成你的 RAG。{total} 條真實標題 / {len(SOURCES)} 個臺灣源 / 5 大分類。">
<meta property="og:title" content="臺灣 RAG — 房仲業務即時知識庫">
<meta property="og:description" content="客戶問房, 即時有答案。{total} 條真實新聞標題, 5 大分類, 純臺灣源自動更新。">
<meta property="og:type" content="website">
<meta property="og:url" content="https://crawl4ai-taiwan-v3-20260807.surge.sh/">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🇹🇼</text></svg>">
<link rel="manifest" href="manifest.json">
<link rel="stylesheet" href="site_v3.css">
</head>
<body>
{sticky_nav}
<main id="main">
<section class="hero">
<div class="wrap">
<span class="hero-eyebrow"><span class="live-pill"><span class="live-dot"></span>LIVE</span> 每日自動更新 · 純臺灣源</span>
<div class="scroll-cue">↓ scroll 探索 5 大分類</div>
<h1 class="hero-title">讓臺灣 web <em>變得</em> 可讀。<br>把房仲知識變成你的 RAG。</h1>
<p class="hero-lede">{total} 條真實標題 / {len(SOURCES)} 個臺灣源 / 5 大分類 — 客戶問房,即時有答案。</p>
<div class="hero-meta">
{hero_stats}
</div>
</div>
</section>
<section class="cats"><div class="wrap"><div class="cat-grid">{cat_html}</div></div></section>
<section class="featured"><div class="wrap"><div class="section-head"><span class="section-num">★</span><h2 class="section-title">即時精選</h2></div><div class="featured-grid">{featured_html}</div></div></section>
{sections_html}
{inspiration_html}
</main>
<footer class="foot"><div class="wrap foot-grid">
<div><div class="foot-brand">臺灣 RAG</div><p class="foot-desc">讓臺灣 web 變得可讀。<br>純臺灣源、零陸網、即時更新。</p></div>
<div><div class="foot-h">資料源</div><ul class="foot-list">
<li>ETtoday / Yahoo 新聞</li>
<li>央行 / 公平會 / 內政部</li>
<li>iThome / INSIDE / 科技新報</li>
<li>Mobile01 / Ptt / Cheers</li>
<li>中央社 / Yahoo 國際</li>
</ul></div>
<div><div class="foot-h">v13 · 5 大分類</div><ul class="foot-list">
<li>房仲新聞 · 政府公開 · 生產力科技</li>
<li>生活環保 · 國際新聞</li>
</ul></div>
</div></footer>
<script src="app.js" defer></script>

</body></html>'''

# === P4: 修 CSS — 確保 site_v3.css 漢堡 menu 完整,沒有 dead-code duplicate ===
CSS_V12 = os.path.join(SITE, "site_v12.css")
src_css = ""
if os.path.exists(CSS_SRC):
    src_css = open(CSS_SRC, encoding="utf-8").read()
hamburger_blocks = list(re.finditer(r'(/\* =+ Hamburger menu \(mobile\) =+ \*/[\s\S]*?)(?=(/\* =+ |$))', src_css))
if len(hamburger_blocks) > 1:
    keep = hamburger_blocks[-1]
    parts = [src_css[:hamburger_blocks[0].start()]]
    for i in range(1, len(hamburger_blocks)):
        prev = hamburger_blocks[i-1]
        parts.append(src_css[prev.end():hamburger_blocks[i].start()])
    parts.append(src_css[keep.start():])
    src_css = "\n".join(parts)
    print(f"Cleaned {len(hamburger_blocks)-1} duplicate Hamburger blocks")
open(CSS_V12, "w", encoding="utf-8").write(src_css)
shutil.copy(CSS_V12, CSS_DST)
print(f"CSS: {CSS_V12} ({os.path.getsize(CSS_V12)} bytes)")

open(HTML, "w", encoding="utf-8").write(html)
print(f"HTML: {HTML} ({len(html.encode('utf-8'))} bytes)")

# === P5: PWA manifest ===
manifest = {
    "name": "臺灣 RAG",
    "short_name": "臺灣 RAG",
    "description": "讓臺灣 web 變得可讀,把房仲知識變成你的 RAG",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#0F172A",
    "theme_color": "#8B2845",
    "icons": [{"src": "data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🇹🇼</text></svg>", "sizes": "192x192", "type": "image/svg+xml"}]
}
open(os.path.join(SITE, "manifest.json"), "w", encoding="utf-8").write(json.dumps(manifest, ensure_ascii=False, indent=2))
print("manifest.json written")
