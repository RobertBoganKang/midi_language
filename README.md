# MIDI Language

## Introduction

Convert Midi into `event` sequence, and represented by mapped `integer array` of tokens (used in NLP).

This could send to `NLP` models for AI auto music composition. 

### multi-instrumental (`multi_track`)

Reference: ***Pop Music Transformer: Beat-based Modeling and Generation of Expressive Pop Piano Compositions*** ([code](https://github.com/YatingMusic/remi)).

Due to **multi-instrumental** considers more about music structures as well as its `chord` and melody on higher level, including `note`, `drum`, `tempo`, musical instrument (`program` in midi) and its expressions  (`tempo` and `velocity`), rather than digging into too much details like sound source & direction, instrumental performing techniques (such as, bend sound, piano sustain pedal, violin overtones), the language of `MIDI` is design this way (see chapter `Details` below).

Library `multi_track_a` extend `REMI` with `Drum` and multi-instrumental support with  `Program`, whereas `multi_track_b` combines the `Position` representations and removes redundant `Note`/`Drum` identifier such that shorten the token size.

### piano (`piano_track)

Reference: **Google Magenta Music-Transformer** and **OpenAI MuseNet**.

Due to **humanized piano** performance ignores the properties of different instrument `program`, and `tempo` changes (keep as ticks precision), but add more piano techniques properties with `controls` (range from `64` to `69`) to keep paddle actions.

Library `piano_track_a` is *Magenta* like version, whereas `piano_track_b` convert `note-off` property into `duration` for better representation, because **Notes** cares about its starting time and duration, and **Paddle** cares about where it will start or end.

## Usage

### Demo code

See the demo file `language_<package>.py`, it contains procedures:

* load `w2i` (word to integer) and `i2w` (integer to word), for not calculating it every time;
* encode `midi` to `iteger array`, each object handle only one `.mid` file, but each `encode()` function can give different variations for data augmentation;
* decode `integer array` to `midi`, each object handle many results and export to `.mid` files;

### Arguments

#### `language_<package>.py`

*  `input`: input file of audio file to encode/decode;
* `output`: output file of audio file to encode;
* `train`: if have, it will switch to training mode with variations (data augmentation);

#### `MidiEncoder` and `MidiDecoder`

Data Augmentation in `MidiEncoder`:

* `pitch_variation_range`: a random pitch shift within a range for whole midi;
* `velocity_scale_variation_range`: a random note/drum velocity scale for whole midi;
* `velocity_noise_scale_variation_range`: a random note/drum velocity scale for each element within midi;
* `tempo_scale_variation_range`: a random tempo change for whole midi;

In package `lib/multi_track`, `MidiDecoder` needs `numerator` and `denominator` time signatures for reconstructing midi files.

## Details

### Event Structure

To see the design of language, please check the comment  at `lib/<package_name>/common.py` in `Event` class.

