"""social_v2_extract.py - 從 social_v2 抽所有真實標題"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from md_to_titles import is_noise, extract
from glob import glob
from datetime import datetime

OUT = os.path.expanduser("~/Desktop/crawl4ai/rag_data")
SOURCES = sorted(glob(os.path.join(OUT, "social_v2_*.json")))
if not SOURCES:
    print("no social_v2_*.json found"); raise SystemExit
SRC = SOURCES[-1]
print(f"Reading: {SRC}")
d = json.load(open(SRC, encoding="utf-8"))
sources = []
for src in d:
    md = src.get("md", "")
    items = extract(md, src["url"])
    sources.append({"label": src["label"], "url": src["url"], "count": len(items), "items": items})
    print(f"  {src['label']:30s} -> {len(items)} titles")
total = sum(s["count"] for s in sources)
print(f"\n=== Total: {total} titles in {len(sources)} sources ===")
fp = os.path.join(OUT, f"social_v2_titles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
open(fp, "w", encoding="utf-8").write(json.dumps({"sources": sources}, ensure_ascii=False, indent=2))
print(f"Wrote: {fp}")
