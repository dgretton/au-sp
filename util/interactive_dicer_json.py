import json, sys
import numpy as np
from ausp import *
from matplotlib import pyplot as plt

datadir = os.path.expanduser('~/.au-sp')

def aulib(sound_dir):
    return os.path.join(datadir, 'audio', sound_dir)

def dicerdir(name):
    return os.path.join('dice', name)

raw_sound = RawSound(dicerdir(sys.argv[1] + '.wav'))
r, data = raw_sound.render_from(None)
downs_data = data[::100]

fig, ax = plt.subplots()
ax.plot((np.arange(len(data))*1.0/raw_sound.rate)[::100], downs_data)

keys_to_list_names = {'s':'start_times', 'e':'end_times', 'r':'reg_pt_times'}
holder = lambda: None
holder.build_json = {v:[] for v in keys_to_list_names.values()}
holder.active_list_name = None

def set_active_list(event):
    print 'SET ACTIVE LIST'
    key = event.key
    print key
    if key == 'enter':
        write_out()
    try:
        mod, key = key.split('+')
    except ValueError:
        unset_active_list()
        return
    if mod != 'alt':
        unset_active_list()
        return
    if key not in keys_to_list_names:
        unset_active_list()
        return
    ln = keys_to_list_names[key]
    holder.active_list_name = ln
    ax.set_title('Click to specify an element of ' + ln)
    fig.canvas.draw()

def unset_active_list():
    print 'UNSET ACTIVE LIST'
    ax.set_title('alt/option + (' + ', '.join((k + ': ' + keys_to_list_names[k] for k in keys_to_list_names)) + ')')
    holder.active_list_name = None
    fig.canvas.draw()

def add_time(event):
    print 'ADD TIME'
    if holder.active_list_name is None:
        return
    time_series = holder.build_json[holder.active_list_name]
    t = event.xdata
    time_series.append(t)
    time_series.sort()
    mark, = ax.plot([t, t], [-.2, .2])
    mark.figure.canvas.draw()

fig.canvas.mpl_connect('key_press_event', set_active_list)
fig.canvas.mpl_connect('button_release_event', add_time)

def write_out():
    fname = dicerdir(sys.argv[1] + '.json')
    print 'WRITING OUT JSON TO ' + fname
    with open(fname, 'w+') as f:
        f.write(json.dumps(holder.build_json))

unset_active_list()
plt.show()

