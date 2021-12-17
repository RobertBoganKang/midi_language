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
        self.numerator = ops.numerator
        self.denominator = ops.denominator

    def do(self, in_path, out_path):
        if os.path.exists(out_path):
            return
        status = False
        # noinspection PyBroadException
        try:
            # read midi now
            midi_obj = miditoolkit.midi.parser.MidiFile(in_path)
            if len(midi_obj.time_signature_changes) > 0:
                # assume, time signature will not change
                num = midi_obj.time_signature_changes[0].numerator
                den = midi_obj.time_signature_changes[0].denominator
                if num in self.numerator and den in self.denominator:
                    status = True
                else:
                    print(f'WARNING: [{in_path}] time_sig is {num}/{den}!')
            else:
                status = True
        except Exception:
            print(f'ERROR: [{in_path}] cannot decode!')
        if status:
            shutil.copy(in_path, out_path)


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
    filter_group.add_argument('--numerator', '-n', type=int, help='the numerator of time signature', nargs='+',
                              default=(2, 4))
    filter_group.add_argument('--denominator', '-d', type=int, help='the numerator of time signature', nargs='+',
                              default=(2, 4))

    args = parser.parse_args()

    # do operation
    FilterMIDI(args)()
