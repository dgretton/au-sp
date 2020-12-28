from ausp import *
from math import pi, sin, cos
from random import randint, random

datadir = os.path.expanduser("~/.au-sp")

def aulib(sound_dir):
    return os.path.join(datadir, "audio", sound_dir)

def rhlib(rh_name):
    return os.path.join(datadir, "rhythm", rh_name + ".rh")

def generic_spread_sound(aulib_name):
    random_sound = RandomSound()
    random_sound.populate_with_dir(aulib(aulib_name))
    return SpreadSound(random_sound, (.2, .2, 0), 0, 1)


high_tom = generic_spread_sound("long_high_tom")
low_tom = generic_spread_sound("long_low_tom")
tink = ClippedSound(generic_spread_sound("wussy_clap"), 1)
snare = generic_spread_sound("snares_off")

random_xylo = RandomPitchedSound()
random_xylo.populate_with_dir(aulib("g_major_xylo"))

raw_bassy = RawPitchedSound(aulib("werb_sine") + "/werb_sine.0.110.wav")
raw_bassy = RawPitchedSound(aulib("voice_oo") + "/loud.0.287.wav")
raw_bassy_rasp = RawPitchedSound(aulib("rasp_bass") + "/rasp_bass_1.0.110.wav")

bass_pulse = RandomSound()
bass_pulse.populate_with_dir(aulib("bass_pulse"))

ding = RandomSound()
ding.populate_with_dir(aulib("crystal_ding"))

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

eighth_dur = .15

def nice_random_location(r):
    return Location((2*pi*random(), pi/2*random()), r)

def chorus_rhythm(beat):
    drums = Track("DrUmS", Sound.default_rate)
    drums_beat = drums.link_root(beat)
    two_in, the_rest = drums_beat.split(2)

    for hit, tom in zip(two_in.split_even(2), (high_tom, low_tom)):
        grace_hit, main_hit = hit.split([1, 7])
        grace_hit.attach(tom, nice_random_location(2.2))
        main_hit.attach(tom, nice_random_location(.5))
        hit.set_duration(eighth_dur*2)

    high_tom_spec = [1, 1, 1, 2, 1, 2, 2, 1, 1, 1, 1, 2,
                1, 1, 1, 3, 1, 1, 2, 1, 1, 2, 2]

    high_tom_track = Track("High Toms", Sound.default_rate)
    high_tom_beats = high_tom_track.link_root(the_rest, drums)
    set_dur_high_tom = None
    for high_tom_beat in high_tom_beats.split(high_tom_spec):
        high_tom_beat.attach(high_tom, nice_random_location(.6))
        set_dur_high_tom = high_tom_beat
    set_dur_high_tom.set_duration(high_tom_spec[-1]*eighth_dur)

    yield high_tom_track
    
    low_tom_spec = [5, 8, 8, 8, 3]

    low_tom_track = Track("Low Toms", Sound.default_rate)
    low_tom_beats = low_tom_track.link_root(the_rest, drums)
    for low_tom_beat in low_tom_beats.split(low_tom_spec):
        low_tom_beat.attach(low_tom, nice_random_location(.5))

    yield low_tom_track

    snare_spec = [6, 8, 8, 8, 2]

    snare_track = Track("Snare", Sound.default_rate)
    snare_beats = snare_track.link_root(the_rest, drums)
    for snare_beat in snare_beats.split(snare_spec):
        snare_beat.attach(snare, nice_random_location(.4))

    yield snare_track

    tink_spec = [3, 3, 6, 2, 2]*2

    tink_track = Track("Tink!", Sound.default_rate, volume=2)
    tink_beats = tink_track.link_root(the_rest, drums)
    for tink_beat in tink_beats.split(tink_spec):
        tink_beat.attach(tink, nice_random_location(1))

    yield tink_track

    yield drums
        

def generate_all_tracks(master_beat):
    for b in master_beat.split_even(4):
        for t in chorus_rhythm(b):
            yield t

mainbeat = Beat()
mix = Mixer("Let's yield, I guess...!", Sound.default_rate, list(generate_all_tracks(mainbeat)))
mix.play(quick_play=True)

exit()


Cm7 = ["C", "Eb", "G", "Bb"]
EbM9= ["Eb", "F", "G", "Bb"]
G9 = ["C", "D", "G", "A"]
D = ["D", "F#", "A"]

def derp():
    synco_dings = Track("Syncopated Ding", Sound.default_rate)
    synco_beat = synco_dings.link_root(beat)
    with open(rhlib("america")) as rf:
        char_times = eval(''.join(rf.readline()))
    for ding_beat in synco_beat.interleave_split(char_times)['j']:
        ding_beat.attach(ding, Location((0, 0), 3))
    #yield synco_dings

         #, bassy_dict = {}):
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


