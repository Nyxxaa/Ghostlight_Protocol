#!/usr/bin/env python3
"""Generate a synthetic WAV with readable spectrogram text."""

from __future__ import annotations

import argparse
import math
import wave
from pathlib import Path

import numpy as np


FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01111", "10000", "10000", "10011", "10001", "10001", "01110"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "_": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
}


def render_columns(text: str) -> list[list[int]]:
    columns: list[list[int]] = []
    for char in text.upper():
        glyph = FONT.get(char)
        if glyph is None:
            glyph = ["00000"] * 7
        for col in range(5):
            columns.append([1 if glyph[row][col] == "1" else 0 for row in range(7)])
        columns.append([0] * 7)
    return columns


def synthesize(text: str, output: Path) -> None:
    sample_rate = 44_100
    column_seconds = 0.045
    fade_seconds = 0.006
    columns = render_columns(text)
    samples_per_column = int(sample_rate * column_seconds)
    fade_samples = max(1, int(sample_rate * fade_seconds))
    total_samples = samples_per_column * len(columns)
    audio = np.zeros(total_samples, dtype=np.float64)

    t_col = np.arange(samples_per_column) / sample_rate
    envelope = np.ones(samples_per_column)
    envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)

    base_freq = 900.0
    freq_step = 245.0
    for col_index, column in enumerate(columns):
        start = col_index * samples_per_column
        end = start + samples_per_column
        for row, active in enumerate(column):
            if not active:
                continue
            freq = base_freq + (6 - row) * freq_step
            phase = (col_index * 0.37 + row * 0.19) * math.pi
            audio[start:end] += 0.12 * np.sin(2 * math.pi * freq * t_col + phase) * envelope

    seconds = np.arange(total_samples) / sample_rate
    drone = (
        0.035 * np.sin(2 * math.pi * 73.0 * seconds)
        + 0.025 * np.sin(2 * math.pi * 146.0 * seconds)
        + 0.018 * np.sin(2 * math.pi * 219.0 * seconds)
    )
    audio += drone
    audio /= max(1.0, float(np.max(np.abs(audio))))
    pcm = (audio * 32767).astype(np.int16)

    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm.tobytes())


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Ghostlight spectrogram audio.")
    parser.add_argument("text", help="Text to reveal in the spectrogram")
    parser.add_argument("output", type=Path, help="Output WAV path")
    args = parser.parse_args()
    synthesize(args.text, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
