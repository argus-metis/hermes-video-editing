# Hermes Video & Audio Editing Skill

A comprehensive video and audio editing toolkit for [Hermes Agent](https://github.com/nousresearch/hermes-agent) — edit videos and audio by describing what you want in natural language.

Built entirely on free, open-source tools. No paid subscriptions required.

## Features

### Video Editing — Core (Free, Local)
- **Trim & cut** — Remove sections by timestamp
- **Concatenate** — Join multiple clips
- **Speed change** — Speed up or slow down footage
- **Audio mixing** — Add music beds, replace audio, normalise levels
- **Text overlays** — Burn titles, lower-thirds, watermarks
- **Platform export** — One-command export for Instagram, YouTube, TikTok, Twitter, Telegram

### Video Editing — AI-Powered (Free, Local)
- **Auto-captioning** — Whisper transcription with subtitle burn-in
- **Silence removal** — Detect and cut silent sections (Silero VAD + ffmpeg fallback)
- **Scene detection** — Automatically find cuts and scene changes (PySceneDetect)
- **Smart reframing** — Face-tracking crop for different aspect ratios (OpenCV)
- **Stabilisation** — Fix shaky footage (ffmpeg vidstab)
- **Background removal** — AI-powered background removal from video
- **Colour enhancement** — Auto brightness, contrast, and denoise

### Audio Editing — Core (Free, Local)
- **Trim & fade** — Cut sections, apply fade-in/fade-out
- **Normalise** — Broadcast-standard loudness normalisation (EBU R128, two-pass)
- **Speed & pitch** — Change tempo or shift pitch independently
- **Volume** — Adjust level by multiplier or dB
- **Mix** — Overlay multiple tracks with per-track level control
- **Concatenate** — Join audio files end-to-end
- **Format conversion** — Convert between MP3, WAV, AAC, OGG, FLAC, M4A, Opus

### Audio Generation
- **Tones** — Generate sine, square, sawtooth, or triangle wave tones
- **Noise** — Generate white, pink, brown, blue, or violet noise
- **Ambient pads** — Synthesise chord pads from note names (e.g. C3,Eb3,G3)

### Audio-Video Bridge
- **Extract audio** — Pull audio from video in any format
- **Replace audio** — Swap the audio track in a video file
- **Sync & mix** — Layer audio onto video with offset, mixing, and optional ducking

### Audio Visualisation
- **Waveform** — Generate a waveform image of an audio file
- **Spectrogram** — Generate a frequency spectrogram image

### Visual Review
- **Frame extraction** — Sample frames at intervals for quality control
- **Thumbnail grid** — Generate contact sheets for at-a-glance review
- **AI vision inspection** — Integration with Hermes vision tools to verify edits

### Cloud APIs (Optional, Paid)
- **Runway ML** — Generative video, style transfer, B-roll generation
- **Shotstack** — Cloud rendering, template-driven production

## Installation

### Quick Start

```bash
# Install dependencies
bash install.sh

# Or core only (no AI tools)
bash install.sh --core

# Check what's installed
bash install.sh --check
```

### Manual Install

```bash
# System dependency
sudo apt-get install ffmpeg

# Core Python packages
pip install moviepy ffmpeg-python opencv-python-headless Pillow numpy

# Optional AI tools
pip install openai-whisper          # Transcription
pip install scenedetect-headless    # Scene detection
pip install torch                   # Silero VAD
pip install backgroundremover       # Background removal
```

### As a Hermes Skill

Copy or symlink this directory to your Hermes skills folder:

```bash
ln -s /path/to/hermes-video-editing ~/.hermes/skills/video-editing
```

## Usage

The toolkit provides two CLI scripts that Hermes calls based on your natural language instructions:

- `scripts/video_toolkit.py` — All video operations
- `scripts/audio_toolkit.py` — All audio operations

### Video Examples

```
You: "Trim the first 30 seconds off this video"
→ python scripts/video_toolkit.py edit trim input.mp4 --start 00:00:30 -o output.mp4

You: "Remove the silences and add subtitles"
→ python scripts/video_toolkit.py silence remove input.mp4 -o /tmp/step1.mp4
→ python scripts/video_toolkit.py caption burn /tmp/step1.mp4 -o output.mp4

You: "Make this vertical for TikTok"
→ python scripts/video_toolkit.py enhance reframe input.mp4 --target 9:16 -o output.mp4

You: "Stabilise the shaky footage and export for YouTube"
→ python scripts/video_toolkit.py enhance stabilise input.mp4 -o /tmp/step1.mp4
→ python scripts/video_toolkit.py edit export /tmp/step1.mp4 --preset youtube -o output.mp4

You: "What's in this video?"
→ python scripts/video_toolkit.py info analyze input.mp4
→ python scripts/video_toolkit.py frames grid input.mp4 -o grid.jpg
```

### Audio Examples

```
You: "Normalise this audio to broadcast standard"
→ python scripts/audio_toolkit.py edit normalise input.mp3 -o output.mp3

You: "Fade in 2 seconds and fade out 3 seconds"
→ python scripts/audio_toolkit.py edit fade input.mp3 --fade-in 2 --fade-out 3 -o output.mp3

You: "Extract the audio from this video as WAV"
→ python scripts/audio_toolkit.py extract input.mp4 --format wav -o audio.wav

You: "Add background music to the video with ducking"
→ python scripts/audio_toolkit.py sync input.mp4 --audio music.mp3 --mix 0.3 --duck -o output.mp4

You: "Generate a 10-second ambient C minor pad"
→ python scripts/audio_toolkit.py generate pad --notes C3,Eb3,G3 --duration 10 -o pad.mp3

You: "Mix a voiceover onto background music"
→ python scripts/audio_toolkit.py edit mix music.mp3 --overlay voice.wav --overlay-level 0.9 -o mixed.mp3

You: "Show me the waveform of this track"
→ python scripts/audio_toolkit.py waveform input.mp3 -o waveform.png
```

### Video Commands

```
info analyze INPUT                          Analyze video properties
edit trim INPUT --start T --end T           Trim between timestamps
edit concat FILE1 FILE2 [...]               Concatenate clips
edit speed INPUT --factor N                 Change speed (1.5 = 50% faster)
edit audio INPUT --audio FILE --mix N       Mix or replace audio
edit text INPUT --text "Title" --at T       Burn text overlay
edit export INPUT --preset NAME             Export with platform preset
caption generate INPUT                      Generate SRT subtitles
caption burn INPUT                          Transcribe and burn subtitles
silence remove INPUT                        Remove silent sections
scenes detect INPUT                         Detect scene changes
frames extract INPUT --interval N           Extract frames for review
frames grid INPUT                           Generate thumbnail grid
enhance stabilise INPUT                     Stabilise shaky footage
enhance bg-remove INPUT                     Remove background
enhance colour INPUT                        Auto colour enhance
enhance reframe INPUT --target 9:16         Smart reframe with face tracking
cloud runway image-to-video ...             Runway ML API (paid)
cloud shotstack ...                         Shotstack API (paid)
```

### Audio Commands

```
info analyze INPUT                          Analyze audio properties
edit trim INPUT --start T --end T           Trim between timestamps
edit fade INPUT --in N --out N              Apply fade-in and/or fade-out
edit normalise INPUT [--target -16]         Normalise loudness (EBU R128)
edit speed INPUT --factor N                 Change speed (affects duration)
edit pitch INPUT --semitones N              Shift pitch without speed change
edit volume INPUT --level N [--db]          Adjust volume (multiplier or dB)
edit mix INPUT --overlay FILE [--overlay-level N]  Mix tracks
edit concat FILE1 FILE2 [...]               Concatenate audio files
edit convert INPUT --format FMT             Convert between audio formats
generate tone --frequency 440 --duration 5  Generate a tone
generate noise --type white --duration 3    Generate coloured noise
generate pad --notes C3,Eb3,G3 --duration 10   Generate ambient chord pad
extract VIDEO [--format mp3]                Extract audio from video
replace VIDEO --audio FILE                  Replace audio in video
sync VIDEO --audio FILE [--offset N] [--duck]   Layer audio onto video
waveform INPUT                              Generate waveform image
spectrogram INPUT                           Generate spectrogram image
```

### Platform Presets

| Preset | Resolution | Notes |
|--------|-----------|-------|
| instagram-reel | 1080x1920 | 9:16, max 90s |
| instagram-post | 1080x1080 | 1:1 square, max 60s |
| youtube | 1920x1080 | 16:9, high bitrate |
| youtube-shorts | 1080x1920 | 9:16, max 60s |
| tiktok | 1080x1920 | 9:16, max 10min |
| twitter | 1280x720 | 16:9, max 2:20 |
| facebook | 1280x720 | 16:9 or 1:1 |
| telegram | 1280x720 | Streaming-optimised |

## Architecture

```
hermes-video-editing/
├── SKILL.md                    Skill definition (loaded by Hermes)
├── install.sh                  Dependency installer
├── scripts/
│   ├── video_toolkit.py        Video CLI toolkit (all video operations)
│   └── audio_toolkit.py        Audio CLI toolkit (all audio operations)
├── templates/
│   └── platforms.yaml          Export preset definitions
└── references/
    └── ffmpeg_reference.md     FFmpeg quick reference
```

## Model Compatibility

This skill is designed to work with any AI model supported by Hermes Agent, including both vision-capable and text-only models. Here is how the experience adapts:

### Models with Vision (e.g. GPT-4o, Claude 3.5 Sonnet, Gemini Pro Vision)

When paired with a model that supports image understanding, the skill provides a full visual review loop:

- Frame extraction and thumbnail grids are sent to the model for visual inspection
- The model can verify caption positioning, colour grading, framing, and artifacts
- Visual quality control happens automatically after each edit pipeline
- Waveform and spectrogram images can be inspected to verify audio properties

This gives the highest-quality results since the model can see the output and request corrections.

### Models without Vision (e.g. GPT-4o-mini-text, Claude 3 Haiku, Llama 3)

Text-only models work with all editing operations through structured output analysis:

- `info analyze` provides rich text metadata (duration, codec, resolution, channels, bit depth, loudness)
- Every command returns a clear one-line status with file path, duration, and key properties
- Frame extraction still runs — the file paths are reported so the user can review them manually
- Audio analysis (RMS level, duration, format) is fully text-based

For audio tasks in particular, text-only models are equally effective since the output is inherently non-visual — properties like loudness, duration, and codec are always reported as text.

### Recommendations

| Task | Vision Model | Text-Only Model |
|------|:-----------:|:---------------:|
| Trim, cut, concat | Great | Great |
| Audio editing | Great | Great |
| Caption positioning | Visual verification | Manual review needed |
| Colour/visual grading | Visual verification | Manual review needed |
| Smart reframing | Visual verification | Metadata + manual review |
| Audio normalisation | Great | Great |
| Silence removal | Great | Great |

All functional operations work identically regardless of model. The difference is in quality assurance — vision models can autonomously verify visual output, while text-only models rely on metadata and the user's own review.

## Sibling Skills

This toolkit pairs with two other creative skills that produce MP4 output. Chain them together for full-spectrum production.

### ascii-video

Terminal-style character art video with audio-reactive visualisers, generative animations, and shader effects (CRT glow, bloom, glitch). Use for: retro aesthetics, music visualisers, title sequences, ASCII overlays on footage.

```
audio.wav → ascii-video → visualiser.mp4 → video_toolkit concat → final.mp4
```

### manim-video

3Blue1Brown-style mathematical and technical animations. Animated proofs, algorithm visualisations, architecture diagrams, data stories. Use for: explainer videos, technical content, educational material.

```
concept → manim render → explainer.mp4 → audio_toolkit sync → video_toolkit export → final.mp4
```

### Full Pipeline Example

Combine all three for a complete production:

1. **Generate** — ASCII title sequence (ascii-video) + Manim technical content (manim-video)
2. **Post-process** — Colour grade and trim (video_toolkit), normalise audio (audio_toolkit)
3. **Assemble** — Concat with crossfade transitions (video_toolkit + ffmpeg xfade), sync audio with ducking (audio_toolkit)
4. **Export** — Platform preset (video_toolkit export)

Each skill works standalone. Together they cover artistic (ASCII) through technical (Manim) to conventional production editing (this toolkit).

## Requirements

- Python 3.10+
- ffmpeg (system package)
- See `install.sh` for Python package list

## License

MIT License — see [LICENSE](LICENSE).
