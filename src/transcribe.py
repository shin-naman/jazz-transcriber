"""
transcribe.py — Main pipeline: audio → separation → transcription → MIDI

This is the core script that chains Demucs and Basic Pitch together.

Usage:
    python src/transcribe.py input.wav
    python src/transcribe.py input.wav --instrument other --output solo.mid
    python src/transcribe.py input.wav --skip-separation  # if audio is already isolated
"""

import argparse
from pathlib import Path
from separate import separate_audio, STEMS, DEMUCS_MODELS
from pitch_detect import transcribe_to_midi, DEFAULT_PARAMS


def run_pipeline(
    input_path: str,
    instrument: str = "other",
    output_path: str | None = None,
    skip_separation: bool = False,
    demucs_model: str = "htdemucs",
    device: str = "cpu",
    onset_threshold: float = DEFAULT_PARAMS["onset_threshold"],
    frame_threshold: float = DEFAULT_PARAMS["frame_threshold"],
    minimum_note_length: float = DEFAULT_PARAMS["minimum_note_length"],
) -> str:
    """
    Run the full transcription pipeline.

    Args:
        input_path: Path to input audio file
        instrument: Which stem to transcribe ("vocals", "drums", "bass", "other")
        output_path: Where to save the MIDI (auto-generated if None)
        skip_separation: If True, skip Demucs and transcribe the raw audio
        demucs_model: Which Demucs model to use
        device: "cpu" or "cuda"
        onset_threshold: Basic Pitch onset threshold
        frame_threshold: Basic Pitch frame threshold
        minimum_note_length: Minimum note length in ms

    Returns:
        Path to the output MIDI file.
    """
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    # Auto-generate output path
    if output_path is None:
        output_path = str(input_path.with_name(f"{input_path.stem}_{instrument}.mid"))

    print("=" * 60)
    print("  Jazz Solo Transcriber")
    print("=" * 60)
    print(f"  Input:      {input_path}")
    print(f"  Instrument: {instrument}")
    print(f"  Output:     {output_path}")
    print(f"  Separation: {'SKIP' if skip_separation else demucs_model}")
    print("=" * 60)

    # ── Step 1: Source separation ───────────────────────────────
    if skip_separation:
        print("\n[1/2] Skipping separation — using raw audio")
        audio_to_transcribe = str(input_path)
    else:
        print(f"\n[1/2] Separating with {demucs_model}...")
        stems = separate_audio(
            str(input_path),
            output_dir="separated",
            model=demucs_model,
            device=device,
        )
        audio_to_transcribe = stems[instrument]
        print(f"  Using stem: {audio_to_transcribe}")

    # ── Step 2: Transcription ──────────────────────────────────
    print(f"\n[2/2] Transcribing to MIDI...")
    midi_path = transcribe_to_midi(
        audio_to_transcribe,
        output_path=output_path,
        onset_threshold=onset_threshold,
        frame_threshold=frame_threshold,
        minimum_note_length=minimum_note_length,
    )

    print("\n" + "=" * 60)
    print(f"  Done! MIDI saved to: {midi_path}")
    print("=" * 60)

    return midi_path


def main():
    parser = argparse.ArgumentParser(
        description="Jazz Solo Transcriber — Audio to MIDI pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/transcribe.py track.wav
  python src/transcribe.py track.wav --instrument bass --output bass.mid
  python src/transcribe.py solo.wav --skip-separation
  python src/transcribe.py track.wav --device cuda --model htdemucs_ft
        """,
    )

    parser.add_argument("input", help="Path to input audio file")
    parser.add_argument(
        "--instrument", "-i",
        choices=STEMS,
        default="other",
        help="Which stem to transcribe (default: other)",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output MIDI file path (auto-generated if not set)",
    )
    parser.add_argument(
        "--skip-separation",
        action="store_true",
        help="Skip Demucs — transcribe the raw audio directly",
    )
    parser.add_argument(
        "--model", "-m",
        choices=list(DEMUCS_MODELS.keys()),
        default="htdemucs",
        help="Demucs model to use (default: htdemucs)",
    )
    parser.add_argument(
        "--device",
        choices=["cpu", "cuda"],
        default="cpu",
        help="Device for Demucs (default: cpu)",
    )
    parser.add_argument(
        "--onset-threshold",
        type=float,
        default=DEFAULT_PARAMS["onset_threshold"],
        help=f"Note onset confidence (default: {DEFAULT_PARAMS['onset_threshold']})",
    )
    parser.add_argument(
        "--frame-threshold",
        type=float,
        default=DEFAULT_PARAMS["frame_threshold"],
        help=f"Frame confidence (default: {DEFAULT_PARAMS['frame_threshold']})",
    )
    parser.add_argument(
        "--min-note-length",
        type=float,
        default=DEFAULT_PARAMS["minimum_note_length"],
        help=f"Min note length in ms (default: {DEFAULT_PARAMS['minimum_note_length']})",
    )

    args = parser.parse_args()

    run_pipeline(
        input_path=args.input,
        instrument=args.instrument,
        output_path=args.output,
        skip_separation=args.skip_separation,
        demucs_model=args.model,
        device=args.device,
        onset_threshold=args.onset_threshold,
        frame_threshold=args.frame_threshold,
        minimum_note_length=args.min_note_length,
    )


if __name__ == "__main__":
    main()
