"""戰場 6: 整理 RAG 資料成單頁可瀏覽 HTML + 部署 Surge
"""
import json
import os
from datetime import datetime
import re

RAG_DIR = os.path.expanduser("~/Desktop/crawl4ai/rag_data")
SITE_DIR = os.path.expanduser("~/Desktop/crawl4ai/site")
os.makedirs(SITE_DIR, exist_ok=True)

# 載入
def load_json(name):
    files = sorted([f for f in os.listdir(RAG_DIR) if f.startswith(name)])
    if not files:
        return None
    with open(os.path.join(RAG_DIR, files[-1]), encoding="utf-8") as f:
        return json.load(f)

def load_md(name):
    files = sorted([f for f in os.listdir(RAG_DIR) if f.startswith(name) and f.endswith(".md")])
    if not files:
        return None
    with open(os.path.join(RAG_DIR, files[-1]), encoding="utf-8") as f:
        return f.read()

# 房市新聞 (clean)
house_news = load_json("house_news_")
house_clean = None
if house_news:
    files = sorted([f for f in os.listdir(RAG_DIR) if f.endswith("_clean.json")])
    if files:
        with open(os.path.join(RAG_DIR, files[-1]), encoding="utf-8") as f:
            house_clean = json.load(f)

# 政府
gov = load_json("gov_data_")

# AI 雷達
ai = load_json("ai_radar_")

# 短劇
drama = load_json("short_drama_market_")

# 防霾
poll = load_json("poll_tex_kb_")
poll_files = []
if poll:
    for p in poll:
        if p.get("file") and os.path.exists(p["file"]):
            poll_files.append(p)

# 生成 HTML
def render_section(title, emoji, items_html):
    return f"""
    <section>
      <h2>{emoji} {title}</h2>
      {items_html}
    </section>"""

def render_news_list(sources):
    if not sources:
        return "<p class=\"empty\">無資料</p>"
    html = []
    for s in sources:
        items = s.get("items", [])
        html.append(f'<div class="source-block">')
        html.append(f'<h3><a href="{s["url"]}" target="_blank">{s["source"]}</a> <span class="count">({len(items)} items)</span></h3>')
        html.append('<ul class="news-list">')
        for it in items[:30]:
            title = it.get("title", "")
            link = it.get("link", "#")
            if isinstance(title, dict):
                title = title.get("title", "")
            html.append(f'<li><a href="{link}" target="_blank">{title[:120]}</a></li>')
        html.append('</ul></div>')
    return "\n".join(html)

def render_md_block(name, content):
    if not content:
        return ""
    # markdown 簡化: 保留 # ## ### 標題
    html = ['<div class="md-block">']
    html.append(f'<h3>{name}</h3>')
    html.append(f'<pre class="md-preview">{content[:3000]}...</pre>')
    html.append('</div>')
    return "\n".join(html)

def render_ai_radar(sources):
    if not sources:
        return "<p class=\"empty\">無資料</p>"
    html = []
    for s in sources:
        items = s.get("items", [])
        html.append(f'<div class="source-block">')
        html.append(f'<h3><a href="{s["url"]}" target="_blank">{s["label"]}</a> <span class="count">({len(items)} items)</span></h3>')
        html.append('<ul class="news-list">')
        for it in items[:25]:
            html.append(f'<li><a href="{it["link"]}" target="_blank">{it["title"]}</a></li>')
        html.append('</ul></div>')
    return "\n".join(html)

def render_drama(sources):
    if not sources:
        return "<p class=\"empty\">無資料</p>"
    html = []
    for s in sources:
        if s.get("status") != "OK":
            continue
        items = s.get("items", [])
        html.append(f'<div class="source-block">')
        html.append(f'<h3>{s["label"]} <span class="count">({len(items)} videos)</span></h3>')
        html.append('<ul class="drama-list">')
        for it in items[:20]:
            html.append(f'<li><a href="https://www.bilibili.com/video/{it["bv"]}" target="_blank"><span class="bv-tag">{it["bv"]}</span> {it["title"]}</a></li>')
        html.append('</ul></div>')
    return "\n".join(html)

# 計算總數
total_news = sum(s.get("count", 0) for s in (house_clean or []))
total_ai = sum(len(s.get("items", [])) for s in (ai or []))
total_drama = sum(s.get("count", 0) for s in (drama or []))
gov_chars = sum(p.get("chars", 0) for p in (gov or []) if p.get("status") == "OK")
poll_chars = sum(p.get("chars", 0) for p in (poll or []) if p.get("status") == "OK")

