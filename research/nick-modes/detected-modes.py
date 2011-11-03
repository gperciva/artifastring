#!/usr/bin/env python

import os
import glob
import numpy
import re
import pylab

HOPSIZE = 1024
FS = 48000.0
HOP_RATE = HOPSIZE / FS

SPECTRUM_DIRS = os.path.abspath(os.path.expanduser(
    "~/spectrum/labVl_a_05"))

dirnames = glob.glob(SPECTRUM_DIRS+"*")
dirnames.sort()

freqss = []
magss = []
for d in dirnames:
    print "reading from dir", d
    filenames = glob.glob(d + "/harms-*.txt")
    filenames.sort()
    freqs = []
    mags = []
    for filename in filenames:
        line = open(filename).readlines()[0].split()
        freq = float(line[0])
        mag = float(line[1])
        freqs.append(freq)
        mags.append(mag)
    freqss.append(numpy.array(freqs))
    magss.append(numpy.array(mags))

for i in range(len(freqss)):
    seconds = numpy.arange(0, len(magss[i])) * HOP_RATE
    db = 20*numpy.log(magss[i])
    pylab.plot(seconds, db, '-',
        label=("%i" % i))

pylab.legend()
pylab.show()




