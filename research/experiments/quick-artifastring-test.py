#!/usr/bin/env python

import sys
sys.path.append('../../build/swig')
sys.path.append('../../build/.libs')


import math
import numpy

import artifastring_instrument
#import monowav

import scipy
import pylab


violin = artifastring_instrument.ArtifastringInstrument()
#wavfile = monowav.MonoWav("artifastring-test.wav")

bp = 0.1
force = 1.0
bv = 0.5
violin.bow(0, bp, force, bv)

buf = numpy.empty(1000, dtype=numpy.int16)
violin.wait_samples(buf)

pylab.plot(buf)
pylab.show()

