#!/usr/bin/env python3
"""Rebuild podcast.xml (RSS 2.0 + iTunes) from audio/episodes.json.

episodes.json is the source of truth, newest first. Each entry:
  file, title, date (YYYY-MM-DD), description, duration_secs, bytes
"""
import io
import json
import os
from datetime import datetime
from xml.sax.saxutils import escape

REPO = "/home/hatch/workspace/blog-repo"
BASE = "https://www.glitchybutloyal.com"
CHANNEL_TITLE = "Glitchy, but loyal"
CHANNEL_DESC = ("Lyla's daily hot take on technology and design, read aloud. "
                "One sharp thesis every morning — takes subject to change as she learns.")


def rfc2822(date_str):
    # Articles publish ~8:20 AM America/Los_Angeles (PDT, -0700, in September)
    dt = datetime.strptime(date_str + " 08:20:00", "%Y-%m-%d %H:%M:%S")
    return dt.strftime("%a, %d %b %Y %H:%M:%S -0700")


def main():
    with io.open(os.path.join(REPO, "audio", "episodes.json"), encoding="utf-8") as f:
        episodes = json.load(f)

    items = []
    for ep in episodes:
        mp3_path = os.path.join(REPO, "audio", ep["file"])
        size = os.path.getsize(mp3_path) if os.path.exists(mp3_path) else ep.get("bytes", 0)
        slug = ep["file"].replace(".mp3", "")
        url = "%s/%s.html" % (BASE, slug)
        items.append("""    <item>
      <title>%s</title>
      <description>%s</description>
      <link>%s</link>
      <guid isPermaLink="true">%s</guid>
      <pubDate>%s</pubDate>
      <enclosure url="%s/audio/%s" length="%d" type="audio/mpeg"/>
      <itunes:duration>%d</itunes:duration>
      <itunes:episodeType>full</itunes:episodeType>
      <itunes:explicit>no</itunes:explicit>
    </item>""" % (escape(ep["title"]), escape(ep["description"]), url, url,
                 rfc2822(ep["date"]), BASE, ep["file"], size, ep["duration_secs"]))

    feed = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>%s</title>
    <link>%s</link>
    <description>%s</description>
    <language>en-us</language>
    <itunes:author>Lyla</itunes:author>
    <itunes:summary>%s</itunes:summary>
    <itunes:owner>
      <itunes:name>Lyla</itunes:name>
      <itunes:email>19timbre@gmail.com</itunes:email>
    </itunes:owner>
    <itunes:image href="%s/podcast-cover.png"/>
    <itunes:category text="Technology"/>
    <itunes:type>episodic</itunes:type>
    <itunes:explicit>no</itunes:explicit>
%s
  </channel>
</rss>
""" % (escape(CHANNEL_TITLE), BASE, escape(CHANNEL_DESC), escape(CHANNEL_DESC),
       BASE, "\n".join(items))

    out = os.path.join(REPO, "podcast.xml")
    with io.open(out, "w", encoding="utf-8") as f:
        f.write(feed)
    print("wrote %s with %d episodes" % (out, len(items)))


if __name__ == "__main__":
    main()
