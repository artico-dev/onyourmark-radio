#!/usr/bin/env python3
"""Generate per-episode HTML pages under episodes/ for the RSS <link> field."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
META = ROOT / "metadata"
AUDIO = ROOT / "audio"
OUT_DIR = ROOT / "episodes"

EP_RE = re.compile(r"^#(\d+)([ab])?\s")
SHOW_TITLE = "onyourmark Radio"
AUDIO_BASE = "https://artico-dev.github.io/onyourmark-radio/audio"
THUMB_BASE = "https://artico-dev.github.io/onyourmark-radio/thumbnails"


def collect() -> list[dict]:
    items = []
    for jf in META.glob("*.info.json"):
        data = json.loads(jf.read_text())
        if data.get("_type") == "playlist":
            continue
        title = data.get("title", "")
        m = EP_RE.match(title)
        if not m:
            continue
        num, suffix = int(m.group(1)), (m.group(2) or "")
        key = f"ep{num:02d}{suffix}"
        mp3 = AUDIO / f"{key}.mp3"
        if not mp3.exists():
            continue
        items.append(
            {
                "key": key,
                "title": title,
                "description": (data.get("description") or "").strip(),
                "timestamp": int(data.get("timestamp", 0)),
                "duration": float(data.get("duration", 0)),
            }
        )
    items.sort(key=lambda x: x["timestamp"], reverse=True)
    return items


def fmt_duration(sec: float) -> str:
    s = int(round(sec))
    h, rem = divmod(s, 3600)
    m, _ = divmod(rem, 60)
    return f"{h}h{m:02d}m" if h else f"{m}min"


def fmt_date(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


def render(it: dict, prev: dict | None, next_: dict | None) -> str:
    audio_url = f"{AUDIO_BASE}/{it['key']}.mp3"
    thumb_url = f"{THUMB_BASE}/{it['key']}.jpg"
    desc = escape(it["description"]).replace("\n", "<br>")
    nav = []
    if prev:
        nav.append(f'<a href="{prev["key"]}.html">← {escape(prev["title"])[:30]}</a>')
    nav.append('<a href="../">一覧</a>')
    if next_:
        nav.append(f'<a href="{next_["key"]}.html">{escape(next_["title"])[:30]} →</a>')
    nav_html = " · ".join(nav)
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>{escape(it['title'])} — {SHOW_TITLE}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(it['description'][:160])}">
  <meta property="og:title" content="{escape(it['title'])}">
  <meta property="og:description" content="{escape(it['description'][:160])}">
  <meta property="og:image" content="{thumb_url}">
  <meta property="og:type" content="music.song">
  <meta property="og:audio" content="{audio_url}">
  <link rel="alternate" type="application/rss+xml" title="{SHOW_TITLE}" href="../feed.xml">
  <style>
    :root {{ color-scheme: light dark; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", "Hiragino Sans", sans-serif; max-width: 760px; margin: 0 auto; padding: 2rem 1.25rem 4rem; line-height: 1.65; }}
    nav.top, nav.bot {{ font-size: .85rem; opacity: .75; margin: 0 0 1.5rem; }}
    nav a {{ color: inherit; }}
    .ep-head {{ display: grid; grid-template-columns: 120px 1fr; gap: 1.25rem; align-items: start; margin-bottom: 1.5rem; }}
    .ep-head img {{ width: 120px; height: 120px; border-radius: 12px; object-fit: cover; }}
    .ep-head h1 {{ font-size: 1.5rem; margin: 0 0 .3rem; }}
    .ep-head .meta {{ font-size: .85rem; opacity: .7; margin: 0; }}
    audio {{ width: 100%; margin: 1rem 0 2rem; }}
    .desc {{ font-size: .95rem; white-space: pre-wrap; word-break: break-word; opacity: .9; }}
    nav.bot {{ margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid color-mix(in srgb, currentColor 12%, transparent); }}
    @media (max-width: 540px) {{ .ep-head {{ grid-template-columns: 1fr; }} .ep-head img {{ width: 100px; height: 100px; }} }}
  </style>
</head>
<body>
  <nav class="top"><a href="../">← {SHOW_TITLE} 一覧</a></nav>
  <article>
    <div class="ep-head">
      <img src="{thumb_url}" alt="">
      <div>
        <h1>{escape(it['title'])}</h1>
        <p class="meta">{fmt_date(it['timestamp'])} · {fmt_duration(it['duration'])}</p>
      </div>
    </div>
    <audio controls preload="none" src="{audio_url}"></audio>
    <p class="desc">{desc}</p>
  </article>
  <nav class="bot">{nav_html}</nav>
</body>
</html>
"""


def main() -> None:
    items = collect()
    OUT_DIR.mkdir(exist_ok=True)
    for i, it in enumerate(items):
        prev = items[i + 1] if i + 1 < len(items) else None  # older
        next_ = items[i - 1] if i > 0 else None  # newer
        out = OUT_DIR / f"{it['key']}.html"
        out.write_text(render(it, prev, next_), encoding="utf-8")
    print(f"Wrote {len(items)} episode pages to {OUT_DIR}/")


if __name__ == "__main__":
    main()
