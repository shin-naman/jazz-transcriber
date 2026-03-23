"""
app.py — Streamlit web interface for Jazz Solo Transcriber.

Run with:
    streamlit run src/app.py
"""

import sys
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend — required for Streamlit
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import pretty_midi
import streamlit as st

# Allow imports from src/
sys.path.insert(0, str(Path(__file__).parent))
from pitch_detect import transcribe_to_midi
from separate import separate_audio


st.set_page_config(page_title="Jazz Solo Transcriber", page_icon="🎷", layout="wide")
st.title("🎷 Jazz Solo Transcriber")
st.markdown("Upload a jazz recording — Demucs splits it into stems, Basic Pitch transcribes the solo to MIDI.")

uploaded_file = st.file_uploader("Upload audio file", type=["wav", "mp3", "flac", "m4a"])

STEM_DESCRIPTIONS = {
    "other":  "Other — solo instruments (sax, trumpet, piano, guitar, etc.)",
    "vocals": "Vocals — sung melody",
    "bass":   "Bass — bass line",
    "drums":  "Drums — percussion (transcription quality will be low)",
}

stem = st.radio(
    "Which part do you want to transcribe?",
    options=list(STEM_DESCRIPTIONS.keys()),
    format_func=lambda s: STEM_DESCRIPTIONS[s],
    horizontal=True,
)

if uploaded_file is not None:
    audio_bytes = uploaded_file.read()
    st.audio(audio_bytes, format=uploaded_file.type)

    if st.button("Run Pipeline", type="primary"):
        # Save uploaded file to a temp path so Demucs/Basic Pitch can read it
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        # ── Step 1: Source separation ────────────────────────────────
        with st.spinner("Step 1/2 — Separating audio with Demucs (this takes ~1 min)..."):
            try:
                stems = separate_audio(tmp_path, output_dir="separated")
            except Exception as e:
                st.error(f"Separation failed: {e}")
                st.stop()

        st.success(f"Separation complete. Using '{stem}' stem: `{stems[stem]}`")

        # ── Step 2: Transcription ────────────────────────────────────
        with st.spinner("Step 2/2 — Transcribing to MIDI with Basic Pitch..."):
            try:
                midi_path = transcribe_to_midi(stems[stem])
            except Exception as e:
                st.error(f"Transcription failed: {e}")
                st.stop()

        # ── Piano roll visualization ─────────────────────────────────
        midi_data = pretty_midi.PrettyMIDI(midi_path)
        notes = midi_data.instruments[0].notes if midi_data.instruments else []

        if not notes:
            st.warning("Transcription produced no notes. Try lowering the onset threshold.")
        else:
            st.success(f"Transcription complete — {len(notes)} notes detected.")

            fig, ax = plt.subplots(figsize=(16, 5))
            for note in notes:
                alpha = 0.4 + 0.6 * (note.velocity / 127)
                ax.add_patch(patches.Rectangle(
                    (note.start, note.pitch - 0.4),
                    note.end - note.start,
                    0.8,
                    linewidth=0.5,
                    edgecolor="white",
                    facecolor="#4A90D9",
                    alpha=alpha,
                ))

            all_pitches = [n.pitch for n in notes]
            min_pitch, max_pitch = min(all_pitches) - 2, max(all_pitches) + 2
            pitch_range = range(min_pitch, max_pitch + 1)

            ax.set_xlim(0, midi_data.get_end_time())
            ax.set_ylim(min_pitch, max_pitch)
            ax.set_yticks(list(pitch_range))
            ax.set_yticklabels([pretty_midi.note_number_to_name(p) for p in pitch_range], fontsize=7)
            ax.set_xlabel("Time (seconds)")
            ax.set_ylabel("Pitch")
            ax.set_title(f"Piano Roll — {Path(uploaded_file.name).stem} ({stem})", fontweight="bold")
            ax.grid(axis="x", alpha=0.3, linewidth=0.5)
            ax.set_facecolor("#1a1a2e")
            fig.patch.set_facecolor("#0f0f23")
            ax.tick_params(colors="white")
            ax.xaxis.label.set_color("white")
            ax.yaxis.label.set_color("white")
            ax.title.set_color("white")
            plt.tight_layout()

            st.pyplot(fig)
            plt.close(fig)

            # ── MIDI download ────────────────────────────────────────
            with open(midi_path, "rb") as f:
                midi_bytes = f.read()

            st.download_button(
                label="⬇️ Download MIDI",
                data=midi_bytes,
                file_name=f"{Path(uploaded_file.name).stem}_transcription.mid",
                mime="audio/midi",
            )
