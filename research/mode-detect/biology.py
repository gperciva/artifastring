#!/usr/bin/env python

import sys
sys.path.append("../shared/")

import os.path
import glob
import pickle

import numpy
import scipy.optimize
import pylab

import estimate_f0_B
import chemistry

import sys
import mode_decays

import defs
import published_constants

try:
    dirname = sys.argv[1]
    basename = sys.argv[2]
except:
    print "biology.py DIRNAME BASENAME"

dirname = os.path.realpath(os.path.expanduser(
    "~/media/phd-data/%s/fixed-wav" % dirname
    ))

def calc_data(dirname, basename):
    search_filename = basename + '*.wav'
    filenames = glob.glob(
        os.path.join(dirname, search_filename))
    filenames.sort()
    if defs.ONLY_N_FILES:
        filenames = filenames[:defs.ONLY_N_FILES]

    detected_freqs, adjusted_freqs, stats, final = estimate_f0_B.estimate_f0_B(filenames)
    f0 = final.f0
    B = final.B

    decayss = []
    for i, wav_filename in enumerate(filenames):
        print "Processing %s" % wav_filename
        plot = False
        decays = chemistry.calc_harmonics(wav_filename, f0, B, plot=plot)
        decayss.extend(decays)
    return decayss, f0, B

def get_data(dirname, basename, recalc=False):
    pickle_filename = os.path.join(dirname, basename+".biology.pickle")
    if os.path.exists(pickle_filename) and not recalc:
        pickle_file = open(pickle_filename, 'rb')
        decayss, f0, B = pickle.load(pickle_file)
        pickle_file.close()
    else:
        decayss, f0, B = calc_data(dirname, basename)
        pickle_file = open(pickle_filename, 'wb')
        pickle.dump(
            (decayss, f0, B),
            pickle_file, -1)
        pickle_file.close()
    return decayss, f0, B


def process(dirname, basename, recalc=False, plot=False):
    inst = basename.split('-')[0]
    st = basename.split('-')[1]
    pc = published_constants.PHYSICAL_CONSTANT_RANGES[inst]
    # find average tension, length
    T = ( pc[st]['T'][0] + pc[st]['T'][1] ) / 2
    L = ( pc['L'][0] + pc['L'][1] ) / 2
    #print T, L

    decayss, f0, B = get_data(dirname, basename)

    nf, nb, na, stats = mode_decays.handle_decays(decayss,
        basename, f0, B, T, L, None,
        plot=plot, recalc=recalc)
    return nf, nb, na, stats, None

process(dirname, basename, plot=True)