HTML = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>crawl4ai 知識庫 — 老蔡版</title>
<style>
:root {{
  --bg: #0f0e14;
  --gold: #d4af6a;
  --red: #b5445d;
  --text: #e8e4d8;
  --muted: #8a8478;
  --card: #1a1820;
  --border: #2a2730;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang TC", "Microsoft JhengHei", sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}}
header {{
  text-align: center;
  padding: 40px 20px 20px;
  border-bottom: 2px solid var(--gold);
  margin-bottom: 30px;
}}
h1 {{ color: var(--gold); font-size: 2.4em; margin-bottom: 8px; }}
.subtitle {{ color: var(--muted); font-size: 0.95em; }}
.stats {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin: 20px 0;
}}
.stat {{
  background: var(--card);
  border: 1px solid var(--border);
  border-left: 3px solid var(--gold);
  padding: 12px 16px;
  border-radius: 6px;
}}
.stat-num {{ font-size: 1.8em; color: var(--gold); font-weight: bold; }}
.stat-label {{ font-size: 0.8em; color: var(--muted); margin-top: 4px; }}
section {{ margin: 40px 0; }}
h2 {{ color: var(--red); font-size: 1.6em; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }}
h3 {{ color: var(--text); font-size: 1.15em; margin: 16px 0 8px; }}
h3 a {{ color: var(--gold); text-decoration: none; }}
.count {{ color: var(--muted); font-size: 0.75em; font-weight: normal; }}
.source-block {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 16px 20px;
  margin-bottom: 16px;
}}
ul.news-list, ul.drama-list {{ list-style: none; padding-left: 0; }}
ul.news-list li, ul.drama-list li {{
  padding: 6px 0;
  border-bottom: 1px dashed var(--border);
  font-size: 0.92em;
}}
ul.news-list li:last-child, ul.drama-list li:last-child {{ border-bottom: none; }}
ul.news-list a, ul.drama-list a {{
  color: var(--text);
  text-decoration: none;
}}
ul.news-list a:hover, ul.drama-list a:hover {{ color: var(--gold); }}
.bv-tag {{
  background: var(--red);
  color: white;
  font-size: 0.7em;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
  margin-right: 6px;
}}
.md-block {{ margin: 16px 0; }}
.md-preview {{
  background: #0a090e;
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 12px;
  font-size: 0.85em;
  overflow: auto;
  max-height: 300px;
  white-space: pre-wrap;
  color: var(--muted);
}}
.empty {{ color: var(--muted); font-style: italic; padding: 12px; }}
footer {{
  text-align: center;
  padding: 30px 20px;
  color: var(--muted);
  font-size: 0.85em;
  border-top: 1px solid var(--border);
  margin-top: 40px;
}}
footer a {{ color: var(--gold); text-decoration: none; }}
</style>
</head>
<body>
<header>
  <h1>📚 crawl4ai 知識庫</h1>
  <p class="subtitle">老蔡即時 RAG 資料 · {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
  <div class="stats">
    <div class="stat"><div class="stat-num">{total_news}</div><div class="stat-label">房市新聞</div></div>
    <div class="stat"><div class="stat-num">{gov_chars//1000}k</div><div class="stat-label">政府資料 chars</div></div>
    <div class="stat"><div class="stat-num">{total_ai}</div><div class="stat-label">AI 雷達 items</div></div>
    <div class="stat"><div class="stat-num">{total_drama}</div><div class="stat-label">短劇 videos</div></div>
    <div class="stat"><div class="stat-num">{poll_chars//1000}k</div><div class="stat-label">防霾知識 chars</div></div>
  </div>
</header>

{render_section("🏠 房市新聞 (ETtoday + Yahoo)", "🏠", render_news_list(house_clean))}

{render_section("🏛️ 政府公開資料 (央行 / 內政部 / 公平會)", "🏛️",
    "<div class='source-block'>" + "".join(
        f'<p><strong>{p.get("label", "")}</strong> — {p.get("chars", 0):,} chars · <a href="{p.get("url", "#")}" target="_blank">原文</a></p>'
        for p in (gov or []) if p.get("status") == "OK"
    ) + "</div>"
)}

{render_section("🤖 AI 技術雷達 (GitHub Trending / HN / HF / Papers)", "🤖", render_ai_radar(ai))}

{render_section("🎬 AI 短劇 / 視頻市場觀察 (B站)", "🎬", render_drama(drama))}

{render_section("🌬️ 防霾紗窗 + 空氣品質 (副業務)", "🌬️",
    "<div class='source-block'>" + "".join(
        f'<p><strong>{p.get("label", "")}</strong> — {p.get("chars", 0):,} chars · <a href="{p.get("url", "#")}" target="_blank">原文</a></p>'
        for p in (poll or []) if p.get("status") == "OK"
    ) + "</div>"
)}

<footer>
  <p>由 <a href="https://github.com/unclecode/crawl4ai" target="_blank">crawl4ai 0.9.2</a> 自動生成</p>
  <p>Pipeline: real_estate_news_rag → gov_data_crawl → ai_radar → short_drama_market → poll_tex_kb</p>
  <p style="margin-top:12px;">🤖 老蔡 Hermes Agent · {datetime.now().isoformat()}</p>
</footer>
</body>
</html>
"""

# 寫出
out = os.path.join(SITE_DIR, "index.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(HTML)
print(f"✓ HTML 生成: {out} ({len(HTML):,} chars)")
print(f"  Total: {total_news} news + {gov_chars//1000}k gov + {total_ai} AI + {total_drama} drama + {poll_chars//1000}k poll_tex")
