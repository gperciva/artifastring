#!/usr/bin/env python

import os.path
import sys
import glob

import numpy
import pylab

HOPSIZE=512
SAMPLE_RATE=48000

MAX_SECONDS = 3.0
#MAX_SECONDS = 0.02

def write_plot(base_filename):
    filenames = glob.glob(os.path.join(
        "spectrum", base_filename, "spectrum-*.txt"))
    filenames.sort()
    for i, filename in enumerate(filenames):
        seconds = i*HOPSIZE / float(SAMPLE_RATE)
        if seconds > MAX_SECONDS:
            print "Reached time cutoff of %.1f" % MAX_SECONDS
            return
        print i, filename
        fft = numpy.loadtxt(filename)
        harms = numpy.loadtxt(filename.replace("spectrum-", "harms-"))
        outfilename = filename.replace("spectrum-", base_filename+"-").replace(".txt", ".png")

        #pylab.figure()
        pylab.semilogy(fft[:,0], fft[:,1])
        pylab.semilogy(harms[:,0], harms[:,1], 'ro')
        pylab.ylim([1e-16, 1e-2])
        pylab.xlabel("Modes")
        pylab.ylabel("Power of FFT")
        pylab.title("Evolution of harmonics: %s\n%.3fs seconds" % (
            base_filename, seconds))
        pylab.savefig(outfilename)
        pylab.close()
        #pylab.show()

write_plot(sys.argv[1])

