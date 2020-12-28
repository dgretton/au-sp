from ausp import *
from math import pi, sin, cos, log
from random import randint, random
import numpy as np

datadir = os.path.expanduser('~/.au-sp')

def aulib(sound_dir):
    return os.path.join(datadir, 'audio', sound_dir)

def rhlib(rh_name):
    return os.path.join(datadir, 'rhythm', rh_name + '.rh')

def spreadloc(r):
    return Location((random()*2*pi, random()*pi), r)

random_mid_drum = RandomSound()
random_mid_drum.populate_with_dir(aulib('long_low_tom'))
random_mid_drum.populate_with_dir(aulib('short_low_tom'))
random_mid_drum.populate_with_dir(aulib('long_high_tom'))
random_mid_drum.populate_with_dir(aulib('short_high_tom'))
random_mid_drum.populate_with_dir(aulib('cymbal_long'))
mid_drum = SpreadSound(random_mid_drum, (.2, .2, 0), 0, 1)

random_viols = RandomPitchedSound()
random_viols.populate_with_dir(aulib('plucked_violin_damp'))

random_xylo = RandomPitchedSound()
random_xylo.populate_with_dir(aulib('g_major_xylo'))

raw_bassy = RawPitchedSound(aulib('werb_sine') + '/werb_sine.0.110.wav')
#raw_bassy = RawPitchedSound(aulib('voice_oo') + '/loud.0.287.wav')
#raw_bassy = RawPitchedSound(aulib('rasp_bass') + '/rasp_bass_1.0.110.wav')
#raw_bassy = RawPitchedSound(aulib('bowed_violin') + '/bowed_violin_2.146.D_4.wav')
#raw_bassy = RawPitchedSound(aulib('crystal_ding') + '/crystal_ding.20.1313.wav')

bass_pulse = RandomSound()
bass_pulse.populate_with_dir(aulib('bass_pulse'))

ding = RandomSound()
ding.populate_with_dir(aulib('crystal_ding'))

shaker1 = RandomIntervalSound(RawSound(aulib('shaker_textures') + '/shaker_texture_regular.wav'))
shaker2 = RandomIntervalSound(RawSound(aulib('shaker_textures') + '/shaker_texture_low.wav'))
shaker3 = RandomIntervalSound(RawSound(aulib('shaker_textures') + '/shaker_texture_high.wav'))
shakers = (shaker1, shaker2, shaker3)

def to_semitone_space(freq):
    return log(freq)/log(2.0**(1.0/12))

def nearest_harmonic_ratio(semitone, mem={}):
    if semitone in mem:
        return mem[semitone]
    min_dist = 13
    best_ratio = None
    for harm in range(1, 60):
        semi_space = to_semitone_space(harm) % 12
        dist = abs(semi_space - semitone)
        if dist < min_dist:
            min_dist = dist
            best_ratio = (2.0**(1.0/12))**semi_space
    mem[semitone] = best_ratio
    return best_ratio

use_natural_harmonics = True
if use_natural_harmonics:
    Cm7 = [0, 3, 7, 10]
    C = [0, 4, 7]
    EbM9 = [3, 5, 7, 10]
    Bbm = [2, 5, 10]
    G9 = [0, 2, 7, 9]
    D = [2, 4, 6, 9]
    Fm = [0, 3, 5, 8]
    Gm = [2, 5, 7, 10]
    Bbm_sus = [3, 5, 10]
    Ab = [0, 5, 8]
    Cm7, C, EbM9, Bbm, G9, D, Fm, Gm , Bbm_sus, Ab = (
            [261.6*nearest_harmonic_ratio(n)/2 for n in scale]
            for scale in (Cm7, C, EbM9, Bbm, G9, D, Fm, Gm, Bbm_sus, Ab))
else:
    Cm7 = ['C', 'Eb', 'G', 'Bb']
    C = ['C', 'E', 'G']
    EbM9= ['Eb', 'F', 'G', 'Bb']
    Bbm = ['D', 'F', 'Bb']
    G9 = ['C', 'D', 'G', 'A']
    #TODO: fix, put back
    D = ['D', 'E', 'F#', 'A']
    Fm = ['C#', 'Eb', 'F', 'Ab']
    Gm = ['D', 'F', 'G', 'Bb']
    Bbm_sus = ['Eb', 'F', 'Bb']
    Ab = ['C', 'Eb', 'Ab']

if use_natural_harmonics:
    def init_pitch_list(scale, start_octave):
        return scale[:]

    def extend_arpeg_list(pitch_list, scale, octave, direction):
        to_add = [f*2**(octave - 3) for f in scale]
        if not direction:
            to_add.reverse()
        pitch_list += to_add

    def yield_pitch(item):
        return item
else:
    def init_pitch_list(scale, start_octave):
        return [(p, octv) for p, octv in zip(scale, [str(start_octave)]*len(scale))]

    def extend_arpeg_list(pitch_list, scale, octave, direction):
        pitch_list += [(p, octv) for p, octv in zip((scale if direction else reversed(scale)),
            [str(octave)]*len(scale))]

    def yield_pitch(item):
        return '_'.join(item)

def random_arpeggiate(scale, jitter=0, start_octave=3, radius=0):
    up = True
    pitch_list = init_pitch_list(scale, start_octave)
    octave = start_octave
    while True:
        if len(pitch_list) < len(scale):
            extend_arpeg_list(pitch_list, scale, octave, up)
            octave += 1 if up else -1
        if abs(octave - start_octave) > radius:
            octave = start_octave + (radius if up else -radius)
            up = not up # the whole world turned upside down
        next_pitch_item = pitch_list.pop(randint(0, jitter)) if jitter else pitch_list.pop(0)
        yield yield_pitch(next_pitch_item)

