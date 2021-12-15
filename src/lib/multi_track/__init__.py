import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from decoder import MidiDecoder
    from encoder import MidiEncoder
    from event_dict import EventDict
except Exception:
    raise ValueError('ERROR: cannot import!')
