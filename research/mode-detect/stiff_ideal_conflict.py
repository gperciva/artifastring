#!/usr/bin/env python

import numpy
import partials

import defs

def stiff_plus(bin_f0, B, n):
    return partials.mode_B2freq(bin_f0, n, B)

#def ideal(bin_f0, B, n):
#    return partials.mode_B2freq(bin_f0, n, B/4)

def ideal(bin_f0, B, n):
    return bin_f0*n

def does_confict(bin_f0, B, bin_spread_below, bin_spread_above, n):
    if n < defs.B_MIN_HARMONIC_F0_CONFLICT:
        return False
    #print bin_f0, B, n
    stiff = stiff_plus(bin_f0, B, n)

    ns = numpy.arange(1, 2*defs.TOTAL_HARMONICS)
    for conflict_n in ns:
        ideala = ideal(bin_f0, B, conflict_n)
        ideal_low = ideala - bin_spread_below
        ideal_high = ideala + bin_spread_above
        if ideal_low < stiff < ideal_high:
            return True
    return False
 

def find_limit(bin_f0, B, bin_spread_below, bin_spread_above, plot=False):
    ns = numpy.arange(1, 2*defs.TOTAL_HARMONICS)
    stiffs = stiff_plus(bin_f0, B, ns) + 1*bin_spread_above
    ideals = ideal(bin_f0, B, ns+1) - 1*bin_spread_below

    limit = 2*defs.TOTAL_HARMONICS
    for i, n in enumerate(ns):
        #print n, stiffs[i], ideals[i]
        if stiffs[i] > ideals[i]:
            #print stiffs[i], ideals[i]
            limit = n - 1 # bail at previous mode
            #print "bail at mode n:\t", n, stiffs[i], ideals[i]
            break
    #plot=True
    if plot:
        import pylab
        pylab.plot(ns, stiffs, label="stiff_plus")
        pylab.plot(ns, ideals, label="ideal+1")
        pylab.legend(loc=2)
        print limit
        pylab.show()
    return limit
    #return defs.TOTAL_HARMONICS

#find_limit(147.7, 1.12e-04, True)

