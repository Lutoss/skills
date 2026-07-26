#!/usr/bin/env python3
"""Fetch a YouTube video's transcript, metadata, description and top comments
into a tidy folder: <outdir>/youtube/<video_id>_<title-slug>/

Outputs:
  transcript.md               metadata header + description + chapters + clean transcript
  transcript_timestamps.txt   [HH:MM:SS] line-by-line transcript (for mapping to frames)
  comments.md                 top comments, raw, sorted by likes (curate manually/by agent)
  source_url.txt              the original URL

Usage:
  python yt_transcript.py <url> --outdir <project-folder> [--lang de] [--no-comments]
"""
import argparse
import datetime
import json
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.request
from pathlib import Path


def ytdlp_cmd():
    """Return a command list that runs yt-dlp, installing it via pip if needed."""
    exe = shutil.which("yt-dlp") or shutil.which("yt-dlp.exe")
    if exe:
        return [exe]
    local = Path.home() / ".local" / "bin" / "yt-dlp"
    if local.exists():
        return [str(local)]
    try:
        import yt_dlp  # noqa: F401
        return [sys.executable, "-m", "yt_dlp"]
    except ImportError:
        pass
    for extra in (["--break-system-packages"], []):
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "yt-dlp"] + extra,
                           capture_output=True)
        if r.returncode == 0:
            break
    try:
        import yt_dlp  # noqa: F401
        return [sys.executable, "-m", "yt_dlp"]
    except ImportError:
        sys.exit("Could not install yt-dlp. Install it manually: pip install yt-dlp")


def fetch_info(url, with_comments=True, max_comments=30, cookies_browser=None):
    cmd = ytdlp_cmd() + ["-J", "--skip-download", "--no-playlist"]
    if cookies_browser:
        cmd += ["--cookies-from-browser", cookies_browser]
    if with_comments:
        cmd += ["--write-comments", "--extractor-args",
                f"youtube:max_comments={max_comments},all,0,0;comment_sort=top"]
    r = subprocess.run(cmd + [url], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0 and with_comments:
        # comments sometimes fail or time out -> retry without them
        return fetch_info(url, with_comments=False, cookies_browser=cookies_browser)
    if r.returncode != 0:
        sys.exit(f"yt-dlp failed:\n{r.stderr[-2000:]}")
    return json.loads(r.stdout)


def slugify(title, max_len=50):
    s = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:max_len].rstrip("-") or "video"


def hms(seconds):
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def pick_track(tracks_by_lang, lang):
    """Pick the best matching language key from a subtitles/automatic_captions dict."""
    if not tracks_by_lang:
        return None, None
    keys = list(tracks_by_lang.keys())
    for cand in ([lang, f"{lang}-orig"] if lang else []):
        if cand in keys:
            return cand, tracks_by_lang[cand]
    if lang:
        for k in keys:
            if k.startswith(lang):
                return k, tracks_by_lang[k]
    for cand in ("en", "en-orig"):
        if cand in keys:
            return cand, tracks_by_lang[cand]
    k = keys[0]
    return k, tracks_by_lang[k]


def fetch_captions(info, lang_pref):
    """Return (items, lang_key, kind) where items = [(start_seconds, text), ...]."""
    lang = lang_pref or info.get("language") or "en"
    for kind, field in (("manual", "subtitles"), ("automatic", "automatic_captions")):
        lang_key, track = pick_track(info.get(field) or {}, lang)
        if not track:
            continue
        fmt = next((t for t in track if t.get("ext") == "json3"), None) or track[0]
        req = urllib.request.Request(fmt["url"], headers={"User-Agent": "Mozilla/5.0"})
        try:
            raw = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
        except Exception as e:
            print(f"warning: could not fetch {kind} captions ({e})", file=sys.stderr)
            continue
        if fmt.get("ext") == "json3":
            data = json.loads(raw)
            items = []
            for ev in data.get("events", []):
                segs = ev.get("segs")
                if not segs or "tStartMs" not in ev:
                    continue
                text = "".join(s.get("utf8", "") for s in segs)
                text = re.sub(r"\s+", " ", text).strip()
                if text:
                    items.append((ev["tStartMs"] / 1000.0, text))
            if items:
                return items, lang_key, kind
        else:
            items = parse_vtt(raw)
            if items:
                return items, lang_key, kind
    return None, None, None


