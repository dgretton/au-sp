import sys, os, time, shutil

datadir = os.path.expanduser('~/.au-sp')
if len(sys.argv) <= 1:
    print '	Must supply a sound lib directory name'
    exit()
sound_name = sys.argv[1]

def aulib(sound_dir):
    return os.path.join(datadir, 'audio', sound_dir)

sound_lib_path = aulib(sound_name)
if not os.path.exists(sound_lib_path):
    print '	Cannot find lib', sound_lib_path
    exit()

backup_folder = os.path.join(sound_lib_path, 'adjust_backup')

if len(sys.argv) >= 3:
    if sys.argv[2] == 'clean':
        if not os.path.exists(backup_folder):
            print 'Nothing to clean.'
            exit()
        backups = os.listdir(backup_folder)
        if not backups:
            print 'Nothing to clean.'
        for backup in backups:
            bkpath = os.path.join(backup_folder, backup)
            print 'Remove', bkpath
            os.remove(bkpath)
        print 'Remove directory', backup_folder
        os.rmdir(backup_folder)
        exit()
    particular_index = int(sys.argv[2])
else:
    particular_index = None

from ausp import *
from matplotlib import pyplot as plt

click_sound = RawSound(aulib(os.path.join('click', 'click_0.0.wav')))

sound_paths = [os.path.join(sound_lib_path, sp) for sp in sorted(os.listdir(sound_lib_path))]
if backup_folder in sound_paths:
    sound_paths.remove(backup_folder)
if not sound_paths:
    print '	No sounds found in', sound_lib_path, 'to align'
    exit()

if particular_index is not None:
    try:
        sound_paths = [sound_paths[particular_index]]
    except IndexError:
        print '	Particular index supplied not in bounds'
        exit()

fig = plt.figure()
ax = fig.add_subplot(111)

print '	Aligning sounds:\n\t\t', '\n\t\t'.join(str(i) + ': ' + sp for i, sp in enumerate(sound_paths))

holder = lambda: None
holder.looping_sound = False
holder.offset = 0
holder.path = ''
holder.rawsound = None
holder.soundnum = -1
holder.vert_line, = ax.plot([0, 0], [5, -5])
holder.horiz_line, = ax.plot([0, 1000], [0, 0])

def update_lines():
    if not holder.rawsound:
        return
    r, data = holder.rawsound.render_from(None)
    reg_ms = 1000.0*r + holder.offset
    holder.vert_line.set_data([reg_ms, reg_ms], [.5, -.5])
    holder.vert_line.figure.canvas.draw()
    len_ms = 1000.0*len(data)/Sound.default_rate
    holder.horiz_line.set_data([0, len_ms], [0, 0])
    holder.horiz_line.figure.canvas.draw()

def next_sound():
    holder.looping_sound = False
    if sound_paths:
        holder.path = sound_paths.pop(0)
        rs = RawSound(holder.path)
        if rs.render_from(None)[0] < .001:
            rs = RawSound(holder.path, registration_point=.001)
        holder.rawsound = rs
    else:
        print '	Finished aligning all sounds.'
        exit()
    holder.soundnum += 1
    print '	Aligning sound', holder.soundnum, 'at path', holder.path
    holder.offset = 0
    update_lines()
    render()

lfile = 'loop_temp.wav'
adjust_unit = 5 # int, ms

beat_interval = .1

def render():
    print '	RENDER!'
    loop_track = Track('>>>Loop<<<', Sound.default_rate)
    top_beat = loop_track.link_root(Beat())
    for i, b in enumerate(top_beat.split_even(30)):
        b.set_duration(beat_interval)
        if i != 0 and i % 8 == 0:
            b.attach(ShiftedSound(holder.rawsound, -holder.offset/1000.0), Location((0, .6, 0)))
        amnt_closer = (i%4==0)*4 + (i%2==0)*2
        b.attach(click_sound, Location((0, 8 - amnt_closer, 0)))
    mix = Mixer('', tracks=[loop_track])
    mix.render_to_file(lfile)
    update_lines()
    print '	Done rendering'

def adjust_and_render(event):
    key = event.key
    if key:
        holder.looping_sound = True
        if key == 'alt+enter':
            write_current_sound()
            next_sound()
        elif key == 'alt+s':
            print '	Skip sound.'
            next_sound()
        elif key == 'left':
            holder.offset -= adjust_unit
            render()
        elif key == 'right':
            holder.offset += adjust_unit
            render()
        elif key == 'cmd+w':
            exit()
        elif key != 'enter':
            holder.looping_sound = False
            
def write_current_sound():
    orig_name = os.path.basename(holder.path)
    parse = orig_name.split('.')
    print '	Overriding old name', orig_name
    print '	Offset is', holder.offset, 'ms'
    try:
        prefix, orig_ms, postfix = parse[0], int(parse[1]), '.'.join(parse[2:])
        new_ms = int(orig_ms + holder.offset)
        if new_ms < 0:
            print '	Something went wrong, not saving a negative reg point'
            exit()
        new_name = '.'.join((prefix, str(new_ms), postfix))
    except ValueError:
        try:
            prefix, postfix = parse[0], '.'.join(parse[1:])
            if holder.offset < 0:
                print '	Something went wrong, not saving a negative reg point'
                exit()
            new_name = '.'.join((prefix, str(holder.offset), postfix))
        except ValueError:
            print '	Parsing dot fields failed, not saving'
            exit()
    print '	New name will be', new_name
    full_new_path = os.path.join(sound_lib_path, new_name)
    # Mixer.render_sound_to_file(holder.rawsound, full_new_path) NO don't do this! Literally just changing the name
    if not os.path.exists(backup_folder):
        os.mkdir(backup_folder)
    backup_file_path = os.path.join(backup_folder, orig_name)
    os.rename(holder.path, backup_file_path)
    shutil.copy(backup_file_path, full_new_path)
    print '	Sound was renamed and backed up to', backup_file_path

next_sound()

fig.canvas.mpl_connect('key_press_event', adjust_and_render)
plt.ion()
while True:
    try:
        if holder.looping_sound:
            print '	SYSTEM PLAY SOUND'
            os.system('afplay ' + lfile)
        plt.pause(max(0.05, beat_interval*2 - .3))
    except KeyboardInterrupt:
        print '	Skip sound.'
        time.sleep(1) # Ctrl+C twice quickly to interrupt
        next_sound()

