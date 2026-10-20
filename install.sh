#!/usr/bin/env bash
# install.sh — Install dependencies for the Video Editing skill
set -euo pipefail

CORE_DEPS="moviepy ffmpeg-python opencv-python-headless Pillow numpy"
# scenedetect >= 0.7 depends on the GUI opencv-python, which would install a
# second cv2 over opencv-python-headless; scenedetect-headless avoids that.
AI_DEPS="openai-whisper scenedetect-headless torch torchaudio backgroundremover rembg"

# pip package name -> module to import when checking whether it is installed
module_for() {
    case "$1" in
        opencv-python-headless) echo cv2 ;;
        Pillow) echo PIL ;;
        ffmpeg-python) echo ffmpeg ;;
        openai-whisper) echo whisper ;;
        scenedetect-headless) echo scenedetect ;;
        *) echo "$1" | sed 's/\[.*//;s/-/_/g' ;;
    esac
}

check_only=false
core_only=false

for arg in "$@"; do
    case "$arg" in
        --check) check_only=true ;;
        --core) core_only=true ;;
        --help|-h)
            echo "Usage: bash install.sh [--core] [--check]"
            echo "  --core   Install only core dependencies (no AI tools)"
            echo "  --check  Check what's installed without installing"
            exit 0
            ;;
    esac
done

echo "=== Video Editing Toolkit — Dependency Installer ==="
echo ""

# Check ffmpeg
if command -v ffmpeg &>/dev/null; then
    echo "[OK] ffmpeg: $(ffmpeg -version | head -1)"
else
    echo "[MISSING] ffmpeg — install with: sudo apt-get install ffmpeg"
fi

# Check Python
if command -v python3 &>/dev/null; then
    echo "[OK] python3: $(python3 --version)"
else
    echo "[MISSING] python3"
    exit 1
fi

echo ""
echo "--- Core Dependencies ---"
for pkg in $CORE_DEPS; do
    mod=$(module_for "$pkg")
    if python3 -c "import $mod" 2>/dev/null; then
        echo "[OK] $pkg"
    else
        if [ "$check_only" = true ]; then
            echo "[MISSING] $pkg"
        else
            echo "[INSTALLING] $pkg"
            pip install "$pkg" 2>&1 | tail -1
        fi
    fi
done

if [ "$core_only" = false ]; then
    echo ""
    echo "--- AI Dependencies (Optional) ---"
    for pkg in $AI_DEPS; do
        mod=$(module_for "$pkg")
        if python3 -c "import $mod" 2>/dev/null; then
            echo "[OK] $pkg"
        else
            if [ "$check_only" = true ]; then
                echo "[MISSING] $pkg (optional)"
            else
                echo "[INSTALLING] $pkg"
                pip install "$pkg" 2>&1 | tail -1
            fi
        fi
    done
fi

echo ""
echo "--- Cloud API Support ---"
for var in RUNWAY_API_KEY SHOTSTACK_API_KEY; do
    if [ -n "${!var:-}" ]; then
        echo "[OK] $var is set"
    else
        echo "[--] $var not set (optional — only needed for cloud features)"
    fi
done

echo ""
echo "Done."
