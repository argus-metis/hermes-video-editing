---
name: video-editing
description: Video and audio editing via natural language — cut, caption, silence removal, scene detection, stabilisation, colour grading, background removal, smart reframing, audio processing, and cloud API integrations. Free local tools with optional paid cloud tiers.
version: 2.0.0
author: Argus-Metis
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Video, Audio, Editing, ffmpeg, Captions, Subtitles, Transcription, Whisper, Scene-Detection, Stabilisation, Colour-Grading, Background-Removal, Smart-Reframe, Podcast, Montage]
    category: creative
    related_skills: [ascii-video, manim-video, p5js, songwriting-and-ai-music, heartmula]
    requires_toolsets: [terminal]
---

# Video & Audio Editing Skill

Programmatic video and audio editing toolkit. Edit media by describing what you want in natural language. Works with any agent — Claude, GPT, Gemini, open-source models, or custom frameworks.

## When to Use

Load this skill when the user:
- Shares a video or audio file and asks to edit it (trim, cut, concatenate, merge)
- Requests captions, subtitles, or transcription
- Wants to remove silences or dead air from a recording
- Asks to stabilise shaky footage or remove a background
- Wants to reframe video for a specific platform (TikTok, Instagram Reels, YouTube Shorts)
- Requests colour grading or visual enhancement
- Asks to mix audio tracks, normalise levels, or adjust volume
- Wants to generate tones, ambient pads, or background music beds
- Asks to convert media formats or export for a specific platform
- Mentions podcast production, montage assembly, or crossfade transitions
- Sends a video via a messaging platform and asks for edits

## Quick Reference

### Video Operations

| Operation | Command |
|-----------|---------|
| Analyze video | `python scripts/video_toolkit.py info analyze INPUT` |
| Trim/cut | `python scripts/video_toolkit.py edit trim INPUT --start 00:01:30 --end 00:03:00 -o OUTPUT` |
| Concatenate | `python scripts/video_toolkit.py edit concat FILE1 FILE2 [FILE3 ...] -o OUTPUT` |
| Change speed | `python scripts/video_toolkit.py edit speed INPUT --factor 1.5 -o OUTPUT` |
| Add audio | `python scripts/video_toolkit.py edit audio INPUT --audio MUSIC.mp3 --mix 0.3 -o OUTPUT` |
| Add text overlay | `python scripts/video_toolkit.py edit text INPUT --text "Title" --start 00:00:01 --end 00:00:05 -o OUTPUT` |
| Export preset | `python scripts/video_toolkit.py edit export INPUT --preset instagram-reel -o OUTPUT` |
| Generate SRT | `python scripts/video_toolkit.py caption generate INPUT -o subtitles.srt` |
| Burn captions | `python scripts/video_toolkit.py caption burn INPUT -o OUTPUT` |
| Remove silence | `python scripts/video_toolkit.py silence remove INPUT -o OUTPUT` |
| Detect scenes | `python scripts/video_toolkit.py scenes detect INPUT` |
| Extract frames | `python scripts/video_toolkit.py frames extract INPUT --interval 2 -d frames/` |
| Thumbnail grid | `python scripts/video_toolkit.py frames grid INPUT -o grid.jpg` |
| Stabilise | `python scripts/video_toolkit.py enhance stabilise INPUT -o OUTPUT` |
| Remove background | `python scripts/video_toolkit.py enhance bg-remove INPUT -o OUTPUT` |
| Auto colour | `python scripts/video_toolkit.py enhance colour INPUT -o OUTPUT` |
| Smart reframe | `python scripts/video_toolkit.py enhance reframe INPUT --target 9:16 -o OUTPUT` |
| Runway cloud | `python scripts/video_toolkit.py cloud runway --help` |
| Shotstack cloud | `python scripts/video_toolkit.py cloud shotstack --help` |

### Audio Operations

