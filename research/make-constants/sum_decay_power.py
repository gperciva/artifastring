#!/usr/bin/env python

import numpy


def test_decaying_power(B1, B2):
    print "Testing B1=%.3f, B2=%.3f" % (B1, B2)
    def rn(n):
        return B1 + B2*(n-1)**2
    
    def power(n):
        ns = numpy.arange(1,n)
        r = 1. / rn(ns)
        s = sum(r)
        return s
    
    total = power(128)
    
    for n in [40, 64, 96, 128]:
        print "%i: %.3f" % ( n, power(n) / total * 100)
        
test_decaying_power(5.90, 0.053)
test_decaying_power(7.62, 0.080)
test_decaying_power(1.64, 0.090)



