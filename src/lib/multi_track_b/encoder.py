import os
import random
import sys

import miditoolkit
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from chord_detect import MIDIChord
    from common import Common, Event, Item
except Exception:
    raise ValueError('ERROR: cannot import!')


class MidiEncoder(Common):
    def __init__(self, file_path, w2i, pitch_variation_range=None,
                 velocity_scale_variation_range=None,
                 velocity_noise_scale_variation_range=None,
                 tempo_scale_variation_range=None):
        super().__init__()
        self.file_path = file_path
        self.w2i = w2i
        self.pitch_variation_range = pitch_variation_range
        self.velocity_scale_variation_range = velocity_scale_variation_range
        self.velocity_noise_scale_variation_range = velocity_noise_scale_variation_range
        self.tempo_scale_variation_range = tempo_scale_variation_range
        # midi parameters
        self.ticks_per_beat = None
        self.ticks_per_bar = None
        self.max_duration_splits = None
        self.quantized_beat_splits = None
        self.max_tick = None
        self.tempo_changes = None
        self.instruments = None
        self.time_sig = None
        self.quantized_ticks = None
        self.chord_method = None
        # common tempo is 4/4
        self.numerator = 4
        self.denominator = 4
        # variation
        self.pitch_variation = None
        self.velocity_variation = None
        self.tempo_variation = None

        # initialization
        self.initialize_midi(self.file_path)

    def initialize_variation(self, variation):
        if variation and self.pitch_variation_range is not None:
            self.pitch_variation = random.randint(self.pitch_variation_range[0],
                                                  self.pitch_variation_range[1])
        else:
            self.pitch_variation = 0
        if variation and self.velocity_scale_variation_range is not None:
            self.velocity_variation = random.uniform(self.velocity_scale_variation_range[0],
                                                     self.velocity_scale_variation_range[1])
        else:
            self.velocity_variation = 1
        if variation and self.tempo_scale_variation_range is not None:
            self.tempo_variation = random.uniform(self.tempo_scale_variation_range[0],
                                                  self.tempo_scale_variation_range[1])
        else:
            self.tempo_variation = 1

    @staticmethod
    def velocity_transform(velocity, scale):
        if scale > 0:
            velocity = min(int(round(scale * velocity)), 127)
        elif scale < 0:
            diff = random.uniform(0, scale * 127)
            velocity = int(round(scale * velocity + diff))
        return velocity

    def velocity_noise_add(self, velocity):
        if self.velocity_noise_scale_variation_range is None:
            return velocity
        else:
            # add dynamic noise
            noise_scale = random.uniform(self.velocity_noise_scale_variation_range[0],
                                         self.velocity_noise_scale_variation_range[0])
            return self.velocity_transform(velocity, noise_scale)

    def pitch_transform(self, pitch):
        target_pitch = pitch + self.pitch_variation
        if target_pitch > 127:
            while target_pitch > 127:
                target_pitch -= 12
        elif target_pitch < 0:
            while target_pitch < 0:
                target_pitch += 12
        return target_pitch

    def tempo_transform(self, tempo):
        return int(tempo * self.tempo_variation)

    def initialize_midi(self, path):
        # read midi now
        midi_obj = miditoolkit.midi.parser.MidiFile(path)
        self.ticks_per_beat = midi_obj.ticks_per_beat
        self.max_tick = midi_obj.max_tick
        self.tempo_changes = midi_obj.tempo_changes
        self.instruments = midi_obj.instruments
        if len(midi_obj.time_signature_changes) > 0:
            # TODO: assume, time signature will not change
            self.time_sig = midi_obj.time_signature_changes[0]
            self.numerator = self.time_sig.numerator
        self.ticks_per_bar = self.ticks_per_beat * self.numerator
        self.max_duration_splits = self.bar_split_fraction * self.max_duration_bars - 1
        self.quantized_beat_splits = self.bar_split_fraction / self.numerator
        self.quantized_ticks = int(self.ticks_per_beat / self.quantized_beat_splits)
        self.chord_method = MIDIChord(numerator=self.numerator, ticks_per_beat=self.ticks_per_beat)

    def read_items(self):
        # note
        notes = [self.instruments[i].notes for i in range(len(self.instruments))
                 if not self.instruments[i].is_drum]
        note_programs = [self.instruments[i].program for i in range(len(self.instruments))
                         if not self.instruments[i].is_drum]

        note_items = []
        for i in range(len(notes)):
            channel_notes = notes[i]
            for note in channel_notes:
                note_velocity = self.velocity_transform(note.velocity, self.velocity_variation)
                note_velocity = self.velocity_noise_add(note_velocity)
                note_items.append(Item(
                    name='Note',
                    start=note.start,
                    end=note.end,
                    velocity=note_velocity,
                    pitch=self.pitch_transform(note.pitch),
                    program=note_programs[i]))
        note_items.sort(key=lambda x: x.start)

        # drum
        drums = [self.instruments[i].notes for i in range(len(self.instruments))
                 if self.instruments[i].is_drum]
        drum_programs = [self.instruments[i].program for i in range(len(self.instruments))
                         if self.instruments[i].is_drum]
        drum_items = []
        for i in range(len(drums)):
            channel_drums = drums[i]
            for drum in channel_drums:
                drum_velocity = self.velocity_transform(drum.velocity, self.velocity_variation)
                drum_velocity = self.velocity_noise_add(drum_velocity)
                drum_items.append(Item(
                    name='Drum',
                    start=drum.start,
                    end=drum.end,
                    velocity=drum_velocity,
                    pitch=drum.pitch,
                    program=drum_programs[i]))
        drum_items.sort(key=lambda x: x.start)

        # tempo
        tempo_items = []
        for tempo in self.tempo_changes:
            tempo_items.append(Item(
                name='Tempo',
                start=tempo.time,
                end=None,
                velocity=None,
                pitch=self.tempo_transform(tempo.tempo),
                program=None))
        tempo_items.sort(key=lambda x: x.start)

        # expand to all beat
        max_tick = tempo_items[-1].start
        existing_ticks = {item.start: item.pitch for item in tempo_items}
        wanted_ticks = np.arange(0, max_tick + 1, self.ticks_per_beat)
        output = []
        for tick in wanted_ticks:
            if tick in existing_ticks:
                output.append(Item(
                    name='Tempo',
                    start=tick,
                    end=None,
                    velocity=None,
                    pitch=existing_ticks[tick],
                    program=None))
            else:
                output.append(Item(
                    name='Tempo',
                    start=tick,
                    end=None,
                    velocity=None,
                    pitch=output[-1].pitch,
                    program=None))
        tempo_items = output
        return note_items, drum_items, tempo_items

    @staticmethod
    def quantize_items(items, ticks):
        # process
        for item in items:
            quantized_start = int(round(item.start / ticks)) * ticks
            shift_start = quantized_start - item.start
            item.start += shift_start
            item.end += shift_start
        return items

    def extract_chords(self, items):
        chords = self.chord_method.extract(notes=items)
        output = []
        for chord in chords:
            output.append(Item(
                name='Chord',
                start=chord[0],
                end=chord[1],
                velocity=None,
                # chord name will not include `/` bass note part
                pitch=chord[2].split('/')[0],
                program=None))
        return output

    @staticmethod
    def group_items(items, max_time, ticks_per_bar):
        items.sort(key=lambda x: x.start)
        downbeats = np.arange(0, max_time + ticks_per_bar, ticks_per_bar)
        groups = []
        for db1, db2 in zip(downbeats[:-1], downbeats[1:]):
            insiders = []
            for item in items:
                if (item.start >= db1) and (item.start < db2):
                    insiders.append(item)
            insiders.sort(key=lambda x: x.start)
            overall = [db1] + insiders + [db2]
            groups.append(overall)
        return groups

    def init_event_by_position(self):
        dic = {}
        for i in range(self.bar_split_fraction):
            dic[i] = []
        return dic

    def item_to_event(self, groups):
        events = []
        n_downbeat = 0
        for group_i in range(len(groups)):
            bar_st, bar_et = groups[group_i][0], groups[group_i][-1]
            n_downbeat += 1
            events.append(Event(
                name='Bar',
                time=None,
                value=None,
                text=f'{n_downbeat}'))
            # elements within `Bar`
            event_by_position = self.init_event_by_position()
            for item in groups[group_i][1:-1]:
                # position (required)
                flags = np.linspace(bar_st, bar_et, self.bar_split_fraction, endpoint=False)
                position_value = int(np.argmin(abs(flags - item.start)))
                # (optional)
                if item.name == 'Note':
                    # program
                    event_by_position[position_value].append(Event(
                        name='Note',
                        time=item.start,
                        value=item.program,
                        text=f'{item.program}'))
                    # pitch
                    event_by_position[position_value].append(Event(
                        name='Pitch',
                        time=item.start,
                        value=item.pitch,
                        text=f'{item.pitch}'))
                    # velocity
                    event_by_position[position_value].append(Event(
                        name='Velocity',
                        time=item.start,
                        value=item.velocity,
                        text=f'{item.velocity}/{128}'))
                    # duration
                    duration = item.end - item.start
                    value = max(min(int(round(duration / self.quantized_ticks)), self.max_duration_splits), 1)
                    event_by_position[position_value].append(Event(
                        name='Duration',
                        time=item.start,
                        value=value,
                        text=f'{duration}/{self.quantized_ticks}'))
                elif item.name == 'Drum':
                    # program
                    event_by_position[position_value].append(Event(
                        name='Drum',
                        time=item.start,
                        value=item.program,
                        text=f'{item.program}'))
                    # pitch
                    event_by_position[position_value].append(Event(
                        name='Pitch',
                        time=item.start,
                        value=item.pitch,
                        text=f'{item.pitch}'))
                    # velocity
                    event_by_position[position_value].append(Event(
                        name='Velocity',
                        time=item.start,
                        value=item.velocity,
                        text=f'{item.velocity}/{128}'))
                    # duration
                    duration = item.end - item.start
                    value = max(min(int(round(duration / self.quantized_ticks)), self.max_duration_splits), 1)
                    event_by_position[position_value].append(Event(
                        name='Duration',
                        time=item.start,
                        value=value,
                        text=f'{duration}/{self.quantized_ticks}'))
                elif item.name == 'Chord':
                    event_by_position[position_value].append(Event(
                        name='Chord',
                        time=item.start,
                        value=item.pitch,
                        text=f'{item.pitch}'))
                elif item.name == 'Tempo':
                    tempo = int(item.pitch)
                    # limit to range
                    tempo = max(self.default_tempo_intervals[0].start, tempo)
                    tempo = min(self.default_tempo_intervals[-1].stop - 1, tempo)
                    tempo_style = tempo_value = None
                    for j in range(len(self.default_tempo_intervals)):
                        if tempo in self.default_tempo_intervals[j]:
                            tempo_style = Event('Tempo_Class', item.start, f'T{j}', None)
                            tempo_value = Event('Tempo_Value', item.start,
                                                tempo - self.default_tempo_intervals[j].start, None)
                    if tempo_value is not None and tempo_style is not None:
                        event_by_position[position_value].append(tempo_style)
                        event_by_position[position_value].append(tempo_value)
            # rebuild events
            for position_i in range(self.bar_split_fraction):
                if len(event_by_position[position_i]):
                    events.append(Event(
                        name='Position',
                        time=None,
                        value=f'{position_i}',
                        text=f'{position_i}/{self.bar_split_fraction}'))
                    events.extend(event_by_position[position_i])
        return events

    def events_to_words(self, events):
        words = []
        for event in events:
            if event.value is None:
                words.append(event.name)
            else:
                words.append(self.separator.join([str(event.name), str(event.value)]))
        return words

    def words_to_integers(self, words):
        integers = []
        for word in words:
            if word in self.w2i:
                integers.append(self.w2i[word])
            else:
                print(f'WARNING: `{word}` not in w2i!')
        return integers

    def encode(self, variation=True):
        # get new initialize variation
        self.initialize_variation(variation)
        # convert to items
        note_items, drum_items, tempo_items = self.read_items()
        # quantize notes / drum items
        note_items = self.quantize_items(note_items, ticks=self.quantized_ticks)
        drum_items = self.quantize_items(drum_items, ticks=self.quantized_ticks)
        # extract chord
        chord_items = self.extract_chords(note_items)
        # combine items (with switch)
        all_items = []
        if self.with_note:
            all_items.extend(note_items)
        if self.with_drum:
            all_items.extend(drum_items)
        if self.with_tempo:
            all_items.extend(tempo_items)
        if self.with_chord:
            all_items.extend(chord_items)
        max_time = note_items[-1].end
        # group items
        groups = self.group_items(all_items, max_time,
                                  ticks_per_bar=self.ticks_per_beat * self.numerator)
        events = self.item_to_event(groups)
        words = self.events_to_words(events)
        ints = self.words_to_integers(words)
        ints = np.array(ints)
        return ints