| Operation | Command |
|-----------|---------|
| Analyze audio | `python scripts/audio_toolkit.py info analyze INPUT` |
| Trim | `python scripts/audio_toolkit.py edit trim INPUT --start 00:00:30 --end 00:01:00 -o OUTPUT` |
| Fade in/out | `python scripts/audio_toolkit.py edit fade INPUT --in 2 --out 3 -o OUTPUT` |
| Normalise | `python scripts/audio_toolkit.py edit normalise INPUT -o OUTPUT` |
| Change speed | `python scripts/audio_toolkit.py edit speed INPUT --factor 1.5 -o OUTPUT` |
| Shift pitch | `python scripts/audio_toolkit.py edit pitch INPUT --semitones 2 -o OUTPUT` |
| Adjust volume | `python scripts/audio_toolkit.py edit volume INPUT --level 1.5 -o OUTPUT` |
| Mix tracks | `python scripts/audio_toolkit.py edit mix INPUT --overlay VOICE --overlay-level 0.8 -o OUTPUT` |
| Concatenate | `python scripts/audio_toolkit.py edit concat FILE1 FILE2 [FILE3 ...] -o OUTPUT` |
| Convert format | `python scripts/audio_toolkit.py edit convert INPUT --format mp3 --bitrate 192 -o OUTPUT` |
| Generate tone | `python scripts/audio_toolkit.py generate tone --frequency 440 --duration 5 -o OUTPUT` |
| Generate noise | `python scripts/audio_toolkit.py generate noise --type white --duration 3 -o OUTPUT` |
| Generate pad/chord | `python scripts/audio_toolkit.py generate pad --notes C3,Eb3,G3 --duration 10 -o OUTPUT` |
| Extract audio from video | `python scripts/audio_toolkit.py extract VIDEO -o OUTPUT` |
| Replace audio in video | `python scripts/audio_toolkit.py replace VIDEO --audio NEW_AUDIO -o OUTPUT` |
| Sync audio to video | `python scripts/audio_toolkit.py sync VIDEO --audio MUSIC --offset 0.5 --mix 0.3 -o OUTPUT` |
| Waveform image | `python scripts/audio_toolkit.py waveform INPUT -o waveform.png` |
| Spectrogram image | `python scripts/audio_toolkit.py spectrogram INPUT -o spectrogram.png` |

## Dependencies

### Required (Tier 1 — Free, Local)
- ffmpeg (system package)
- Python 3.10+
- moviepy, ffmpeg-python, opencv-python-headless, Pillow

### Optional AI (Tier 2 — Free, Local)
- openai-whisper (transcription)
- silero (voice activity detection via torch)
- scenedetect (PySceneDetect)
- backgroundremover (background removal)
- rembg (alternative background removal)
- numpy

### Optional Cloud (Tier 2 — Paid APIs)
- Runway API (generative video, style transfer)
- Shotstack API (cloud rendering, templates)

### Install

```bash
# System dependency
sudo apt-get install ffmpeg   # Debian/Ubuntu
# brew install ffmpeg          # macOS

# Python dependencies
pip install moviepy ffmpeg-python opencv-python-headless Pillow numpy

# Optional AI tools (install individually as needed)
pip install openai-whisper    # For transcription/captions
pip install scenedetect-headless  # For scene detection
pip install torch             # For Silero VAD (silence detection)
pip install backgroundremover # For background removal
pip install rembg             # Alternative background removal
```

Or use the install script:
```bash
bash install.sh               # Core + all optional
bash install.sh --core        # Core only
bash install.sh --check       # Check what's installed
```

## Workflow

### 1. Receive and understand the request

Parse the user's natural language editing instructions. Common patterns:

**Video patterns:**
- "Cut the first 30 seconds" → trim from 00:00:30 to end
- "Remove the bit between 2:00 and 3:30" → cut that range, concatenate the rest
- "Add subtitles" → transcribe with Whisper, burn in SRT
- "Remove silences" → Silero VAD detection, cut silent segments
- "Make it vertical for TikTok" → smart reframe to 9:16
- "Fix the shaky footage" → stabilise with vidstab
- "Make it pop more" → colour enhancement
- "Export for Instagram Reels" → reframe + export preset (1080x1920, H.264, AAC)
- "Remove the background" → backgroundremover
- "Add a lower-third title at 1:30 saying 'Chapter 2'" → text overlay at timestamp

**Audio patterns:**
- "Make it louder" → volume adjustment (or normalise if uneven)
- "Fade the intro/outro" → fade in/out with specified duration
- "Speed it up 1.5x" → speed change (optionally preserve pitch with rubberband)
- "Make the voice deeper" → pitch shift down 2-3 semitones
- "Mix the voiceover with background music" → mix tracks with overlay-level control
- "Normalize the audio" → normalise to target loudness
- "Extract the audio from this video" → extract to standalone file
- "Replace the music in this video" → replace audio track
- "Generate a background tone/chord" → generate pad with note names
- "Show me the waveform" → generate waveform PNG
- "What does the frequency spectrum look like?" → generate spectrogram PNG
- "Convert this WAV to MP3" → format conversion with bitrate control

