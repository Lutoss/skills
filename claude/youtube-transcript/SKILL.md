---
name: youtube-transcript
description: Save a YouTube video as a local transcript folder — transcript.md with metadata, description, chapters and top comments, plus optional contact-sheet frame cards so an agent can "see" the video. Use whenever the user shares a YouTube link/URL and wants a transcript, captions, subtitles, wants the video "abgelegt"/saved/archived, asks what a video says, or wants it "mit Bildern/Frames/Screenshots". Also use when the user just pastes a YouTube URL and says something like "transcript" or "ablegen".
---

# YouTube → Transcript

Turn a YouTube link into a self-contained folder that an agent (or human) can read
instead of watching the video: clean transcript, the video's own description and
chapters, notable comments, and — on request — contact-sheet images of frames.

## Output layout

Everything goes to `<project>/youtube/<video_id>_<title-slug>/` inside the folder
the user is currently working in (their project folder, or the session outputs
folder if none is mounted):

```
youtube/xmGY276gEFY_boris-has-some-really-good-advice/
├── transcript.md               # metadata, description, chapters, transcript, notable comments
├── transcript_timestamps.txt   # [HH:MM:SS] lines — for mapping text to frames
├── comments.md                 # raw top comments (kept as source material)
├── source_url.txt
├── contact_sheet_01_00-00-00_to_00-03-30.jpg   # only when frames requested
├── ...
└── frames_info.txt
```

## Workflow

### 1. Always: transcript + metadata + comments

```bash
python scripts/yt_transcript.py "<url>" --outdir "<project-folder>"
```

The script installs yt-dlp if missing, prefers manually-created captions in the
video's original language and falls back to auto-generated ones, cleans the text
into readable paragraphs, and writes all files listed above. `--lang de` forces a
caption language; `--no-comments` skips comment fetching (use it if the fetch is
slow or the run before failed on comments).

### 2. Always: curate the comments

`comments.md` is raw material, not the deliverable. Read it and pick only comments
that add something to the video: corrections of factual errors, first-hand
knowledge, important context or caveats, useful links. Append them to
`transcript.md` as:

```markdown
## Notable comments

> **author** (123 likes): the comment text …
```

Two or three good ones are typical; if nothing qualifies, append the section with
"Nothing substantive." so future readers know the comments were checked. Skip
pure praise ("great video!"), jokes, and timestamps-only comments.

### 3. On request: frames as contact sheets

Only when the user asks for frames/images/screenshots (transcript alone is much
faster — no video download needed):

```bash
python scripts/yt_frames.py "<url>" --outdir "<the folder created in step 1>"
```

This downloads the video once in low resolution (≤480p) and samples frames with
a **hybrid strategy** (uniform-only sampling is known to miss cuts and slide
changes in video-LLM research, and pure scene detection under-covers static
talking-head stretches):

- a uniform base grid — duration/80, clamped to a 5–30 s interval — guarantees
  coverage everywhere;
- plus **scene-change keyframes** (ffmpeg scene filter, threshold 0.30) that
  catch cuts, slide flips and demo transitions; they appear with an amber `*`
  next to their timestamp;
- near-duplicates are merged, total frames capped at 128 (= 8 cards).

Frames are assembled into 4×4 grid cards (~1580 px wide) with the timestamp
burned in under each tile — grid montages match individual-frame accuracy for
multimodal models at a fraction of the token cost, provided tiles stay above
~200 px (these are 384×216). A 20-minute video becomes ~6 cards; even a 2-hour
video stays ≤ 8, few enough that an agent can view all of them. The temp video
and single frames are deleted afterwards; useful flags: `--keep-video`,
`--interval N` (e.g. 10 for dense slide decks), `--scene-threshold 0.2` (more
keyframes) or `--no-scenes`.

### How an agent should "watch" a saved video

Reading order matters: research on video understanding shows models do best when
frames and text are **interleaved**, not consumed separately. So:

1. Read `transcript.md` (description + transcript) for the narrative.
2. View the contact sheets **in order**, and for each card look up the matching
   section of `transcript_timestamps.txt` — the burned-in tile timestamps are
   the join key. This tells you what was said while each thing was on screen.
3. `*`-marked tiles are scene changes — on screen-heavy videos these are the
   slides/demos worth reading closely.
4. If one specific moment needs more detail than a 384 px tile offers, extract
   a single full-res frame: `yt-dlp` the video (or use `--keep-video` next
   time) and `ffmpeg -ss <timestamp> -i video -frames:v 1 out.jpg`.

### 4. Wrap up

Tell the user where the folder is and give a 2–3 sentence summary of what the
video is about (from the transcript you just saved — read at least the beginning
and the description). If captions were auto-generated, mention that names and
technical terms may be mis-transcribed.

## Environment notes

- Both scripts need Python 3 and network access to youtube.com; `yt_frames.py`
  additionally needs `ffmpeg` on PATH and installs Pillow if missing.
- In a sandbox with short command timeouts, run the scripts in the background
  (`nohup … &`) and poll the log — metadata+comments+captions typically takes
  15–60 s, the frames step 1–4 min depending on video length.
- If yt-dlp errors mention throttling or missing formats, retry once; if captions
  are missing entirely, say so — do not fabricate a transcript from the
  description.
- If YouTube answers "Sign in to confirm you're not a bot", rerun with
  `--cookies-from-browser chrome` (or firefox/edge — must run on the user's own
  machine, not in a sandbox, and the browser should be closed on Windows).
- All YouTube URL forms work: `watch?v=`, `youtu.be/`, `shorts/`, with extra
  query params. Playlists: only the single linked video is processed
  (`--no-playlist` is built in); for several links, run the script once per link.
