#!/usr/bin/env python

NUM_PROCESSES = 1
DEBUG_CMD = 1

import multiprocessing

import os.path

import short

# no clue why I need this.  :(
from harmonics_data import HarmonicsStats

DATA = {'glasgow': [
  'violin-%s-glasgow',
  'cello-%s-glasgow',
  ],
#    'vancouver': [
#        'violin-%s-graham',
#        'violin-%s-colin',
#        'violin-%s-mom',
#        'violin-%s-jen',
#        'viola-%s-graham',
#        'viola-%s-wcams',
#        'cello-%s-graham',
#        'cello-%s-old',
#        'cello-%s-wilf',
#        ]
    }
STRINGS = {'violin': ['e', 'a', 'd', 'g'],
    'viola': ['a', 'd', 'g', 'c'],
    'cello': ['a', 'd', 'g', 'c'],
    }

def inst_string(queue, city, inst):
    nf, nb, na, stats, harm_stats = short.process(city, inst)
    datum = (inst, nf, nb, na, stats, harm_stats)
    queue.put(datum)

pool = multiprocessing.Pool(processes=NUM_PROCESSES)
manager = multiprocessing.Manager()
queue = manager.Queue()
for city in DATA:
    for inst in DATA[city]:
        for strings in STRINGS[inst.split('-')[0]]:
            for st in strings:
                inst_st = inst % st
                inst_string(queue, city, inst_st)
                #pool.apply_async(inst_string, args=(queue, city, inst_st))
pool.close()
pool.join()

data = []
while not queue.empty():
    datum = queue.get()
    data.append(datum)

def get_split_filename(dirname):
    return os.path.basename(dirname).split('-')

def sort_inst_names(a):
    at = get_split_filename(a[0])
    value = 0
    ### instrument type
    if at[0] == 'violin':
        value += 100
    elif at[0] == 'viola':
        value += 200
    elif at[0] == 'cello':
        value += 300
    else:
        print "Don't recognize that instrument:", at[0]
    ### string
    if at[1] == 'e':
        value += 10
    elif at[1] == 'a':
        value += 20
    elif at[1] == 'd':
        value += 30
    elif at[1] == 'g':
        value += 40
    elif at[1] == 'c':
        value += 50
    else:
        print "Don't recognize string:", at[1]
    ### instrument owner
    if at[2] == 'glasgow':
        value += 1
    elif at[2] == 'colin':
        value += 2
    elif at[2] == 'graham':
        value += 3
    elif at[2] == 'jen':
        value += 4
    elif at[2] == 'mom':
        value += 5
    elif at[2] == 'wilf':
        value += 6
    elif at[2] == 'wcams':
        value += 8
    elif at[2] == 'old':
        value += 9
    else:
        print "Don't recognize owner:", at[2]
    return value

data = sorted(data, key=sort_inst_names)
prev_consider = ''

removing_filename = os.path.join("out", "string-removing.txt")
out_removing = open(removing_filename, 'w')
out_removing.write(short.get_stats_header().replace("\t", "&") + "\n")

out_filename = os.path.join("out", "string-decays.txt")
out = open(out_filename, 'w')
out.write(short.get_header().replace("\t", "&") + "\n")
for datum in data:
    inst, nf, nb, na, stats, harm_stats = datum
    consider = '-'.join( inst.split('-')[0:2] )
    if consider != prev_consider:
        out.write("\n")
        out_removing.write("\n")
        prev_consider = consider

    text = short.get_info(inst, nf, nb, na, stats)
    out.write(text.replace("\t", "&") + "\n")

    text = short.get_stats_info(inst, harm_stats)
    out_removing.write(text.replace("\t", "&") + "\n")
out.close()
out_removing.close()

