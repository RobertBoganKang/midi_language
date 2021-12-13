import os
import random
import sys

import miditoolkit
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from common import Common, Item, Event
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
        self.notes = []
        self.controls = []
        self.ticks_per_beat = None
        self.quantized_tick_to_frame_scale = None
        # variation
        self.pitch_variation = None
        self.velocity_variation = None
        self.tempo_variation = None

        # initialization
        self.initialize_midi(self.file_path)

    def initialize_midi(self, path):
        # read midi now
        midi_obj = miditoolkit.midi.parser.MidiFile(path)
        self.ticks_per_beat = midi_obj.ticks_per_beat
        # assume all channel notes and controls are piano
        for instrument in midi_obj.instruments:
            self.notes.extend(instrument.notes)
            for control in instrument.control_changes:
                if 64 <= control.number <= 69:
                    self.controls.append(control)
        # assume default `bpm` is 120
        self.quantized_tick_to_frame_scale = (
                self.ticks_per_beat * self.default_beat_per_minute / 60 * self.quantized_time)

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

    def tempo_transform(self, tempo):
        return int(tempo * self.tempo_variation)

    def pitch_transform(self, pitch):
        target_pitch = pitch + self.pitch_variation
        if target_pitch > 127:
            while target_pitch > 127:
                target_pitch -= 12
        elif target_pitch < 0:
            while target_pitch < 0:
                target_pitch += 12
        return target_pitch

    def read_items(self):
        # notes
        note_items = []
        for note in self.notes:
            note_velocity = self.velocity_transform(note.velocity, self.velocity_variation)
            note_velocity = self.velocity_noise_add(note_velocity)
            note_items.append(Item(
                name='Note',
                start=self.tempo_transform(note.start),
                end=self.tempo_transform(note.end),
                velocity=note_velocity,
                pitch=self.pitch_transform(note.pitch)))
        note_items.sort(key=lambda x: x.start)

        # control
        control_items = []
        status = False
        start = 0
        for control in self.controls:
            value = control.value
            if value > 0:
                if not status:
                    start = control.time
                status = True
            else:
                if status:
                    control_items.append(Item(
                        name='Control',
                        start=self.tempo_transform(start),
                        end=self.tempo_transform(control.time),
                        velocity=None,
                        pitch=control.number))
                status = False
        control_items.sort(key=lambda x: x.start)
        return note_items, control_items

    def quantize_items(self, items):
        """ convert to quantized `bigger` frames """
        # process
        for item in items:
            quantized_start = int(round(item.start / self.quantized_tick_to_frame_scale))
            quantized_end = int(round(item.end / self.quantized_tick_to_frame_scale))
            item.start = quantized_start
            item.end = quantized_end
        return items

    def time_or_duration_transform(self, duration):
        return min(self.quantized_max_frame, max(1, duration))

    def item_to_event(self, items):
        events = []
        temp_time = None
        for item in items:
            start_time = item.start
            if temp_time is None:
                temp_time = start_time
            elif start_time - temp_time != 0:
                events.append(Event(
                    name='Duration',
                    time=start_time,
                    value=self.time_or_duration_transform(start_time - temp_time),
                    text='delta_time'))
                temp_time = start_time
            # notes
            if item.name == 'Note':
                events.append(Event(
                    name='Pitch',
                    time=start_time,
                    value=item.pitch,
                    text='pitch'))
                events.append(Event(
                    name='Velocity',
                    time=start_time,
                    value=item.velocity,
                    text='velocity'))
                # duration should larger than `1` frame
                events.append(Event(
                    name='Duration',
                    time=start_time,
                    value=self.time_or_duration_transform(item.end - item.start),
                    text='duration'))
            elif item.name == 'Control':
                events.append(Event(
                    name='Control',
                    time=start_time,
                    value=item.pitch,
                    text='control'))
                events.append(Event(
                    name='Duration',
                    time=start_time,
                    value=self.time_or_duration_transform(item.end - item.start),
                    text='duration'))
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
        self.initialize_variation(variation)
        note_items, control_items = self.read_items()
        note_items = self.quantize_items(note_items)
        control_items = self.quantize_items(control_items)
        all_items = []
        if self.with_note:
            all_items.extend(note_items)
        if self.with_control:
            all_items.extend(control_items)
        all_items.sort(key=lambda x: x.start)
        events = self.item_to_event(all_items)
        words = self.events_to_words(events)
        ints = self.words_to_integers(words)
        ints = np.array(ints)
        return ints
