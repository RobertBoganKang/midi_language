import argparse

from piano_track import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='encode & decode midi test with MIDI Language')
    parser.add_argument('--input', '-i', type=str, help='input file of audio file to encode/decode',
                        default='demo/piano_track.mid')
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
                         pitch_variation_range=(-6, 6),
                         velocity_scale_variation_range=(0.96, 1.04),
                         velocity_noise_scale_variation_range=(0.98, 1.02),
                         tempo_scale_variation_range=(0.9, 1.1))
    else:
        me = MidiEncoder(args.input, w2i)
    res = me.encode()

    # decode integer array to midi
    md = MidiDecoder(i2w)
    md.decode(res, args.output)
