import argparse

from midi_language import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='encode & decode midi test with MIDI Language')
    parser.add_argument('--input', '-i', type=str, help='input file of audio file to encode/decode',
                        default='demo/in.mid')
    parser.add_argument('--output', '-o', type=str, help='output file of audio file to encode',
                        default='demo/out.mid')
    parser.add_argument('--train', '-t', action='store_true', help='training mode with variations (data augmentation)')
    args = parser.parse_args()

    # initialize dict once
    w2i, i2w = EventDict().check_and_load_dict()
    print(f'Dict length: {len(w2i)}')

    # encode midi to integer array
    if args.train:
        me = MidiEncoder(args.input, w2i,
                         pitch_variation_range=(-12, 12),
                         velocity_scale_variation_range=(0.8, 1),
                         velocity_noise_scale_variation_range=(0.95, 1.05),
                         tempo_scale_variation_range=(0.7, 1.4))
    else:
        me = MidiEncoder(args.input, w2i)
    res = me.encode()

    # decode integer array to midi
    md = MidiDecoder(i2w, numerator=4, denominator=4)
    md.decode(res, args.output)
