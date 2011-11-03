#!/usr/bin/env python

import math
import numpy
import scipy.stats
numpy.seterr(all='raise')
numpy.seterr(under='ignore')

import stft

import defs
import classes

import plots
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


def qifft_synthesize(peak_bin, peak_mag, half_curvature, radius):
    """ synthesize a parabolic peak from quadratic interpolation """
    fx = numpy.vectorize(lambda x: numpy.exp(
        half_curvature*((x - peak_bin)**2) + numpy.log(peak_mag)
        ))
    low = int(peak_bin) - radius
    high = int(peak_bin) + radius
    bin_numbers = numpy.arange(low, high)
    return fx(bin_numbers)


def get_peaks(signal, bin_target, bin_spread_below, bin_spread_above):
    """ find peaks around bin_target in signal, with radius
    bin_spread.  Peaks must be significantly higher than the
    surrounding values."""
    peaks = []
    low = bin_target - bin_spread_below
    high = bin_target + bin_spread_above+1
    #print "target:", bin_target, bin_spread_below, bin_spread_above
    #surrounding = signal[bin_target-4*bin_spread_below :
    #    bin_target+4*bin_spread_above+1]
    #surrounding_mean = (defs.B_HIGHER_THAN_SURROUNDING_FACTOR
    #    #*scipy.stats.gmean(surrounding))
    #    *scipy.mean(surrounding))
    for i in xrange(low, high):
        if i+1 >= len(signal):
            break
        if signal[i-1] < signal[i] > signal[i+1]:
            #if i > 600:
            #if False:
            #    print "attempting", bin_target
            #    print surrounding_mean, signal[i]
            #    pylab.figure()
            #    pylab.plot(range(bin_target-4*bin_spread_below,
            #        bin_target+4*bin_spread_above+1), surrounding)
            #    pylab.axhline(surrounding_mean)
            #    pylab.show()
            #    exit(1)
            #    print surrounding_mean, signal[i]
            #if signal[i] > surrounding_mean:
            peaks.append(i)
    return peaks

def areas(num_harmonics, bin_f0, B, fft, bin_spread_below, bin_spread_above):
    harms = []
    #pylab.plot(fft)
    for n in range(1, num_harmonics+1):
        if n is 1:
            low_exact = 0.0
        else:
            low_exact = mode_B2freq(bin_f0, n-1, B)
        this_exact = mode_B2freq(bin_f0, n, B)
        #high_exact = mode_B2freq(bin_f0, n+1, B)
        #radius = (this_exact - low_exact) * 0.05
        #bin_low = int(this_exact - radius)
        #bin_high = int(this_exact + radius + 1)
        bin_low = int(this_exact - bin_spread_below)
        bin_high = int(math.ceil(this_exact + bin_spread_above))

        area = fft[bin_low:bin_high]
        area_bins = numpy.arange(bin_low, bin_high)
        #window = scipy.signal.get_window("hamming",
        #    bin_high-bin_low)
        wind = (area_bins - bin_low) / float((bin_high-bin_low-1))
        window = numpy.sin( wind * numpy.pi )
        consider = area*window
        #pylab.plot(consider)
        #pylab.show()
        #print len(consider)


        exp, local_snr = partial_explanatory(fft,
            classes.HarmonicFrame(this_exact, fft[this_exact], n, 0),
            bin_spread_below, bin_spread_above)
        if local_snr < 5:
            #print '------------------'
            harms.append(
                classes.HarmonicFrame(0, 0, n, 0) )
        else:
            harms.append(
                classes.HarmonicFrame(this_exact, sum(consider), n, 0) )

        #pylab.plot(area)
        #pylab.plot(consider)
        #pylab.show()

    return harms

