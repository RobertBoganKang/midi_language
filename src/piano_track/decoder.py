import os
import sys

import miditoolkit

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from common import Common, Event
except Exception:
    raise ValueError('ERROR: cannot import!')


class MidiDecoder(Common):
    def __init__(self, i2w, ticks_per_beat=480, decode_note=True, decode_control=True):
        super().__init__()
        self.i2w = i2w

        # other params
        self.default_ticks_per_beat = ticks_per_beat
        self.decode_note = decode_note
        self.decode_control = decode_control

        # system parameters
        self.notes_status = [[0, 0]] * 127

        # calculate
        self.quantized_tick_to_frame_scale = (ticks_per_beat * self.default_beat_per_minute / 60 * self.quantized_time)

    def extract_events(self, events):
        # get downbeat and note (no time)
        temp_notes = []
        temp_controls = []
        accumulate_time = 0
        i = 0
        while i < len(events):
            if i < len(events) - 1 and events[i].name == 'NoteOn' \
                    and events[i + 1].name == 'Velocity':
                # pitch
                pitch = int(events[i].value)
                # velocity
                velocity = int(events[i + 1].value)
                # start/end time
                time = int(round(accumulate_time))
                # adding
                temp_notes.append([pitch, velocity, time, True])
                i += 2
            elif i < len(events) and events[i].name == 'NoteOff':
                # pitch
                pitch = int(events[i].value)
                # start/end time
                time = int(round(accumulate_time))
                # adding
                temp_notes.append([pitch, None, time, False])
                i += 1
            elif i < len(events) and events[i].name == 'PaddleOn':
                # control
                control = int(events[i].value)
                # start/end time
                time = int(round(accumulate_time))
                # adding
                temp_controls.append([control, time, True])
                i += 1
            elif i < len(events) and events[i].name == 'PaddleOff':
                # control
                control = int(events[i].value)
                # start/end time
                time = int(round(accumulate_time))
                # adding
                temp_controls.append([control, time, False])
                i += 1
            elif events[i].name == 'Time':
                # delta time
                delta_time = events[i].value * self.quantized_tick_to_frame_scale
                accumulate_time += delta_time
                i += 1
            else:
                # bad case incrementation
                i += 1
        return temp_notes, temp_controls

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

    def build_notes(self, temp_notes):
        notes_list = []
        for note in temp_notes:
            pitch, velocity, time, status = note
            if status:
                # note-on
                self.notes_status[pitch] = [velocity, time]
            else:
                # note-off
                on_velocity, on_time = self.notes_status[pitch]
                notes_list.append(miditoolkit.Note(on_velocity, pitch, on_time, time))
        return notes_list

    @staticmethod
    def build_controls(temp_controls):
        controls_list = []
        for control in temp_controls:
            control, time, status = control
            if status:
                # control-on
                controls_list.append(miditoolkit.ControlChange(number=control, value=127, time=time))
            else:
                # control-off
                controls_list.append(miditoolkit.ControlChange(number=control, value=0, time=time))
        return controls_list

    def decode(self, integers, output_path):
        # decode to events
        words = self.integers_to_words(integers)
        events = self.words_to_events(words)

        # decode properties
        temp_notes, temp_controls = self.extract_events(events)

        # get specific time for items
        # notes
        notes = self.build_notes(temp_notes)
        # controls
        controls = self.build_controls(temp_controls)

        # write MIDI
        midi = miditoolkit.midi.parser.MidiFile(ticks_per_beat=self.default_ticks_per_beat)
        midi.ticks_per_beat = self.default_ticks_per_beat

        # program language is not encoded
        inst = miditoolkit.midi.containers.Instrument(0, is_drum=False, name='piano_track')
        # write instrument (notes)
        if self.decode_note:
            inst.notes = notes
        if self.decode_control:
            inst.control_changes = controls
        midi.instruments.append(inst)

        # export MIDI
        midi.dump(output_path)
