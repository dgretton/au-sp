import json, sys

times_lists = {
        'start_times':[],
        'end_times':[]
        }

with open(sys.argv[1], 'w+') as f:
    f.write(json.dumps(times_lists, 'times_lists_for_' + sys.argv[1] + '.json'))
