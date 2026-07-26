#!/usr/bin/env python3
"""Extract frames from a YouTube video and assemble them into contact-sheet cards
(grid images with burned-in timestamps) so an agent can 'see' the video cheaply.

Sampling is hybrid, informed by video-LLM research:
  * uniform base grid: duration / 80 target frames, clamped to 5-30 s interval
    (guarantees coverage even in slow, static videos)
  * plus scene-change keyframes (ffmpeg scene filter): catches cuts, slide
    changes and demos that a fixed grid would miss; marked with '*' on the card
Frames closer together than ~40% of the interval are deduplicated.

Cards are 4x4 grids ~1580 px wide. Research on multimodal models shows grid
montages match individual-frame accuracy at a fraction of the token cost, as
long as tiles stay above ~200 px — ours are 384x216.

Usage:
  python yt_frames.py <url> --outdir <video-folder> [--interval N]
      [--scene-threshold 0.30 | --no-scenes] [--cookies-from-browser chrome]
"""
import argparse
import math
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

COLS, ROWS = 4, 4
TILE_W = 384
LABEL_H = 22
PAD = 6
JPEG_QUALITY = 82
MAX_FRAMES = 128          # hard cap: 8 sheets
MAX_SCENE_FRAMES = 48


def ytdlp_cmd():
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
        if subprocess.run([sys.executable, "-m", "pip", "install", "-q", "yt-dlp"] + extra,
                          capture_output=True).returncode == 0:
            break
    return [sys.executable, "-m", "yt_dlp"]


def ensure_pillow():
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        for extra in (["--break-system-packages"], []):
            if subprocess.run([sys.executable, "-m", "pip", "install", "-q", "Pillow"] + extra,
                              capture_output=True).returncode == 0:
                break


def hms(seconds, with_hours):
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if with_hours else f"{m:d}:{s:02d}"


def fname_ts(seconds):
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}-{m:02d}-{s:02d}"


