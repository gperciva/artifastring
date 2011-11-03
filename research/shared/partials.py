#!/usr/bin/env python

import math
import numpy
import scipy.stats
numpy.seterr(all='raise')

try:
    import classes
    import plots
except:
    pass

import pylab

### convenience functions
def mode_B2freq(base, mode, B):
    return mode * base * numpy.sqrt(1.0 + B * mode**2)

def peak_stiff(base, mode, B):
    return mode_B2freq(base, mode, B)
def peak_ideal(base, mode):
    return mode * base


### extract partials
def quadratic_interpolation(bin_highest, fft_power):
    """ implementation of
    https://ccrma.stanford.edu/~jos/sasp/Quadratic_Interpolation_Spectral_Peaks.html
    and
    https://ccrma.stanford.edu/~jos/sasp/Matlab_Parabolic_Peak_Interpolation.html
    fit to peak forumula:
        y(x) = a*(x-p)^2+b
    """
    alpha = math.log( fft_power[bin_highest-1] )
    beta  = math.log( fft_power[bin_highest  ] )
    gamma = math.log( fft_power[bin_highest+1] )
    #p = 0.5 * (alpha-gamma) / (alpha-2*beta+gamma)
    p = (gamma-alpha) / (2*(2*beta-gamma-alpha))
    if abs(p) > 0.5:
        raise Exception("error in p")
    # height y
    yp = beta - 0.25*(alpha-gamma)*p
    if yp < beta:
        raise Exception("error in yp")
    # location (on x axis)
    interpolated_bin = bin_highest + p
    # half-curvature
    a = 0.5*(alpha - 2*beta + gamma)
    return interpolated_bin, math.exp( yp ), a


def qifft_synthesize(peak_bin, peak_mag, half_curvature, length):
    """ synthesize a parabolic peak from quadratic interpolation """
    fx = numpy.vectorize(lambda x: numpy.exp(
        half_curvature*((x - peak_bin)**2) + numpy.log(peak_mag)
        ))
    bin_numbers = numpy.arange(length)
    return fx(bin_numbers)


def get_peaks(signal, bin_target, bin_spread_below, bin_spread_above):
    """ find peaks around bin_target in signal, with radius
    bin_spread.  Peaks must be higher than the geometric mean of
    the surrounding values."""
    peaks = []
    surrounding = signal[bin_target-bin_spread_below : bin_target+bin_spread_above+1]
    surrounding_gmean = scipy.stats.gmean(surrounding)
    for i in xrange(bin_target-bin_spread_below, bin_target+bin_spread_above+1):
        if i+1 >= len(signal):
            break
        if signal[i-1] < signal[i] > signal[i+1]:
            if signal[i] > surrounding_gmean:
                peaks.append(i)
    return peaks


def get_freqs_mags(num_harmonics, bin_f0, B, fft,
        bin_spread_below, bin_spread_above,
        only_peaks=False, Bsearch=False):
    stiff_partials = []
    ideal_partials = []
    for n in range(1, num_harmonics+1):
        stiff_bin_exact = mode_B2freq(bin_f0, n, B)
        if stiff_bin_exact >= len(fft):
            continue
        stiff_bin = int(stiff_bin_exact)
        stiff_peaks = get_peaks(fft, stiff_bin,
            bin_spread_below, bin_spread_above)
        # ASSUME: we never "catch up" with the next ideal frequency
        # this is a false assumption, but we'll remove those later
   
        ideal_bin = int(bin_f0 * n)
        ideal_peaks = get_peaks(fft, ideal_bin,
            bin_spread_below, bin_spread_above)
        ideal_peaks[:] = [ ip for ip in ideal_peaks if ip not in stiff_peaks]

        consider = []
        for sp in stiff_peaks:
            peak_bin, peak_mag, curvature_a = quadratic_interpolation(
                sp, fft)
            if peak_mag < fft[stiff_bin]:
                continue
            if not Bsearch:
                ### find the nearest+highest peak?
                delta = abs(peak_bin - stiff_bin_exact)
                key = delta / peak_mag
                consider.append( (key,
                    classes.HarmonicFrame(peak_bin, peak_mag, n, curvature_a)) )
            else:
                ### yes, remove the abs here -- favor
                ### high-frequency peaks (but still keep them >0)
                delta = peak_bin - stiff_bin_exact + bin_spread_below
                key = -delta / peak_mag
                consider.append( (key,
                    classes.HarmonicFrame(peak_bin, peak_mag, n, curvature_a)) )
        consider.sort()
        if len(consider) == 0:
            if not only_peaks:
                # TODO: what's reasonable for the curvature here?
                surrounding = fft[stiff_bin-bin_spread_below :
                    stiff_bin+bin_spread_above+1]
                surrounding_gmean = scipy.stats.gmean(surrounding)
                mag = surrounding_gmean
                stiff_partials.append(
                    classes.HarmonicFrame(stiff_bin, mag, n,
                        curvature_a=-1e-4))
        else:
            stiff_partials.append( consider[0][1] )

        # yes, keep all ideal peaks
        for ip in ideal_peaks:
            peak_bin, peak_mag, curvature_a = quadratic_interpolation(
                ip, fft)
            ideal_partials.append(
                classes.HarmonicFrame(peak_bin, peak_mag, n, curvature_a))
    return stiff_partials, ideal_partials