def double_nest(beat, arpeggiator):
    for section in beat.split_even(4):
        basic_tr = Track('...', Sound.default_rate)
        track_beat = basic_tr.link_root(section)
        for b, arpeg_pitch in zip(track_beat.split_even(6),
                #[10, 8, 7, 6.5, 6, 5.25]),
                arpeggiator):
            for sb in b.split_even(randint(2, 5)):
                sb.attach(random_xylo.for_pitch(arpeg_pitch), Location((pi/2, pi/4), 1))
        yield basic_tr

def nested_yield_test(beat):
    beat1, beat2 = beat.split_even(2)
    arp = random_arpeggiate(test_scale, jitter=3, start_octave=3)
    for t in double_nest(beat1, arp):
        yield t
    for t in double_nest(beat2, arp):
        yield t

eighth_dur = .12

def on_a_third_iter():
    while True:
        yield True
        yield False
        yield False

def make_vibrato(sound, n):
    return ResampledSound(sound, freq_func=lambda x: 1.0+.03*np.sin(x*n*2.0*pi))

def six_chords(beat, bassy_dict = {}):
    chords = [C, Fm, EbM9, Gm, Bbm, Fm, C]#[D, G9, D, Cm7, Cm7, EbM9, EbM9]
    last_chord = None
    arpeggiator = None
    viol_arpeggiator = None
    
    bass_track = Track('Arp Bass', Sound.default_rate, end_padding=1.0)
    track_beat = bass_track.link_root(beat)
    viols = Track('Violins', Sound.default_rate)
    viols_beat = viols.link_root(beat)


    for shaker in shakers:
        dur = eighth_dur*8*6*2
        for i in range(2):
            track_beat.attach(ClippedSound(shaker.for_interval(dur), dur*.99, margin=dur*.4),
                    spreadloc(1.0*(i*3+1)))
    for meas_beat, viol_meas_beat, chord in zip(track_beat.split_even(6),
                viols_beat.split_even(6), chords):
        if chord != last_chord:
            arpeggiator = random_arpeggiate(chord, jitter=1, start_octave=3)
            viol_arpeggiator = random_arpeggiate(chord, jitter=len(chord)-1, start_octave=4)
        last_chord = chord
        on_a_third = on_a_third_iter()
        for b in meas_beat.split_even(4):
            b.set_duration(eighth_dur*4)

            chord_size = 5
            random_chord = [arpeggiator.next() for i in range(chord_size)]
            chord_dur = eighth_dur*4*1.12

            for random_pitch in random_chord:
                bassy = bassy_dict.get(random_pitch, make_vibrato(RandomIntervalSound(
                    raw_bassy.for_pitch(random_pitch),
                    chord_dur, margin=.01), 2+random()*3))
                bassy_dict[random_pitch] = bassy
                offset_snd = ShiftedSound(bassy, -random()*.06)
                b.attach(offset_snd, spreadloc((1.5 + random())*.2))

            b1, b2 = b.split_even(2)
            def add_drum(b, d):
                b.attach(random_mid_drum, spreadloc(d))
            if on_a_third.next():
                add_drum(b1, .2)
                b3, b4 = b2.split([1, 1.3])
                add_drum(b3, 1.5)
                add_drum(b4, 1.5)
            if on_a_third.next():
                b3, b4 = b1.split_even(2)
                add_drum(b3, 1.1)
                add_drum(b4, 1.1)
                add_drum(b2, .2)
            b1.attach(random_mid_drum, Location((-pi*random(), pi/4*random()), 2.0 + random()*2))

        for b in viol_meas_beat.split_even(16):
            b.attach(random_viols.for_pitch(viol_arpeggiator.next()), spreadloc(1.5))

    yield bass_track
    yield viols

    synco_dings = Track('Syncopated Ding', Sound.default_rate)
    synco_beat = synco_dings.link_root(beat)
    with open(rhlib('america')) as rf:
        char_times = eval(''.join(rf.readline()))
    for ding_beat in synco_beat.interleave_split(char_times)['j']:
        ding_beat.attach(ding, Location((0, 0), 42))

    yield synco_dings

def sevenfour_out(beat):
    werbs_track = Track('Werbs', Sound.default_rate)
    werbs_beat = werbs_track.link_root(beat)
    count_dist = [1, 2, 4]
    counts = werbs_beat.split_even(sum(count_dist))
    def yieldgroups(counts_list, count_spec):
        templist = counts_list[:]
        for counts in count_spec:
            yield templist[:counts]
            templist = templist[counts:]
    one_count, two_count, four_count = yieldgroups(counts, count_dist)
    print one_count, two_count, four_count
    chords = C, Bbm_sus, Ab
    for count_group, chord, num_counts \
                in zip((one_count, two_count, four_count), chords, count_dist):
        for pitch in chord:
            chord_count_dur = eighth_dur*4
            count_group[0].set_duration(chord_count_dur)
            count_group[0].attach(RandomIntervalSound(raw_bassy.for_pitch(pitch),
                    num_counts*chord_count_dur, margin=.03), spreadloc(.3))
    yield werbs_track

def generate_all_tracks(master_beat):
    sec1, out1 = master_beat.split(2)
    for b in sec1.split_even(2):
        for t in six_chords(b):
            yield t
    for t in sevenfour_out(out1):
        yield t

mainbeat = Beat()
mix = Mixer("Let's yield, I guess...!", tracks=list(generate_all_tracks(mainbeat)))
mix.play(quick_play=True) #, t0=15, t1=16)

