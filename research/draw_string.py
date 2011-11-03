#!/usr/bin/env python 

import os.path
import sys

import numpy
import pylab

DRAW_SAMPLE_RATE = 44100
FINGER_DOT = 0.75
# set to 0 to disable
MAX_TIME = 0.01
PNG_DIRNAME = "out-disp"

filename = sys.argv[1]
basename = os.path.splitext(os.path.basename(filename))[0]

data = numpy.loadtxt(filename)

num_rows, num_columns = data.shape
seconds = data[:,0]
displacements = data[:,1:]
ylim = numpy.max(abs(displacements), axis=None)

#print seconds
#print displacements
#print num_columns

x = numpy.linspace(0, 1, num_columns-1)

if MAX_TIME > 0:
    plot_up_to_row = int(44100*MAX_TIME)
else:
    plot_up_to_row = num_rows

for i in range(plot_up_to_row):
    if i % (44100 / DRAW_SAMPLE_RATE) > 0:
        continue
    seconds = float(i)/44100.0
    filename = os.path.join(PNG_DIRNAME,
        "%s-%.6f.png" % (basename, seconds))

    pylab.figure()
    pylab.plot(x, displacements[i])
    if FINGER_DOT > 0:
        pylab.plot( FINGER_DOT, 0, '.', color='red')

    pylab.ylim([-ylim, ylim])
    pylab.xlabel("Position along string (bridge at 0, nut at 1)")
    pylab.ylabel("Displacement (m)")
    pylab.title("String at %.6f seconds" % seconds)
    pylab.savefig(filename)
    pylab.close()


