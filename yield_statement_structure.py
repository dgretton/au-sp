from ausp import *
from math import pi, sin, cos
from random import randint, random

datadir = os.path.expanduser("~/.au-sp")

def aulib(sound_dir):
    return os.path.join(datadir, "audio", sound_dir)

def rhlib(rh_name):
    return os.path.join(datadir, "rhythm", rh_name + ".rh")

random_mid_drum = RandomSound()
random_mid_drum.populate_with_dir(aulib("long_low_tom"))
random_mid_drum.populate_with_dir(aulib("short_low_tom"))
random_mid_drum.populate_with_dir(aulib("long_high_tom"))
random_mid_drum.populate_with_dir(aulib("short_high_tom"))
mid_drum = SpreadSound(random_mid_drum, (.2, .2, 0), 0, 1)

random_xylo = RandomPitchedSound()
random_xylo.populate_with_dir(aulib("g_major_xylo"))

raw_bassy = RawPitchedSound(aulib("werb_sine") + "/werb_sine.0.110.wav")
raw_bassy = RawPitchedSound(aulib("voice_oo") + "/loud.0.287.wav")
raw_bassy_rasp = RawPitchedSound(aulib("rasp_bass") + "/rasp_bass_1.0.110.wav")

bass_pulse = RandomSound()
bass_pulse.populate_with_dir(aulib("bass_pulse"))

ding = RandomSound()
ding.populate_with_dir(aulib("crystal_ding"))

Cm7 = ["C", "Eb", "G", "Bb"]
EbM9= ["Eb", "F", "G", "Bb"]
G9 = ["C", "D", "G", "A"]
D = ["D", "F#", "A"]

def random_arpeggiate(scale, jitter=0, start_octave=3):
    up = True
    pitch_list = [(p, octv) for p, octv in zip(scale, [str(start_octave)]*len(scale))]
    octave = start_octave
    radius = 0
    while True:
        if len(pitch_list) < len(scale):
            octave += 1 if up else -1
            pitch_list += [(p, octv) for p, octv in zip((scale if up else reversed(scale)),
                [str(octave)]*len(scale))]
        if abs(octave - start_octave) > radius:
            octave = start_octave + (radius if up else -radius)
            up = not up # the whole world turned upside down
        print up, octave
        yield "_".join(pitch_list.pop(randint(0, jitter)) if jitter else pitch_list.pop(0))

def double_nest(beat, arpeggiator):
    for section in beat.split_even(4):
        basic_tr = Track("...", Sound.default_rate)
        track_beat = basic_tr.link_root(section)
        for b, arpeg_pitch in zip(track_beat.split_even(6),
                #[10, 8, 7, 6.5, 6, 5.25]),
                arpeggiator):
            for sb in b.split_even(randint(2, 5)):
                sb.attach(random_xylo.for_pitch(arpeg_pitch), Location((pi/2, pi/4), 1))
        yield basic_tr

def nested_yield_test(beat):
    beat1, beat2 = beat.split_even(2)
    arp = random_arpeggiate(test_scale, jitter=3, start_octave=4)
    for t in double_nest(beat1, arp):
        yield t
    for t in double_nest(beat2, arp):
        yield t

eighth_dur = .3

def six_chords(beat, bassy_dict = {}):
    chords = [D, G9, D, Cm7, Cm7, EbM9, EbM9]
    last_chord = None
    arpeggiator = None
    bass_track = Track("Arp Bass", Sound.default_rate, end_padding=1.0)
    track_beat = bass_track.link_root(beat)
    for meas_beat, chord in zip(track_beat.split_even(6), chords):
        if chord != last_chord:
            arpeggiator = random_arpeggiate(chord, jitter=1, start_octave=2)
        last_chord = chord
        for b, pitch1, pitch2 in zip(meas_beat.split_even(16), arpeggiator, arpeggiator):
            b.set_duration(eighth_dur)
            loc = Location((pi*random(), pi/4*random()), 1.0 + random())

            print "this is bassy was there", pitch1 in bassy_dict, "at", pitch1
            bassy = bassy_dict.get(pitch1, RandomIntervalSound(raw_bassy.for_pitch(pitch1),
                eighth_dur*2, margin=.01))
            bassy_dict[pitch1] = bassy

            #b.attach(bassy, loc)

            bassy = bassy_dict.get(pitch2, RandomIntervalSound(raw_bassy.for_pitch(pitch2),
                eighth_dur*2, margin=.01))
            bassy_dict[pitch2] = bassy

            #b.attach(bassy, loc)

            #b.attach(RandomIntervalSound(raw_bassy_rasp.for_pitch(pitch1), eighth_dur*2.2, margin=.01), loc)
            b1, b2 = b.split_even(2)
            b1.attach(random_mid_drum, Location((-pi*random(), pi/4*random()), .5 + random()*1))
            if random() < .25:
                pass
                b2.attach(random_mid_drum, Location((-pi*random(), pi/4*random()), 2.0 + random()*2))

    yield bass_track

    synco_dings = Track("Syncopated Ding", Sound.default_rate)
    synco_beat = synco_dings.link_root(beat)
    with open(rhlib("america")) as rf:
        char_times = eval(''.join(rf.readline()))
    for ding_beat in synco_beat.interleave_split(char_times)['j']:
        ding_beat.attach(ding, Location((0, 0), 3))
    #yield synco_dings
        

def generate_all_tracks(master_beat):
    for b in master_beat.split_even(2):
        for t in six_chords(b):
            yield t

mainbeat = Beat()
mix = Mixer("Let's yield, I guess...!", Sound.default_rate, list(generate_all_tracks(mainbeat)))
mix.play(quick_play=True)

