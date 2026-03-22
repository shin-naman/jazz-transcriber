# Contributing to Jazz Solo Transcriber

## Team Setup

We're a two-person team. Here's how we work together without stepping on each other's toes.

### First-Time Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/jazz-transcriber.git
cd jazz-transcriber

# 2. Create your virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install ffmpeg (needed for audio processing)
# macOS:   brew install ffmpeg
# Ubuntu:  sudo apt install ffmpeg
# Windows: download from https://ffmpeg.org/download.html

# 5. Verify everything works
python -c "import demucs; print('Demucs OK')"
python -c "import basic_pitch; print('Basic Pitch OK')"
```

### Git Workflow

We use a simple **branch-per-feature** workflow:

```bash
# 1. Always start from main
git checkout main
git pull origin main

# 2. Create a branch for your work
git checkout -b feature/piano-roll-viz    # descriptive name

# 3. Do your work, commit often
git add .
git commit -m "Add piano roll visualization using matplotlib"

# 4. Push your branch
git push origin feature/piano-roll-viz

# 5. Open a Pull Request on GitHub
#    - Your partner reviews it (even a quick look is fine)
#    - Merge into main once approved

# 6. After merge, clean up
git checkout main
git pull origin main
git branch -d feature/piano-roll-viz
```

### Branch Naming

- `feature/` — new functionality (e.g., `feature/streamlit-ui`)
- `fix/` — bug fixes (e.g., `fix/midi-timing-offset`)
- `docs/` — documentation only (e.g., `docs/evaluation-notes`)
- `experiment/` — trying something that might not work (e.g., `experiment/sam-audio-comparison`)

### Who Works on What

To avoid merge conflicts, try to work on **different files**. A rough split:

| Area | Files |
|------|-------|
| Separation + pipeline | `src/separate.py`, `src/transcribe.py` |
| Transcription + viz | `src/pitch_detect.py`, `src/visualize.py` |
| Web app | `src/app.py` |
| Docs + evaluation | `docs/` |

Communicate on what you're working on — a quick text or message before starting is enough.

### Commit Messages

Keep them short and descriptive:
- ✅ `Add Demucs wrapper with stem selection`
- ✅ `Fix MIDI export dropping short notes`
- ❌ `update stuff`
- ❌ `changes`

### Adding Dependencies

If you need a new library:
1. Install it: `pip install <package>`
2. Update requirements: `pip freeze > requirements.txt`
3. Tell your partner so they can `pip install -r requirements.txt`

## Code Style

- Keep it simple. We're building a project, not a framework.
- Add comments for anything non-obvious.
- Use descriptive variable names (`isolated_audio` not `x`).
- Each file in `src/` should do one thing and do it well.
