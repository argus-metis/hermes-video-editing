#!/usr/bin/env python3
"""
video_toolkit.py — Command-line video editing toolkit.

Works standalone or alongside audio_toolkit.py for advanced audio operations.
For audio editing (trim, fade, normalise, pitch shift, mix, generate, sync),
see audio_toolkit.py in the same directory.

Usage:
    python video_toolkit.py info analyze INPUT
    python video_toolkit.py edit trim INPUT --start 00:01:30 --end 00:03:00 -o OUTPUT
    python video_toolkit.py edit concat FILE1 FILE2 [FILE3 ...] -o OUTPUT
    python video_toolkit.py edit speed INPUT --factor 1.5 -o OUTPUT
    python video_toolkit.py edit audio INPUT --audio MUSIC.mp3 --mix 0.3 -o OUTPUT
    python video_toolkit.py edit text INPUT --text "Hello" --at 00:00:05 -o OUTPUT
    python video_toolkit.py edit export INPUT --preset instagram-reel -o OUTPUT
    python video_toolkit.py caption generate INPUT [-o subtitles.srt]
    python video_toolkit.py caption burn INPUT [-o OUTPUT]
    python video_toolkit.py silence remove INPUT [-o OUTPUT]
    python video_toolkit.py scenes detect INPUT
    python video_toolkit.py frames extract INPUT --interval 2 -d frames/
    python video_toolkit.py frames grid INPUT [-o grid.jpg]
    python video_toolkit.py enhance stabilise INPUT -o OUTPUT
    python video_toolkit.py enhance bg-remove INPUT -o OUTPUT
    python video_toolkit.py enhance colour INPUT -o OUTPUT
    python video_toolkit.py enhance reframe INPUT --target 9:16 -o OUTPUT
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(cmd, **kwargs):
    """Run a subprocess command, returning CompletedProcess."""
    if isinstance(cmd, str):
        cmd = cmd.split()
    return subprocess.run(cmd, capture_output=True, text=True, timeout=3600, **kwargs)


def ffprobe_json(path):
    """Get full ffprobe info as a dict."""
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", str(path)
    ]
    r = run(cmd)
    if r.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {r.stderr}")
    return json.loads(r.stdout)


def get_duration(path):
    """Get duration in seconds."""
    info = ffprobe_json(path)
    fmt = info.get("format", {})
    dur = fmt.get("duration")
    if dur:
        return float(dur)
    for s in info.get("streams", []):
        if "duration" in s:
            return float(s["duration"])
    return 0.0


def format_duration(seconds):
    """Format seconds as HH:MM:SS.mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def ensure_output(path, default_suffix=".mp4"):
    """Return output path, generating one in /tmp if not provided."""
    if path:
        return Path(path)
    return Path(tempfile.mktemp(suffix=default_suffix))


def parse_timestamp(ts):
    """Parse a timestamp string (HH:MM:SS, MM:SS, or seconds) to seconds."""
    if ts is None:
        return None
    ts = str(ts).strip()
    parts = ts.split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    else:
        return float(ts)


# ---------------------------------------------------------------------------
# Info / Analysis
# ---------------------------------------------------------------------------

def cmd_info_analyze(args):
    """Analyze a video file and print its properties."""
    path = Path(args.input)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    info = ffprobe_json(path)
    fmt = info.get("format", {})
    streams = info.get("streams", [])

    print(f"File: {path}")
    print(f"Size: {int(fmt.get('size', 0)) / 1024 / 1024:.1f} MB")
    print(f"Duration: {format_duration(float(fmt.get('duration', 0)))}")
    print(f"Format: {fmt.get('format_long_name', 'unknown')}")
    print(f"Bitrate: {int(fmt.get('bit_rate', 0)) / 1000:.0f} kbps")
    print()

    for s in streams:
        codec_type = s.get("codec_type")
        if codec_type == "video":
            w = s.get("width", "?")
            h = s.get("height", "?")
            fps = s.get("r_frame_rate", "?")
            codec = s.get("codec_name", "?")
            pix_fmt = s.get("pix_fmt", "?")
            print(f"Video: {w}x{h}, {fps} fps, {codec}, {pix_fmt}")
        elif codec_type == "audio":
            codec = s.get("codec_name", "?")
            channels = s.get("channels", "?")
            sample_rate = s.get("sample_rate", "?")
            print(f"Audio: {codec}, {channels} ch, {sample_rate} Hz")

    return 0


# ---------------------------------------------------------------------------
# Edit operations
# ---------------------------------------------------------------------------

def cmd_edit_trim(args):
    """Trim a video between start and end timestamps."""
    inp = Path(args.input)
    out = ensure_output(args.output)
    start = parse_timestamp(args.start)
    end = parse_timestamp(args.end)

    cmd = ["ffmpeg", "-y", "-i", str(inp)]
    if start is not None:
        cmd += ["-ss", format_duration(start)]
    if end is not None:
        cmd += ["-to", format_duration(end)]
    cmd += ["-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart", str(out)]

    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    print(f"Trimmed: {out} ({format_duration(get_duration(str(out)))})")
    return 0


