"""
visualize.py — Piano roll visualization for transcribed MIDI.

Displays notes as horizontal bars on a pitch vs. time grid.

Usage:
    from visualize import plot_piano_roll
    plot_piano_roll("solo.mid")

    # Or from command line:
    python src/visualize.py solo.mid
"""

import pretty_midi
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from pathlib import Path


def plot_piano_roll(
    midi_path: str,
    save_path: str | None = None,
    title: str | None = None,
    figsize: tuple = (16, 6),
    show: bool = True,
) -> None:
    """
    Plot a piano roll from a MIDI file.

    Args:
        midi_path: Path to the MIDI file
        save_path: If provided, save the figure to this path (png, pdf, etc.)
        title: Plot title (auto-generated from filename if None)
        figsize: Figure size as (width, height)
        show: Whether to display the plot interactively
    """
    midi_path = Path(midi_path)
    if not midi_path.exists():
        raise FileNotFoundError(f"MIDI file not found: {midi_path}")

    midi_data = pretty_midi.PrettyMIDI(str(midi_path))

    if not midi_data.instruments:
        print("No instruments found in MIDI file.")
        return

    notes = midi_data.instruments[0].notes
    if not notes:
        print("No notes found in MIDI file.")
        return

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Plot each note as a colored rectangle
    for note in notes:
        # Color by velocity (louder = more opaque)
        alpha = 0.4 + 0.6 * (note.velocity / 127)
        rect = patches.Rectangle(
            (note.start, note.pitch - 0.4),   # (x, y)
            note.end - note.start,             # width
            0.8,                               # height
            linewidth=0.5,
            edgecolor="white",
            facecolor="#4A90D9",
            alpha=alpha,
        )
        ax.add_patch(rect)

    # Set axis limits
    all_pitches = [n.pitch for n in notes]
    min_pitch = min(all_pitches) - 2
    max_pitch = max(all_pitches) + 2
    end_time = midi_data.get_end_time()

    ax.set_xlim(0, end_time)
    ax.set_ylim(min_pitch, max_pitch)

    # Add pitch labels (note names) on y-axis
    pitch_range = range(min_pitch, max_pitch + 1)
    pitch_labels = [pretty_midi.note_number_to_name(p) for p in pitch_range]
    ax.set_yticks(list(pitch_range))
    ax.set_yticklabels(pitch_labels, fontsize=7)

    # Add gridlines for readability
    ax.set_axisbelow(True)
    ax.grid(axis="x", alpha=0.3, linewidth=0.5)
    ax.grid(axis="y", alpha=0.15, linewidth=0.5)

    # Labels
    ax.set_xlabel("Time (seconds)", fontsize=11)
    ax.set_ylabel("Pitch", fontsize=11)

    if title is None:
        title = f"Piano Roll — {midi_path.stem}"
    ax.set_title(title, fontsize=13, fontweight="bold")

    # Summary stats in bottom-right
    stats_text = (
        f"{len(notes)} notes  |  "
        f"{pretty_midi.note_number_to_name(min(all_pitches))}–"
        f"{pretty_midi.note_number_to_name(max(all_pitches))}  |  "
        f"{end_time:.1f}s"
    )
    ax.text(
        0.99, 0.02, stats_text,
        transform=ax.transAxes,
        fontsize=9, color="gray",
        ha="right", va="bottom",
    )

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Piano roll saved to: {save_path}")

    if show:
        plt.show()
    else:
        plt.close(fig)


# ── Quick test ──────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python src/visualize.py <midi_file> [output_image.png]")
        sys.exit(1)

    midi_file = sys.argv[1]
    save_file = sys.argv[2] if len(sys.argv) > 2 else None

    plot_piano_roll(midi_file, save_path=save_file)
