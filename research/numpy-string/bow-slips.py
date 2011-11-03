#!/usr/bin/env python

import numpy
import scipy.io.wavfile

from defs import *
import defs
import numpy_string

#FS_CANDIDATES = [55000]
FS_CANDIDATES = [55000, 66150, 88200]
#FS_CANDIDATES = [48000, 66150]
#FS_CANDIDATES = [88200]
#FS_CANDIDATES = [44100]
#N_CANDIDATES = [24,28,32,36,]
N_CANDIDATES = [40]
#FS_CANDIDATES = [60000]
#FORCE_CANDIDATES = [0.01, 0.03, 0.1, 0.3, 1.0, 3.0]
#VELOCITY_CANDIDATES = [0.01, 0.03, 0.1, 0.3, 1.0]
#FS_CANDIDATES = [48000]

FORCE_CANDIDATES = numpy.logspace(-1, 0.1, 5)
VELOCITY_CANDIDATES = numpy.logspace(-1, 0, 10)
VELOCITY = 0.1
#FORCE_CANDIDATES = [0.4]
#VELOCITY_CANDIDATES = [1.0]

FORCE_CANDIDATES = numpy.linspace(0.01, 2.0, 5)
POSITION_CANDIDATES = numpy.linspace(0.09, 0.2, 20)

#BOW_POSITION = 0.08


def play(fs, N, bow_position, bow_force, bow_velocity):
    defs.FS = fs
    defs.N = N
    numpy_string.set_constants()
    num_samples = int(SECONDS * FS)
    vln = numpy_string.Violin(num_samples)
    #outs = numpy.empty(num_samples)
    #xf = 2.0/3.0
    xf = 0.0
    vln.finger(xf, K_finger, R_finger)
    #vln.bow(x0, 1.0, 0.2)
    vln.bow(bow_position, bow_force, bow_velocity)

    # skipping
    for i in range(num_samples):
        _ = vln.tick()
    return vln.debug_slips

#go(0.2, 0.5)
#exit(1)

import constants
def thesis_filename(text):
    return "%s-%s.txt" % (text, constants.which_string)


all_file = open("all-fs-N.txt", "w")
for fs in FS_CANDIDATES:
    for N in N_CANDIDATES:
        slips_file = open("%i-%i.txt" % (fs, N), "w")
        for force in FORCE_CANDIDATES:
            velocity = VELOCITY
            for position in POSITION_CANDIDATES:
            #for velocity in VELOCITY_CANDIDATES:
                num_samples = int(SECONDS * FS)
                slips = play(fs, N, position, force, velocity)
                slips_file.write("%.5g\t%.5g\t%.5g\t%.5g\n" % (
                    position, force, velocity, float(slips)/num_samples))
                #all_file.write("%i\t%i\t%.5g\t%.5g\t%.5g\n" % (
                #    fs, N, force, velocity, float(slips)/num_samples))
                all_file.write("%i\t%i\t%.5g\n" % (
                    fs, N, float(slips)/num_samples))
            slips_file.write("\n")
        slips_file.close()
    all_file.write("\n")
all_file.close()

