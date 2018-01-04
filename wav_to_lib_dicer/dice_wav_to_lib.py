import json, sys
sys.path += ['../']
from ausp import *

datadir = os.path.expanduser('~/.au-sp')

def aulib(sound_dir):
    return os.path.join(datadir, 'audio', sound_dir)

raw_shaker = RawSound(sys.argv[1] + '.wav')
mix = Mixer("Let's chop chop")

with open(sys.argv[1] + '.json') as f:
    times_lists = json.loads(f.readline())

start_times = times_lists['start_times']
end_times = times_lists['end_times']

for st, et, idx in zip(division_times, end_times, range(len(division_times))):
    dur = et - st
    shift_shaker = ShiftedSound(raw_shaker, -st)
    clip = ClippedSound(shift_shaker, dur)
    Mixer.render_sound_to_file(clip,
            aulib('.'.join(('shaker_singles/shaker_singles_' + str(idx), str(10), 'wav'))))