def get_font(size=14):
    from PIL import ImageFont
    for name in ("DejaVuSans.ttf", "arial.ttf", "Arial.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "C:/Windows/Fonts/arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", **kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--outdir", required=True,
                    help="the video's transcript folder (cards are written here)")
    ap.add_argument("--interval", type=int, default=None,
                    help="seconds between uniform frames (default: adaptive duration/80, 5-30s)")
    ap.add_argument("--scene-threshold", type=float, default=0.30,
                    help="ffmpeg scene-change threshold (lower = more keyframes)")
    ap.add_argument("--no-scenes", action="store_true", help="uniform sampling only")
    ap.add_argument("--max-height", type=int, default=480)
    ap.add_argument("--cookies-from-browser", default=None,
                    help="e.g. chrome/firefox/edge - use if YouTube demands a sign-in check")
    ap.add_argument("--keep-video", action="store_true")
    args = ap.parse_args()

    ensure_pillow()
    from PIL import Image, ImageDraw

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg is required but not found on PATH.")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    yt = ytdlp_cmd()
    if args.cookies_from_browser:
        yt += ["--cookies-from-browser", args.cookies_from_browser]

    # -- duration --------------------------------------------------------------
    r = run(yt + ["-J", "--skip-download", "--no-playlist", args.url])
    if r.returncode != 0:
        sys.exit(f"yt-dlp metadata failed:\n{r.stderr[-1500:]}")
    duration = json.loads(r.stdout).get("duration") or 0
    if not duration:
        sys.exit("Could not determine video duration.")

    interval = args.interval or max(5, min(30, round(duration / 80)))
    print(f"duration={duration}s -> uniform interval={interval}s"
          + ("" if args.no_scenes else f", scene threshold={args.scene_threshold}"))

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        # -- download low-res video -------------------------------------------
        print("Downloading low-res video ...")
        fmt = f"bv*[height<={args.max_height}]/b[height<={args.max_height}]/wv*/w"
        r = run(yt + ["-f", fmt, "--no-playlist", "-o", str(tmp / "video.%(ext)s"), args.url])
        vids = [p for p in tmp.iterdir() if p.stem == "video"]
        if not vids:
            sys.exit(f"video download failed:\n{r.stderr[-1500:]}")
        video = vids[0]

        # -- pass 1: uniform frames -------------------------------------------
        print("Extracting uniform frames ...")
        uni_dir = tmp / "uni"
        uni_dir.mkdir()
        r = run(["ffmpeg", "-loglevel", "error", "-i", str(video),
                 "-vf", f"fps=1/{interval},scale={TILE_W}:-2",
                 "-q:v", "3", str(uni_dir / "u_%05d.jpg")])
        uniform = [((i * interval), p, False)
                   for i, p in enumerate(sorted(uni_dir.glob("u_*.jpg")))]
        if not uniform:
            sys.exit(f"ffmpeg frame extraction failed:\n{r.stderr[-1500:]}")

        # -- pass 2: scene-change keyframes -----------------------------------
        scene = []
        if not args.no_scenes:
            print("Detecting scene changes ...")
            sc_dir = tmp / "sc"
            sc_dir.mkdir()
            r = run(["ffmpeg", "-loglevel", "info", "-i", str(video),
                     "-vf", f"select='gt(scene,{args.scene_threshold})',"
                            f"showinfo,scale={TILE_W}:-2",
                     "-vsync", "vfr", "-q:v", "3", str(sc_dir / "s_%05d.jpg")])
            times = [float(m) for m in re.findall(r"pts_time:\s*([0-9.]+)", r.stderr)]
            files = sorted(sc_dir.glob("s_*.jpg"))
            scene = [(t, p, True) for t, p in zip(times, files)]
            if len(scene) > MAX_SCENE_FRAMES:  # keep an evenly spaced subset
                step = len(scene) / MAX_SCENE_FRAMES
                scene = [scene[int(i * step)] for i in range(MAX_SCENE_FRAMES)]
            print(f"  {len(scene)} scene keyframes kept")

        # -- merge + dedupe ----------------------------------------------------
        min_gap = max(2.0, interval * 0.4)
        merged = []
        for item in sorted(uniform + scene, key=lambda x: x[0]):
            near = next((m for m in merged if abs(m[0] - item[0]) < min_gap), None)
            if near is None:
                merged.append(item)
            elif item[2] and not near[2]:      # prefer scene frame over uniform twin
                merged[merged.index(near)] = item
        if len(merged) > MAX_FRAMES:
            step = len(merged) / MAX_FRAMES
            merged = [merged[int(i * step)] for i in range(MAX_FRAMES)]
        print(f"{len(merged)} frames -> {math.ceil(len(merged) / (COLS * ROWS))} contact sheets")

        # -- build contact sheets ---------------------------------------------
        with_hours = duration >= 3600
        font = get_font(14)
        tile_h = Image.open(merged[0][1]).height
        cell_w, cell_h = TILE_W + PAD, tile_h + LABEL_H + PAD
        sheet_w = COLS * cell_w + PAD
        per_sheet = COLS * ROWS

        if args.keep_video:
            shutil.copy2(video, outdir / f"video_lowres{video.suffix}")

        made = []
        for s_idx in range(math.ceil(len(merged) / per_sheet)):
            chunk = merged[s_idx * per_sheet:(s_idx + 1) * per_sheet]
            rows = math.ceil(len(chunk) / COLS)
            sheet = Image.new("RGB", (sheet_w, rows * cell_h + PAD), (18, 18, 18))
            draw = ImageDraw.Draw(sheet)
            for i, (ts, fp, is_scene) in enumerate(chunk):
                img = Image.open(fp)
                x = PAD + (i % COLS) * cell_w
                y = PAD + (i // COLS) * cell_h
                if img.width > TILE_W:
                    img = img.resize((TILE_W, tile_h))
                sheet.paste(img, (x, y))
                label = hms(ts, with_hours) + (" *" if is_scene else "")
                draw.text((x + 2, y + tile_h + 3), label,
                          fill=(255, 210, 120) if is_scene else (230, 230, 230), font=font)
            t0, t1 = chunk[0][0], chunk[-1][0]
            name = f"contact_sheet_{s_idx + 1:02d}_{fname_ts(t0)}_to_{fname_ts(t1)}.jpg"
            sheet.save(outdir / name, quality=JPEG_QUALITY)
            made.append(name)
            print(f"  {name}  ({len(chunk)} tiles)")

        n_scene = sum(1 for m in merged if m[2])

    (outdir / "frames_info.txt").write_text(
        f"uniform_interval_seconds={interval}\nscene_keyframes={n_scene}\n"
        f"total_frames={len(merged)}\nsheets={len(made)}\ngrid={COLS}x{ROWS}\n"
        "Timestamps are burned in under each tile; '*' (amber) = scene-change keyframe.\n",
        encoding="utf-8")
    print(f"\nDone. {len(made)} contact sheets in {outdir}")


if __name__ == "__main__":
    main()
