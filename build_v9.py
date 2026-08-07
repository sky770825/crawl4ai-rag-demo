"""build_v5.py - 加 sticky nav + fade-up animation + design category inspired"""
import json, os, shutil, glob
from datetime import datetime
OUT = os.path.expanduser("~/Desktop/crawl4ai/rag_data")
SITE = os.path.expanduser("~/Desktop/crawl4ai/site")
HTML = os.path.join(SITE, "index.html")
CSS_SRC = os.path.expanduser("~/Desktop/crawl4ai/site_v4.css")
CSS_DST = os.path.join(SITE, "site_v3.css")
SOURCES = []
fp = sorted(glob.glob(os.path.join(OUT, "tw_titles_*.json")))[-1]
print(f"Using: {fp}")
d = json.load(open(fp, encoding="utf-8"))
for s in d["sources"]:
    SOURCES.append(s)
print(f"Loaded {len(SOURCES)} sources, {sum(len(s['items']) for s in SOURCES)} titles")

CATS = [
    {"key": "news", "name": "房仲新聞", "desc": "即時臺灣房仲 / 房市新聞,客戶問房即時有答案", "icon": "🏠", "color": "#8B2845",
     "svg": '<svg viewBox="0 0 24 24"><path d="M12 3L2 12h3v8h6v-6h2v6h6v-8h3L12 3z"/></svg>',
     "kw": ["ettoday", "yahoo", "新聞", "房市", "住展", "591"]},
    {"key": "gov", "name": "政府公開", "desc": "央行 / 公平會 / 內政部 — 政策法規即時查詢", "icon": "🏛️", "color": "#1E3A8A",
     "svg": '<svg viewBox="0 0 24 24"><path d="M12 2L2 7v2h20V7l-10-5zm0 4.7l6 3v.3H6v-.3l6-3zM4 11v8H2v2h20v-2h-2v-8h-2v8h-4v-8h-2v8H8v-8H4z"/></svg>',
     "kw": ["央行", "公平會", "內政部", "環保署"]},
    {"key": "ai", "name": "生產力科技", "desc": "iThome / INSIDE / 數位時代 — AI 與職場新知", "icon": "💼", "color": "#0E7490",
     "svg": '<svg viewBox="0 0 24 24"><path d="M20 6h-4V4c0-1.1-.9-2-2-2h-4c-1.1 0-2 .9-2 2v2H4c-1.1 0-2 .9-2 2v11c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm-6 0h-4V4h4v2z"/></svg>',
     "kw": ["ithome", "inside", "數位時代", "科技新報", "經理人", "cheers", "大紀元"]},
    {"key": "life", "name": "生活環保", "desc": "Mobile01 / Ptt / Cheers — 在地生活", "icon": "🌿", "color": "#15803D",
     "svg": '<svg viewBox="0 0 24 24"><path d="M17 8C8 10 5.9 16.17 3.82 21.34l1.89.66.95-2.3c.48.17.98.3 1.34.3C19 20 22 3 22 3c-1 2-8 2.25-13 3.25S2 11.5 2 13.5s1.75 3.75 1.75 3.75C7 8 17 8 17 8z"/></svg>',
     "kw": ["mobile01", "ptt", "lifeismoney", "taichung", "環保", "poll-tex", "痞客邦", "方格子"]},
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
if others:
    for o in others:
        lbl = o["label"].lower()
        if any(k in lbl for k in ["ithome", "inside", "數位時代", "科技", "經理人", "cheers", "大紀元"]):
            buckets["ai"].append(o)
        elif any(k in lbl for k in ["央行", "公平會", "內政", "環保"]):
            buckets["gov"].append(o)
        else:
            buckets["life"].append(o)
total = sum(sum(s["count"] for s in buckets[k]) for k in buckets)
print(f"Total: {total} titles")

# Featured (過濾明顯 nav / 廣告 / search action)
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

# Cat cards
cat_html = ""
for c in CATS:
    cnt = sum(s["count"] for s in buckets[c["key"]])
    nsrc = len(buckets[c["key"]])
    cat_html += f'<div class="cat-name">{c["name"]}</div>'
    cat_html += f'<div class="cat-num">{cnt}</div>'
    cat_html += f'<div class="cat-src">{nsrc} 個來源</div>'
    cat_html += f'<div class="cat-desc">{c["desc"]}</div>'
    cat_html += '</a>'

sections_html = ""
for c in CATS:
    section_idx += 1
    sec_items_html = ""
    for src in buckets[c["key"]]:
        sec_items_html += f'<div class="src-block"><h4 class="src-name">{src["label"]} <span class="src-count">{src["count"]}</span></h4><div class="items-grid">'
        for it in src["items"][:8]:
            t = (it.get("title") or "").replace("<", "&lt;").replace(">", "&gt;")[:100]
            sec_items_html += f'<a class="item-card fade-up" href="{it.get("link", "#")}"><span class="item-title">{t}</span><span class="item-arrow">→</span></a>'
        sec_items_html += '</div></div>'
    sections_html += f'<section class="section" id="{c["key"]}"><div class="wrap"><div class="section-head"><span class="section-num">{roman[section_idx-1]}</span><div><h2 class="section-title">{c["name"]}</h2><p class="section-desc">{c["desc"]}</p></div></div>{sec_items_html}</div></section>'
# Inspiration Wall (AI 真實作品 alt 文字)
INSPIRATION_SRC = r"C:\Users\user\Desktop\crawl4ai\rag_data\ai_assets\inspirations_v2.json"
inspiration_html = ""
if os.path.exists(INSPIRATION_SRC):
    try:
        ins = json.load(open(INSPIRATION_SRC, encoding="utf-8"))
        inspiration_html = '<section class="section insp"><div class="wrap"><div class="section-head"><span class="section-num">V</span><div><h2 class="section-title">靈感牆</h2><p class="section-desc">從 Krea / OpenArt / Playground 抓到的真實 AI 作品描述 — 給你下一個 prompt 的種子</p></div></div>'
        inspiration_html += '<div class="insp-grid">'
        for it in ins[:24]:
            txt = it.get("text", "").replace("<", "&lt;")[:180]
            src = it.get("src", "")
            bg_map = {"krea.ai": "bg-1", "openart.ai": "bg-2", "playground.com": "bg-3", "lexica.art": "bg-4", "other": "bg-3"}
            site = it.get("site", "other")
            txt = it["text"][:200]
            inspiration_html += f'<div class="insp-card {bg_map.get(site, "bg-3")}"><span class="insp-site">{site}</span><p class="insp-title">{txt}</p></div>'
        inspiration_html += '</div></div></section>'
    except Exception as e:
        print(f"inspiration load fail: {e}")# Sticky nav
sticky_nav = '<nav class="sticky-nav"><div class="wrap"><span class="brand">臺灣 RAG</span><a href="#news">房仲新聞</a><a href="#gov">政府公開</a><a href="#ai">生產力科技</a><a href="#life">生活環保</a></div></nav>'

html = f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>臺灣 RAG — 房仲知識即時查詢</title>
<meta name="description" content="從臺灣 23 個公開資料源,自動累積房仲、政府、生產力、生活即時新聞,給老蔡客戶問房時即時查詢。">
<link rel="stylesheet" href="site_v3.css">
</head>
<body>
{sticky_nav}
<section class="hero">
<div class="wrap">
<span class="hero-eyebrow"><span class="live-pill"><span class="live-dot"></span>LIVE</span> 每日自動更新 · 純臺灣源</span>
<div class="scroll-cue">↓ scroll 探索 5 大分類</div>
<h1 class="hero-title">讓臺灣 web <em>變得</em> 可讀。<br>把房仲知識變成你的 RAG。</h1>
<p class="hero-lede">{sum(sum(s["count"] for s in buckets[k]) for k in buckets)} 條真實標題 / {len(SOURCES)} 個臺灣源 / 4 大分類 — 客戶問房,即時有答案。</p>
<div class="hero-meta">
<span><strong>{sum(s["count"] for s in buckets["news"])}</strong> 房仲新聞</span>
<span><strong>{sum(s["count"] for s in buckets["gov"])}</strong> 政府公開</span>
<span><strong>{sum(s["count"] for s in buckets["ai"])}</strong> 生產力科技</span>
<span><strong>{sum(s["count"] for s in buckets["life"])}</strong> 生活環保</span>
</div>
</div>
</section>
<section class="cats"><div class="wrap"><div class="cat-grid">{cat_html}</div></div></section>
<section class="featured"><div class="wrap"><div class="section-head"><span class="section-num">★</span><h2 class="section-title">即時精選</h2></div><div class="featured-grid">{featured_html}</div></div></section>
{sections_html}
{inspiration_html}
<footer class="foot"><div class="wrap foot-grid">
<div><div class="foot-brand">臺灣 RAG</div><p class="foot-desc">讓臺灣 web 變得可讀。<br>純臺灣源、零陸網、即時更新。</p></div>
<div><div class="foot-h">資料源</div><ul class="foot-list">
<li>ETtoday / Yahoo 新聞</li>
<li>央行 / 公平會 / 內政部</li>
<li>iThome / INSIDE / 數位時代</li>
<li>Mobile01 / Ptt / Cheers</li>
</ul></div>
<div><div class="foot-h">技術</div><ul class="foot-list">
<li>crawl4ai 0.9.2 headless</li>
<li>Python 3.11 venv</li>
<li>Surge static hosting</li>
<li>GitHub Pages backup</li>
</ul></div>
</div></footer>
<script>
document.documentElement.classList.add('js');
const obs = new IntersectionObserver(es => es.forEach(e => e.isIntersecting && e.target.classList.add('show')), {{threshold: 0.1}});
document.querySelectorAll('.fade-up').forEach(el => obs.observe(el));
</script>
</body></html>'''

shutil.copy(CSS_SRC, CSS_DST)
open(HTML, "w", encoding="utf-8").write(html)
print(f"HTML: {HTML} ({len(html.encode('utf-8'))} bytes)")