def cmd_edit_concat(args):
    """Concatenate multiple video files."""
    files = args.inputs
    out = ensure_output(args.output)

    # Create concat file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for fp in files:
            f.write(f"file '{Path(fp).resolve()}'\n")
        concat_file = f.name

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart",
        str(out)
    ]
    r = run(cmd)
    os.unlink(concat_file)

    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    print(f"Concatenated {len(files)} files: {out} ({format_duration(get_duration(str(out)))})")
    return 0


def cmd_edit_speed(args):
    """Change video playback speed."""
    inp = Path(args.input)
    out = ensure_output(args.output)
    factor = float(args.factor)

    # Adjust both video and audio speed
    video_filter = f"setpts={1/factor}*PTS"
    audio_filter = f"atempo={factor}" if 0.5 <= factor <= 2.0 else f"atempo=2.0,atempo={factor/2}"

    cmd = [
        "ffmpeg", "-y", "-i", str(inp),
        "-filter_complex", f"[0:v]{video_filter}[v];[0:a]{audio_filter}[a]",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart",
        str(out)
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    print(f"Speed x{factor}: {out} ({format_duration(get_duration(str(out)))})")
    return 0


def cmd_edit_audio(args):
    """Add or replace audio track with mixing control.
    
    For advanced audio operations (normalise, pitch shift, fade, generate,
    sidechain ducking, waveforms, spectrograms), use audio_toolkit.py instead:
        python audio_toolkit.py sync VIDEO --audio MUSIC --mix 0.3 --duck
    """
    inp = Path(args.input)
    audio = Path(args.audio)
    out = ensure_output(args.output)
    mix = float(args.mix)
    replace = args.replace

    if replace:
        # Replace audio entirely
        cmd = [
            "ffmpeg", "-y", "-i", str(inp), "-i", str(audio),
            "-c:v", "copy", "-c:a", "aac",
            "-map", "0:v", "-map", "1:a",
            "-shortest", "-movflags", "+faststart", str(out)
        ]
    else:
        # Mix audio with original
        cmd = [
            "ffmpeg", "-y", "-i", str(inp), "-i", str(audio),
            "-filter_complex",
            f"[0:a]volume=1.0[a0];[1:a]volume={mix}[a1];[a0][a1]amix=inputs=2:duration=longest[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac",
            "-movflags", "+faststart", str(out)
        ]

    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    print(f"Audio mixed: {out}")
    return 0


def cmd_edit_text(args):
    """Burn text overlay onto video at a specific timestamp."""
    inp = Path(args.input)
    out = ensure_output(args.output)
    text = args.text
    at = parse_timestamp(args.at)
    duration = parse_timestamp(args.duration) if args.duration else 3.0
    fontsize = args.fontsize or 48
    color = args.color or "white"
    position = args.position or "bottom"

    # Position mapping
    pos_map = {
        "center": "(w-text_w)/2:(h-text_h)/2",
        "top": "(w-text_w)/2:40",
        "bottom": "(w-text_w)/2:h-text_h-40",
        "top-left": "40:40",
        "top-right": "w-text_w-40:40",
        "bottom-left": "40:h-text_h-40",
        "bottom-right": "w-text_w-40:h-text_h-40",
    }
    xy = pos_map.get(position, pos_map["bottom"])

    # Escape special chars for ffmpeg
    safe_text = text.replace("'", "'\\''").replace(":", "\\:")

    enable = f"between(t,{at},{at + duration})" if at is not None else "1"

    vf = (
        f"drawtext=text='{safe_text}':"
        f"fontsize={fontsize}:fontcolor={color}:"
        f"borderw=2:bordercolor=black:"
        f"x={xy}:enable='{enable}'"
    )

    cmd = [
        "ffmpeg", "-y", "-i", str(inp),
        "-vf", vf,
        "-c:v", "libx264", "-c:a", "copy", "-movflags", "+faststart",
        str(out)
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    print(f"Text overlay added: {out}")
    return 0


# ---------------------------------------------------------------------------
# Platform export presets
# ---------------------------------------------------------------------------

PRESETS = {
    "instagram-reel": {"w": 1080, "h": 1920, "fps": 30, "br": "5M", "max_dur": 90},
    "instagram-post": {"w": 1080, "h": 1080, "fps": 30, "br": "5M", "max_dur": 60},
    "youtube": {"w": 1920, "h": 1080, "fps": 30, "br": "10M", "max_dur": None},
    "youtube-shorts": {"w": 1080, "h": 1920, "fps": 30, "br": "5M", "max_dur": 60},
    "tiktok": {"w": 1080, "h": 1920, "fps": 30, "br": "5M", "max_dur": 600},
    "twitter": {"w": 1280, "h": 720, "fps": 30, "br": "5M", "max_dur": 140},
    "facebook": {"w": 1280, "h": 720, "fps": 30, "br": "5M", "max_dur": None},
    "telegram": {"w": 1280, "h": 720, "fps": 30, "br": "4M", "max_dur": None},
}


def cmd_edit_export(args):
    """Export video with a platform preset."""
    inp = Path(args.input)
    out = ensure_output(args.output)
    preset_name = args.preset

    if preset_name not in PRESETS:
        print(f"Unknown preset '{preset_name}'. Available: {', '.join(PRESETS.keys())}", file=sys.stderr)
        return 1

    p = PRESETS[preset_name]
    dur = get_duration(str(inp))

    if p["max_dur"] and dur > p["max_dur"]:
        print(f"Warning: video is {dur:.0f}s but {preset_name} max is {p['max_dur']}s")

    cmd = [
        "ffmpeg", "-y", "-i", str(inp),
        "-vf", f"scale={p['w']}:{p['h']}:force_original_aspect_ratio=decrease,pad={p['w']}:{p['h']}:(ow-iw)/2:(oh-ih)/2:black",
        "-r", str(p["fps"]),
        "-c:v", "libx264", "-b:v", p["br"],
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        str(out)
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    print(f"Exported ({preset_name}): {out}")
    return 0


# ---------------------------------------------------------------------------
# Captions / Transcription
# ---------------------------------------------------------------------------

def cmd_caption_generate(args):
    """Generate SRT subtitle file from video audio using Whisper."""
    try:
        import whisper
    except ImportError:
        print("Error: openai-whisper not installed. Run: pip install openai-whisper", file=sys.stderr)
        return 1

    inp = Path(args.input)
    model_name = args.model or "base"

    print(f"Loading Whisper model '{model_name}'...", file=sys.stderr)
    model = whisper.load_model(model_name)

    print(f"Transcribing {inp}...", file=sys.stderr)
    result = model.transcribe(str(inp), verbose=False)

    # Write SRT
    out_path = Path(args.output) if args.output else inp.with_suffix(".srt")
    with open(out_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(result["segments"], 1):
            start = format_srt_time(seg["start"])
            end = format_srt_time(seg["end"])
            text = seg["text"].strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    lang = result.get("language", "unknown")
    print(f"Transcription ({lang}): {out_path} ({len(result['segments'])} segments)")
    return 0


def format_srt_time(seconds):
    """Format seconds as SRT timestamp: HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def cmd_caption_burn(args):
    """Transcribe video and burn subtitles into the video."""
    inp = Path(args.input)
    out = ensure_output(args.output)
    model_name = args.model or "base"
    font_size = args.font_size or 24
    style = args.style or "outline"

    # Step 1: Generate SRT
    with tempfile.NamedTemporaryFile(suffix=".srt", delete=False, mode="w") as tmp:
        srt_path = tmp.name

    print("Step 1: Transcribing...", file=sys.stderr)
    ret = cmd_caption_generate(argparse.Namespace(input=str(inp), output=srt_path, model=model_name))
    if ret != 0:
        return ret

    # Step 2: Burn subtitles
    print("Step 2: Burning subtitles...", file=sys.stderr)
    subtitles_filter = (
        f"subtitles={srt_path}:force_style='FontSize={font_size},"
        f"PrimaryColour=&Hffffff,OutlineColour=&H000000,Outline=2,"
        f"Alignment=2,MarginV=30'"
    )

    cmd = [
        "ffmpeg", "-y", "-i", str(inp),
        "-vf", subtitles_filter,
        "-c:v", "libx264", "-c:a", "copy", "-movflags", "+faststart",
        str(out)
    ]
    r = run(cmd)
    os.unlink(srt_path)

    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    print(f"Captions burned: {out}")
    return 0


# ---------------------------------------------------------------------------
# Silence Removal
# ---------------------------------------------------------------------------

def cmd_silence_remove(args):
    """Remove silent sections from video using Silero VAD."""
    inp = Path(args.input)
    out = ensure_output(args.output)
    threshold = float(args.threshold) if args.threshold else 0.3
    min_silence = int(args.min_silence) if args.min_silence else 500
    padding = float(args.padding) if args.padding else 0.1

    # Try Silero VAD first, fall back to ffmpeg silence detection
    try:
        return _silence_remove_silero(inp, out, threshold, min_silence, padding)
    except ImportError:
        print("Silero VAD not available, using ffmpeg silence detection...", file=sys.stderr)
        return _silence_remove_ffmpeg(inp, out, threshold, padding)


def _silence_remove_silero(inp, out, threshold, min_silence_ms, padding):
    """Remove silence using Silero VAD (torch-based)."""
    import torch

    model, utils = torch.hub.load(
        repo_or_dir="snakers4/silero-vad",
        model="silero_vad",
        trust_repo=True
    )
    (get_speech_timestamps, _, read_audio, _, _) = utils

    # Read audio at 16kHz for VAD
    wav = read_audio(str(inp), sampling_rate=16000)
    speech_ts = get_speech_timestamps(wav, model, return_seconds=True,
                                       threshold=threshold,
                                       min_silence_duration_ms=min_silence_ms)

    if not speech_ts:
        print("No speech detected — copying file as-is")
        shutil.copy2(inp, out)
        return 0

    # Build segments list with padding
    segments = []
    for seg in speech_ts:
        start = max(0, seg["start"] - padding)
        end = seg["end"] + padding
        segments.append((start, end))

    # Merge overlapping segments
    merged = [segments[0]]
    for start, end in segments[1:]:
        if start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    print(f"Keeping {len(merged)} speech segments...", file=sys.stderr)

    # Concatenate speech segments using ffmpeg
    return _concat_segments(inp, out, merged)


def _silence_remove_ffmpeg(inp, out, threshold, padding):
    """Remove silence using ffmpeg's silencedetect filter (fallback)."""
    # Detect silence
    cmd = [
        "ffmpeg", "-i", str(inp),
        "-af", f"silencedetect=noise=-{int(threshold*60)}dB:d=0.5",
        "-f", "null", "-"
    ]
    r = run(cmd)
    output = r.stderr

    # Parse silence periods
    silences = []
    for m in re.finditer(r"silence_start: ([\d.]+)", output):
        start = float(m.group(1))
        silences.append({"start": start})

    for i, m in enumerate(re.finditer(r"silence_end: ([\d.]+)", output)):
        if i < len(silences):
            silences[i]["end"] = float(m.group(1))

    if not silences:
        print("No silence detected — copying file as-is")
        shutil.copy2(inp, out)
        return 0

    # Invert silence periods to get speech periods
    dur = get_duration(str(inp))
    segments = []
    current = 0
    for s in silences:
        if current < s["start"] - padding:
            segments.append((current, s["start"] - padding))
        current = s.get("end", s["start"])
    if current < dur:
        segments.append((current, dur))

    print(f"Keeping {len(segments)} speech segments...", file=sys.stderr)
    return _concat_segments(inp, out, segments)


def _concat_segments(inp, out, segments):
    """Concatenate time segments from a video file."""
    # Use ffmpeg segment extraction and concat
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for start, end in segments:
            tmp_out = tempfile.mktemp(suffix=".ts")
            cmd = [
                "ffmpeg", "-y", "-i", str(inp),
                "-ss", format_duration(start), "-to", format_duration(end),
                "-c:v", "libx264", "-c:a", "aac",
                "-f", "mpegts", tmp_out
            ]
            r = run(cmd)
            if r.returncode == 0:
                f.write(f"file '{tmp_out}'\n")
        concat_file = f.name

    # Concat
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart",
        str(out)
    ]
    r = run(cmd)

    # Cleanup temp segments
    with open(concat_file) as f:
        for line in f:
            p = line.strip().split("'", 2)[1]
            if os.path.exists(p):
                os.unlink(p)
    os.unlink(concat_file)

    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1

    new_dur = get_duration(str(out))
    print(f"Silence removed: {out} ({format_duration(new_dur)})")
    return 0


# ---------------------------------------------------------------------------
# Scene Detection
# ---------------------------------------------------------------------------

def cmd_scenes_detect(args):
    """Detect scene changes in a video."""
    try:
        from scenedetect import detect, AdaptiveDetector, ContentDetector
        from scenedetect import split_video_ffmpeg
    except ImportError:
        print("Error: scenedetect not installed. Run: pip install scenedetect[opencv]", file=sys.stderr)
        return 1

    inp = Path(args.input)
    threshold = float(args.threshold) if args.threshold else 27.0

    print(f"Detecting scenes in {inp}...", file=sys.stderr)
    # scenedetect 0.7 renamed AdaptiveDetector's `threshold` to `adaptive_threshold`.
    # Accept both so this works across versions (0.6 and earlier vs 0.7+).
    try:
        detector = AdaptiveDetector(adaptive_threshold=threshold)
    except TypeError:
        detector = AdaptiveDetector(threshold=threshold)
    scene_list = detect(str(inp), detector)

    if not scene_list:
        print("No scene changes detected.")
        return 0

    print(f"Found {len(scene_list)} scene(s):\n")
    for i, (start, end) in enumerate(scene_list, 1):
        print(f"  Scene {i}: {start.get_timecode()} --> {end.get_timecode()}")

    if args.split:
        outdir = Path(args.split)
        outdir.mkdir(parents=True, exist_ok=True)
        split_video_ffmpeg(str(inp), scene_list, output_dir=str(outdir))
        print(f"\nSplit into {len(scene_list)} files in {outdir}/")

    return 0


# ---------------------------------------------------------------------------
# Frame Extraction / Review
# ---------------------------------------------------------------------------

def cmd_frames_extract(args):
    """Extract frames at regular intervals for visual review."""
    inp = Path(args.input)
    outdir = Path(args.outdir or tempfile.mkdtemp(prefix="frames_"))
    interval = int(args.interval) if args.interval else 5

    outdir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y", "-i", str(inp),
        "-vf", f"fps=1/{interval}",
        "-q:v", "2",
        str(outdir / "frame_%04d.jpg")
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1

    count = len(list(outdir.glob("frame_*.jpg")))
    print(f"Extracted {count} frames to {outdir}/ (1 every {interval}s)")
    return 0


def cmd_frames_grid(args):
    """Generate a contact sheet / thumbnail grid of the video."""
    inp = Path(args.input)
    out = ensure_output(args.output, default_suffix=".jpg")
    cols = int(args.cols) if args.cols else 4
    interval = int(args.interval) if args.interval else 5

    # Extract frames to temp dir
    tmpdir = tempfile.mkdtemp(prefix="grid_")
    cmd = [
        "ffmpeg", "-y", "-i", str(inp),
        "-vf", f"fps=1/{interval}",
        "-q:v", "2",
        str(Path(tmpdir) / "frame_%04d.jpg")
    ]
    r = run(cmd)
    if r.returncode != 0:
        shutil.rmtree(tmpdir)
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1

    # Build grid with Pillow
    try:
        from PIL import Image
    except ImportError:
        print("Error: Pillow not installed. Run: pip install Pillow", file=sys.stderr)
        shutil.rmtree(tmpdir)
        return 1

    frames = sorted(Path(tmpdir).glob("frame_*.jpg"))
    if not frames:
        print("No frames extracted", file=sys.stderr)
        shutil.rmtree(tmpdir)
        return 1

    # Open first frame to get dimensions
    first = Image.open(frames[0])
    fw, fh = first.size

    # Scale down for grid
    scale = min(320, fw)
    sw = scale
    sh = int(fh * scale / fw)

    rows = (len(frames) + cols - 1) // cols
    grid_w = cols * sw + (cols + 1) * 4
    grid_h = rows * sh + (rows + 1) * 4 + rows * 20

    grid = Image.new("RGB", (grid_w, grid_h), (30, 30, 30))

    for i, fpath in enumerate(frames):
        img = Image.open(fpath).resize((sw, sh), Image.LANCZOS)
        col = i % cols
        row = i // cols
        x = col * sw + (col + 1) * 4
        y = row * (sh + 20) + (row + 1) * 4
        grid.paste(img, (x, y))

    grid.save(str(out), quality=90)
    shutil.rmtree(tmpdir)
    print(f"Thumbnail grid: {out} ({len(frames)} frames, {cols} columns)")
    return 0


# ---------------------------------------------------------------------------
# Enhancement
# ---------------------------------------------------------------------------

def cmd_enhance_stabilise(args):
    """Stabilise shaky video using vidstab."""
    inp = Path(args.input)
    out = ensure_output(args.output)

    with tempfile.NamedTemporaryFile(suffix=".trf", delete=False) as f:
        trf = f.name

    # Pass 1: Analyse
    cmd1 = [
        "ffmpeg", "-y", "-i", str(inp),
        "-vf", f"vidstabdetect=result={trf}:shakiness=5:accuracy=15",
        "-f", "null", "-"
    ]
    r = run(cmd1)
    if r.returncode != 0:
        os.unlink(trf)
        print(f"Error (analysis): {r.stderr}", file=sys.stderr)
        return 1

    # Pass 2: Stabilise
    cmd2 = [
        "ffmpeg", "-y", "-i", str(inp),
        "-vf", f"vidstabtransform=input={trf}:smoothing=10:optzoom=1",
        "-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart",
        str(out)
    ]
    r = run(cmd2)
    os.unlink(trf)

    if r.returncode != 0:
        print(f"Error (stabilise): {r.stderr}", file=sys.stderr)
        return 1
    print(f"Stabilised: {out}")
    return 0


def cmd_enhance_bg_remove(args):
    """Remove video background using backgroundremover."""
    inp = Path(args.input)
    out = ensure_output(args.output, default_suffix=".webm")

    try:
        from backgroundremover.bg import remove
    except ImportError:
        print("Error: backgroundremover not installed. Run: pip install backgroundremover", file=sys.stderr)
        return 1

    print(f"Removing background from {inp}... (this may take a while on CPU)", file=sys.stderr)

    # Use ffmpeg to extract frames, process each, reassemble
    tmpdir = tempfile.mkdtemp(prefix="bgrem_")
    try:
        # Extract frames
        cmd = ["ffmpeg", "-y", "-i", str(inp), str(Path(tmpdir) / "frame_%05d.png")]
        r = run(cmd)
        if r.returncode != 0:
            print(f"Error extracting frames: {r.stderr}", file=sys.stderr)
            return 1

        frames = sorted(Path(tmpdir).glob("frame_*.png"))
        outdir = Path(tmpdir) / "output"
        outdir.mkdir()

        for i, fpath in enumerate(frames):
            with open(fpath, "rb") as f:
                data = f.read()
            result = remove(data)
            with open(outdir / f"frame_{i+1:05d}.png", "wb") as f:
                f.write(result)
            if (i + 1) % 50 == 0:
                print(f"  Processed {i+1}/{len(frames)} frames...", file=sys.stderr)

        # Reassemble with alpha channel
        cmd = [
            "ffmpeg", "-y",
            "-framerate", "30",
            "-i", str(outdir / "frame_%05d.png"),
            "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
            "-auto-alt-ref", "0",
            str(out)
        ]
        r = run(cmd)
        if r.returncode != 0:
            # Fallback to H.264 without alpha
            out = out.with_suffix(".mp4")
            cmd = [
                "ffmpeg", "-y",
                "-framerate", "30",
                "-i", str(outdir / "frame_%05d.png"),
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                str(out)
            ]
            r = run(cmd)

        if r.returncode != 0:
            print(f"Error reassembling: {r.stderr}", file=sys.stderr)
            return 1

        print(f"Background removed: {out}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def cmd_enhance_colour(args):
    """Auto-enhance colour and brightness."""
    inp = Path(args.input)
    out = ensure_output(args.output)

    # Analyse video brightness
    cmd_analysis = [
        "ffmpeg", "-i", str(inp),
        "-vf", "signalstats",
        "-f", "null", "-"
    ]
    r = run(cmd_analysis)

    # Apply auto-enhancement filters
    filters = "eq=brightness=0.05:contrast=1.1:saturation=1.1,hqdn3d=4:3:6:4.5"

    cmd = [
        "ffmpeg", "-y", "-i", str(inp),
        "-vf", filters,
        "-c:v", "libx264", "-c:a", "copy", "-movflags", "+faststart",
        str(out)
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    print(f"Colour enhanced: {out}")
    return 0


def cmd_enhance_reframe(args):
    """Smart reframe video to a different aspect ratio, tracking faces."""
    inp = Path(args.input)
    out = ensure_output(args.output)
    target = args.target or "9:16"

    # Parse target aspect ratio
    parts = target.split(":")
    if len(parts) == 2:
        tw, th = int(parts[0]), int(parts[1])
    else:
        print(f"Invalid target ratio '{target}'. Use W:H format, e.g. 9:16", file=sys.stderr)
        return 1

    # Target resolution
    target_h = 1920 if th > tw else 1080
    target_w = int(target_h * tw / th)

    try:
        import cv2
        return _reframe_opencv(inp, out, target_w, target_h, tw, th)
    except ImportError:
        print("OpenCV not available, using centre crop...", file=sys.stderr)
        return _reframe_center(inp, out, target_w, target_h, tw, th)


def _reframe_center(inp, out, tw, th, ratio_w, ratio_h):
    """Centre crop reframe (no face tracking)."""
    info = ffprobe_json(str(inp))
    for s in info["streams"]:
        if s["codec_type"] == "video":
            ow, oh = s["width"], s["height"]
            break

    # Calculate crop to match target ratio
    src_ratio = ow / oh
    tgt_ratio = ratio_w / ratio_h

    if src_ratio > tgt_ratio:
        # Source is wider — crop sides
        new_w = int(oh * tgt_ratio)
        new_h = oh
    else:
        # Source is taller — crop top/bottom
        new_w = ow
        new_h = int(ow / tgt_ratio)

    vf = f"crop={new_w}:{new_h}:(ow-iw)/2:(oh-ih)/2,scale={tw}:{th}"

    cmd = [
        "ffmpeg", "-y", "-i", str(inp),
        "-vf", vf,
        "-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart",
        str(out)
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    print(f"Reframed ({ratio_w}:{ratio_h}): {out}")
    return 0


def _reframe_opencv(inp, out, tw, th, ratio_w, ratio_h):
    """Face-tracking smart reframe using OpenCV."""
    import cv2

    cap = cv2.VideoCapture(str(inp))
    fps = cap.get(cv2.CAP_PROP_FPS)
    ow = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    oh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    crop_w = int(oh * ratio_w / ratio_h)
    crop_h = oh

    # Analyse faces to determine crop positions
    positions = []
    for i in range(total):
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) > 0:
            # Use largest face centre
            fx, fy, fw, fh = max(faces, key=lambda f: f[2] * f[3])
            cx = fx + fw // 2
            positions.append(cx)
        else:
            positions.append(ow // 2)

        if i % 100 == 0:
            print(f"  Analysing frame {i}/{total}...", file=sys.stderr)

    cap.release()

    if not positions:
        return _reframe_center(inp, out, tw, th, ratio_w, ratio_h)

    # Smooth positions to avoid jitter
    from statistics import mean
    smoothed = []
    window = max(1, int(fps * 1.5))  # 1.5 second window
    for i in range(len(positions)):
        start = max(0, i - window)
        end = min(len(positions), i + window)
        smoothed.append(int(mean(positions[start:end])))

    # Write positions to file for ffmpeg zoompan
    pos_file = tempfile.mktemp(suffix=".txt")
    with open(pos_file, "w") as f:
        for x in smoothed:
            crop_x = max(0, min(x - crop_w // 2, ow - crop_w))
            f.write(f"{crop_x}\n")

    # Use ffmpeg with the crop positions
    # For simplicity, re-encode frame by frame using pipe
    tmpdir = tempfile.mkdtemp(prefix="reframe_")
    try:
        cap = cv2.VideoCapture(str(inp))
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(
            str(Path(tmpdir) / "reframed.mp4"), fourcc, fps, (tw, th)
        )

        for i in range(min(len(smoothed), total)):
            ret, frame = cap.read()
            if not ret:
                break
            crop_x = max(0, min(smoothed[i] - crop_w // 2, ow - crop_w))
            cropped = frame[:, crop_x:crop_x + crop_w]
            resized = cv2.resize(cropped, (tw, th), interpolation=cv2.INTER_LANCZOS4)
            writer.write(resized)

            if i % 100 == 0:
                print(f"  Reframing frame {i}/{total}...", file=sys.stderr)

        writer.release()
        cap.release()

        # Copy audio from original
        cmd = [
            "ffmpeg", "-y",
            "-i", str(Path(tmpdir) / "reframed.mp4"),
            "-i", str(inp),
            "-c:v", "libx264", "-c:a", "aac",
            "-map", "0:v", "-map", "1:a",
            "-movflags", "+faststart",
            str(out)
        ]
        r = run(cmd)
        if r.returncode != 0:
            # No audio? Just copy video
            shutil.copy2(Path(tmpdir) / "reframed.mp4", out)

        print(f"Smart reframed ({ratio_w}:{ratio_h}): {out}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Cloud API (Optional, Paid)
# ---------------------------------------------------------------------------

def cmd_cloud_runway(args):
    """Runway ML API integration (requires RUNWAY_API_KEY)."""
    api_key = os.environ.get("RUNWAY_API_KEY")
    if not api_key:
        print("Error: RUNWAY_API_KEY not set", file=sys.stderr)
        return 1

    action = args.action
    if action == "image-to-video":
        return _runway_image_to_video(args, api_key)
    elif action == "text-to-image":
        return _runway_text_to_image(args, api_key)
    else:
        print(f"Unknown Runway action: {action}", file=sys.stderr)
        return 1


def _runway_image_to_video(args, api_key):
    """Generate video from an image using Runway Gen-4.5."""
    import urllib.request

    inp = Path(args.input)
    prompt = args.prompt or ""
    duration = int(args.duration or 5)

    url = "https://api.dev.runwayml.com/v1/image_to_video"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Runway-Version": "2024-11-06"
    }

    # Read and encode image
    import base64
    with open(inp, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    payload = {
        "model": "gen4.5",
        "promptImage": f"data:image/png;base64,{img_b64}",
        "promptText": prompt,
        "duration": duration,
    }

    req = urllib.request.Request(url, json.dumps(payload).encode(), headers)
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
        task_id = result.get("id")
        print(f"Runway task created: {task_id}")
        print(f"Poll for status: python video_toolkit.py cloud runway status --task-id {task_id}")
        return 0
    except Exception as e:
        print(f"Runway API error: {e}", file=sys.stderr)
        return 1


def _runway_text_to_image(args, api_key):
    """Generate image from text using Runway Gen-4 Image."""
    import urllib.request

    prompt = args.prompt
    url = "https://api.dev.runwayml.com/v1/text_to_image"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Runway-Version": "2024-11-06"
    }
    payload = {"model": "gen4_image", "promptText": prompt}

    req = urllib.request.Request(url, json.dumps(payload).encode(), headers)
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
        print(f"Runway task created: {result.get('id')}")
        return 0
    except Exception as e:
        print(f"Runway API error: {e}", file=sys.stderr)
        return 1


def cmd_cloud_shotstack(args):
    """Shotstack API integration (requires SHOTSTACK_API_KEY)."""
    api_key = os.environ.get("SHOTSTACK_API_KEY")
    if not api_key:
        print("Error: SHOTSTACK_API_KEY not set", file=sys.stderr)
        return 1

    print("Shotstack integration: define a JSON timeline and render via API.")
    print("See https://shotstack.io/docs/guide/ for timeline JSON format.")
    return 0


# ---------------------------------------------------------------------------
# Main argument parser
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Video Editing Toolkit for Hermes Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="group")

    # info
    p_info = sub.add_parser("info")
    p_info_sub = p_info.add_subparsers(dest="command")
    p_analyze = p_info_sub.add_parser("analyze", help="Analyze video properties")
    p_analyze.add_argument("input")

    # edit
    p_edit = sub.add_parser("edit")
    p_edit_sub = p_edit.add_subparsers(dest="command")

    p_trim = p_edit_sub.add_parser("trim", help="Trim video")
    p_trim.add_argument("input")
    p_trim.add_argument("--start", help="Start timestamp")
    p_trim.add_argument("--end", help="End timestamp")
    p_trim.add_argument("-o", "--output")

    p_concat = p_edit_sub.add_parser("concat", help="Concatenate videos")
    p_concat.add_argument("inputs", nargs="+")
    p_concat.add_argument("-o", "--output")

    p_speed = p_edit_sub.add_parser("speed", help="Change speed")
    p_speed.add_argument("input")
    p_speed.add_argument("--factor", required=True, help="Speed factor (1.5 = 50%% faster)")
    p_speed.add_argument("-o", "--output")

    p_audio = p_edit_sub.add_parser("audio", help="Add/replace audio")
    p_audio.add_argument("input")
    p_audio.add_argument("--audio", required=True, help="Audio file path")
    p_audio.add_argument("--mix", default="0.3", help="Mix level (0-1)")
    p_audio.add_argument("--replace", action="store_true", help="Replace audio instead of mixing")
    p_audio.add_argument("-o", "--output")

    p_text = p_edit_sub.add_parser("text", help="Burn text overlay")
    p_text.add_argument("input")
    p_text.add_argument("--text", required=True)
    p_text.add_argument("--at", help="Timestamp to show text")
    p_text.add_argument("--duration", default="3", help="Duration to show text")
    p_text.add_argument("--fontsize", type=int)
    p_text.add_argument("--color", default="white")
    p_text.add_argument("--position", default="bottom",
                        choices=["center", "top", "bottom", "top-left", "top-right", "bottom-left", "bottom-right"])
    p_text.add_argument("-o", "--output")

    p_export = p_edit_sub.add_parser("export", help="Export with platform preset")
    p_export.add_argument("input")
    p_export.add_argument("--preset", required=True, choices=list(PRESETS.keys()))
    p_export.add_argument("-o", "--output")

    # caption
    p_cap = sub.add_parser("caption")
    p_cap_sub = p_cap.add_subparsers(dest="command")

    p_gen = p_cap_sub.add_parser("generate", help="Generate SRT subtitles")
    p_gen.add_argument("input")
    p_gen.add_argument("-o", "--output")
    p_gen.add_argument("--model", default="base", help="Whisper model (tiny/base/small/medium/large)")

    p_burn = p_cap_sub.add_parser("burn", help="Transcribe and burn subtitles")
    p_burn.add_argument("input")
    p_burn.add_argument("-o", "--output")
    p_burn.add_argument("--model", default="base")
    p_burn.add_argument("--font-size", type=int, default=24)
    p_burn.add_argument("--style", default="outline")

    # silence
    p_sil = sub.add_parser("silence")
    p_sil_sub = p_sil.add_subparsers(dest="command")

    p_srem = p_sil_sub.add_parser("remove", help="Remove silent sections")
    p_srem.add_argument("input")
    p_srem.add_argument("-o", "--output")
    p_srem.add_argument("--threshold", help="VAD threshold (0-1)")
    p_srem.add_argument("--min-silence", help="Min silence duration in ms")
    p_srem.add_argument("--padding", help="Padding around speech in seconds")

    # scenes
    p_sc = sub.add_parser("scenes")
    p_sc_sub = p_sc.add_subparsers(dest="command")

    p_sdet = p_sc_sub.add_parser("detect", help="Detect scene changes")
    p_sdet.add_argument("input")
    p_sdet.add_argument("--threshold", help="Detection threshold")
    p_sdet.add_argument("--split", help="Output directory to split into scenes")

    # frames
    p_fr = sub.add_parser("frames")
    p_fr_sub = p_fr.add_subparsers(dest="command")

    p_fext = p_fr_sub.add_parser("extract", help="Extract frames at intervals")
    p_fext.add_argument("input")
    p_fext.add_argument("--interval", default="5", help="Seconds between frames")
    p_fext.add_argument("-d", "--outdir")

    p_fgrid = p_fr_sub.add_parser("grid", help="Generate thumbnail grid")
    p_fgrid.add_argument("input")
    p_fgrid.add_argument("-o", "--output")
    p_fgrid.add_argument("--cols", default="4")
    p_fgrid.add_argument("--interval", default="5")

    # enhance
    p_enh = sub.add_parser("enhance")
    p_enh_sub = p_enh.add_subparsers(dest="command")

    p_stab = p_enh_sub.add_parser("stabilise", help="Stabilise shaky video")
    p_stab.add_argument("input")
    p_stab.add_argument("-o", "--output")

    p_bgrem = p_enh_sub.add_parser("bg-remove", help="Remove background")
    p_bgrem.add_argument("input")
    p_bgrem.add_argument("-o", "--output")

    p_colour = p_enh_sub.add_parser("colour", help="Auto colour enhance")
    p_colour.add_argument("input")
    p_colour.add_argument("-o", "--output")

    p_reframe = p_enh_sub.add_parser("reframe", help="Smart reframe")
    p_reframe.add_argument("input")
    p_reframe.add_argument("--target", default="9:16", help="Target ratio (e.g. 9:16)")
    p_reframe.add_argument("-o", "--output")

    # cloud
    p_cloud = sub.add_parser("cloud")
    p_cloud_sub = p_cloud.add_subparsers(dest="command")

    p_runway = p_cloud_sub.add_parser("runway", help="Runway ML API")
    p_runway.add_argument("action", choices=["image-to-video", "text-to-image", "status"])
    p_runway.add_argument("--input", help="Input image for image-to-video")
    p_runway.add_argument("--prompt", help="Text prompt")
    p_runway.add_argument("--duration", default="5", help="Video duration in seconds")
    p_runway.add_argument("--task-id", help="Task ID for status check")

    p_shotstack = p_cloud_sub.add_parser("shotstack", help="Shotstack API")
    p_shotstack.add_argument("--timeline", help="Timeline JSON file")

    args = parser.parse_args()

    if not args.group:
        parser.print_help()
        return 1

    # Dispatch
    dispatch = {
        ("info", "analyze"): cmd_info_analyze,
        ("edit", "trim"): cmd_edit_trim,
        ("edit", "concat"): cmd_edit_concat,
        ("edit", "speed"): cmd_edit_speed,
        ("edit", "audio"): cmd_edit_audio,
        ("edit", "text"): cmd_edit_text,
        ("edit", "export"): cmd_edit_export,
        ("caption", "generate"): cmd_caption_generate,
        ("caption", "burn"): cmd_caption_burn,
        ("silence", "remove"): cmd_silence_remove,
        ("scenes", "detect"): cmd_scenes_detect,
        ("frames", "extract"): cmd_frames_extract,
        ("frames", "grid"): cmd_frames_grid,
        ("enhance", "stabilise"): cmd_enhance_stabilise,
        ("enhance", "bg-remove"): cmd_enhance_bg_remove,
        ("enhance", "colour"): cmd_enhance_colour,
        ("enhance", "reframe"): cmd_enhance_reframe,
        ("cloud", "runway"): cmd_cloud_runway,
        ("cloud", "shotstack"): cmd_cloud_shotstack,
    }

    handler = dispatch.get((args.group, args.command))
    if handler:
        return handler(args)
    else:
        parser.parse_args(["--help"])
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
