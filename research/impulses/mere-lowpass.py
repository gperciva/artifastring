#!/usr/bin/env python

import numpy
import scipy
import scipy.signal
import pylab

PLOT = True
PLOT = False
NUM_TAPS = 63
CUTOFF = 18000.0

NO_IMPULSES = True

HEADER_BEGIN = """/* This file was automatically generated */
#ifndef BODY_MERE_LOWPASS_H
#define BODY_MERE_LOWPASS_H

const int NUM_TAPS_%(mult)i = %(num_taps)i;
const int BODY_%(name_upper)s_NUMBER_%(mult)i = %(num_instruments)i;
const float BODY_%(name_upper)s_S_%(mult)i[%(num_instruments)i][%(num_taps)i] = {
"""
HEADER_BOTTOM = """
};
#endif
"""


def try_fs(mul):
    fs = 44100.0 * mul
    cutoff_rel = CUTOFF / (fs/2)
    
    b = scipy.signal.firwin(NUM_TAPS, cutoff=cutoff_rel)
    #w, h = scipy.signal.freqz(b, worN=2048)
    w, h = scipy.signal.freqz(b)
    
    w = w/numpy.pi * (fs/2)
    h_db = 20*numpy.log(abs(h))

    orig = numpy.zeros(101)
    orig[0] = 1.0
    filt = scipy.signal.lfilter(b, 1, orig)
    
    if PLOT:
        pylab.plot(w, h_db)
        #pylab.xlim([1.0, (fs/2)])
        pylab.xlim([1.0, 44100/2])
        pylab.ylim([-100, 0])

    #pylab.plot(b)
    #pylab.show()
    pylab.plot(orig)
    pylab.plot(filt)
    pylab.show()


try_fs(1)
try_fs(2)

if PLOT:
    pylab.show()

