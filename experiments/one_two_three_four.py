# So here's the idea for a song: there's a pattern of numbers 1-4 that defines the whole song. However, the definition is at the meta-est possible level: it means, given a list of things to operate on of the same length as the list of numbers 1-4, and four "things to do" (functions, probably), do the indicated thing to each thing, e.g. given 3 measures and [2, 4, 1], do the second thing to the first measure, the fourth thing to the second measure, and the first thing to the third measure. So, the motif specified by the initial pattern of numbers appears throughout the fabric of the piece, and everything is subject to it.

template = [1, 2, 4, 3, 1, 2]


from ausp import *
from math import pi, sin, cos
from random import randint, random
import os


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
        print "doin thing"
        yield actions[index - 1](thing) # I just wanted it to be 1-indexed... but pain... hrr

def new_track_for_beat(beat, name='--', mom_track=None):
    new_tr = Track(name, Sound.default_rate, end_padding=2.0)
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

low_drum = RandomSound()
low_drum.populate_with_dir(aulib("long_low_tom"))
high_drum = RandomSound()
high_drum.populate_with_dir(aulib("long_high_tom"))
clap = RandomSound()
clap.populate_with_dir(aulib("wussy_clap"))
pulse = RandomSound()
pulse.populate_with_dir(aulib("bass_pulse"))
snare = RandomSound()
snare.populate_with_dir(aulib("snares_off"))
cymbal = RandomSound()
cymbal.populate_with_dir(aulib("cymbal_long"))
bass = RandomSound()
bass.populate_with_dir(aulib("bass_drum_clink"))

def add_low_tom(b):
    b.attach(low_drum, Location((1, 1), 1))

raw_bassy = RawPitchedSound(aulib("werb_sine") + "/werb_sine.0.110.wav")
raw_bassy = RawPitchedSound(aulib("voice_oo") + "/loud.0.287.wav")
raw_bassy_rasp = RawPitchedSound(aulib("rasp_bass") + "/rasp_bass_1.0.110.wav")

def add_bass_blip(b, plus):
#            bassy = bassy_dict.get(pitch1, RandomIntervalSound(raw_bassy.for_pitch(pitch1),
#                eighth_dur*2, margin=.01))
#            bassy_dict[pitch1] = bassy
#
    b.attach(RandomIntervalSound(raw_bassy.for_pitch(['C', 'D', 'E', 'F', 'G', 'A', 'B'][plus%7] + "_2"), .3), Location((-1, 1), 1))

def cover_evenly(thing, reps, func):
    for t in abstract_split(thing, reps):
        yield func(t)

def even_coverer(reps, func):
    print "ok, yes"
    return lambda b: cover_evenly(b, reps, func)

def three_to_one(beat, first_func, second_func):
    b1, b2 = beat.split([3,1])
    print "got this far"
    yield first_func(b1)
    yield second_func(b2)

def eight_alternate(beat, first_func, second_func, fill=None):
    if fill is None:
        fill = second_func
    first7, last = beat.split([7, 1])
    for b, f in zip(first7.split_even(7), [first_func, second_func]*4):
        list(f(b))

def hash_rand(x):
    return (hash(str(hash(str(x)))) % 65536)/65536.0

from types import GeneratorType

def flatten(*stack):
    stack = list(stack)
    while stack:
        try: x = stack[0].next()
        except StopIteration:
            stack.pop(0)
            continue
        if isinstance(x, GeneratorType): stack.insert(0, x)
        else: yield x

def locator(seed):
    return lambda x: Location((hash_rand(x*seed)*2*pi, hash_rand(-x*seed)*pi), 2)

def generate_all_tracks():
    mainbeat = Beat()
    mainbeat.set_duration(20)
    sound_options = [bass, low_drum, cymbal, snare]
    loc_options = [locator(i) for i in range(4)]
    basic_tr = new_track_for_beat(mainbeat)
    top_b = basic_tr.top_beat
    def attchr(tup):
        i, snd = tup
        return lambda b: b.attach(snd, locator(i)(0))
    aops = [attchr(x) for x in enumerate(sound_options)]
    permutors = [pick_permutor(i + 1) for i in range(4)]
    eight_alternate_options = [
            lambda b: eight_alternate(b, even_coverer(2, aops[0]), even_coverer(2, aops[0])),
            lambda b: eight_alternate(b, even_coverer(2, aops[3]), even_coverer(4, aops[1])),
            lambda b: eight_alternate(b, lambda bb: three_to_one(bb, even_coverer(3, aops[2]), aops[0]),
                even_coverer(2, aops[0])),
            lambda b: eight_alternate(b, lambda bb: three_to_one(bb, even_coverer(3, aops[3]), aops[2]),
                even_coverer(2, aops[0]), even_coverer(1, aops[3]))
            ]

    sections = [new_track_for_beat(b, mom_track=basic_tr) for b in top_b.split_even(len(template))]
    sec_top_bs = [sec.top_beat for sec in sections]
    list(process(sec_top_bs, eight_alternate_options))
    for sec in sections:
        yield sec

    another_go_track = new_track_for_beat(top_b, mom_track=basic_tr)
    sections = [new_track_for_beat(b, mom_track=another_go_track) for b in another_go_track.top_beat.split_even(len(template))]
    sec_top_bs = [sec.top_beat for sec in sections]
    print sec_top_bs
    #sec_top_bs = list(pick_permute(sec_top_bs, 3))
    sec_top_bs = sec_top_bs[3:] + sec_top_bs[:3]
    print sec_top_bs
    list(process(sec_top_bs, eight_alternate_options))
    for sec in sections:
        yield sec

    yield basic_tr

mix = Mixer("Let's template, I guess...!", Sound.default_rate, list(generate_all_tracks()))
mix.play(quick_play=True)

