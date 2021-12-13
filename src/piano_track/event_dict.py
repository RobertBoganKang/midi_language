import os
import pickle
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from common import Common, Event
except Exception:
    raise ValueError('ERROR: cannot import!')


class EventDict(Common):
    def __init__(self):
        super().__init__()

        self.global_counter = 0
        self.w2i = {}
        self.i2w = {}

        # calculate
        self.build_all()

    def update(self, word):
        self.w2i[word] = self.global_counter
        self.i2w[self.global_counter] = word
        self.global_counter += 1

    def build_control(self):
        """ piano_track control from `64` to `69` """
        for control in range(64, 70):
            self.update('Control' + self.separator + str(control))

    def build_velocity(self):
        for velocity in range(128):
            self.update('Velocity' + self.separator + str(velocity))

    def build_pitch(self):
        for pitch in range(128):
            self.update('Pitch' + self.separator + str(pitch))

    def build_duration(self):
        for duration in range(1, self.quantized_max_frame + 1):
            self.update('Duration' + self.separator + str(duration))

    def build_all(self):
        if self.with_control:
            self.build_control()
        if self.with_note or self.with_control:
            self.build_pitch()
            self.build_velocity()
            self.build_duration()

    def export(self):
        result = [self.w2i, self.i2w]
        with open(self.dic_path, 'wb') as w:
            pickle.dump(result, w)

    def check_and_load_dict(self):
        if not os.path.exists(self.dic_path):
            self.export()
        with open(self.dic_path, 'rb') as f:
            w2i, i2w = pickle.load(f)
        return w2i, i2w
