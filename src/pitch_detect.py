"""
pitch_detect.py — Wrapper around Basic Pitch for audio-to-MIDI transcription.

Takes an audio file (ideally an isolated stem from Demucs) and produces
a MIDI file with detected notes.

Usage:
    from pitch_detect import transcribe_to_midi
    midi_path = transcribe_to_midi("separated/htdemucs/song/other.wav")
"""

from pathlib import Path
from basic_pitch.inference import predict
from basic_pitch import build_icassp_2022_model_path, FilenameSuffix
import pretty_midi

# Use the ONNX model — faster on CPU and avoids TensorFlow compatibility issues
MODEL_PATH = build_icassp_2022_model_path(FilenameSuffix.onnx)


# ── Default parameters ──────────────────────────────────────────
# These control how aggressively Basic Pitch detects notes.
# Tweak these based on your evaluation — jazz solos may need
# different settings than pop vocals.
#
# Lower onset_threshold → detects more notes (including faint ones)
# Higher onset_threshold → only detects confident notes
# Lower minimum_note_length → catches fast runs
# Higher minimum_note_length → filters out noise

DEFAULT_PARAMS = {
    "onset_threshold": 0.5,          # How confident a note onset must be (0.0–1.0)
    "frame_threshold": 0.3,          # How confident a frame must be to sustain a note
    "minimum_note_length": 58,       # Minimum note duration in milliseconds
    "minimum_frequency": None,       # Min pitch in Hz (None = no limit)
    "maximum_frequency": None,       # Max pitch in Hz (None = no limit)
    "midi_tempo": 120,               # BPM for MIDI output timing
}


def transcribe_to_midi(
    input_path: str,
    output_path: str | None = None,
    onset_threshold: float = DEFAULT_PARAMS["onset_threshold"],
    frame_threshold: float = DEFAULT_PARAMS["frame_threshold"],
    minimum_note_length: float = DEFAULT_PARAMS["minimum_note_length"],
    minimum_frequency: float | None = DEFAULT_PARAMS["minimum_frequency"],
    maximum_frequency: float | None = DEFAULT_PARAMS["maximum_frequency"],
    midi_tempo: float = DEFAULT_PARAMS["midi_tempo"],
) -> str:
    """
    Transcribe an audio file to MIDI using Basic Pitch.

    Args:
        input_path: Path to the audio file (wav recommended)
        output_path: Where to save the MIDI file (auto-generated if None)
        onset_threshold: Note onset confidence threshold (0.0–1.0)
        frame_threshold: Frame confidence threshold (0.0–1.0)
        minimum_note_length: Minimum note length in ms
        minimum_frequency: Minimum pitch in Hz (or None)
        maximum_frequency: Maximum pitch in Hz (or None)
        midi_tempo: Tempo for the MIDI file

    Returns:
        Path to the saved MIDI file.
    """
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Audio file not found: {input_path}")

    # Auto-generate output path if not provided
    if output_path is None:
        output_path = str(input_path.with_suffix(".mid"))

    print(f"Transcribing '{input_path.name}' to MIDI...")
    print(f"  Onset threshold: {onset_threshold}")
    print(f"  Frame threshold: {frame_threshold}")
    print(f"  Min note length: {minimum_note_length}ms")

    # Run Basic Pitch inference
    # Returns: (model_output, midi_data, note_events)
    #   model_output: raw model predictions (numpy arrays)
    #   midi_data: a pretty_midi.PrettyMIDI object
    #   note_events: list of (start_time, end_time, pitch, velocity, confidence)
    model_output, midi_data, note_events = predict(
        str(input_path),
        model_or_model_path=MODEL_PATH,
        onset_threshold=onset_threshold,
        frame_threshold=frame_threshold,
        minimum_note_length=minimum_note_length,
        minimum_frequency=minimum_frequency,
        maximum_frequency=maximum_frequency,
        midi_tempo=midi_tempo,
    )

    # Save the MIDI file
    midi_data.write(str(output_path))

    # Print summary
    notes = midi_data.instruments[0].notes if midi_data.instruments else []
    duration = midi_data.get_end_time()

    print(f"\nTranscription complete!")
    print(f"  Notes detected: {len(notes)}")
    print(f"  Duration: {duration:.1f} seconds")
    if notes:
        pitches = [n.pitch for n in notes]
        print(f"  Pitch range: {pretty_midi.note_number_to_name(min(pitches))} – "
              f"{pretty_midi.note_number_to_name(max(pitches))}")
    print(f"  Saved to: {output_path}")

    return str(output_path)


def get_note_events(input_path: str, **kwargs) -> list[dict]:
    """
    Transcribe and return structured note events (useful for visualization).

    Returns a list of dicts with keys:
        start_time, end_time, pitch, pitch_name, velocity, confidence
    """
    input_path = Path(input_path)
    model_output, midi_data, note_events = predict(
        str(input_path),
        model_or_model_path=MODEL_PATH,
        onset_threshold=kwargs.get("onset_threshold", DEFAULT_PARAMS["onset_threshold"]),
        frame_threshold=kwargs.get("frame_threshold", DEFAULT_PARAMS["frame_threshold"]),
        minimum_note_length=kwargs.get("minimum_note_length", DEFAULT_PARAMS["minimum_note_length"]),
        midi_tempo=kwargs.get("midi_tempo", DEFAULT_PARAMS["midi_tempo"]),
    )

    events = []
    for start, end, pitch, velocity, confidence in note_events:
        events.append({
            "start_time": start,
            "end_time": end,
            "pitch": int(pitch),
            "pitch_name": pretty_midi.note_number_to_name(int(pitch)),
            "velocity": int(velocity),
            "confidence": round(confidence, 3),
        })

    return events


# ── Quick test ──────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python src/pitch_detect.py <audio_file> [output.mid]")
        print()
        print("Parameters can be set in the DEFAULT_PARAMS dict in this file.")
        sys.exit(1)

    audio_file = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) > 2 else None

    midi_path = transcribe_to_midi(audio_file, output_path=out_file)
    print(f"\nYou can now visualize with:")
    print(f"  python src/visualize.py {midi_path}")