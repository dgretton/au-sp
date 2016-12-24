from ausp import *
from math import pi, sin, cos

datadir = os.path.expanduser("~/.mu-sp")

def aulib(sound_dir):
    return os.path.join(datadir, "audio", sound_dir)

random_mid_drum = RandomSound()
random_mid_drum.populate_with_dir(aulib("snares_off"))
mid_drum = SpreadSound(random_mid_drum, (.2, .2, 0), 0, 1)

def generate_all_tracks(master_beat):
    master_beat.set_duration(5)
    print "WELL THATS THE EXTENT OF THAT"
    for section in master_beat.split_even(4):
        basic_tr = Track("...", Sound.default_rate)
        track_beat = basic_tr.link_root(section)
        for b in track_beat.split([10, 8, 7, 6.5, 6, 5.25]):
            b.attach(mid_drum, Location((pi/2, pi/4), 1))
        yield basic_tr

mainbeat = Beat()
#print "helohelo"
#for i in generate_all_tracks(mainbeat):
#    print "HELOOOO??"
#    print i
mix = Mixer("Let's yield, I guess...!", Sound.default_rate, list(generate_all_tracks(mainbeat)))
mix.play(quick_play=False)
