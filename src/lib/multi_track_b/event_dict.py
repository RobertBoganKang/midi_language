import os
import pickle
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from common import Common, Event
except Exception:
    raise ValueError('ERROR: cannot import!')


class EventDict(Common):
    def __init__(self):
        super().__init__()
        self.pitch_class = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.chord_class = ['maj', 'min', 'dim', 'aug', 'dom']

        self.global_counter = 0
        self.w2i = {}
        self.i2w = {}

        # calculate
        self.build_all()

    def update(self, word):
        self.w2i[word] = self.global_counter
        self.i2w[self.global_counter] = word
        self.global_counter += 1

    def build_bar(self):
        self.update('Bar')

    def build_position(self):
        for i in range(self.bar_split_fraction):
            self.update('Position' + self.separator + str(i))

    def build_chord(self):
        # get all possible chords
        chords = ['N:N']
        for p in self.pitch_class:
            for c in self.chord_class:
                chords.append(f'{p}:{c}')
        for chord in chords:
            self.update('Chord' + self.separator + chord)

    def build_tempo(self):
        for i in range(len(self.default_tempo_intervals)):
            self.update('Tempo_Class' + self.separator + f'T{i}')
        for v in range(0, 60):
            self.update('Tempo_Value' + self.separator + str(v))

    def build_velocity(self):
        for velocity in range(128):
            self.update('Velocity' + self.separator + str(velocity))

    def build_note_program(self):
        for velocity in range(128):
            self.update('Note' + self.separator + str(velocity))

    def build_drum_program(self):
        for velocity in range(128):
            self.update('Drum' + self.separator + str(velocity))

    def build_pitch(self):
        for pitch in range(128):
            self.update('Pitch' + self.separator + str(pitch))

    def build_duration(self):
        for duration in range(self.bar_split_fraction * self.max_duration_bars):
            self.update('Duration' + self.separator + str(duration))

    def build_all(self):
        # required
        self.build_bar()
        self.build_position()
        # optional (with switch)
        if self.with_note:
            self.build_note_program()
        if self.with_drum:
            self.build_drum_program()
        if self.with_note or self.with_drum:
            self.build_pitch()
            self.build_velocity()
            self.build_duration()
        if self.with_tempo:
            self.build_tempo()
        if self.with_chord:
            self.build_chord()

    def export(self):
        result = [self.w2i, self.i2w]
        with open(self.dic_path, 'wb') as w:
            pickle.dump(result, w)

    def check_and_load_dict(self):
        if not os.path.exists(self.dic_path):
            self.export()
        with open(self.dic_path, 'rb') as f:
            w2i, i2w = pickle.load(f)
        return w2i, i2w