seen_partials = []
def partial_explanatory(fft, partial, bin_spread_below, bin_spread_above):
    #if partial.n < 15 and partial.n > 1:
    bin_target = int(partial.fft_bin)
    #print bin_target
    radius_factor = 1

    wide_radius_factor = 3
    wide_low  = bin_target - wide_radius_factor*bin_spread_below
    wide_high = bin_target + wide_radius_factor*bin_spread_above+2
    wide = fft[wide_low:wide_high]
    wide_gmean = scipy.stats.gmean(wide)
    local_snr = stft.amplitude2db(partial.mag / wide_gmean)
    #pylab.plot(wide)
    #pylab.show()

    #print bin_target
    bin_spread_below = 10
    bin_spread_above = 10
    low  = bin_target - radius_factor*bin_spread_below
    high = bin_target + radius_factor*bin_spread_above+2
    #print low, bin_target, high
    surrounding = fft[low:high]


    #synth_min_cutoff = 0.9 * min(numpy.where(fft>0, fft, 1))
    synthesized_peak = qifft_synthesize(partial.fft_bin, partial.mag,
        partial.curvature_a, bin_spread_below+2)
    synthesized_peak = synthesized_peak[2:]
    #print synthesized_peak
    #synthesized_peak = synthesized_peak[low:high]
    #synthesized_peak = numpy.where(
    #                synthesized_peak > synth_min_cutoff,
    #                            synthesized_peak, 0)
    residual = surrounding - synthesized_peak
    residual = numpy.sqrt(residual**2)
    residual_rms = numpy.sqrt( residual**2 ).mean()
    #residual_ratio = partial.mag / residual_rms

    surrounding_rms = numpy.sqrt( surrounding**2 ).mean()
    residual_removed = (surrounding_rms - residual_rms) / surrounding_rms
    explanatory = residual_removed

    #print partial.n, residual_ratio, residual_removed

    global seen_partials
    #if False:
    if True:
        return explanatory, local_snr
    elif partial.n in seen_partials:
        return explanatory
    else:
        seen_partials.append(partial.n)
    #surrounding_mean = (defs.B_HIGHER_THAN_SURROUNDING_FACTOR
    #if partial.n > 15:
    #if True:
        large_surrounding = fft[low-10:high+10]
        pylab.semilogy(numpy.arange(low, len(surrounding)+low),
            surrounding, '-')
        pylab.semilogy(partial.fft_bin, partial.mag, 'o')
        pylab.semilogy(
                numpy.array([ f for f, m in enumerate(synthesized_peak) if m > 0.0 ]) + low,
                numpy.array(
                    [ m for f, m in enumerate(synthesized_peak) if m > 0.0 ],
                    ))
        pylab.semilogy(numpy.arange(low, high), residual, '-')
        pylab.ylim([1e-6, 1e-1])

        #pylab.semilogy(numpy.arange(low-10,high+10),
        #    large_surrounding, '-')
        pylab.show()
    #exit(1)
    return explanatory, local_snr


def get_freqs_mags(num_harmonics, bin_f0, B, fft,
        bin_spread_below, bin_spread_above,
        only_peaks=False, Bsearch=False):
    if Bsearch is False:
        return areas(num_harmonics, bin_f0, B, fft,
            bin_spread_below, bin_spread_above), []
    if False:
    #if Bsearch is False:
        harms = []
        for n in range(1, num_harmonics+1):
            stiff_bin_exact = mode_B2freq(bin_f0, n, B)
            x1 = int(stiff_bin_exact)
            x2 = int(stiff_bin_exact)+1
            mag = numpy.interp(
                stiff_bin_exact,
                [x1, x2],
                [fft[x1], fft[x2]])

            harms.append(
                classes.HarmonicFrame(stiff_bin_exact,
                    mag, n, 0) )
        return harms

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
                #print "omit, peak too low to be of interest"
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
                #delta = peak_bin - stiff_bin_exact + bin_spread_below
                #key = -delta / peak_mag
                ### no, that's wrong
                delta = abs(peak_bin - stiff_bin_exact)
                #key = delta / peak_mag
                partial = classes.HarmonicFrame(peak_bin, peak_mag,
                    n, curvature_a)
                exp, local_snr = partial_explanatory(fft, partial, bin_spread_below, bin_spread_above)
                partial.explanatory = exp
                partial.local_snr = local_snr
                key = exp / delta
                consider.append( (key, partial) )
        consider.sort(reverse=True)
        #print '  ', n, len(consider)
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
        elif len(consider) == 1:
            stiff_partials.append( consider[0][1] )
        else:
            #print '--- multi  ', n
            #for c in consider:
            #    print c[1].fft_bin
            #    print c[1].explanatory
            #print '--- /multi'
            stiff_partials.append( consider[0][1] )
            #print 'picked: ', consider[0][1].fft_bin

        # yes, keep all ideal peaks
        for ip in ideal_peaks:
            peak_bin, peak_mag, curvature_a = quadratic_interpolation(
                ip, fft)
            ideal_partials.append(
                classes.HarmonicFrame(peak_bin, peak_mag, n, curvature_a))

    if not Bsearch:
        pars = stiff_partials
    else:
        pars = []
        for partial in stiff_partials:
            #print partial.explanatory
            #exp = partial_explanatory(fft, partial, bin_spread_below, bin_spread_above)
            #partial.explanatory = exp
            if partial.explanatory > defs.B_MIN_PEAK_EXPLANATORY:
                if partial.local_snr > defs.B_MIN_LOCAL_SNR:
                    pars.append(partial)
                else:   
                    #print "bail from SNR", partial.n, partial.local_snr
                    pass
            else:
                #print "bail from EXPLANATORY", partial.n, partial.explanatory
                pass
    #print [ h.fft_bin for h in stiff_partials if h.n >= 19 ]
    #return stiff_partials, ideal_partials
    #return pars, ideal_partials
    return pars, []


