# MIDI Language

## Introduction

### Reference

Paper: ***Pop Music Transformer: Beat-based Modeling and Generation of Expressive Pop Piano Compositions*** ([code](https://github.com/YatingMusic/remi))

This is a modified version with an extension of **multi-instrumental** support.

### Function

Convert Midi into `event` sequence, and represented by mapped `integer array` of tokens (used in NLP).

This could send to `NLP` models for AI auto music composition. 

Due to this project considers more about music structures as well as its chord and melody on higher level, including `note`, `drum`, `tempo`, musical instrument (`program` in midi) and its expressions  (`tempo` and `velocity`), rather than digging into too much details like sound source & direction, instrumental performing techniques (such as, bend sound, piano sustain pedal, violin overtones), the language of `MIDI` is design this way (see chapter `Details` below).

## Usage

See `language.py`, it contains procedures:

* load `w2i` (word to integer) and `i2w` (integer to word), for not calculating it every time;
* encode `midi` to `iteger array`, each object handle one `mid` file;
* decode `integer array` to `midi`, each object handle many results and export to `mid` files;

The code `language.py` has arguments:

*  `input`: input file of audio file to encode/decode;
* `output`: output file of audio file to encode;
* `train`: if have, it will switch to training mode with variations (data augmentation);

`MidiEncoder` data augmentation:

* `pitch_variation_range`: a random pitch shift within a range for whole midi;
* `velocity_scale_variation_range`: a random note/drum velocity scale for whole midi;
* `velocity_noise_scale_variation_range`: a random note/drum velocity scale for each element within midi;
* `tempo_scale_variation_range`: a random tempo change for whole midi;

`MidiDecoder` needs `numerator` and `denominator` time signatures for reconstructing midi files.

## Details

### Event Structure

#### Required:

* Bar
* Position (0~`split-1`)

#### Optional:

* note:
    * `Note`
    * `Program` (0~127)
    * `Pitch` (0~127)
    * `Velocity` (0~127)
    * `Duration` (0~`split`*`bar_scale-1`)
* drum:
    * `Drum`
    * `Program` (0~127)
    * `Pitch` (0~127)
    * `Velocity` (0~127)
    * `Duration` (0~`split`*`bar_scale-1`)
* chord:
    * `Chord` (`chroma_name`:`chord_name`)
* tempo:
    * `Tempo_Class` (`T0`~`Ti`)
    * `Tempo_Value` (0~59)
