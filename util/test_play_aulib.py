import sys, os
from ausp import *

datadir = os.path.expanduser('~/.au-sp')
sound_name = sys.argv[1]

def aulib(sound_dir):
    return os.path.join(datadir, 'audio', sound_dir)

sound_lib_path = aulib(sound_name)
if not os.path.exists(sound_lib_path):
    print 'Cannot find lib', sound_lib_path

test_sound = RandomSound()
test_sound.populate_with_dir(sound_lib_path)

track = Track('tester', Sound.default_rate)
top_beat = track.link_root(Beat())
for b in top_beat.split_even(50):
    b.set_duration(.11)
    b.attach(test_sound, Location((0, .6, 0)))

mix = Mixer("Anything but... That.", tracks=[track])
mix.play()

