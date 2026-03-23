#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  Jazz Solo Transcriber — Environment Setup Script
#  Run this from the project root: bash setup.sh
# ─────────────────────────────────────────────────────────────

set -e  # Exit on any error

echo "========================================"
echo "  Jazz Solo Transcriber — Setup"
echo "========================================"
echo ""

# ── 1. Check Python version ────────────────────────────────
echo "[1/6] Checking Python..."

# Try versioned binaries first (Homebrew on macOS installs these)
# then fall back to generic python3 / python
PYTHON=""
for candidate in python3.13 python3.12 python3.11 python3.10 python3 python; do
    if command -v "$candidate" &> /dev/null; then
        PY_MAJOR=$($candidate -c "import sys; print(sys.version_info.major)" 2>/dev/null)
        PY_MINOR=$($candidate -c "import sys; print(sys.version_info.minor)" 2>/dev/null)
        if [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -ge 10 ]; then
            PYTHON=$candidate
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "  ❌ Python 3.10+ not found!"
    echo ""
    echo "  Your system Python is too old. Install a newer version:"
    echo "    macOS:   brew install python@3.12"
    echo "    Ubuntu:  sudo apt install python3.12 python3.12-venv"
    echo "    Windows: https://www.python.org/downloads/"
    echo ""
    echo "  Then re-run this script."
    exit 1
fi

PY_VERSION=$($PYTHON --version 2>&1)
echo "  ✓ Found $PY_VERSION (using '$PYTHON')"

# ── 2. Check ffmpeg ─────────────────────────────────────────
echo ""
echo "[2/6] Checking ffmpeg..."

if command -v ffmpeg &> /dev/null; then
    FF_VERSION=$(ffmpeg -version 2>&1 | head -n1)
    echo "  ✓ $FF_VERSION"
else
    echo "  ❌ ffmpeg not found!"
    echo ""
    echo "  Install ffmpeg:"
    echo "    macOS:   brew install ffmpeg"
    echo "    Ubuntu:  sudo apt install ffmpeg"
    echo "    Windows: Download from https://ffmpeg.org/download.html"
    echo "             Then add to your PATH"
    echo ""
    echo "  After installing, re-run this script."
    exit 1
fi

# ── 3. Check Git ────────────────────────────────────────────
echo ""
echo "[3/6] Checking Git..."

if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    echo "  ✓ $GIT_VERSION"
else
    echo "  ❌ Git not found!"
    echo "  Install from https://git-scm.com/downloads"
    exit 1
fi

# ── 4. Create virtual environment ───────────────────────────
echo ""
echo "[4/6] Setting up virtual environment..."

if [ -d "venv" ]; then
    echo "  ⚠ venv/ already exists — skipping creation"
else
    $PYTHON -m venv venv
    echo "  ✓ Created virtual environment in venv/"
fi

# Activate it
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo "  ✓ Activated virtual environment"

# ── 5. Install dependencies ─────────────────────────────────
echo ""
echo "[5/6] Installing Python dependencies..."
echo "  (This may take a few minutes — Demucs and Basic Pitch pull in PyTorch)"
echo ""

pip install --upgrade pip --quiet
pip install -r requirements.txt

echo ""
echo "  ✓ All dependencies installed"

# ── 6. Verify everything works ──────────────────────────────
echo ""
echo "[6/6] Verifying installations..."

PASS=true

$PYTHON -c "import demucs; print('  ✓ Demucs')" 2>/dev/null || { echo "  ❌ Demucs failed to import"; PASS=false; }
$PYTHON -c "import basic_pitch; print('  ✓ Basic Pitch')" 2>/dev/null || { echo "  ❌ Basic Pitch failed to import"; PASS=false; }
$PYTHON -c "import pretty_midi; print('  ✓ pretty_midi')" 2>/dev/null || { echo "  ❌ pretty_midi failed to import"; PASS=false; }
$PYTHON -c "import music21; print('  ✓ music21')" 2>/dev/null || { echo "  ❌ music21 failed to import"; PASS=false; }
$PYTHON -c "import matplotlib; print('  ✓ matplotlib')" 2>/dev/null || { echo "  ❌ matplotlib failed to import"; PASS=false; }
$PYTHON -c "import streamlit; print('  ✓ Streamlit')" 2>/dev/null || { echo "  ❌ Streamlit failed to import"; PASS=false; }
$PYTHON -c "import soundfile; print('  ✓ soundfile')" 2>/dev/null || { echo "  ❌ soundfile failed to import"; PASS=false; }
$PYTHON -c "import librosa; print('  ✓ librosa')" 2>/dev/null || { echo "  ❌ librosa failed to import"; PASS=false; }

echo ""

if [ "$PASS" = true ]; then
    echo "========================================"
    echo "  ✅ Setup complete! You're ready to go."
    echo "========================================"
    echo ""
    echo "  Next steps:"
    echo "    1. Activate your venv each time you work:"
    echo "         source venv/bin/activate"
    echo "    2. Test separation on any audio file:"
    echo "         python src/separate.py your_track.wav"
    echo "    3. Test transcription:"
    echo "         python src/pitch_detect.py your_audio.wav"
    echo ""
else
    echo "========================================"
    echo "  ⚠ Some packages failed to install."
    echo "  Try running: pip install -r requirements.txt"
    echo "  If issues persist, check the error messages above."
    echo "========================================"
fi