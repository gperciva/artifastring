#!/usr/bin/env python

### convenience classs
class HarmonicFrame:
    def __init__(self, fft_bin=None, mag=None, n=None,
curvature_a=None, explanatory=None):
        self.fft_bin = fft_bin
        self.mag = mag
        self.n = n
        self.curvature_a = curvature_a
        self.explanatory = explanatory

class HarmonicSignal:
    def __init__(self, n=None):
        self.n = n
        self.mags = []
        self.frame_numbers = []

class Decay:
    def __init__(self, freq, w, n, alpha, Q, rsquared, variance, drop):
        self.freq = freq
        self.w = w
        self.n = n
        self.alpha = alpha
        self.Q = Q
        self.rsquared = rsquared
        self.variance = variance
        self.drop = drop


