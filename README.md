# Jazz Solo Transcriber 🎷

**AI-powered audio-to-MIDI transcription for jazz musicians.**

Upload a jazz recording → isolate the solo instrument → get a MIDI transcription + piano roll visualization.

Built with [Demucs](https://github.com/facebookresearch/demucs) (Meta) for source separation and [Basic Pitch](https://github.com/spotify/basic-pitch) (Spotify) for audio-to-MIDI transcription.

## Why This Exists

Learning jazz solos by ear is one of the best ways to grow as a musician — but it's slow. This tool automates the tedious part (figuring out the notes) so you can focus on the musical part (understanding *why* those notes work).

## Features

- **Source separation**: Isolate a solo instrument from a full band recording using Demucs
- **Audio-to-MIDI**: Transcribe the isolated audio to MIDI using Basic Pitch
- **Piano roll visualization**: See the transcribed notes displayed as a piano roll
- **MIDI download**: Export the transcription as a `.mid` file for use in any DAW or notation software
- **Web interface**: Simple Streamlit app — upload, click, download

## Getting Started

### Prerequisites

- Python 3.10+
- A machine with at least 4GB RAM (GPU optional but speeds up Demucs)
- `ffmpeg` installed and on your PATH

### Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/jazz-transcriber.git
cd jazz-transcriber

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Quick Start (CLI)

```bash
# Transcribe a jazz recording
python src/transcribe.py input.wav --instrument other --output solo.mid
```

### Quick Start (Web App)

```bash
streamlit run src/app.py
```

## Project Structure

```
jazz-transcriber/
├── src/
│   ├── transcribe.py      # Core pipeline: separation → transcription → MIDI
│   ├── separate.py        # Demucs source separation wrapper
│   ├── pitch_detect.py    # Basic Pitch transcription wrapper
│   ├── visualize.py       # Piano roll visualization
│   └── app.py             # Streamlit web interface
├── tests/                 # Unit tests
├── examples/              # Example outputs and screenshots
├── docs/                  # Technical writeup and evaluation notes
├── requirements.txt
├── CONTRIBUTING.md
└── README.md
```

## Tech Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| Source Separation | Demucs (Meta) | Isolate instruments from a mix |
| Audio-to-MIDI | Basic Pitch (Spotify) | Neural pitch detection → MIDI |
| MIDI Processing | pretty_midi / music21 | Inspect and convert MIDI |
| Visualization | matplotlib | Piano roll display |
| Web Interface | Streamlit | Upload, process, download |

## Evaluation

We evaluated transcription quality across different jazz styles and instruments. See [`docs/evaluation.md`](docs/evaluation.md) for detailed findings.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions and workflow.

## License

MIT

## Acknowledgments

- [Demucs](https://github.com/facebookresearch/demucs) by Meta Research
- [Basic Pitch](https://github.com/spotify/basic-pitch) by Spotify
- Built as an undergraduate research portfolio project, Spring 2026
