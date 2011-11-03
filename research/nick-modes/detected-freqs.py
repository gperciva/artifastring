#!/usr/bin/env python

import os
import glob
import re
import pylab

DATA_DIR = os.path.abspath(os.path.expanduser(
    "~/strauss/Violin_Tester/"))

filenames = glob.glob(DATA_DIR+"/*.wav")

def get_freq(filename):
    freq = int( os.path.basename(filename).split('_')[2] )
    return freq

freqs = list(set( [ get_freq(filename) for filename in filenames ] ))
freqs.sort()
print freqs


pylab.plot(freqs)
pylab.show()



