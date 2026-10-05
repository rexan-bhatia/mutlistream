"""Generate original, short instrumental sketches for the local demo."""

import math
import random
import struct
import wave
from pathlib import Path


AUDIO_DIR = Path(__file__).resolve().parent / "audio"
SAMPLE_RATE = 22050
DURATION_SECONDS = 30
TEMPO = 120
BEAT_SECONDS = 60 / TEMPO
SCALES = (
    (0, 2, 4, 7, 9, 7, 4, 2),
    (0, 3, 5, 7, 10, 7, 5, 3),
    (0, 2, 5, 7, 9, 7, 5, 2),
    (0, 4, 5, 7, 11, 7, 5, 4),
)
CHORDS = ((0, 4, 7), (5, 9, 0), (7, 11, 2), (0, 4, 7))


def note_frequency(semitones_from_a4):
    return 440 * (2 ** (semitones_from_a4 / 12))


def generate_track(track_number):
    """Write one distinct 30-second synth instrumental as a PCM WAV."""
    randomizer = random.Random(track_number * 7919)
    scale = SCALES[(track_number - 1) % len(SCALES)]
    root = 45 + (track_number % 5) * 2
    sample_count = SAMPLE_RATE * DURATION_SECONDS
    output_path = AUDIO_DIR / f"demo{track_number}.wav"
    melody_step_samples = round(BEAT_SECONDS * SAMPLE_RATE / 2)
    beat_samples = round(BEAT_SECONDS * SAMPLE_RATE)
    chord_samples = beat_samples * 4

    with wave.open(str(output_path), "wb") as audio_file:
        audio_file.setnchannels(1)
        audio_file.setsampwidth(2)
        audio_file.setframerate(SAMPLE_RATE)

        frames = bytearray()
        for sample_index in range(sample_count):
            time_seconds = sample_index / SAMPLE_RATE
            beat_position = sample_index % beat_samples
            chord_index = (sample_index // chord_samples) % len(CHORDS)
            chord_notes = CHORDS[chord_index]
            step_index = sample_index // melody_step_samples
            melody_note = scale[(step_index + track_number) % len(scale)]
            melody_frequency = note_frequency(root + 12 + melody_note)

            pad = sum(
                math.sin(2 * math.pi * note_frequency(root + interval) * time_seconds)
                for interval in chord_notes
            ) / len(chord_notes)
            pad *= 0.12

            melody_phase = (time_seconds * melody_frequency) % 1
            melody_envelope = min(1, beat_position / (SAMPLE_RATE * 0.025))
            melody_envelope *= max(0, 1 - beat_position / melody_step_samples)
            melody = math.sin(2 * math.pi * melody_phase) * 0.18 * melody_envelope

            bass_frequency = note_frequency(root - 12 + chord_notes[0])
            bass = math.sin(2 * math.pi * bass_frequency * time_seconds) * 0.16
            kick = 0
            if beat_position < SAMPLE_RATE * 0.16:
                kick_envelope = 1 - beat_position / (SAMPLE_RATE * 0.16)
                kick_frequency = 70 - 35 * beat_position / (SAMPLE_RATE * 0.16)
                kick = math.sin(2 * math.pi * kick_frequency * time_seconds) * kick_envelope * 0.28

            percussion = 0
            if (sample_index // beat_samples) % 4 in (1, 3) and beat_position < SAMPLE_RATE * 0.07:
                snare_envelope = 1 - beat_position / (SAMPLE_RATE * 0.07)
                percussion = randomizer.uniform(-1, 1) * snare_envelope * 0.07

            fade_seconds = 1.5
            fade_in = min(1, time_seconds / fade_seconds)
            fade_out = min(1, (DURATION_SECONDS - time_seconds) / fade_seconds)
            sample = max(-1, min(1, (pad + melody + bass + kick + percussion) * fade_in * fade_out))
            frames.extend(struct.pack("<h", round(sample * 32767)))

        audio_file.writeframes(frames)
    return output_path


def main():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    for track_number in range(1, 13):
        output_path = generate_track(track_number)
        print(f"Created {output_path.name}")


if __name__ == "__main__":
    main()
