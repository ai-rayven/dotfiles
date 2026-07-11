#!/usr/bin/env python3
"""Error-class label tracking for the feedback skill.

Stores one label per error class in <repo-root>/.feedback/labels.json and records a
timestamped occurrence every time that class of error is addressed again. Three
subcommands:

  view_labels       list labels and counts (human table, or --json)
  add_labels        create-or-increment a label with a new occurrence
  visualize_labels  render a self-contained offline HTML time-series (user-triggered)

Python 3 standard library only. The storage path is fixed by convention; there is no
override flag.
"""

import argparse
import datetime
import html
import json
import os
import re
import subprocess
import sys
import tempfile

SCHEMA_VERSION = 1


# --------------------------------------------------------------------------- paths

def repo_root():
    """Return the git repo root, falling back to the current working directory."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        root = out.stdout.strip()
        if root:
            return root
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return os.getcwd()


def store_path():
    return os.path.join(repo_root(), ".feedback", "labels.json")


def html_path():
    return os.path.join(repo_root(), ".feedback", "labels.html")


# ----------------------------------------------------------------------------- git

def git_context():
    """Return (branch, commit) for the current repo, or (None, None) when unavailable."""
    def _run(args):
        try:
            out = subprocess.run(args, capture_output=True, text=True, check=True)
            value = out.stdout.strip()
            return value or None
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    commit = _run(["git", "rev-parse", "HEAD"])
    return branch, commit


# --------------------------------------------------------------------------- helpers

def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(name):
    """Kebab-case a short label name into a filesystem/JSON-friendly slug."""
    if not name:
        return ""
    slug = name.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


def load_store(path):
    """Load the label store, tolerating a missing/empty/corrupt file."""
    if not os.path.exists(path):
        return {"version": SCHEMA_VERSION, "labels": {}}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError):
        return {"version": SCHEMA_VERSION, "labels": {}}
    if not isinstance(data, dict):
        return {"version": SCHEMA_VERSION, "labels": {}}
    data.setdefault("version", SCHEMA_VERSION)
    labels = data.get("labels")
    if not isinstance(labels, dict):
        data["labels"] = {}
    return data


def save_store(path, data):
    """Write the store atomically (temp file in the same dir, then rename)."""
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".labels-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def unique_slug(labels, base):
    """Return base, or base with a short numeric suffix if it collides."""
    if base and base not in labels:
        return base
    if not base:
        base = "label"
    n = 2
    while f"{base}-{n}" in labels:
        n += 1
    return f"{base}-{n}"


def last_seen(label):
    occ = label.get("occurrences") or []
    stamps = [o.get("timestamp") for o in occ if o.get("timestamp")]
    return max(stamps) if stamps else label.get("created_at")


# ------------------------------------------------------------------------ add logic

def add_occurrence(store, *, slug=None, name=None, description=None,
                   file=None, line=None, timestamp=None, branch=None, commit=None):
    """Create-or-increment a single label with one occurrence. Returns the slug used."""
    labels = store["labels"]

    if slug:
        if slug not in labels:
            raise ValueError(
                f"--slug '{slug}' does not exist; create it with --name/--description first"
            )
        target = slug
    else:
        if not name:
            raise ValueError("a new label requires --name (and ideally --description)")
        target = unique_slug(labels, slugify(name))
        labels[target] = {
            "name": name,
            "description": description or "",
            "created_at": timestamp or now_iso(),
            "occurrences": [],
        }

    occurrence = {"timestamp": timestamp or now_iso()}
    if file:
        occurrence["file"] = file
    if line is not None:
        occurrence["line"] = line
    occurrence["branch"] = branch
    occurrence["commit"] = commit
    labels[target].setdefault("occurrences", []).append(occurrence)
    return target


# ------------------------------------------------------------------------ subcommands

def cmd_view_labels(args):
    store = load_store(store_path())
    labels = store.get("labels", {})

    if args.json:
        out = []
        for slug, label in sorted(labels.items()):
            occ = label.get("occurrences") or []
            out.append({
                "slug": slug,
                "name": label.get("name", slug),
                "description": label.get("description", ""),
                "count": len(occ),
                "created_at": label.get("created_at"),
                "last_seen": last_seen(label),
            })
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    if not labels:
        print("no labels yet")
        return 0

    rows = []
    for slug, label in sorted(labels.items()):
        occ = label.get("occurrences") or []
        rows.append((
            label.get("name", slug),
            slug,
            str(len(occ)),
            (label.get("created_at") or "")[:10],
            (last_seen(label) or "")[:10],
            label.get("description", ""),
        ))

    headers = ("NAME", "SLUG", "COUNT", "CREATED", "LAST SEEN", "DESCRIPTION")
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    # Keep the free-text description column from being padded to a huge width.
    widths[5] = len(headers[5])

    def fmt(row):
        return "  ".join(
            cell.ljust(widths[i]) if i < len(row) - 1 else cell
            for i, cell in enumerate(row)
        )

    print(fmt(headers))
    for row in rows:
        print(fmt(row))
    return 0


def cmd_add_labels(args):
    path = store_path()
    store = load_store(path)
    branch, commit = git_context()

    items = []
    if args.items:
        with open(args.items, "r", encoding="utf-8") as fh:
            loaded = json.load(fh)
        if not isinstance(loaded, list):
            print("error: --items file must contain a JSON array", file=sys.stderr)
            return 1
        items = loaded
    else:
        if not args.slug and not args.name:
            print("error: provide --slug, or --name (with --description), or --items",
                  file=sys.stderr)
            return 1
        items = [{
            "slug": args.slug,
            "name": args.name,
            "description": args.description,
            "file": args.file,
            "line": args.line,
            "timestamp": args.timestamp,
        }]

    used = []
    for item in items:
        try:
            slug = add_occurrence(
                store,
                slug=item.get("slug"),
                name=item.get("name"),
                description=item.get("description"),
                file=item.get("file"),
                line=item.get("line"),
                timestamp=item.get("timestamp"),
                branch=branch,
                commit=commit,
            )
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        used.append(slug)

    save_store(path, store)
    for slug in used:
        count = len(store["labels"][slug].get("occurrences") or [])
        print(f"recorded '{slug}' (count now {count})")
    return 0


def cmd_visualize_labels(args):
    store = load_store(store_path())
    out = html_path()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(render_html(store))
    print(out)
    if args.open:
        try:
            subprocess.run(["open", out], check=False)
        except FileNotFoundError:
            pass
    return 0


# -------------------------------------------------------------------------- html view

def render_html(store):
    labels = store.get("labels", {})
    payload = []
    for slug, label in sorted(labels.items()):
        occ = sorted(
            (o for o in (label.get("occurrences") or []) if o.get("timestamp")),
            key=lambda o: o["timestamp"],
        )
        payload.append({
            "slug": slug,
            "name": label.get("name", slug),
            "description": label.get("description", ""),
            "occurrences": [
                {
                    "timestamp": o.get("timestamp"),
                    "file": o.get("file"),
                    "line": o.get("line"),
                    "branch": o.get("branch"),
                    "commit": o.get("commit"),
                }
                for o in occ
            ],
        })
    data_json = json.dumps(payload, ensure_ascii=False)
    generated = html.escape(now_iso())
    return _HTML_TEMPLATE.replace("__DATA__", data_json).replace("__GENERATED__", generated)


_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Feedback error-class labels</title>
<style>
  :root { color-scheme: light dark; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
         margin: 24px; line-height: 1.4; }
  h1 { font-size: 20px; margin: 0 0 4px; }
  .meta { color: #888; font-size: 12px; margin-bottom: 16px; }
  .wrap { display: flex; gap: 24px; flex-wrap: wrap; align-items: flex-start; }
  .legend { min-width: 240px; max-width: 360px; }
  .legend label { display: flex; align-items: baseline; gap: 8px; padding: 4px 0;
                  cursor: pointer; font-size: 13px; }
  .legend .swatch { width: 12px; height: 12px; border-radius: 2px; flex: 0 0 auto;
                    display: inline-block; margin-top: 2px; }
  .legend .desc { color: #888; font-size: 11px; }
  .controls { margin-bottom: 12px; font-size: 13px; }
  .controls button { margin-right: 8px; }
  svg { background: transparent; max-width: 100%; height: auto; border: 1px solid #8884; }
  .tip { position: fixed; pointer-events: none; background: #222; color: #eee;
         padding: 6px 8px; border-radius: 4px; font-size: 12px; max-width: 320px;
         opacity: 0; transition: opacity .1s; z-index: 10; }
  .axis { stroke: #8886; stroke-width: 1; }
  .grid { stroke: #8882; stroke-width: 1; }
  .tick { fill: #888; font-size: 10px; }
  .empty { color: #888; }
</style>
</head>
<body>
<h1>Feedback error-class labels</h1>
<div class="meta">Cumulative occurrences over time. Generated __GENERATED__.</div>
<div class="controls">
  <label><input type="checkbox" id="trend"> show trend lines</label>
  &nbsp;&nbsp;
  granularity:
  <select id="gran">
    <option value="none" selected>raw</option>
    <option value="day">day</option>
    <option value="week">week</option>
  </select>
  &nbsp;&nbsp;
  <button id="all">show all</button>
  <button id="none">hide all</button>
</div>
<div class="wrap">
  <div class="legend" id="legend"></div>
  <div>
    <svg id="chart" width="820" height="440" viewBox="0 0 820 440"></svg>
  </div>
</div>
<div class="tip" id="tip"></div>
<script>
const DATA = __DATA__;
const COLORS = ["#4e79a7","#f28e2b","#e15759","#76b7b2","#59a14f","#edc948",
                "#b07aa1","#ff9da7","#9c755f","#bab0ac","#1b9e77","#d95f02"];
const svg = document.getElementById("chart");
const tip = document.getElementById("tip");
const W = 820, H = 440, M = {top: 20, right: 20, bottom: 40, left: 44};
const iw = W - M.left - M.right, ih = H - M.top - M.bottom;
const visible = new Set(DATA.map(d => d.slug));

function color(i){ return COLORS[i % COLORS.length]; }
function parse(ts){ return Date.parse(ts); }

function bucketStart(ms, gran){
  const d = new Date(ms);
  d.setUTCHours(0,0,0,0);
  if (gran === "week"){ d.setUTCDate(d.getUTCDate() - d.getUTCDay()); }
  return d.getTime();
}

// Build cumulative series per label given the current granularity.
function series(gran){
  return DATA.map((label, i) => {
    let pts = label.occurrences
      .map(o => ({ t: parse(o.timestamp), o }))
      .filter(p => !isNaN(p.t))
      .sort((a,b) => a.t - b.t);
    if (gran !== "none"){
      const byBucket = new Map();
      for (const p of pts){
        const b = bucketStart(p.t, gran);
        byBucket.set(b, (byBucket.get(b) || []).concat(p.o));
      }
      pts = [...byBucket.keys()].sort((a,b)=>a-b).map(b => ({
        t: b, o: { timestamp: new Date(b).toISOString(), _group: byBucket.get(b) }
      }));
    }
    let cum = 0;
    const points = pts.map(p => ({ t: p.t, y: (cum += (p.o._group ? p.o._group.length : 1)), o: p.o }));
    return { label, i, color: color(i), points };
  });
}

function extent(all){
  let minT = Infinity, maxT = -Infinity, maxY = 1;
  for (const s of all){
    if (!visible.has(s.label.slug)) continue;
    for (const p of s.points){
      minT = Math.min(minT, p.t); maxT = Math.max(maxT, p.t);
      maxY = Math.max(maxY, p.y);
    }
  }
  if (!isFinite(minT)){ const now = Date.now(); minT = now - 86400000; maxT = now; }
  if (minT === maxT){ minT -= 86400000; maxT += 86400000; }
  return { minT, maxT, maxY };
}

function draw(){
  const gran = document.getElementById("gran").value;
  const showTrend = document.getElementById("trend").checked;
  const all = series(gran);
  const { minT, maxT, maxY } = extent(all);
  const x = t => M.left + (t - minT) / (maxT - minT) * iw;
  const y = v => M.top + ih - (v / maxY) * ih;
  const ns = "http://www.w3.org/2000/svg";
  while (svg.firstChild) svg.removeChild(svg.firstChild);

  function line(x1,y1,x2,y2,cls){
    const el = document.createElementNS(ns,"line");
    el.setAttribute("x1",x1); el.setAttribute("y1",y1);
    el.setAttribute("x2",x2); el.setAttribute("y2",y2);
    el.setAttribute("class",cls); svg.appendChild(el); return el;
  }
  function text(tx,ty,str,anchor){
    const el = document.createElementNS(ns,"text");
    el.setAttribute("x",tx); el.setAttribute("y",ty);
    el.setAttribute("class","tick");
    el.setAttribute("text-anchor",anchor||"middle");
    el.textContent = str; svg.appendChild(el); return el;
  }

  // axes + y grid
  line(M.left, M.top, M.left, M.top+ih, "axis");
  line(M.left, M.top+ih, M.left+iw, M.top+ih, "axis");
  const yticks = Math.min(maxY, 5);
  for (let k=0;k<=yticks;k++){
    const v = Math.round(maxY * k / yticks);
    const yy = y(v);
    line(M.left, yy, M.left+iw, yy, "grid");
    text(M.left-6, yy+3, String(v), "end");
  }
  // x ticks (start/mid/end)
  for (const frac of [0,0.5,1]){
    const t = minT + (maxT-minT)*frac;
    const xx = x(t);
    line(xx, M.top+ih, xx, M.top+ih+4, "axis");
    text(xx, M.top+ih+16, new Date(t).toISOString().slice(0,10));
  }

  for (const s of all){
    if (!visible.has(s.label.slug) || s.points.length === 0) continue;
    // step line
    let d = "";
    s.points.forEach((p, idx) => {
      const px = x(p.t), py = y(p.y);
      if (idx === 0){ d += `M ${px} ${y(0)} L ${px} ${py}`; }
      else {
        const prev = s.points[idx-1];
        d += ` L ${x(p.t)} ${y(prev.y)} L ${px} ${py}`;
      }
    });
    const path = document.createElementNS(ns,"path");
    path.setAttribute("d", d);
    path.setAttribute("fill","none");
    path.setAttribute("stroke", s.color);
    path.setAttribute("stroke-width","2");
    svg.appendChild(path);

    // points
    for (const p of s.points){
      const c = document.createElementNS(ns,"circle");
      c.setAttribute("cx", x(p.t)); c.setAttribute("cy", y(p.y));
      c.setAttribute("r","3.5"); c.setAttribute("fill", s.color);
      c.addEventListener("mousemove", ev => showTip(ev, s, p));
      c.addEventListener("mouseleave", hideTip);
      svg.appendChild(c);
    }

    // simple linear trend (least squares) across the label's points
    if (showTrend && s.points.length >= 2){
      const xs = s.points.map(p => p.t), ys = s.points.map(p => p.y);
      const n = xs.length;
      const mx = xs.reduce((a,b)=>a+b,0)/n, my = ys.reduce((a,b)=>a+b,0)/n;
      let num=0, den=0;
      for (let k=0;k<n;k++){ num += (xs[k]-mx)*(ys[k]-my); den += (xs[k]-mx)**2; }
      const slope = den === 0 ? 0 : num/den;
      const b = my - slope*mx;
      const t0 = xs[0], t1 = xs[n-1];
      const tl = line(x(t0), y(slope*t0+b), x(t1), y(slope*t1+b), "");
      tl.setAttribute("stroke", s.color);
      tl.setAttribute("stroke-width","1");
      tl.setAttribute("stroke-dasharray","4 3");
      tl.setAttribute("opacity","0.7");
    }
  }
}

function showTip(ev, s, p){
  const o = p.o || {};
  let lines = [`<b>${esc(s.label.name)}</b> (count ${p.y})`];
  if (s.label.description) lines.push(esc(s.label.description));
  if (o._group){
    lines.push(`${o._group.length} occurrence(s) in this bucket`);
  } else {
    if (o.file) lines.push(esc(o.file) + (o.line != null ? ":" + o.line : ""));
    if (o.branch) lines.push("branch: " + esc(o.branch));
    if (o.commit) lines.push("commit: " + esc(String(o.commit).slice(0,10)));
  }
  lines.push(new Date(p.t).toISOString());
  tip.innerHTML = lines.join("<br>");
  tip.style.left = (ev.clientX + 12) + "px";
  tip.style.top = (ev.clientY + 12) + "px";
  tip.style.opacity = 1;
}
function hideTip(){ tip.style.opacity = 0; }
function esc(s){ return String(s).replace(/[&<>"]/g, c => (
  {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c])); }

function buildLegend(){
  const el = document.getElementById("legend");
  el.innerHTML = "";
  if (DATA.length === 0){ el.innerHTML = '<div class="empty">no labels yet</div>'; return; }
  DATA.forEach((label, i) => {
    const row = document.createElement("label");
    const cb = document.createElement("input");
    cb.type = "checkbox"; cb.checked = true;
    cb.addEventListener("change", () => {
      if (cb.checked) visible.add(label.slug); else visible.delete(label.slug);
      draw();
    });
    const sw = document.createElement("span");
    sw.className = "swatch"; sw.style.background = color(i);
    const txt = document.createElement("span");
    txt.innerHTML = `<b>${esc(label.name)}</b> <span class="desc">` +
      `${esc(label.description || "")}</span> (${label.occurrences.length})`;
    row.appendChild(cb); row.appendChild(sw); row.appendChild(txt);
    el.appendChild(row);
  });
}

document.getElementById("gran").addEventListener("change", draw);
document.getElementById("trend").addEventListener("change", draw);
document.getElementById("all").addEventListener("click", () => {
  DATA.forEach(d => visible.add(d.slug));
  document.querySelectorAll("#legend input").forEach(cb => cb.checked = true);
  draw();
});
document.getElementById("none").addEventListener("click", () => {
  visible.clear();
  document.querySelectorAll("#legend input").forEach(cb => cb.checked = false);
  draw();
});

buildLegend();
draw();
</script>
</body>
</html>
"""


# -------------------------------------------------------------------------------- cli

def build_parser():
    parser = argparse.ArgumentParser(
        prog="labels.py",
        description="Track and visualize feedback error-class labels.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_view = sub.add_parser("view_labels", help="list labels and counts")
    p_view.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    p_view.set_defaults(func=cmd_view_labels)

    p_add = sub.add_parser("add_labels", help="create-or-increment a label occurrence")
    p_add.add_argument("--slug", help="increment an existing label by slug")
    p_add.add_argument("--name", help="short handle for a new label")
    p_add.add_argument("--description", help="full explanatory sentence for a new label")
    p_add.add_argument("--file", help="file the addressed feedback lived in")
    p_add.add_argument("--line", type=int, help="line number of the addressed feedback")
    p_add.add_argument("--timestamp", help="ISO8601 UTC; defaults to now")
    p_add.add_argument("--items", help="path to a JSON array of items for batch add")
    p_add.set_defaults(func=cmd_add_labels)

    p_viz = sub.add_parser("visualize_labels", help="render the time-series HTML")
    p_viz.add_argument("--open", action="store_true", help="open the HTML after writing")
    p_viz.set_defaults(func=cmd_visualize_labels)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
