import json, sys
from ausp import *

datadir = os.path.expanduser('~/.au-sp')
sound_name = sys.argv[1]

def aulib(sound_dir):
    return os.path.join(datadir, 'audio', sound_dir)

def dicerdir(name):
    return os.path.join('dice', name)

source_sound_path = dicerdir(sound_name + '.wav')
json_path = dicerdir(sound_name + '.json')

if not os.path.isfile(source_sound_path):
    print 'Source sound', source_sound_path, 'not found'
    exit()
if not os.path.isfile(json_path):
    print 'json', json_path, 'not found'
    exit()

sound_lib_path = aulib(sound_name)
if not os.path.exists(sound_lib_path):
    print 'MAKING SOUND LIB DIRECTORY', sound_lib_path
    os.mkdir(sound_lib_path)
if os.listdir(sound_lib_path):
    print 'Clear out', sound_lib_path, 'before dicing'
    exit()

raw_shaker = RawSound(source_sound_path)
mix = Mixer("Let's chop chop")

with open(json_path) as f:
    times_lists = json.loads(f.readline())

start_times = times_lists['start_times']
end_times = times_lists['end_times']
reg_times = times_lists['reg_pt_times']

for st, et, rt, idx in zip(start_times, end_times, reg_times, range(len(start_times))):
    dur = et - st
    reg_offset = rt - st
    reg_offset_ms = int(reg_offset*1000)
    shift_shaker = ShiftedSound(raw_shaker, -st)
    clip = ClippedSound(shift_shaker, dur)
    Mixer.render_sound_to_file(clip, aulib('.'.join((
            os.path.join(sound_name, sound_name + '_' + str(idx)),
            str(reg_offset_ms),
            'wav'))))
    mix.play_sound(clip)

