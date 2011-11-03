#!/usr/bin/env python

NUM_PROCESSES = 3
DEBUG_CMD = 1

import multiprocessing

import os.path

import short

DATA = {'glasgow': ['violin-%s-glasgow', 'cello-%s-glasgow'],
    }
STRINGS = {'violin': ['e', 'a', 'd', 'g'],
    'cello': ['a', 'd', 'g', 'c'],
    }
# no clue why I need this.  :(
from harmonics_data import HarmonicsStats

def inst_string(queue, city, inst):
    #print city, inst
    nf, nb, na, rsquared, harm_stats = short.process(city, inst, recalc=True)
    datum = (inst, nf, nb, na, rsquared, harm_stats)
    #print datum[0]
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
    if at[2] == 'colin':
        value += 1
    elif at[2] == 'graham':
        value += 2
    elif at[2] == 'jen':
        value += 3
    elif at[2] == 'mom':
        value += 4
    elif at[2] == 'wilf':
        value += 5
    elif at[2] == 'wcams':
        value += 6
    elif at[2] == 'old':
        value += 7
    elif at[2] == 'melissa':
        value += 8
    else:
        print "Don't recognize owner:", at[2]
    return value

data = sorted(data, key=sort_inst_names)
prev_consider = ''
#print "# name\tnf\tnb\tna\trsquared"
out = open("fits-initial-decays.txt", "w")
out.write("INITIAL_DECAYS = {\n")
for datum in data:
    inst, nf, nb, na, stats, harm_stats = datum
    #print inst
    consider = '-'.join( inst.split('-')[0:2] )
    #if consider != prev_consider:
    #    print
    #    prev_consider = consider
    #print "%s\t%.3g\t%.3g\t%.3g\t%.2f" % (
    #    inst, nf, nb, na, rsquared)
    out.write("    '%s': [" % (consider))
    out.write("%.5e, %.5e, %.5e" % ( nf, nb, na))
    out.write("],\n")
out.write("    'default': [1e-5, 1e-2, 1],\n")
out.write("}\n")

out.close()

