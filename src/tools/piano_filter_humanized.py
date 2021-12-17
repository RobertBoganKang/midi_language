import argparse
import os
import shutil

import miditoolkit

# https://github.com/RobertBoganKang/file_processing
from file_processing import FileProcessing


class FilterMIDI(FileProcessing):
    """
    filter midi with specific requirement
    """

    def __init__(self, ops):
        super().__init__(ops)

    @staticmethod
    def print_error(in_path):
        print(f'WARNING: [{in_path}] is not humanized piano performance!')

    def do(self, in_path, out_path):
        if os.path.exists(out_path):
            return
        # noinspection PyBroadException
        try:
            # read midi now
            midi_obj = miditoolkit.midi.parser.MidiFile(in_path)
            notes_v = []
            notes_t = []
            notes_d = set()
            if len(midi_obj.tempo_changes) > 2:
                self.print_error(in_path)
                return
            for instrument in midi_obj.instruments:
                if instrument.program != 0:
                    self.print_error(in_path)
                    return
                if instrument.is_drum:
                    self.print_error(in_path)
                    return
                for note in instrument.notes:
                    notes_v.append(note.velocity)
                    notes_t.append(note.start)
                    notes_d.add(note.end - note.start)
            notes_t.sort()
            # check repeat
            counter = 0
            for i in range(len(notes_v) - 2):
                a = notes_v[i]
                b = notes_v[i + 1]
                c = notes_v[i + 2]
                if a == b == c:
                    counter += 1
            repeat_v_ratio = counter / len(notes_v)
            counter = 0
            for i in range(len(notes_t) - 2):
                a = notes_t[i]
                b = notes_t[i + 1]
                c = notes_t[i + 2]
                if a == b == c:
                    counter += 1
            repeat_t_ratio = counter / len(notes_t)
            if repeat_v_ratio > 0.01 or repeat_t_ratio > 0.01 or len(notes_d) < 100:
                self.print_error(in_path)
                return
            shutil.copy(in_path, out_path)
        except Exception:
            print(f'ERROR: [{in_path}] cannot decode!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='filter midi with specific requirement')
    fp_group = parser.add_argument_group('file processing arguments')
    fp_group.add_argument('--input', '-i', type=str, help='the input folder/file, or a text file for paths',
                          default='in')
    fp_group.add_argument('--in_format', '-if', type=str, help='the input format', default='mid')
    fp_group.add_argument('--output', '-o', type=str, help='the output folder/file', default='out')
    fp_group.add_argument('--out_format', '-of', type=str, help='the output format', default='mid')
    fp_group.add_argument('--cpu_number', '-j', type=int, help='cpu number of processing', default=0)

    filter_group = parser.add_argument_group('filter midi arguments')

    args = parser.parse_args()

    # do operation
    FilterMIDI(args)()
