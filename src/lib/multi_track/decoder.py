import os
import sys

import miditoolkit
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from common import Common, Event
except Exception:
    raise ValueError('ERROR: cannot import!')


class MidiDecoder(Common):
    def __init__(self, i2w, numerator=4, denominator=4, ticks_per_beat=480,
                 decode_note=True, decode_drum=True, decode_tempo=True, decode_chord=True):
        super().__init__()
        self.i2w = i2w
        # numerator/denominator will be given outside
        self.numerator = numerator
        self.denominator = denominator
        # other params
        self.default_ticks_per_beat = ticks_per_beat
        self.decode_note = decode_note
        self.decode_drum = decode_drum
        self.decode_tempo = decode_tempo
        self.decode_chord = decode_chord
        # calculate
        self.quantized_beat_splits = self.bar_split_fraction / numerator
        self.default_quantized_ticks = int(self.default_ticks_per_beat / self.quantized_beat_splits)
        self.ticks_per_bar = self.default_ticks_per_beat * numerator

    def extract_events(self, events):
        # get downbeat and note (no time)
        temp_notes = []
        temp_drums = []
        temp_chords = []
        temp_tempos = []
        i = 0
        while i < len(events):
            if events[i].name == 'Bar' and i > 0:
                temp_notes.append('Bar')
                temp_drums.append('Bar')
                temp_chords.append('Bar')
                temp_tempos.append('Bar')
                i += 1
            elif i < len(events) - 5 and events[i].name == 'Position' and \
                    events[i + 1].name == 'Note' and \
                    events[i + 2].name == 'Program' and \
                    events[i + 3].name == 'Pitch' and \
                    events[i + 4].name == 'Velocity' and \
                    events[i + 5].name == 'Duration':
                # start time and end time from position
                position = int(events[i].value)
                # program
                program = int(events[i + 2].value)
                # pitch
                pitch = int(events[i + 3].value)
                # velocity
                velocity = int(events[i + 4].value)
                # duration
                duration = events[i + 5].value * self.default_quantized_ticks
                # adding
                temp_notes.append([position, program, pitch, velocity, duration])
                i += 5
            elif i < len(events) - 5 and events[i].name == 'Position' and \
                    events[i + 1].name == 'Drum' and \
                    events[i + 2].name == 'Program' and \
                    events[i + 3].name == 'Pitch' and \
                    events[i + 4].name == 'Velocity' and \
                    events[i + 5].name == 'Duration':
                # start time and end time from position
                position = int(events[i].value)
                # program
                program = int(events[i + 2].value)
                # pitch
                pitch = int(events[i + 3].value)
                # velocity
                velocity = int(events[i + 4].value)
                # duration
                duration = events[i + 5].value * self.default_quantized_ticks
                # adding
                temp_drums.append([position, program, pitch, velocity, duration])
                i += 5
            elif i < len(events) - 1 and events[i].name == 'Position' and events[i + 1].name == 'Chord':
                position = int(events[i].value)
                temp_chords.append([position, events[i + 1].value])
                i += 2
            elif i < len(events) - 2 and events[i].name == 'Position' and \
                    events[i + 1].name == 'Tempo_Class' and \
                    events[i + 2].name == 'Tempo_Value':
                position = int(events[i].value)
                tempo = None
                for j in range(len(self.default_tempo_intervals)):
                    if events[i + 1].value == f'T{j}':
                        tempo = self.default_tempo_intervals[j].start + int(events[i + 2].value)
                if tempo is not None:
                    temp_tempos.append([position, tempo])
                i += 3
            else:
                # bad case
                i += 1
        return temp_notes, temp_drums, temp_chords, temp_tempos

    def build_notes_drums(self, temp_xs):
        xs_dict = {}
        current_bar = 0
        for xx in temp_xs:
            if xx == 'Bar':
                current_bar += 1
            else:
                position, program, pitch, velocity, duration = xx
                # position (start time)
                current_bar_st = current_bar * self.ticks_per_bar
                current_bar_et = (current_bar + 1) * self.ticks_per_bar
                flags = np.linspace(current_bar_st, current_bar_et, self.bar_split_fraction, endpoint=False,
                                    dtype=int)
                st = flags[position]
                # duration (end time)
                et = st + duration
                if program not in xs_dict:
                    xs_dict[program] = [miditoolkit.Note(velocity, pitch, st, et)]
                else:
                    xs_dict[program].append(miditoolkit.Note(velocity, pitch, st, et))
        return xs_dict

    def build_tempos(self, temp_tempos):
        tempos = []
        current_bar = 0
        for tempo in temp_tempos:
            if tempo == 'Bar':
                current_bar += 1
            else:
                position, value = tempo
                # position (start time)
                current_bar_st = current_bar * self.ticks_per_bar
                current_bar_et = (current_bar + 1) * self.ticks_per_bar
                flags = np.linspace(current_bar_st, current_bar_et, self.bar_split_fraction, endpoint=False,
                                    dtype=int)
                st = flags[position]
                tempos.append([int(st), value])
        return tempos

    def build_chords(self, temp_chords):
        chords = []
        if len(temp_chords) > 0:
            current_bar = 0
            for chord in temp_chords:
                if chord == 'Bar':
                    current_bar += 1
                else:
                    position, value = chord
                    # position (start time)
                    current_bar_st = current_bar * self.ticks_per_bar
                    current_bar_et = (current_bar + 1) * self.ticks_per_bar
                    flags = np.linspace(current_bar_st, current_bar_et, self.bar_split_fraction, endpoint=False,
                                        dtype=int)
                    st = flags[position]
                    chords.append([st, value])
        return chords

    @staticmethod
    def to_int(string):
        # noinspection PyBroadException
        try:
            return int(string)
        except Exception:
            return string

    def words_to_events(self, words):
        events = []
        for word in words:
            word_split = word.split(self.separator)
            if self.separator not in word:
                events.append(Event(name=word_split[0], time=None, value=None, text=None))
            else:
                events.append(Event(name=word_split[0], time=None, value=self.to_int(word_split[1]), text=None))
        return events

    def integers_to_words(self, integers):
        words = []
        for integer in integers:
            if integer in self.i2w:
                words.append(self.i2w[integer])
            else:
                print(f'WARNING: `{integer}` not in i2w!')
        return words

    def decode(self, integers, output_path):
        # decode to events
        words = self.integers_to_words(integers)
        events = self.words_to_events(words)

        # decode properties
        temp_notes, temp_drums, temp_chords, temp_tempos = self.extract_events(events)
        # get specific time for items
        # notes
        notes_dict = self.build_notes_drums(temp_notes)
        # drums
        drums_dict = self.build_notes_drums(temp_drums)
        # chords
        chords = self.build_chords(temp_chords)
        # tempos
        tempos = self.build_tempos(temp_tempos)

        # write MIDI
        midi = miditoolkit.midi.parser.MidiFile(ticks_per_beat=self.default_ticks_per_beat)
        # write (default settings)
        inst_time_sig = miditoolkit.midi.containers.TimeSignature(self.numerator, self.denominator, 0)
        midi.time_signature_changes.append(inst_time_sig)
        midi.ticks_per_beat = self.default_ticks_per_beat

        # write instrument (notes)
        if self.decode_note:
            for program, notes in notes_dict.items():
                # program will be random (instrument sound)
                inst = miditoolkit.midi.containers.Instrument(program, is_drum=False,
                                                              name='instrument_' + str(program))
                inst.notes = notes
                midi.instruments.append(inst)

        # write instrument (drums)
        if self.decode_drum:
            for program, drums in drums_dict.items():
                inst = miditoolkit.midi.containers.Instrument(program, is_drum=True,
                                                              name='drum_' + str(program))
                inst.notes = drums
                midi.instruments.append(inst)

        # write (tempo)
        if self.decode_tempo:
            tempo_changes = []
            for st, bpm in tempos:
                tempo_changes.append(miditoolkit.midi.containers.TempoChange(bpm, st))
            midi.tempo_changes = tempo_changes

        # write (chord into marker)
        if self.decode_chord and len(temp_chords) > 0:
            for c in chords:
                midi.markers.append(
                    miditoolkit.midi.containers.Marker(text=c[1], time=c[0]))

        # export MIDI
        midi.dump(output_path)
