#!/usr/bin/env python

NUM_PROCESSES = 3
DEBUG_CMD = 0

import multiprocessing

import os.path

import estimate_f0_B

import tables

DATA = {
    'yvr': [
        'violin-%s-colin',
        'violin-%s-graham',
        'violin-%s-jen',
        'violin-%s-melissa',
        'violin-%s-mom',
        'viola-%s-graham',
        'viola-%s-wcams',
        'cello-%s-graham',
        'cello-%s-old',
        'cello-%s-wilf',
    ],
#    'glasgow': ['violin-%s-glasgow', 'cello-%s-glasgow'],
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
    dirname = os.path.join("/main/media/phd-data",
        "%s/fixed-wav/%s" % (city, inst))
    #print dirname
    datum = estimate_f0_B.process(dirname)
    queue.put( (inst, datum) )

pool = multiprocessing.Pool(processes=NUM_PROCESSES)
manager = multiprocessing.Manager()
queue = manager.Queue()
for city in DATA:
    for inst in DATA[city]:
        for strings in STRINGS[inst.split('-')[0]]:
            for st in strings:
                inst_st = inst % st
                print inst_st
                if DEBUG_CMD:
                    inst_string(queue, city, inst_st)
                else:
                    pool.apply_async(inst_string, args=(queue, city, inst_st))
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
    if at[2] == 'colin':
        value += 1
    elif at[2] == 'graham':
        value += 2
    elif at[2] == 'jen':
        value += 3
    elif at[2] == 'mom':
        value += 5
    elif at[2] == 'wilf':
        value += 5
    elif at[2] == 'wcams':
        value += 6
    elif at[2] == 'old':
        value += 7
    elif at[2] == 'melissa':
        value += 4
    else:
        print "Don't recognize owner:", at[2]
    return value

data = sorted(data, key=sort_inst_names)
prev_consider = ''

out_filename = os.path.join("out", "string-Bs.txt")
out = open(out_filename, 'w')
out.write(estimate_f0_B.get_header().replace("\t", "&") + "\n")
for datum in data:
    inst, dat = datum
    consider = '-'.join( get_split_filename(inst)[0:2] )
    if consider != prev_consider:
        out.write("\n")
        prev_consider = consider
    detected_freqs, adjusted_freqs, stats, final = dat
    text = tables.anonymize_name(inst) + "&" + estimate_f0_B.get_info(detected_freqs, adjusted_freqs, stats, final)
    out.write(text.replace("\t", "&") + "\n")
out.close()

