#!/usr/bin/env python3
"""reports/index.html: one card per project with its weekly activity (entries per ISO week), counts and last publish date.
Reads only counts and dates from the local report directories and the published manifests; titles of findings never appear here
(the reports themselves are password vaults). Runs at the end of build_report_vault.py; `python3 tools/build_reports_index.py` rebuilds by hand."""
import datetime, glob, html, json, os, re

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.expanduser("~/Documents/reports")
# slug -> (title, tagline, local dir, status, colour)
PROJECTS = [
    ("policy-customization", "TAILOR", "Few-shot customization of generalist robot policies: elicit a behaviour the base never shows, then consolidate it into the weights.",
     "policy_customization", "active", "#c64b2f"),
    ("boost", "BOOST", "Online RL on top of a frozen generative policy: a steering head, a demo-anchored residual and a critic that picks one of K candidates.",
     "boost_results", "active", "#0173B2"),
    ("oopsie", "Oopsie dataset", "Viewer and audit of the failure-recovery dataset: cleaned episodes and per-lab galleries.",
     "oopsie_dataset", "static", "#029E73"),
]
esc = html.escape

def weeks_of(local):
    """{monday: (key findings, extra entries)} from the project's week pages."""
    out = {}
    for f in glob.glob(os.path.join(REPORTS, local, "20??-??-??.html")):
        s = open(f).read(); mon = datetime.date.fromisoformat(os.path.basename(f)[:10])
        key = s.count("<article class=\"entry\"")
        also = re.search(r"Also this week \((\d+)\)", s)
        out[mon] = (key, int(also.group(1)) if also else 0)
    return out

def built(slug):
    f = os.path.join(SITE, "reports", slug, "manifest.json")
    return json.load(open(f)).get("built", "") if os.path.exists(f) else ""

def fmt(d): return d.strftime("%b %d").replace(" 0", " ")

def card(slug, title, tag, local, status, color):
    wk = weeks_of(local); b = built(slug)
    today = datetime.date.today(); this_mon = today - datetime.timedelta(days=today.weekday())
    span = [this_mon - datetime.timedelta(weeks=i) for i in range(SPAN_WEEKS - 1, -1, -1)]   # shared window, oldest first
    peak = max([k + a for k, a in wk.values()] + [1])
    bars = []
    for m in span:
        k, a = wk.get(m, (0, 0)); tot = k + a
        h = lambda v: max(2 if v else 0, round(54 * v / peak))
        tip = f"{fmt(m)}: {k} key finding{'s' if k != 1 else ''}" + (f", {a} more" if a else "") if tot else f"{fmt(m)}: no entries"
        bars.append(f"<div class=\"wk\" title=\"{esc(tip)}\"><div class=\"extra\" style=\"height:{h(a)}px\"></div><div class=\"key\" style=\"height:{h(k)}px;background:{color}\"></div></div>")
    nk = sum(k for k, _ in wk.values()); na = sum(a for _, a in wk.values())
    meta = (f"{len(wk)} week{'s' if len(wk) != 1 else ''} logged · <b>{nk}</b> key finding{'s' if nk != 1 else ''}" + (f" · {na} more entries" if na else "")) if wk else "static report"
    upd = f"updated {b[:10]}" if b else "not published"
    strip = f"<div class=\"strip\">{''.join(bars)}</div><div class=\"axis\"><span>{fmt(span[0])}</span><span>this week</span></div>" if wk else "<div class=\"strip empty\">no weekly log</div>"
    return f"""
<a class="card" href="{slug}/" style="--c:{color}">
  <div class="top"><span class="chip {status}">{status}</span><span class="upd">{esc(upd)}</span></div>
  <h2>{esc(title)}</h2>
  <p>{esc(tag)}</p>
  {strip}
  <div class="meta">{meta}</div>
  <div class="open">Open report <span class="lock" aria-hidden="true">&#128274;</span></div>
</a>"""

