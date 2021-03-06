import os


class Common(object):
    def __init__(self):
        self.quantized_time = 0.02
        self.max_time_or_duration = 5
        self.default_beat_per_minute = 120
        self.separator = '~'
        self.dic_path = os.path.join(os.path.dirname(__file__), 'dic.pkl')

        # switch (element to build)
        self.with_note = True
        self.with_control = True

        # calculate
        self.quantized_max_frame = int(self.max_time_or_duration / self.quantized_time)


class Item(object):
    def __init__(self, name, time, velocity, pitch):
        self.name = name
        self.time = time
        self.velocity = velocity
        self.pitch = pitch

    def __repr__(self):
        return f'Item(name={self.name}, time={self.time}, ' \
               f'velocity={self.velocity}, pitch={self.pitch})'


class Event(object):
    """
    Event Structure:
    * note:
        * note-on:
            * `NoteOn` (0~127)
            * `Velocity` (0~127)
        * note-off:
            * `NoteOff` (0~127)
    * paddle:
        * `PaddleOn` (64~69)
        * `PaddleOff` (64~69)
    * delta time:
        * `Time` (0~`max_time_or_duration`/`quantized_time`)
    """

    def __init__(self, name, time, value, text):
        self.name = name
        self.time = time
        self.value = value
        self.text = text

    def __repr__(self):
        return f'Event(name={self.name}, time={self.time}, value={self.value}, text={self.text})'