### 2. Analyze the source media

Always start by running `info analyze` to understand what you are working with:

```bash
# Video analysis — returns duration, resolution, framerate, codec, bitrate, audio tracks, file size
python scripts/video_toolkit.py info analyze INPUT.mp4

# Audio analysis — returns duration, codec, channels, sample rate, bit depth, RMS level, file size
python scripts/audio_toolkit.py info analyze INPUT.mp3
```

### 3. Plan the edit pipeline

Break complex requests into sequential operations. Execute in the right order:

1. **Structural edits first** (trim, cut, concatenate, silence removal)
2. **Enhancement** (stabilise, colour, background removal)
3. **Reframing/cropping** (aspect ratio changes)
4. **Overlays** (text, captions, watermarks)
5. **Audio processing** (normalise, fade, pitch shift, speed, mix)
6. **Audio-video sync** (replace audio, mix music bed, sync offset)
7. **Export** (codec, format, platform preset)

### 4. Execute each step

Run each operation, checking the exit code and stderr. Use temporary files between steps for complex pipelines.

For multi-step edits, chain operations using temp files:
```bash
# Step 1: Remove silence
python scripts/video_toolkit.py silence remove input.mp4 -o /tmp/step1.mp4
# Step 2: Stabilise
python scripts/video_toolkit.py enhance stabilise /tmp/step1.mp4 -o /tmp/step2.mp4
# Step 3: Normalise audio
python scripts/audio_toolkit.py extract /tmp/step2.mp4 -o /tmp/audio.wav
python scripts/audio_toolkit.py edit normalise /tmp/audio.wav -o /tmp/audio_norm.wav
python scripts/audio_toolkit.py replace /tmp/step2.mp4 --audio /tmp/audio_norm.wav -o /tmp/step3.mp4
# Step 4: Burn captions
python scripts/video_toolkit.py caption burn /tmp/step3.mp4 -o /tmp/step4.mp4
# Step 5: Reframe for Reels
python scripts/video_toolkit.py edit export /tmp/step4.mp4 --preset instagram-reel -o final.mp4
# Cleanup
rm /tmp/step*.mp4 /tmp/audio*.wav
```

### 5. Visual and audio review (quality control)

After editing, **always review the result** before delivering.

#### Approach A — Agents with native vision tools

If the agent has a built-in image analysis tool (e.g. Claude's computer vision, GPT-4V, Gemini's multimodal input), use it directly to inspect visual output:

```bash
# Generate a contact sheet for quick overview
python scripts/video_toolkit.py frames grid OUTPUT.mp4 -o /tmp/review_grid.jpg

# Extract key frames for detailed inspection
python scripts/video_toolkit.py frames extract OUTPUT.mp4 --interval 5 -d /tmp/review_frames/
```

Then pass the generated image(s) to the agent's native vision tool and check:
- Are cuts clean? No black frames at edit points?
- Are captions readable and properly positioned?
- Is the framing correct for the target platform?
- Any visual artifacts or glitches?
- Is the colour/brightness consistent across edits?

For audio review, generate visual representations:
```bash
# Waveform for amplitude/level inspection
python scripts/audio_toolkit.py waveform OUTPUT.mp4 -o /tmp/review_waveform.png

# Spectrogram for frequency content
python scripts/audio_toolkit.py spectrogram OUTPUT.mp4 -o /tmp/review_spectrogram.png
```

Pass waveform and spectrogram images to the native vision tool and check:
- Is the audio level consistent (no sudden spikes or drops)?
- Is there unwanted noise or silence at the start/end?
- Are fade-ins/outs smooth?
- Is the frequency range appropriate for the content?

#### Approach B — Agents without native vision tools

If the agent cannot natively analyse images, rely on metadata extraction and structured data instead:

