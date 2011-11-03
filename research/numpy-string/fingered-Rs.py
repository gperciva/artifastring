#!/usr/bin/env python

import os
import numpy
import scipy.io.wavfile

from defs import *
import defs
import numpy_string
import scipy.signal
import scipy.stats
import pylab

K_finger = 1e5
K_pluck = 1e4
R_finger = 1e1
R_pluck = 1e1
num_samples = int(8.0 * FS)
release = int(0.1*FS)

DIRNAME="out-fingered-Rs"
if not os.path.exists(DIRNAME):
    os.makedirs(DIRNAME)

def pluck(x1, R_finger):
    filename = DIRNAME + "/pluck-%.3f-%06i.wav" % (x1, R_finger)
    outs = numpy.empty(num_samples)

    vln = numpy_string.Violin()
    vln.finger(1.0 - x1, K_finger, R_finger)

    vln.pluck(0.2, K_pluck, R_pluck)
    for i in range(num_samples):
        outs[i] = vln.tick()

    # calc before normalizing
    #release_samples = outs[ release : ]

    scipy.io.wavfile.write(filename, FS,
        numpy.array(SCALE_WAV_OUTPUT*outs*2**15, dtype=numpy.int16))


R_values = [0, 1, 3, 10, 30, 100]
#R_values = numpy.logspace(-1, 2, 10)

#for x1 in [0.0, 0.109, 0.251, 0.333, 0.5]:
#for x1 in [0.0, 0.251, 0.5]:
pluck(0, 0)
for x1 in [0.109]:
    for R in R_values:
        pluck(x1, R)


pylab.show()


