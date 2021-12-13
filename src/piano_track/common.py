import os


class Common(object):
    def __init__(self):
        self.quantized_time = 0.02
        self.max_time_or_duration = 10
        self.default_beat_per_minute = 120
        self.separator = '~'
        self.dic_path = os.path.join(os.path.dirname(__file__), 'dic.pkl')

        # switch (element to build)
        self.with_note = True
        self.with_control = True

        # calculate
        self.quantized_max_frame = int(self.max_time_or_duration / self.quantized_time)


class Item(object):
    def __init__(self, name, start, end, velocity, pitch):
        self.name = name
        self.start = start
        self.end = end
        self.velocity = velocity
        self.pitch = pitch

    def __repr__(self):
        return f'Item(name={self.name}, start={self.start}, end={self.end}, ' \
               f'velocity={self.velocity}, pitch={self.pitch})'


class Event(object):
    """
    Event Structure:
    * note:
        * `Pitch` (0~127)
        * `Velocity` (0~127)
        * `Duration` (0~`max_time_or_duration`/`quantized_time`)
    * paddle:
        * `Control` (64~69)
        * `Duration` (0~`max_time_or_duration`/`quantized_time`)
    * delta time:
        * `Duration` (0~`max_time_or_duration`/`quantized_time`)
    """

    def __init__(self, name, time, value, text):
        self.name = name
        self.time = time
        self.value = value
        self.text = text

    def __repr__(self):
        return f'Event(name={self.name}, time={self.time}, value={self.value}, text={self.text})'
