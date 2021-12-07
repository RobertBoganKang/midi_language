# MIDI Language

## Introduction

### Reference

Paper: ***Pop Music Transformer: Beat-based Modeling and Generation of Expressive Pop Piano Compositions***: [code]((https://github.com/YatingMusic/remi))

This is a modified version with an extension of **multi-instrumental** support.

### Function

Convert Midi into `event` sequence, and represented by mapped `integer array`.

This could send to `NLP` models for AI auto music composition. 

Due to this project considers more about music structures as well as its chord and melody on higher level, including `note`, `drum`, `tempo`, musical instrument (`program` in midi) and its expressions  (`tempo` and `velocity`), rather than digging into too much details like sound source & direction, instrumental performing techniques (such as, bend sound, piano sustain pedal, violin overtones), the language of `MIDI` is design this way (see chapter `Details` below).

## Usage

See `demo.py`, it contains procedures:

* load `w2i` (word to integer) and `i2w` (integer to word), for not calculating it every time;
* encode `midi` to `iteger array`, each object handle one `mid` file;
* decode `integer array` to `midi`, each object handle many results and export to `mid` files;

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