```bash
# 1. Get full output metadata
python scripts/video_toolkit.py info analyze OUTPUT.mp4
# Returns: duration, resolution, framerate, codec, bitrate, audio tracks — compare to expected values

# 2. Generate a contact sheet (save for the user to review manually)
python scripts/video_toolkit.py frames grid OUTPUT.mp4 -o /tmp/review_grid.jpg

# 3. Extract frames and list them (timestamps confirm continuity)
python scripts/video_toolkit.py frames extract OUTPUT.mp4 --interval 5 -d /tmp/review_frames/
ls -la /tmp/review_frames/
# Check: number of frames ≈ duration / interval, filenames show sequential timestamps

# 4. For audio, get detailed analysis
python scripts/audio_toolkit.py info analyze OUTPUT.mp4
# Returns: codec, channels, sample rate, RMS level, bit depth, duration, bitrate

# 5. Generate waveform and spectrogram for the user
python scripts/audio_toolkit.py waveform OUTPUT.mp4 -o /tmp/review_waveform.png
python scripts/audio_toolkit.py spectrogram OUTPUT.mp4 -o /tmp/review_spectrogram.png

# 6. Compare input vs output metadata to detect anomalies
```

Automated checks the agent can perform from the text output alone:
- Duration matches expected length (±1s tolerance for trim/concat operations)
- Resolution and framerate match the target platform preset
- Audio codec and channels are correct
- File size is reasonable for the duration (no corruption → typically 5-50 MB/min for H.264)
- RMS level is in a healthy range (-20 to -6 dB for normalised audio)

**Always deliver the contact sheet and/or waveform images to the user for manual visual confirmation** when the agent cannot inspect them itself.

If issues are found, fix and re-review.

### 6. Deliver the final file

Report to the user:
- What operations were performed
- Output file path and size
- Duration and format details
- Any warnings or notes

If the user sent the media via a messaging platform, send the file back as an attachment.

## Audio Deep Dive

### Audio Analysis

Always run `info analyze` on audio files before editing. The output includes:

- **Duration** — total length in HH:MM:SS.mmm
- **Codec** — encoding format (aac, mp3, pcm_s16le, etc.)
- **Channels** — mono (1), stereo (2), or surround layouts
- **Sample rate** — typically 44100 or 48000 Hz
- **Bit depth** — 16-bit, 24-bit, 32-bit float, etc.
- **Bitrate** — in kbps
- **RMS level** — average loudness in dB (healthy range: -20 to -6 dB)
- **File size** — in MB

```bash
python scripts/audio_toolkit.py info analyze podcast.wav
```

### Audio Edit Operations

#### Trim
```bash
python scripts/audio_toolkit.py edit trim interview.mp3 --start 00:02:00 --end 00:15:30 -o clip.mp3
```

#### Fade In / Fade Out
```bash
# 2-second fade in, 3-second fade out
python scripts/audio_toolkit.py edit fade song.wav --in 2 --out 3 -o song_faded.wav
```

#### Normalise
Bring audio to a target loudness level. Essential before mixing or publishing.
```bash
python scripts/audio_toolkit.py edit normalise quiet_recording.wav -o loud_and_clear.wav
```

#### Speed Change
```bash
# 1.5x speed (also raises pitch — use pitch correction after if needed)
python scripts/audio_toolkit.py edit speed lecture.mp3 --factor 1.5 -o fast.mp3
```

#### Pitch Shift
```bash
# Shift up 2 semitones (make voice slightly higher/brighter)
python scripts/audio_toolkit.py edit pitch voice.wav --semitones 2 -o pitched.wav
# Shift down 3 semitones (deeper voice)
python scripts/audio_toolkit.py edit pitch voice.wav --semitones -3 -o deep.wav
```

#### Volume Adjustment
```bash
# 1.5x louder. Values > 1.0 increase, < 1.0 decrease
python scripts/audio_toolkit.py edit volume quiet.mp3 --level 1.5 -o louder.mp3
# Halve the volume
python scripts/audio_toolkit.py edit volume loud.mp3 --level 0.5 -o quieter.mp3
```

#### Mix Multiple Tracks
```bash
# Mix background music with voiceover — voice at 80% of original level
python scripts/audio_toolkit.py edit mix music.mp3 --overlay voiceover.wav --overlay-level 0.8 -o mixed.mp3
```

#### Concatenate
```bash
# Join multiple audio files sequentially
python scripts/audio_toolkit.py edit concat part1.mp3 part2.mp3 part3.mp3 -o full_episode.mp3
```

