#!/usr/bin/env python

import numpy
import scipy.io.wavfile

from defs import *
import defs
import numpy_string

K_finger = 1e6
R_finger = 0
num_samples = 1
#num_samples = int(SECONDS * FS)

def play(x0, x1):
    vln = numpy_string.Violin(num_samples)
    #outs = numpy.empty(num_samples)
    vln.finger(x1, K_finger, R_finger)
    vln.bow(x0, 1.0, 0.2)

    # skipping
    for i in range(num_samples):
        val = vln.tick()
        #if val is None:
        #    print "breaking on sample", i
         #   #outs /= max(outs)
        #    break
        #else:
        #    outs[i] = val
    return vln

def go(x0, x1, fs=48000, a11b00_file=None, d5_file=None):
    defs.FS = fs
    numpy_string.set_constants()
    vln = play(x0, x1)
    #d5 = vln.D5
    #max_dv0h = vln.debug_max_dv0h
    A11 = vln.debug_A11
    A10 = vln.debug_A10
    B00 = vln.debug_B00
    B01 = vln.debug_B01
    return vln.debug_B00
    #print "A11, B00:", A11, B00
    #print "A10, B01:", A10, B01
    #print "fake A11, B00:", vln.debug_A11_fake, vln.debug_B00_fake
    #print "fake A01:", vln.debug_A01_fake
    #print "%g\t%g\t%g" % (vln.A00, vln.A01, vln.A11)

    val = A11*B00 - A10*B01
    val2 = vln.D5
    #val = vln.debug_B00
    #val2 = vln.debug_B01
    #val = vln.debug_A11
    #val2 = vln.debug_A10
    #val = vln.debug_B00 - vln.debug_B01
    #val2 = vln.debug_A11 - vln.debug_A10
    text = "%g\t%g\t%g" % (
       x0, x1, val)
    text2 = "%g\t%g\t%g" % (
       x0, x1, val2)
    if a11b00_file is not None:
        a11b00_file.write(text + "\n")
    if d5_file is not None:
        if x0 > 0:
            d5_file.write(text2 + "\n")

#go(0.2, 0.5)
#exit(1)

#FS_CANDIDATES = [22050, 44100, 96000]
#FS_CANDIDATES = [48000]
#FS_CANDIDATES = [53000, 55000, 60000, 66150, 96000, 192000]
FS_CANDIDATES = numpy.linspace(53000, 300000, 100)

import constants
def thesis_filename(text):
    return "%s-%s.txt" % (text, constants.which_string)

a11b00_file = open(thesis_filename("a11b00-a10b01"), 'w')
d5_file = open(thesis_filename("d5"), 'w')

numpy_string.N = 40
numpy_string.n = numpy.arange(1, numpy_string.N+1)

MIN_X0 = 0.1
MAX_X0 = 0.2
STEPS = 100
for fs in FS_CANDIDATES:
    #b00_file = open(thesis_filename("b00-%i" % fs), 'w')
    ###   D5 is negative?!
    #for x0 in numpy.linspace(0.0, 0.0005, STEPS):
    #    for x1 in numpy.linspace(0.016, 0.017, STEPS):
    ### beginning
    #for x0 in numpy.linspace(0.0, 0.04, STEPS):
    #    for x1 in numpy.linspace(0.0, 0.04, STEPS):
    #for x0 in numpy.linspace(0.1, 0.101, STEPS):
    #    for x1 in numpy.linspace(0.1, 0.101, STEPS):
    B00s = []
    for x0 in numpy.linspace(MIN_X0, MAX_X0, STEPS):
        B00 = go(x0, 0, fs, a11b00_file, d5_file)
        #b00_file.write("%g\t%g\n" % (x0, B00) )
        B00s.append(B00)
        continue
    print fs, min(B00s), max(B00s)

    if False:
        for x1 in numpy.linspace(1.0, 0.0, STEPS):
        #for x1 in numpy.linspace(0.99, 1.0, STEPS):
            if not x0 < x1 - 1e-6:
                a11b00_file.write("nan nan nan\n")
                d5_file.write("nan nan nan\n")
                continue
            if x0 == 0 or x1 == 0 or x0 == 1.0 or x1 == 1.0:
                a11b00_file.write("nan nan nan\n")
                d5_file.write("nan nan nan\n")
                continue
            #print '------', x0, x1
            go(x0, x1, fs, a11b00_file, d5_file)
        a11b00_file.write("\n")
        d5_file.write("\n")
    #b00_file.close()
a11b00_file.close()
d5_file.close()



