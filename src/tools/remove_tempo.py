import argparse
import os

import miditoolkit

# https://github.com/RobertBoganKang/file_processing
from file_processing import FileProcessing


class RemoveTempoSingle(object):
    def __init__(self, in_path, out_path, tempo_scale=1, ticks_per_beat=480):
        super().__init__()
        self.tempo_scale = tempo_scale
        self.default_beat_per_minute = 120
        self.default_ticks_per_beat = ticks_per_beat

        # system param
        self.tick_delta_time = []
        self.accumulated_tick_time = []
        self.ticks_per_beat = None
        self.max_tick = None
        self.tempos = None
        self.instruments = None

        # calculate
        self.initialize_midi(in_path)
        self.build_tempo_ticks()
        self.remove(out_path)

    def initialize_midi(self, path):
        # read midi now
        midi_obj = miditoolkit.midi.parser.MidiFile(path)
        self.ticks_per_beat = midi_obj.ticks_per_beat
        self.max_tick = midi_obj.max_tick
        self.tempos = midi_obj.tempo_changes
        self.instruments = midi_obj.instruments

    def build_tempo_ticks(self):
        tempo_timestamp = []
        for tempo_obj in self.tempos:
            tempo = tempo_obj.tempo
            time = tempo_obj.time
            tempo_timestamp.append([time, tempo])
        tempo_timestamp.sort(key=lambda x: x[0])
        if len(tempo_timestamp) == 0 or tempo_timestamp[0][0] != 0:
            tempo_timestamp = [[0, self.default_beat_per_minute]] + tempo_timestamp
        tempo_timestamp = tempo_timestamp + [[self.max_tick, self.default_beat_per_minute]]
        # calculate accumulate tick
        for i in range(len(tempo_timestamp) - 1):
            delta_time = tempo_timestamp[i + 1][0] - tempo_timestamp[i][0]
            tempo = tempo_timestamp[i][1]
            for _ in range(delta_time):
                scaled_tick = (self.tempo_scale *
                               self.default_beat_per_minute / tempo
                               / self.ticks_per_beat * self.default_ticks_per_beat)
                self.tick_delta_time.append(scaled_tick)
        accumulate = 0
        for st in self.tick_delta_time:
            self.accumulated_tick_time.append(int(round(accumulate)))
            accumulate += st

    def remove(self, out_path):
        # write MIDI
        midi = miditoolkit.midi.parser.MidiFile(ticks_per_beat=self.default_ticks_per_beat)
        for instrument in self.instruments:
            program = instrument.program
            is_drum = instrument.is_drum
            if is_drum:
                word = 'drum_'
            else:
                word = 'instrument_'
            inst = miditoolkit.midi.containers.Instrument(program, is_drum=is_drum,
                                                          name=word + str(program))
            # rebuild notes
            rebuild_notes = []
            for note in instrument.notes:
                pitch = note.pitch
                velocity = note.velocity
                st = self.accumulated_tick_time[note.start]
                et = self.accumulated_tick_time[note.end]
                rebuild_notes.append(miditoolkit.Note(velocity, pitch, st, et))
            inst.notes = rebuild_notes
            # rebuild controls
            rebuild_controls = []
            for control in instrument.control_changes:
                number = control.number
                value = control.value
                time = self.accumulated_tick_time[control.time]
                rebuild_controls.append(miditoolkit.ControlChange(number, value, time))
            inst.control_changes = rebuild_controls
            # push tracks
            midi.instruments.append(inst)
        # export MIDI
        midi.dump(out_path)


class RemoveTempo(FileProcessing):
    def __init__(self, ops):
        super().__init__(ops)
        self.tempo_scale = ops.tempo_scale
        self.ticks_per_beat = ops.ticks_per_beat

    def do(self, in_path, out_path):
        if os.path.exists(out_path):
            return
        RemoveTempoSingle(in_path, out_path,
                          tempo_scale=self.tempo_scale,
                          ticks_per_beat=self.ticks_per_beat)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='remove midi tempo to not-aligned style')
    fp_group = parser.add_argument_group('file processing arguments')
    fp_group.add_argument('--input', '-i', type=str, help='the input folder/file, or a text file for paths',
                          default='in')
    fp_group.add_argument('--in_format', '-if', type=str, help='the input format', default='mid')
    fp_group.add_argument('--output', '-o', type=str, help='the output folder/file', default='out')
    fp_group.add_argument('--out_format', '-of', type=str, help='the output format', default='mid')
    fp_group.add_argument('--cpu_number', '-j', type=int, help='cpu number of processing', default=0)

    filter_group = parser.add_argument_group('remove tempo arguments')
    filter_group.add_argument('--tempo_scale', '-ts', type=int, help='the numerator of time signature',
                              default=1)
    filter_group.add_argument('--ticks_per_beat', '-tpb', type=int, help='the numerator of time signature',
                              default=480)
    args = parser.parse_args()

    RemoveTempo(args)()