#### Format Conversion
```bash
# Convert WAV to MP3 at 192 kbps
python scripts/audio_toolkit.py edit convert recording.wav --format mp3 --bitrate 192 -o recording.mp3
# Convert to AAC for video compatibility
python scripts/audio_toolkit.py edit convert music.wav --format aac --bitrate 256 -o music.m4a
```

### Audio Generation

#### Tone Generation
```bash
# 440 Hz (A4) sine wave for 5 seconds
python scripts/audio_toolkit.py generate tone --frequency 440 --duration 5 -o a4.mp3
```

#### Noise Generation
```bash
# White noise for 3 seconds (useful for testing or ambient beds)
python scripts/audio_toolkit.py generate noise --type white --duration 3 -o noise.mp3
# Also supports: pink, brown
python scripts/audio_toolkit.py generate noise --type pink --duration 10 -o pink_noise.mp3
```

#### Pad / Chord Generation
Generate multi-note ambient pads from musical note names. Useful for background music beds.
```bash
# C minor chord pad for 10 seconds
python scripts/audio_toolkit.py generate pad --notes C3,Eb3,G3 --duration 10 -o cmin.mp3
# Extended chord
python scripts/audio_toolkit.py generate pad --notes C3,E3,G3,B3 --duration 15 -o cmaj7.mp3
```

