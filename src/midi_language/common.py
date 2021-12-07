import os


class Common(object):
    """
    ref: https://github.com/YatingMusic/remi
    """

    def __init__(self):
        # position per bar ==> `default_split_fraction`
        self.bar_split_fraction = 32
        self.max_duration_bars = 1
        self.separator = '~'
        self.dic_path = os.path.join(os.path.dirname(__file__), 'dic.pkl')
        # tempos (do not change)
        self.default_tempo_intervals = [range(30, 90), range(90, 150), range(150, 210), range(210, 270)]

        # switch (element to build)
        self.with_note = True
        self.with_drum = True
        self.with_tempo = True
        self.with_chord = True
        self.include_program = True


class Item(object):
    def __init__(self, name, start, end, velocity, pitch, program):
        self.name = name
        self.start = start
        self.end = end
        self.velocity = velocity
        self.pitch = pitch
        self.program = program

    def __repr__(self):
        return f'Item(name={self.name}, start={self.start}, end={self.end}, ' \
               f'velocity={self.velocity}, pitch={self.pitch}, program={self.program})'


class Event(object):
    """
    Event Structure:
    1. Required:
    * `Bar`
    * `Position` (0~`split-1`)

    2. Optional:
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
    """

    def __init__(self, name, time, value, text):
        self.name = name
        self.time = time
        self.value = value
        self.text = text

    def __repr__(self):
        return f'Event(name={self.name}, time={self.time}, value={self.value}, text={self.text})'
