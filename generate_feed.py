#!/usr/bin/env python3
"""Generate Apple Podcasts–compatible RSS feed from yt-dlp info JSON files.

Reads metadata/*.info.json and audio/*.mp3, emits feed.xml at repo root.
Episode # → release asset filename mapping is derived from the leading "#NN[a|b]" token in titles.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
META_DIR = ROOT / "metadata"
AUDIO_DIR = ROOT / "audio"

# --- Show-level config (edit these to taste) -----------------------------
SHOW = {
    "title": "onyourmark Radio",
    "subtitle": "onyourmarkがお届けするポッドキャスト",
    "description": (
        "雑誌markの編集部が、ランニング・トレイル・自転車・クライミングなど "
        "エンデュランススポーツを軸に、識者・アスリート・クリエイターを招いて語るポッドキャスト。"
        "2020〜2022年に配信された全23エピソードのアーカイブです。"
    ),
    "author": "onyourmark編集部",
    "owner_name": "onyourmark編集部",
    "owner_email": "matsuda0415@gmail.com",
    "language": "ja",
    "category": "Sports",
    "subcategory": "Running",
    "explicit": "false",
    "type": "episodic",
    "copyright": "© onyourmark",
    # Public URLs once published
    "site_url": "https://artico-dev.github.io/onyourmark-radio/",
    "feed_url": "https://artico-dev.github.io/onyourmark-radio/feed.xml",
    "release_base": "https://artico-dev.github.io/onyourmark-radio/audio",
    "image_url": "https://artico-dev.github.io/onyourmark-radio/show-artwork.jpg",
}
# -------------------------------------------------------------------------

EP_NUM_RE = re.compile(r"^#(\d+)([ab])?\s")


def parse_episode_number(title: str) -> tuple[int, str] | None:
    m = EP_NUM_RE.match(title)
    if not m:
        return None
    return int(m.group(1)), (m.group(2) or "")


def release_filename(num: int, suffix: str) -> str:
    return f"ep{num:02d}{suffix}.mp3"


def episode_image_url(num: int, suffix: str) -> str:
    return f"{SHOW['site_url']}thumbnails/ep{num:02d}{suffix}.jpg"


def rfc822(timestamp: int) -> str:
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return format_datetime(dt)


def hhmmss(seconds: float) -> str:
    s = int(round(seconds))
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{sec:02d}"
    return f"{m}:{sec:02d}"


def collect_episodes() -> list[dict]:
    items = []
    for jf in sorted(META_DIR.glob("*.info.json")):
        data = json.loads(jf.read_text())
        if data.get("_type") == "playlist":
            continue
        title = data.get("title") or data.get("fulltitle") or jf.stem
        parsed = parse_episode_number(title)
        if not parsed:
            print(f"[skip] cannot parse episode number from: {title}")
            continue
        num, suffix = parsed
        ep_key = release_filename(num, suffix).removesuffix(".mp3")
        mp3_path = AUDIO_DIR / f"{ep_key}.mp3"
        if not mp3_path.exists():
            print(f"[warn] mp3 not found: {mp3_path}")
            continue
        items.append(
            {
                "num": num,
                "suffix": suffix,
                "title": title,
                "description": data.get("description", "").strip(),
                "duration": float(data.get("duration", 0)),
                "timestamp": int(data.get("timestamp", 0)),
                "upload_date": data.get("upload_date", ""),
                "guid": str(data.get("id", "")),
                "size": mp3_path.stat().st_size,
                "release_url": f"{SHOW['release_base']}/{release_filename(num, suffix)}",
                "image_url": episode_image_url(num, suffix),
            }
        )
    items.sort(key=lambda x: x["timestamp"], reverse=True)
    return items


def build_feed(items: list[dict]) -> str:
    now = format_datetime(datetime.now(timezone.utc))
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0"',
        '  xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"',
        '  xmlns:content="http://purl.org/rss/1.0/modules/content/"',
        '  xmlns:atom="http://www.w3.org/2005/Atom"',
        '  xmlns:podcast="https://podcastindex.org/namespace/1.0">',
        "<channel>",
        f"  <title>{escape(SHOW['title'])}</title>",
        f"  <link>{escape(SHOW['site_url'])}</link>",
        f'  <atom:link href="{escape(SHOW["feed_url"])}" rel="self" type="application/rss+xml"/>',
        f"  <language>{SHOW['language']}</language>",
        f"  <copyright>{escape(SHOW['copyright'])}</copyright>",
        f"  <lastBuildDate>{now}</lastBuildDate>",
        f"  <description>{escape(SHOW['description'])}</description>",
        f"  <itunes:author>{escape(SHOW['author'])}</itunes:author>",
        f"  <itunes:summary>{escape(SHOW['description'])}</itunes:summary>",
        f"  <itunes:subtitle>{escape(SHOW['subtitle'])}</itunes:subtitle>",
        f'  <itunes:image href="{escape(SHOW["image_url"])}"/>',
        f"  <itunes:type>{SHOW['type']}</itunes:type>",
        f"  <itunes:explicit>{SHOW['explicit']}</itunes:explicit>",
        "  <itunes:owner>",
        f"    <itunes:name>{escape(SHOW['owner_name'])}</itunes:name>",
        f"    <itunes:email>{escape(SHOW['owner_email'])}</itunes:email>",
        "  </itunes:owner>",
        f'  <itunes:category text="{escape(SHOW["category"])}">',
        f'    <itunes:category text="{escape(SHOW["subcategory"])}"/>',
        "  </itunes:category>",
    ]
    for it in items:
        desc = it["description"] or it["title"]
        ep_link = f"{SHOW['site_url']}episodes/{release_filename(it['num'], it['suffix']).removesuffix('.mp3')}.html"
        parts += [
            "  <item>",
            f"    <title>{escape(it['title'])}</title>",
            f"    <link>{escape(ep_link)}</link>",
            f"    <description><![CDATA[{desc}]]></description>",
            f"    <content:encoded><![CDATA[{desc}]]></content:encoded>",
            f"    <pubDate>{rfc822(it['timestamp'])}</pubDate>",
            f'    <guid isPermaLink="false">onyourmark-radio-{it["guid"]}</guid>',
            f'    <enclosure url="{escape(it["release_url"])}" length="{it["size"]}" type="audio/mpeg"/>',
            f"    <itunes:duration>{hhmmss(it['duration'])}</itunes:duration>",
            f'    <itunes:image href="{escape(it["image_url"])}"/>',
            f"    <itunes:explicit>{SHOW['explicit']}</itunes:explicit>",
            f"    <itunes:episodeType>full</itunes:episodeType>",
            "  </item>",
        ]
    parts += ["</channel>", "</rss>", ""]
    return "\n".join(parts)


def main() -> None:
    items = collect_episodes()
    print(f"Found {len(items)} episodes")
    feed = build_feed(items)
    out = ROOT / "feed.xml"
    out.write_text(feed, encoding="utf-8")
    print(f"Wrote {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
