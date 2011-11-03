#!/usr/bin/env python

import glob
import os
import sys

import numpy
import pylab
import matplotlib

try:
    basename = sys.argv[1]
except:
    print "need basename"
    exit(1)

MAX_MODES = 35
ns = numpy.arange(1, MAX_MODES)

def main():
    filenames = glob.glob(
        os.path.join("out", basename + "*.detected.modes.txt"))
    for fi, filename in enumerate(filenames):
        color = matplotlib.cm.gist_rainbow(float(fi)/len(filenames))
        detected = numpy.loadtxt(filename)
        pylab.plot(detected[:,0], detected[:,1], '.', color=color)

        medians = []
        ones = 0
        for row in detected:
            if row[0] == 1:
                ones += 1
        min_for_median = max(3, ones/2)
        for i in range(MAX_MODES):
            n = i+1
            decays = []
            for row in detected:
                if row[0] == n:
                    decays.append(row[1])
            #print decays
            if len(decays) >= min_for_median:
                median = numpy.median(decays)
                medians.append(median)
            else:
                medians.append(None)
            #print medians
        pylab.plot(
            [n for n, m in zip(ns, medians)
                if m is not None],
            [m for n, m in zip(ns, medians)
                if m is not None],
            'o', color=color)
        #all_medians.append( numpy.array(medians) )
        #print detected
    pylab.show()

main()