Supported note names: C2 through B5 with sharps/flats (e.g. C#3, Bb4). Common chords:
- Major: C3,E3,G3 | Minor: C3,Eb3,G3 | Diminished: C3,Eb3,Gb3
- Major 7th: C3,E3,G3,B3 | Minor 7th: C3,Eb3,G3,Bb3
- Power chord: C3,G3 | Octave: C3,C4

### Video-Audio Integration

#### Extract Audio from Video
```bash
# Pull the audio track out as a standalone file
python scripts/audio_toolkit.py extract video.mp4 -o audio.wav
```

#### Replace Audio in Video
```bash
# Swap the video's audio track entirely
python scripts/audio_toolkit.py replace video.mp4 --audio new_music.mp3 -o video_new_audio.mp4
```

#### Sync Audio to Video with Mixing
The most powerful video-audio operation. Adds an audio track alongside the existing video audio with offset and level control.
```bash
# Add background music starting 0.5s in, mixed at 30% of original
python scripts/audio_toolkit.py sync video.mp4 --audio bgm.mp3 --offset 0.5 --mix 0.3 -o final.mp4
```

Typical sync workflows:
- Background music under voiceover: `--mix 0.2` to `--mix 0.4`
- Sound effect at timestamp: `--offset <seconds> --mix 0.8`
- Replace original audio but keep 10% for ambience: `--mix 0.1`

### Audio Visualisation

#### Waveform
Generates a PNG showing the amplitude envelope over time. Useful for spotting silence, clipping, and level issues.
```bash
python scripts/audio_toolkit.py waveform podcast.mp3 -o waveform.png
```

#### Spectrogram
Generates a PNG showing frequency content over time. Useful for identifying noise, bandwidth issues, and frequency balance.
```bash
python scripts/audio_toolkit.py spectrogram podcast.mp3 -o spectrogram.png
```

### Common Audio Workflows

**Podcast production:**
```bash
# 1. Normalise levels
python scripts/audio_toolkit.py edit normalise raw.wav -o /tmp/step1.wav
# 2. Trim intro/outro silence
python scripts/audio_toolkit.py edit trim /tmp/step1.wav --start 00:00:03 --end 00:45:00 -o /tmp/step2.wav
# 3. Fade in/out
python scripts/audio_toolkit.py edit fade /tmp/step2.wav --in 1.5 --out 2 -o /tmp/step3.wav
# 4. Convert to MP3 for distribution
python scripts/audio_toolkit.py edit convert /tmp/step3.wav --format mp3 --bitrate 192 -o podcast_final.mp3
rm /tmp/step*.wav
```

**Video soundtrack replacement:**
```bash
# 1. Extract original audio for reference
python scripts/audio_toolkit.py extract video.mp4 -o /tmp/original.wav
# 2. Prepare new audio (normalise + trim to match video duration)
python scripts/audio_toolkit.py edit normalise new_music.mp3 -o /tmp/music_norm.mp3
python scripts/audio_toolkit.py edit trim /tmp/music_norm.mp3 --end 00:02:30 -o /tmp/music_trimmed.mp3
# 3. Fade the new music
python scripts/audio_toolkit.py edit fade /tmp/music_trimmed.mp3 --in 2 --out 3 -o /tmp/music_final.mp3
# 4. Replace audio in video
python scripts/audio_toolkit.py replace video.mp4 --audio /tmp/music_final.mp3 -o video_new.mp4
rm /tmp/original.wav /tmp/music_*.mp3
```

**Generate a custom background music bed:**
```bash
# 1. Generate a moody ambient pad
python scripts/audio_toolkit.py generate pad --notes C3,Eb3,G3,B3 --duration 30 -o /tmp/pad.mp3
# 2. Fade in and out
python scripts/audio_toolkit.py edit fade /tmp/pad.mp3 --in 3 --out 4 -o /tmp/pad_faded.mp3
# 3. Mix under video at 25%
python scripts/audio_toolkit.py sync video.mp4 --audio /tmp/pad_faded.mp3 --mix 0.25 -o video_with_music.mp4
rm /tmp/pad*.mp3
```

## Platform Export Presets

| Preset | Resolution | Framerate | Codec | Notes |
|--------|-----------|-----------|-------|-------|
| instagram-reel | 1080x1920 | 30 | H.264 | 9:16, max 90s, AAC audio |
| instagram-post | 1080x1080 | 30 | H.264 | 1:1 square, max 60s |
| youtube | 1920x1080 | 30 | H.264 | 16:9, high bitrate |
| youtube-shorts | 1080x1920 | 30 | H.264 | 9:16, max 60s |
| tiktok | 1080x1920 | 30 | H.264 | 9:16, max 10min |
| twitter | 1280x720 | 30 | H.264 | 16:9, max 2:20 |
| facebook | 1280x720 | 30 | H.264 | 16:9 or 1:1 |
| telegram | 1280x720 | 30 | H.264 | Optimised for streaming |

## Cloud API Integration (Optional, Paid)

These require API keys configured in environment variables.

### Runway ML
- `RUNWAY_API_KEY` — Generative video (text-to-video, image-to-video, video-to-video)
- Use for: AI style transfer, B-roll generation, background generation
- `python scripts/video_toolkit.py cloud runway --help`

### Shotstack
- `SHOTSTACK_API_KEY` — Cloud rendering API
- Use for: Template-driven production, data-driven personalisation, complex multi-track compositions
- `python scripts/video_toolkit.py cloud shotstack --help`

## Sourcing Free Stock Footage

When the user asks to download footage for editing:

- **Pexels and Pixabay** block automated access (Cloudflare challenge) — do not use
- **Coverr** (coverr.co) works well. CDN pattern: `https://cdn.coverr.co/videos/coverr-{slug}/720p.mp4`
- To find slugs: browse the search page, then extract video source URLs from the DOM via browser console:
  ```javascript
  document.querySelectorAll('video source').forEach(v => console.log(v.src))
  ```
- Slugs are derived from the video title (e.g., "Twilight City Call" → `coverr-twilight-city-call`)
- If a slug 404s, try alternative forms or extract from the page's `__NEXT_DATA__` JSON
- All Coverr footage is free for commercial use, no attribution required

## Building Montages with Crossfade Transitions

The `edit concat` command joins clips end-to-end without transitions. For crossfades, use ffmpeg's `xfade` filter chain directly:

```bash
# 5 clips with 0.8s crossfade transitions
ffmpeg -y \
  -i n0.mp4 -i n1.mp4 -i n2.mp4 -i n3.mp4 -i n4.mp4 \
  -filter_complex "\
    [0:v][1:v]xfade=transition=fadeblack:duration=0.8:offset=4.2[v01];\
    [v01][2:v]xfade=transition=slideleft:duration=0.8:offset=8.4[v12];\
    [v12][3:v]xfade=transition=dissolve:duration=0.8:offset=15.6[v23];\
    [v23][4:v]xfade=transition=fadeblack:duration=0.8:offset=20.8[v34]" \
  -map "[v34]" -c:v libx264 -preset medium output.mp4
```

Offset formula for xfade N (0-indexed):
```
offset_N = sum(clip_durations[0..N+1]) - (N+1) * transition_duration
```

Available transitions: `fade`, `fadeblack`, `dissolve`, `slideleft`, `slideright`, `wipeleft`, `wiperight`, `circlecrop`, `radial`, and many more.

**Important**: MoviePy 2.x removed `crossfadein`/`crossfadeout` — use ffmpeg xfade instead.

## Generating Synthetic Audio Beds

When no music file is available, generate a moody ambient pad with ffmpeg:

```bash
ffmpeg -y \
  -f lavfi -i "sine=frequency=130.81:duration=30,lowpass=f=800,volume=0.15" \
  -f lavfi -i "sine=frequency=155.56:duration=30,lowpass=f=800,volume=0.12" \
  -f lavfi -i "sine=frequency=196.00:duration=30,lowpass=f=800,volume=0.10" \
  -filter_complex "\
    [0:a][1:a][2:a]amix=inputs=3:duration=longest,\
    afade=t=in:st=0:d=2,afade=t=out:st=27:d=3,\
    lowpass=f=400,volume=0.5[a]" \
  -map "[a]" -c:a aac -b:a 128k ambient.m4a
```

Or use the audio toolkit's pad generator for a simpler approach:
```bash
python scripts/audio_toolkit.py generate pad --notes C3,Eb3,G3 --duration 30 -o ambient.mp3
python scripts/audio_toolkit.py edit fade ambient.mp3 --in 2 --out 3 -o ambient_faded.mp3
```

Useful chord frequencies (Hz): C3=130.81, Eb3=155.56, G3=196.00, C4=261.63, E4=329.63, G4=392.00.

## Text Overlay Fade Effects

ffmpeg `drawtext` supports animated alpha for smooth text fade-in/fade-out:

```
drawtext=text='TITLE':fontsize=72:fontcolor=white:
  borderw=3:bordercolor=black@0.7:
  x=(w-text_w)/2:y=(h-text_h)/2:
  enable='between(t,0.5,3.0)':
  alpha='if(lt(t,1.5),(t-0.5)/1,if(gt(t,2.5),(3.0-t)/0.5,1))'
```

The `alpha` expression: fades in from t=0.5 to t=1.5, holds at 1.0, fades out from t=2.5 to t=3.0.

## Tips and Pitfalls

- Always analyze before editing — check duration, resolution, and audio properties first
- ffmpeg operations on large files can be slow on CPU — warn the user if the video is long
- Whisper transcription is the slowest operation — use the "base" model for speed, "medium" for accuracy
- Background removal on video is very slow on CPU — process frame by frame, warn about time
- When concatenating video clips, all clips must have the same resolution and framerate — transcode first if needed
- When concatenating audio files, sample rate and channel count must match — convert first if needed
- Temp files can be large — clean up after each edit pipeline
- For messaging platform delivery, files may have size limits (Telegram: 50MB) — consider splitting or reducing quality
- The `fps=1` frame extraction filter sometimes only extracts 2 frames on certain codecs — use `select=not(mod(n\,50))` with `-vsync vfr` instead for reliable evenly-spaced keyframe extraction
- Normalise audio before mixing to avoid clipping and inconsistent levels
- Always verify output metadata (duration, codec, channels) matches expectations after audio edits
- Use `-v` / `--verbose` for detailed ffmpeg output during debugging

## Verification

After every edit, confirm the output is correct:

1. **Run `info analyze` on the output file** and compare against expected values:
   - Duration matches expected length (±1s for trim/concat operations)
   - Resolution and framerate match the target or source
   - Audio codec, channels, and sample rate are correct
   - File size is reasonable for the duration (typically 5-50 MB/min for H.264)
   - RMS level is in a healthy range (-20 to -6 dB for normalised audio)

2. **Visual inspection** (if agent has vision capability):
   - Generate a contact sheet: `python scripts/video_toolkit.py frames grid OUTPUT -o /tmp/review.jpg`
   - Check for black frames at edit points, correct framing, readable captions
   - For audio: generate waveform and spectrogram PNGs and inspect them

3. **For agents without vision**, extract metadata and deliver review assets:
   - Extract key frames and list them (timestamps confirm continuity)
   - Deliver contact sheet, waveform, and spectrogram to the user for manual confirmation

4. **If issues are found**, fix and re-verify before delivering the final file.

## Related Capabilities

This toolkit is part of a family of complementary skills. Each produces MP4 output that chains directly into the video and audio toolkits.

### ASCII Video (creative/ascii-video)

Terminal-style character art video with audio-reactive visualisers, generative animations, and shader effects.

**What it adds:**
- Video-to-ASCII conversion (recreates footage using text characters)
- Audio-reactive music visualisers (FFT-driven rings, spirals, tunnels)
- Generative ASCII art animations (particles, noise fields, cellular automata)
- Hybrid mode: ASCII overlay composited onto regular video
- Rich shader pipeline: CRT glow, bloom, chromatic aberration, glitch, retro scanlines

**Integration workflows:**

1. ASCII visualiser as B-roll in a montage:
   ```bash
   # Generate ASCII visualiser from audio
   python ascii_project.py  # outputs ascii_visualiser.mp4
   
   # Combine with regular footage using this toolkit
   python scripts/video_toolkit.py edit concat footage.mp4 ascii_visualiser.mp4 -o combined.mp4
   python scripts/audio_toolkit.py sync combined.mp4 --audio music.mp3 --mix 0.4 -o final.mp4
   ```

2. ASCII title sequence for a video:
   ```bash
   # Generate ASCII title animation (manim or ascii-video)
   # Then concat as intro
   python scripts/video_toolkit.py edit concat ascii_intro.mp4 main_content.mp4 -o with_intro.mp4
   ```

3. Audio-reactive background layer:
   ```bash
   # Use audio_toolkit to extract and prep audio
   python scripts/audio_toolkit.py extract video.mp4 --format wav -o audio.wav
   # Feed to ASCII video skill for visualiser generation
   # Overlay visualiser on original video with blend
   ```

### Manim Video (creative/manim-video)

Mathematical and technical animations — 3Blue1Brown-style explainers, algorithm visualisations, equation derivations, architecture diagrams.

**What it adds:**
- Animated mathematical proofs and derivations (LaTeX-rendered equations)
- Algorithm and data structure visualisations
- Animated architecture/system diagrams
- 3D surface and parametric curve visualisations
- Data stories with animated charts and counters

**Integration workflows:**

1. Manim explainer segment in a larger video:
   ```bash
   # Render Manim scene to MP4
   manim -qh script.py Scene1_Introduction Scene2_CoreConcept
   
   # Stitch scenes together
   ffmpeg -f concat -safe 0 -i concat.txt -c copy manim_explainer.mp4
   
   # Add narration audio bed
   python scripts/audio_toolkit.py generate pad --notes C3,E4,G4 --duration 60 --lowpass 350 -o bg_music.mp3
   python scripts/audio_toolkit.py sync manim_explainer.mp4 --audio bg_music.mp3 --mix 0.2 --duck -o explainer_with_music.mp4
   
   # Concat with other footage
   python scripts/video_toolkit.py edit concat intro.mp4 explainer_with_music.mp4 outro.mp4 -o final.mp4
   ```

2. Manim diagram as overlay in a screen recording:
   ```bash
   # Render Manim diagram with transparent background (Manim supports -t flag)
   # Then composite onto footage using ffmpeg overlay filter
   ```

3. Full production pipeline with all three skills:
   ```bash
   # 1. Generate ASCII title sequence (ascii-video skill)
   # 2. Render Manim technical content (manim-video skill)
   # 3. Combine with stock footage (this toolkit — trim, concat, crossfade)
   # 4. Add generated ambient music (audio_toolkit pad generation)
   # 5. Normalise and export for platform (audio_toolkit + video_toolkit export)
   ```

### Chaining Pattern

All three skills produce MP4 output. The general chaining pattern is:

```
SOURCE(S) → GENERATE/RENDER → POST-PROCESS → ASSEMBLE → EXPORT
```

1. **Generate**: ASCII video, Manim scenes, or stock footage downloads
2. **Post-process**: Colour grade (video_toolkit enhance), normalise audio (audio_toolkit normalise), trim to length
3. **Assemble**: Concat with transitions (video_toolkit concat or ffmpeg xfade), sync audio (audio_toolkit sync)
4. **Export**: Platform preset (video_toolkit export), or final encode with custom settings

Each skill is independently useful. Together they cover the full spectrum from artistic (ASCII) through technical (Manim) to conventional production editing (this toolkit).