def parse_vtt(raw):
    """Minimal VTT fallback parser with dedup of rolling auto-sub lines."""
    items, seen_tail = [], ""
    ts = re.compile(r"(\d+):(\d+):(\d+)[.,](\d+)\s*-->")
    cur = None
    for line in raw.splitlines():
        m = ts.match(line.strip())
        if m:
            h, mnt, s, _ = m.groups()
            cur = int(h) * 3600 + int(mnt) * 60 + int(s)
            continue
        line = re.sub(r"<[^>]+>", "", line).strip()
        if not line or line.isdigit() or line.startswith(("WEBVTT", "Kind:", "Language:")):
            continue
        if cur is None or line == seen_tail:
            continue
        items.append((float(cur), line))
        seen_tail = line
        cur = None
    return items


def build_paragraphs(items, gap=4.0, max_len=1200):
    """Join caption lines into readable paragraphs, breaking on pauses."""
    paras, buf, last_end = [], [], None
    for start, text in items:
        if buf and ((last_end is not None and start - last_end > gap and len(" ".join(buf)) > 400)
                    or len(" ".join(buf)) > max_len):
            paras.append(" ".join(buf))
            buf = []
        buf.append(text)
        last_end = start
    if buf:
        paras.append(" ".join(buf))
    return paras


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--outdir", default=".", help="base folder; files go to <outdir>/youtube/<id>_<slug>/")
    ap.add_argument("--lang", default=None, help="caption language (default: video's original language)")
    ap.add_argument("--no-comments", action="store_true")
    ap.add_argument("--max-comments", type=int, default=30)
    ap.add_argument("--cookies-from-browser", default=None,
                    help="e.g. chrome/firefox/edge - use if YouTube demands a sign-in check")
    args = ap.parse_args()

    print("Fetching metadata" + ("" if args.no_comments else " + comments") + " ...")
    info = fetch_info(args.url, with_comments=not args.no_comments,
                      max_comments=args.max_comments,
                      cookies_browser=args.cookies_from_browser)

    vid = info.get("id", "video")
    title = info.get("title", "Untitled")
    folder = Path(args.outdir) / "youtube" / f"{vid}_{slugify(title)}"
    folder.mkdir(parents=True, exist_ok=True)

    print("Fetching captions ...")
    items, lang_key, kind = fetch_captions(info, args.lang)
    if not items:
        print("warning: no captions found for this video", file=sys.stderr)

    today = datetime.date.today().isoformat()
    upload = info.get("upload_date", "")
    upload = f"{upload[:4]}-{upload[4:6]}-{upload[6:]}" if len(upload) == 8 else upload
    duration = info.get("duration") or 0

    md = [f"# {title}", ""]
    md += [f"- **Channel:** {info.get('channel') or info.get('uploader', '?')}",
           f"- **Upload date:** {upload}",
           f"- **Duration:** {hms(duration)}",
           f"- **Views:** {info.get('view_count', '?')}",
           f"- **URL:** {info.get('webpage_url', args.url)}",
           f"- **Retrieved:** {today}"]
    if items:
        md.append(f"- **Captions:** {lang_key} ({kind})")
    md.append("")

    desc = (info.get("description") or "").strip()
    if desc:
        md += ["## Description", "", desc, ""]

    chapters = info.get("chapters") or []
    if chapters:
        md += ["## Chapters", ""]
        md += [f"- {hms(c.get('start_time', 0))} {c.get('title', '')}" for c in chapters]
        md.append("")

    if items:
        md += ["## Transcript", ""]
        for p in build_paragraphs(items):
            md += [p, ""]

    (folder / "transcript.md").write_text("\n".join(md), encoding="utf-8")
    (folder / "source_url.txt").write_text(info.get("webpage_url", args.url) + "\n", encoding="utf-8")

    if items:
        lines = [f"[{hms(s)}] {t}" for s, t in items]
        (folder / "transcript_timestamps.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    comments = info.get("comments") or []
    if comments:
        comments.sort(key=lambda c: c.get("like_count") or 0, reverse=True)
        cm = [f"# Top comments — {title}", "",
              f"Raw top-level comments (sorted by likes), retrieved {today}. "
              "Curate: anything that corrects, contradicts or adds facts to the video "
              "belongs in a 'Notable comments' section of transcript.md.", ""]
        for c in comments:
            author = c.get("author", "?")
            likes = c.get("like_count") or 0
            text = (c.get("text") or "").strip()
            cm += [f"## {author} ({likes} likes)", "", text, ""]
        (folder / "comments.md").write_text("\n".join(cm), encoding="utf-8")

    print(f"\nDone. Output folder: {folder}")
    for f in sorted(folder.iterdir()):
        print(f"  {f.name}")
    print(f"\nvideo_id={vid}")
    print(f"duration_seconds={duration}")


if __name__ == "__main__":
    main()
