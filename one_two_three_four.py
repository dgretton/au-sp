# So here's the idea for a song: there's a pattern of numbers 1-4 that defines the whole song. However, the definition is at the meta-est possible level: it means, given a list of things to operate on of the same length as the list of numbers 1-4, and four "things to do" (functions, probably), do the indicated thing to each thing, e.g. given 3 measures and [2, 4, 1], do the second thing to the first measure, the fourth thing to the second measure, and the first thing to the third measure. So, the motif specified by the initial pattern of numbers appears throughout the fabric of the piece, and everything is subject to it.

template = [1, 2, 4, 3, 1, 2]


from ausp import *
from math import pi, sin, cos
from random import randint, random


datadir = os.path.expanduser("~/.au-sp")

def aulib(sound_dir):
    return os.path.join(datadir, "audio", sound_dir)

def rhlib(rh_name):
    return os.path.join(datadir, "rhythm", rh_name + ".rh")


def process(things, actions):
    if len(things) != len(template):
        print "Didn't align some stuff right..."
        print "Here are some things that should have lined up with", str(template) + ':'
        print things
        exit()
    if len(actions) != 4:
        print "Gotta be 4 things to do to things, that's the point, man!"
        print actions
        exit()
    for thing, index in zip(things, template):
        yield actions[index - 1](thing) # I just wanted it to be 1-indexed... but pain... hrr

def new_track_for_beat(beat, name='--', mom_track=None):
    new_tr = Track(name, Sound.default_rate)
    new_tr.link_root(beat, mom_track)
    return new_tr

def abstract_split(thing, num):
    if num <= 0:
        print "What are you even splitting?"
        exit()
    if isinstance(thing, Beat):
        if num == 1:
            yield thing
            return
        for splut in thing.split_even(num):
            yield splut
    elif isinstance(thing, Track):
        yield thing
        for n in range(num - 1):
            yield new_track_for_beat(thing.top_beat, thing.name + "_" + str(n), thing)
    else:
        for leftover in [thing]*num:
            yield leftover

def abstract_splitter(num):
    return lambda x: abstract_split(x, num)

def template_split(things):
    for thing, index in zip(things, template):
        yield abstract_split(thing, index)

def abstract_destroy(thing):
    if isinstance(thing, Beat):
        thing.clear()
        return
    else:
        del thing
        return
    yield # News! You're a generator!

nothing = lambda a: a

def pick_permute(things, step):
    place = step
    things = list(things)
    while things:
        yield things.pop(place % len(things))
        place += step

def pick_permutor(step):
    return lambda x: pick_permute(x, step)

random_low_drum = RandomSound()
random_low_drum.populate_with_dir(aulib("long_low_tom"))

def add_low_tom(b):
    b.attach(random_low_drum, Location((1, 1), 1))

raw_bassy = RawPitchedSound(aulib("werb_sine") + "/werb_sine.0.110.wav")
raw_bassy = RawPitchedSound(aulib("voice_oo") + "/loud.0.287.wav")
raw_bassy_rasp = RawPitchedSound(aulib("rasp_bass") + "/rasp_bass_1.0.110.wav")

def add_bass_blip(b, plus):
#            bassy = bassy_dict.get(pitch1, RandomIntervalSound(raw_bassy.for_pitch(pitch1),
#                eighth_dur*2, margin=.01))
#            bassy_dict[pitch1] = bassy
#
    b.attach(RandomIntervalSound(raw_bassy.for_pitch(['C', 'D', 'E', 'F', 'G', 'A', 'B'][plus%7] + "_2"), .3), Location((-1, 1), 1))

def generate_all_tracks():
    mainbeat = Beat()
    mainbeat.set_duration(10)
    basic_tr = new_track_for_beat(mainbeat)
    splitters =  [abstract_splitter((i + 1)*3) for i in range(4)]
    splits = process(basic_tr.top_beat.split_even(len(template)), splitters)
    permutors = [pick_permutor(i + 1) for i in range(4)]
    permuted = process(list(splits), permutors)
    for split in permuted:
        for i, b in enumerate(split):
            add_low_tom(b)
            add_bass_blip(b, i)
    yield basic_tr

mix = Mixer("Let's template, I guess...!", Sound.default_rate, list(generate_all_tracks()))
mix.play(quick_play=True)
