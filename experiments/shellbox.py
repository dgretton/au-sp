from ausp import *
import numpy as np

datadir = os.path.expanduser('~/.au-sp')

def aulib(sound_dir):
    return os.path.join(datadir, 'audio', sound_dir)

shellbox_sound = RandomSound()
shellbox_sound.populate_with_dir(aulib('shellbox'))

dotquarter_dur = 60.0/30
eighth_dur = dotquarter_dur/3

def falling_sound(snd, dur, start_ratio=1):
    return ResampledSound(ClippedSound(snd, dur*start_ratio), lambda t: np.exp(1-t/dur)*start_ratio)

raw_sine_bass = RawPitchedSound(os.path.join(aulib('werb_sine'), 'werb_sine.0.110.wav'))

rasp_bass = RandomIntervalSound(RawPitchedSound(os.path.join(aulib('rasp_bass'),
'rasp_bass_1.0.110.wav')).for_pitch('D_2'), margin=.5)
string_bass = RandomIntervalSound(RawPitchedSound(os.path.join(aulib('bowed_violin'),
'bowed_violin_3.120.D_4.wav')).for_pitch('D_2'), margin=.5)

low_tom = RandomSound()
low_tom.populate_with_dir(aulib('long_low_tom'))

cym_snd = RandomSound()
cym_snd.populate_with_dir(aulib('hi_hat_close'))

bass_pulse = RandomSound()
bass_pulse.populate_with_dir(aulib('bass_pulse'))

one_shaker = RandomSound()
one_shaker.populate_with_dir(aulib('shaker_singles'))

def generate_all_tracks(master_beat):
    pickup, firstsec = master_beat.split(2)
    tr = Track('Pickup slide-downs', end_padding=40)
    pickup_tr_beat = tr.link_root(pickup)
    pickup_eighths = 9 # must be at least 4
    start_r = 1.0
    for i, b in enumerate(pickup_tr_beat.split_even(pickup_eighths*2)):
        start_r -= .025
        b.set_duration(eighth_dur/2)
        if i == pickup_eighths*2 - 4*2:
            pass
            #b.attach(shellbox_sound, Location((.1, .2), 2))
            #b.attach(shellbox_sound, Location((-.15, .2), 3))
        if i % 2 == 0:
            b.attach(ClippedSound(falling_sound(raw_sine_bass.for_pitch('A_0'),
                    dotquarter_dur, start_ratio=start_r), dotquarter_dur), Location((1, 1), .6))
            b.attach(bass_pulse, Location(1, 2, .4))
            steenth1, steenth2 = b.split([.55, .45])
            steenth2.attach(low_tom, Location(-5, 2, 2))
            b.attach(low_tom, Location(-5, 2, 2))
    yield tr
    tr2 = Track('Start raspy bass', end_padding=40)
    tr_beat = tr2.link_root(firstsec)
    sec_dur = dotquarter_dur*4*4
    tr_beat.set_duration(sec_dur)
    meas1and2, meas3, meas4 = tr_beat.split([2, 1, 1])
    meas1and2.attach(rasp_bass.for_interval(sec_dur/2), Location(-2, 2, .2))
    meas1and2.attach(string_bass.for_interval(sec_dur/2), Location(-5, 2, -2))
    meas1and2.attach(string_bass.for_interval(sec_dur/2), Location(5, -2, .2))
    meas4.attach(rasp_bass.for_interval(sec_dur/4), Location(-2, 2, .2))
    meas4.attach(string_bass.for_interval(sec_dur/4), Location(-5, 2, -2))
    meas4.attach(string_bass.for_interval(sec_dur/4), Location(5, -2, .2))
    yield tr2
    tr3 = Track('heartBeat')
    tr_beat = tr3.link_root(firstsec)
    for meas_b in tr_beat.split_even(4):
        for dotquart in meas_b.split_even(4):
            for eighth in dotquart.split_even(3):
                eighth.attach(SpreadSound(low_tom, (.1,)*3, .02, 3), Location(-2, 2, 2))
                eighth.attach(SpreadSound(one_shaker, (.1,)*3, .02, 3), Location(2, -2, 20))
                for beat32 in eighth.split([1, .8, .9, .8]):
                    spread_shake = SpreadSound(one_shaker, (.1,)*3, .01, 3)
                    beat32.attach(spread_shake, Location(4, -2, 30))
                    beat32.attach(ShiftedSound(spread_shake, -.05), Location(-4, 3, 40))
    yield tr3


mainbeat = Beat()
mix = Mixer('Box in the Shell!', tracks=list(generate_all_tracks(mainbeat)))
mix.play(quick_play=False) #, t0=15, t1=16)

