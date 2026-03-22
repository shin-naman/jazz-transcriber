"""
separate.py — Wrapper around Demucs for source separation.

Takes an audio file and splits it into stems:
  - vocals
  - drums
  - bass
  - other (this is usually where solo instruments end up)

Usage:
    from separate import separate_audio
    stems = separate_audio("my_jazz_track.wav")
    # stems is a dict: {"vocals": path, "drums": path, "bass": path, "other": path}
"""

import subprocess
import os
from pathlib import Path


# Available Demucs models — htdemucs is the default and usually best
DEMUCS_MODELS = {
    "htdemucs": "Hybrid Transformer Demucs (default, best quality)",
    "htdemucs_ft": "Fine-tuned version (slightly better, slower)",
    "mdx_extra": "MDX architecture (alternative, worth comparing)",
}

# The four stems Demucs always outputs
STEMS = ["vocals", "drums", "bass", "other"]


def separate_audio(
    input_path: str,
    output_dir: str = "separated",
    model: str = "htdemucs",
    device: str = "cpu",  # change to "cuda" if you have a GPU
) -> dict[str, str]:
    """
    Separate an audio file into stems using Demucs.

    Args:
        input_path: Path to the input audio file (wav, mp3, flac, etc.)
        output_dir: Directory to save separated stems
        model: Demucs model to use (see DEMUCS_MODELS)
        device: "cpu" or "cuda"

    Returns:
        Dictionary mapping stem names to their file paths.
        Example: {"vocals": "separated/htdemucs/song/vocals.wav", ...}
    """
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Audio file not found: {input_path}")

    if model not in DEMUCS_MODELS:
        raise ValueError(
            f"Unknown model '{model}'. Choose from: {list(DEMUCS_MODELS.keys())}"
        )

    print(f"Separating '{input_path.name}' with {model}...")
    print(f"  Device: {device}")
    print(f"  Output: {output_dir}/")

    # Run Demucs as a subprocess
    # This is the simplest approach and avoids importing Demucs internals
    cmd = [
        "python", "-m", "demucs",
        "--name", model,
        "--out", output_dir,
        "--device", device,
        str(input_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Demucs error output:\n{result.stderr}")
        raise RuntimeError(f"Demucs failed with exit code {result.returncode}")

    # Demucs saves stems to: output_dir/model_name/track_name/stem.wav
    track_name = input_path.stem
    stems_dir = Path(output_dir) / model / track_name

    # Verify all stems were created
    stem_paths = {}
    for stem in STEMS:
        stem_path = stems_dir / f"{stem}.wav"
        if not stem_path.exists():
            raise FileNotFoundError(f"Expected stem not found: {stem_path}")
        stem_paths[stem] = str(stem_path)

    print(f"Separation complete! Stems saved to {stems_dir}/")
    for stem, path in stem_paths.items():
        print(f"  {stem}: {path}")

    return stem_paths


def list_models():
    """Print available Demucs models."""
    print("Available Demucs models:")
    for name, description in DEMUCS_MODELS.items():
        print(f"  {name}: {description}")


# ── Quick test ──────────────────────────────────────────────────
# Run this file directly to test separation on a sample file:
#   python src/separate.py path/to/audio.wav
#
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python src/separate.py <audio_file> [model]")
        print()
        list_models()
        sys.exit(1)

    audio_file = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else "htdemucs"

    stems = separate_audio(audio_file, model=model_name)
    print("\nDone! You can now transcribe a stem with:")
    print(f"  python src/pitch_detect.py {stems['other']}")
