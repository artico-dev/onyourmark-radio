#!/usr/bin/env python3
"""Generate index.html landing page from the same metadata as the RSS feed."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
META = ROOT / "metadata"
AUDIO = ROOT / "audio"

EP_RE = re.compile(r"^#(\d+)([ab])?\s")
SHOW_TITLE = "onyourmark Radio"
SHOW_SUBTITLE = "onyourmarkがお届けするポッドキャスト ｜ アーカイブ"
SHOW_DESC = (
    "雑誌markの編集部が、ランニング・トレイル・自転車・クライミングなど "
    "エンデュランススポーツを軸に、識者・アスリート・クリエイターを招いて語るポッドキャスト。"
    "2020〜2022年に配信された全23エピソードのアーカイブです。"
)
RELEASE_BASE = "https://artico-dev.github.io/onyourmark-radio/audio"
FEED_URL = "feed.xml"


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
                "num": num,
                "suffix": suffix,
                "key": key,
                "title": title,
                "description": (data.get("description") or "").strip(),
                "timestamp": int(data.get("timestamp", 0)),
                "duration": float(data.get("duration", 0)),
                "size": mp3.stat().st_size,
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


def fmt_size(n: int) -> str:
    return f"{n / 1024 / 1024:.0f}MB"


def render_item(it: dict) -> str:
    audio_url = f"{RELEASE_BASE}/{it['key']}.mp3"
    desc_html = escape(it["description"]).replace("\n", "<br>")
    return f"""    <article class="ep" id="{it['key']}">
      <header>
        <h2><a href="#{it['key']}">{escape(it['title'])}</a></h2>
        <p class="meta">{fmt_date(it['timestamp'])} · {fmt_duration(it['duration'])} · {fmt_size(it['size'])}</p>
      </header>
      <audio controls preload="none" src="{audio_url}"></audio>
      <p class="desc">{desc_html}</p>
    </article>"""


def main() -> None:
    items = collect()
    body = "\n".join(render_item(it) for it in items)
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>{escape(SHOW_TITLE)} — アーカイブ</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(SHOW_DESC)}">
  <link rel="alternate" type="application/rss+xml" title="{escape(SHOW_TITLE)}" href="{FEED_URL}">
  <style>
    :root {{ color-scheme: light dark; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", "Hiragino Sans", sans-serif; max-width: 760px; margin: 0 auto; padding: 2rem 1.25rem 4rem; line-height: 1.65; }}
    header.show {{ border-bottom: 1px solid color-mix(in srgb, currentColor 15%, transparent); padding-bottom: 1.5rem; margin-bottom: 2rem; display: grid; grid-template-columns: 140px 1fr; gap: 1.25rem; align-items: start; }}
    header.show img {{ width: 140px; height: 140px; border-radius: 12px; object-fit: cover; }}
    header.show h1 {{ font-size: 1.6rem; margin: 0 0 .3rem; }}
    header.show .sub {{ font-size: .95rem; opacity: .75; margin: 0 0 .8rem; }}
    header.show .desc {{ font-size: .9rem; opacity: .85; margin: 0; }}
    header.show .links {{ margin-top: .6rem; font-size: .85rem; }}
    header.show .links a {{ margin-right: 1rem; }}
    .ep {{ border-top: 1px solid color-mix(in srgb, currentColor 12%, transparent); padding: 1.5rem 0; }}
    .ep h2 {{ font-size: 1.1rem; margin: 0 0 .25rem; }}
    .ep h2 a {{ color: inherit; text-decoration: none; }}
    .ep h2 a:hover {{ text-decoration: underline; }}
    .ep .meta {{ font-size: .8rem; opacity: .65; margin: 0 0 .75rem; }}
    .ep audio {{ width: 100%; margin-bottom: .75rem; }}
    .ep .desc {{ font-size: .9rem; opacity: .9; white-space: pre-wrap; word-break: break-word; }}
    @media (max-width: 540px) {{ header.show {{ grid-template-columns: 1fr; }} header.show img {{ width: 100px; height: 100px; }} }}
  </style>
</head>
<body>
  <header class="show">
    <img src="show-artwork.jpg" alt="{escape(SHOW_TITLE)}">
    <div>
      <h1>{escape(SHOW_TITLE)}</h1>
      <p class="sub">{escape(SHOW_SUBTITLE)}</p>
      <p class="desc">{escape(SHOW_DESC)}</p>
      <p class="links"><a href="{FEED_URL}">RSS</a> · <a href="https://podcasts.apple.com/">Apple Podcasts</a> · <a href="https://open.spotify.com/">Spotify</a></p>
    </div>
  </header>
  <main>
{body}
  </main>
  <footer style="margin-top: 3rem; font-size: .8rem; opacity: .55; text-align: center;">
    Hosted on GitHub Pages · Generated {datetime.now(timezone.utc).strftime("%Y-%m-%d")}
  </footer>
</body>
</html>
"""
    out = ROOT / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out} ({len(items)} episodes)")


if __name__ == "__main__":
    main()
