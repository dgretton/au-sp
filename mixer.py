import wave, struct, os
from .sound import Sound
from ausp import OSTYPE, WIN_OSTYPE, MAC_OSTYPE
import numpy as np


class Mixer:

    attenuation_boost = 1
    if OSTYPE == WIN_OSTYPE:
        import pyaudio

    def __init__(self, name, rate=Sound.default_rate, tracks=[]):
        self.name = name
        self.tracks = tracks
        self.rate = rate

    def set_rate(self, rate):
        self.rate = rate

    @staticmethod
    def _os_audio_play(wavname):
        if OSTYPE == MAC_OSTYPE:
            os.system('afplay ' + wavname)
            return
        if OSTYPE == WIN_OSTYPE:
            wf = wave.open(wavname, 'rb')
            if wf.getframerate() != self.rate:
                print "Don't play back a work with the wrong rate!"
                exit()
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                                    channels=wf.getnchannels(),
                                    rate=wf.getframerate(),
                                    output=True)
            chunksize = 1024
            data = wf.readframes(chunksize)
            while data != '':
                stream.write(data)
                data = wf.readframes(chunksize)
            stream.stop_stream()
            stream.close()
            p.terminate()
            return
        print 'ignoring play call because operating system not known'

    def play(self, t0=0, t1=None, quick_play=True):
        self.render_to_file('temp.wav', t0, t1, quick_play=quick_play)
        print "Begin playback."
        Mixer._os_audio_play('temp.wav')

    def play_beat(self, beat, quick_play=True):
        self.play(beat.time(), beat.time() + beat.duration(), quick_play)

    def play_sound(self, sound, *args, **kwargs):
        Mixer.render_sound_to_file(sound, 'sound_temp.wav', *args, **kwargs)
        Mixer._os_audio_play('sound_temp.wav')

    def render_to_file(self, out_file_name, t0=None, t1=None, quick_play=False):
        if os.path.isfile(out_file_name):
            check_file_free = open(out_file_name).close()
        Sound.quick_play = quick_play
        if not t0:
            t0 = min([track.start_time() for track in self.tracks])
        if not t1:
            t1 = max([track.start_time() + track.duration() for track in self.tracks])
        data_buffer = np.zeros((2, int(self.rate * (t1 - t0)) + 1))
        for track in self.tracks:
            data_buffer = track.mix_into(t0, data_buffer)
        Mixer.write_to_file(self.rate, out_file_name, data_buffer)

    @staticmethod
    def render_sound_to_file(sound, wavname, location=None, repeats=1, quick_play=True):
        if not wavname:
            print 'Must supply a name for the file to which to render a sound!'
            return
        Sound.quick_play = quick_play
        buffer = np.array([[],[]])
        for n in range(repeats):
            sound_data = sound.render_from(location)[1]
            if len(sound_data.shape) == 1:
                sound_data = [sound_data, sound_data]
            buffer = np.hstack((buffer, sound_data))
        Mixer.write_to_file(sound.rate, wavname, buffer)

    @staticmethod
    def write_to_file(rate, out_file_name, buffer):
        data_buffer = (buffer * 2**15 * Mixer.attenuation_boost).astype(np.int16)
        print "Finished rendering, writing out buffer..."
        print "Max level:"
        print float(data_buffer.max())/2**15
        output_wav = wave.open(out_file_name, 'w')
        output_wav.setparams((2, 2, rate, 0, 'NONE', 'not compressed')) # (nchannels, samplewidth, framerate, nframes, compressiontype, compressionname)
        write_chunk_size = 10000
        write_chunk = ''
        for left_sample, right_sample in zip(data_buffer[0], data_buffer[1]):
            left_bytes = struct.pack('h', left_sample)
            right_bytes = struct.pack('h', right_sample)
            write_chunk += ''.join((left_bytes, right_bytes))
            if len(write_chunk) == write_chunk_size:
                output_wav.writeframes(write_chunk)
                write_chunk = ''
        output_wav.writeframes(write_chunk)
        output_wav.close()
