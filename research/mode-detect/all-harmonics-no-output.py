#!/usr/bin/env python

NUM_PROCESSES = 4
DEBUG_CMD = 0

import multiprocessing

import os.path

import harmonics_data

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
#'glasgow': ['violin-%s-glasgow', 'cello-%s-glasgow'],
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
    print city, inst
    _ = harmonics_data.HarmonicsData(city, inst, recalc=True)

pool = multiprocessing.Pool(processes=NUM_PROCESSES)
manager = multiprocessing.Manager()
queue = manager.Queue()
for city in DATA:
    for inst in DATA[city]:
        for strings in STRINGS[inst.split('-')[0]]:
            for st in strings:
                inst_st = inst % st
                #inst_string(queue, city, inst_st)
                pool.apply_async(inst_string, args=(queue, city, inst_st))
pool.close()
pool.join()