CSS = """
:root { --paper:#f3f0e8; --sheet:#fbfaf6; --ink:#20201d; --soft:#62625c; --rule:#d8d3c7; --accent:#c64b2f; }
* { box-sizing:border-box; } html { background:var(--paper); }
body { margin:0; color:var(--ink); font-family:"EB Garamond", Georgia, serif; line-height:1.5;
  background: linear-gradient(90deg, transparent 0 31px, rgba(198,75,47,.10) 31px 32px, transparent 32px), var(--paper); }
.page { max-width:1100px; margin:0 auto; padding:72px 40px 96px; }
.eyebrow { font:600 12px/1 -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; letter-spacing:.1em; text-transform:uppercase; color:var(--accent); }
h1 { font-size:clamp(44px, 7vw, 72px); font-weight:400; line-height:1; margin:10px 0 8px; letter-spacing:-.01em; }
.lead { color:var(--soft); font-size:20px; margin:0 0 10px; }
.totals { font-family:-apple-system, "Segoe UI", Helvetica, Arial, sans-serif; font-size:13px; color:var(--soft); padding-bottom:28px; border-bottom:1px solid var(--ink); margin-bottom:36px; }
.totals b { color:var(--ink); }
.grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(320px, 1fr)); gap:22px; }
.card { display:block; position:relative; background:var(--sheet); border:1px solid var(--rule); border-top:3px solid var(--c); padding:22px 24px 20px; color:inherit; text-decoration:none;
  transition: transform .18s ease, box-shadow .18s ease; }
.card:hover { transform:translateY(-3px); box-shadow:0 14px 34px rgba(32,32,29,.10); }
.top { display:flex; justify-content:space-between; align-items:center; font-family:-apple-system, "Segoe UI", Helvetica, Arial, sans-serif; font-size:11.5px; color:var(--soft); }
.chip { text-transform:uppercase; letter-spacing:.08em; font-weight:600; padding:2px 8px; border-radius:3px; border:1px solid var(--rule); }
.chip.active { color:#0b7a4b; border-color:#b9dfc9; background:#eaf6ef; } .chip.static { color:var(--soft); }
.chip.closed { color:#b3261e; border-color:#efc4bf; background:#fbeceb; }
.card h2 { font-size:30px; font-weight:500; margin:12px 0 4px; }
.card p { margin:0 0 18px; color:#3e3e39; font-size:16.5px; min-height:3em; }
.strip { display:flex; align-items:flex-end; gap:5px; height:56px; padding-top:2px; border-bottom:1px solid var(--rule); }
.strip.empty { align-items:center; justify-content:center; color:var(--soft); font-size:13px; font-family:-apple-system, "Segoe UI", Helvetica, Arial, sans-serif; border-bottom:1px solid var(--rule); }
.wk { flex:1; display:flex; flex-direction:column; justify-content:flex-end; height:100%; }
.wk .key, .wk .extra { width:100%; border-radius:2px 2px 0 0; }
.wk .extra { background:#d8d3c7; } .wk .key { margin-top:1px; }
.axis { display:flex; justify-content:space-between; font-family:-apple-system, "Segoe UI", Helvetica, Arial, sans-serif; font-size:10.5px; color:var(--soft); margin-top:4px; }
.meta { font-family:-apple-system, "Segoe UI", Helvetica, Arial, sans-serif; font-size:13px; color:var(--soft); margin-top:14px; } .meta b { color:var(--ink); }
.open { margin-top:14px; font-family:-apple-system, "Segoe UI", Helvetica, Arial, sans-serif; font-size:13px; font-weight:600; color:var(--c); }
.lock { font-size:12px; margin-left:4px; }
footer { margin-top:56px; font-family:-apple-system, "Segoe UI", Helvetica, Arial, sans-serif; font-size:12.5px; color:var(--soft); display:flex; justify-content:space-between; }
footer a { color:inherit; }
@media (max-width:640px) { .page { padding:48px 20px 64px; } }
"""

SPAN_WEEKS = 6

def main():
    global SPAN_WEEKS
    today = datetime.date.today(); this_mon = today - datetime.timedelta(days=today.weekday())
    first = min([m for p in PROJECTS for m in weeks_of(p[3])] + [this_mon])
    SPAN_WEEKS = max(6, (this_mon - first).days // 7 + 2)   # from the first logged week (plus one of lead-in) to this week
    cards = [card(*p) for p in PROJECTS]
    allw = [weeks_of(p[3]) for p in PROJECTS]
    nk = sum(k for w in allw for k, _ in w.values()); nw = len({m for w in allw for m in w})
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
<title>Reports — Anthony Liang</title><link rel="icon" type="image/png" href="../img/me.png">
<link rel="preconnect" href="https://fonts.gstatic.com"><link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<style>{CSS}</style></head>
<body><main class="page">
  <div class="eyebrow">Research logs</div>
  <h1>Reports</h1>
  <p class="lead">One weekly research log per project: an overview page, then the key findings of each week with their plots and clips.</p>
  <div class="totals"><b>{len(PROJECTS)}</b> projects · <b>{nk}</b> key findings over <b>{nw}</b> weeks · bars = entries per week (colour = key findings, grey = the rest) · rebuilt {datetime.datetime.now():%Y-%m-%d %H:%M}</div>
  <div class="grid">{''.join(cards)}</div>
  <footer><span>Reports are shared by direct link; each has its own password.</span><a href="../">aliang8.github.io</a></footer>
</main></body></html>
"""
    open(os.path.join(SITE, "reports", "index.html"), "w").write(doc)
    print(f"reports/index.html: {len(PROJECTS)} projects, {nk} key findings, {nw} weeks")

if __name__ == "__main__":
    main()
