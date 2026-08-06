"""build_fresh_site.py - 用最新 fresh_titles 重新生成
"""
import json, os
from datetime import datetime

SRC = os.path.expanduser("~/Desktop/crawl4ai/rag_data/fresh_titles_20260806.json")
SITE = os.path.expanduser("~/Desktop/crawl4ai/site")
HTML = os.path.join(SITE, "index.html")
CSS_SRC = os.path.expanduser("~/Desktop/crawl4ai/site_v2.css")
CSS_DST = os.path.join(SITE, "site_v2.css")

d = json.load(open(SRC, encoding="utf-8"))

# Sections 配色
SECTIONS = {
    "ETtoday_房產焦點": ("房市新聞", "📰", "#8B2845", "ETtoday 房產焦點"),
    "ETtoday_新聞總覽": ("新聞總覽", "📰", "#8B2845", "ETtoday 即時"),
    "Yahoo_房地產": ("Yahoo 房地產", "🏠", "#A21CAF", "Yahoo 房地產"),
    "央行_最新業務": ("央行業務", "🏛️", "#1E3A8A", "中央銀行"),
    "公開資訊觀測站": ("公開資訊", "📊", "#0E7490", "上市公司公告"),
    "公平會最新": ("公平會", "⚖️", "#166534", "公平交易委員會"),
    "內政部地政": ("地政司", "🗺️", "#0E7490", "內政部地政司"),
    "GitHub_Trending_Python": ("GitHub Trending", "🐙", "#0F172A", "Python 熱門"),
    "Hacker_News": ("Hacker News", "💬", "#FB923C", "科技頂尖"),
    "B站_AI短劇": ("B站 AI 短劇", "🎬", "#B45309", "B站 短劇"),
    "B站_Seedance": ("Seedance 教學", "🎥", "#B45309", "B站 Seedance"),
    "B站_可靈": ("可靈 教學", "🎥", "#B45309", "B站 可靈"),
}

# 計算總計
total = d["total_titles"]
per_src = d["per_source"]
now = datetime.now()

cards_html = []
for src in d["sources"]:
    label = src["label"]
    if label not in SECTIONS: continue
    sec_label, emoji, color, subtitle = SECTIONS[label]
    items = src["items"]
    if not items: continue
    inner = []
    for it in items[:30]:
        t = it["title"].replace("<", "&lt;").replace(">", "&gt;")[:120]
        link = it.get("link", "#")
        if link and link != "#" and not link.startswith("http"):
            link = "#"
        inner.append(f'''<a class="card" href="{link}" target="_blank" rel="noopener" style="--c: {color}">
<div class="card-bar"></div>
<div class="card-body">
  <h3>{t}</h3>
  <div class="card-foot"><span>{sec_label}</span><span>→</span></div>
</div>
</a>''')
    cards_html.append(f'''
<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="num">№ {len(cards_html)+1:02d}</span>
      <h2><span class="emoji">{emoji}</span> {sec_label}</h2>
      <span class="count">{len(items)} 條</span>
    </div>
    <p class="section-sub">{subtitle}</p>
    <div class="grid">
      {chr(10).join(inner)}
    </div>
  </div>
</section>''')

# 取前 6 條最重要的當 hero
hero_picks = []
for src in d["sources"]:
    if not src["items"]: continue
    for it in src["items"][:2]:
        hero_picks.append((src["label"], it))
        if len(hero_picks) >= 6: break
    if len(hero_picks) >= 6: break

hero_html = []
for src_label, it in hero_picks:
    if src_label in SECTIONS:
        sec_label, emoji, color, _ = SECTIONS[src_label]
    else:
        sec_label, emoji, color = src_label, "•", "#666"
    t = it["title"].replace("<", "&lt;").replace(">", "&gt;")[:80]
    link = it.get("link", "#")
    if link and link != "#" and not link.startswith("http"):
        link = "#"
    hero_html.append(f'''<a class="hero-card" href="{link}" target="_blank" rel="noopener">
<div class="hero-card-meta"><span class="dot" style="background:{color}"></span>{sec_label}</div>
<div class="hero-card-title">{t}</div>
</a>''')

html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Crawl4AI 知識庫 — 抓最新、有用、過濾雜訊</title>
  <meta name="description" content="老蔡的 crawl4ai 0.9.2 業務 RAG 知識庫 — 房市新聞、政府公開、AI 雷達、短劇市場、防霾紗窗">
  <link rel="stylesheet" href="site_v2.css">
</head>
<body>
  <header class="hero">
    <div class="wrap">
      <div class="hero-eyebrow">
        <span class="live-pill"><span class="live-dot"></span> LIVE</span>
        <span>Issue №{now.strftime("%Y%m%d.%H%M")}</span>
      </div>
      <h1>讓 web <em>變得</em> 可讀。<br>把整個網路變成你的 RAG。</h1>
      <p class="hero-lede">crawl4ai 0.9.2 自動從 <b>房市新聞、政府公開、AI 雷達、短劇市場</b> 抓最新資料。<b>{total} 條</b>真實標題,<b>已智慧去噪</b>。</p>
      <div class="hero-meta">
        <span>📦 <b>{total}</b> 條</span>
        <span>🌐 <b>{len(d["sources"])}</b> 來源站</span>
        <span>⏰ {now.strftime("%H:%M")} 更新</span>
        <span>🔄 cron 6h</span>
      </div>
    </div>
  </header>

  <div class="hero-picks">
    <div class="wrap">
      <h3 class="hero-picks-title">即時精選</h3>
      <div class="hero-picks-grid">
        {chr(10).join(hero_html)}
      </div>
    </div>
  </div>

  {chr(10).join(cards_html)}

  <footer class="foot">
    <div class="wrap">
      <div class="foot-meta">Crawl4AI 0.9.2 · patchright stealth · chromium-headless-shell v1228 · Python 3.11</div>
      <div class="foot-credit">Built by <a href="https://github.com/sky770825" target="_blank">老蔡</a> · 達爾 Q / MiniMax-M3</div>
      <div class="foot-meta" style="margin-top: 12px;">Auto-rebuild every 6h · cron job 65efba3a52de</div>
    </div>
  </footer>
</body>
</html>
"""

os.makedirs(SITE, exist_ok=True)
open(HTML, "w", encoding="utf-8").write(html)
import shutil
shutil.copy(CSS_SRC, CSS_DST)
print(f"=== 重新生成 ===")
print(f"Total: {total} titles in {len(d['sources'])} sources")
print(f"HTML: {HTML} ({len(html)} chars)")
