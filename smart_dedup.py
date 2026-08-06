"""smart_dedup.py - 智慧去噪 + 重複過濾 v2"""
import json, os, re
from collections import Counter
from datetime import datetime

BENCH_DIR = os.path.expanduser("~/Desktop/crawl4ai/benchmark")
raws = sorted([f for f in os.listdir(BENCH_DIR) if f.startswith('benchmark_raw_')])
if not raws:
    print("NO BENCH"); raise SystemExit(1)
latest = os.path.join(BENCH_DIR, raws[-1])
print(f"Reading: {latest}")
with open(latest, 'r', encoding='utf-8') as f:
    all_data = json.load(f)

GLOBAL_NOISE = Counter()
for site, runs in all_data.items():
    site_titles = set()
    for run in runs:
        for t in run['titles']:
            site_titles.add(t['h'])
    for h in site_titles:
        GLOBAL_NOISE[h] += 1

CROSS_SITE_NOISE = {h for h, c in GLOBAL_NOISE.items() if c >= 3}
print(f"Cross-site noise: {len(CROSS_SITE_NOISE)}")

TIME_RE = re.compile(r'^\d+\s*(hour|minute|day|second)s?\s*(ago)?$', re.IGNORECASE)

def is_short_cn(t):
    return len(t.strip()) < 4 and re.search(r'[\u4e00-\u9fff]', t)

NAV_WORDS = {'Skip to', 'Sponsor', 'Cookie', 'Google News', 'App Store', 'Google Play',
             'GitHub', '登入', '註冊', '首頁', '更多', '熱門', '客服', 'English',
             '星標', '收藏', '分享', '追蹤', '通知', '下載'}

stats = {}
for site, runs in all_data.items():
    total = 0; kept = 0
    rt = rn = rs = rc = 0
    keep_titles = []
    for run in runs:
        run_keep = []
        for t in run['titles']:
            total += 1
            title = t['title']
            if TIME_RE.match(title.strip()):
                rt += 1; continue
            if any(n in title for n in NAV_WORDS) and len(title) < 30:
                rn += 1; continue
            if is_short_cn(title):
                rs += 1; continue
            if t['h'] in CROSS_SITE_NOISE and len(title) < 30:
                rc += 1; continue
            run_keep.append(t); kept += 1
        keep_titles.append({'run': run['run'], 'ts': run['ts'], 'titles': run_keep})
    stats[site] = {'total': total, 'kept': kept, 'rt': rt, 'rn': rn, 'rs': rs, 'rc': rc,
                   'pct': kept*100/max(total,1)}
    out = os.path.join(BENCH_DIR, f"{site}_clean_runs.json")
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(keep_titles, f, ensure_ascii=False, indent=2)

print("\n=== Smart Dedup Results ===")
for site, s in stats.items():
    print(f"## {site}")
    print(f"  raw {s['total']:>5} -> keep {s['kept']:>5} ({s['pct']:.1f}%)")
    print(f"  removed: time={s['rt']} nav={s['rn']} short_cn={s['rs']} cross={s['rc']}")
    print()

report = [f"# Smart Dedup v2 Report\n\nDate: {datetime.now().isoformat()}\nSource: {raws[-1]}\n\n"]
report.append("## Cross-Site Noise (>=3 sites)\n")
for h, c in sorted(GLOBAL_NOISE.items(), key=lambda x: -x[1])[:30]:
    if c >= 3:
        orig = '?'
        for site, runs in all_data.items():
            for run in runs:
                for t in run['titles']:
                    if t['h'] == h:
                        orig = t['title'][:60]; break
                if orig != '?': break
            if orig != '?': break
        report.append(f"- [{c} sites] {orig}\n")
report.append("\n## Stats per site\n")
for site, s in stats.items():
    report.append(f"### {site}\n- raw={s['total']} keep={s['kept']} ({s['pct']:.1f}%)\n- removed: time={s['rt']} nav={s['rn']} short_cn={s['rs']} cross={s['rc']}\n\n")
out_r = os.path.join(BENCH_DIR, f"smart_dedup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
with open(out_r, 'w', encoding='utf-8') as f:
    f.writelines(report)
print(f"Report: {out_r}")
