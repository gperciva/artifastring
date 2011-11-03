#!/usr/bin/env python

import math
import os.path

import numpy
import scipy.io.wavfile
import scipy.fftpack
import scipy.optimize
import scipy.signal
import scipy.stats
import pylab

import defs
import classes

import estimate_f0_B

PLOT_INPUT = False
SECONDS_MAXIMUM = 200.0
NODES_MAXIMUM = defs.TOTAL_HARMONICS

def remove_DC_offset(x):
    return x - x.mean()

def truncate_to_maximum_length(x, maximum_length):
    if len(x) > maximum_length:
        return x[:maximum_length]
    return x

def zero_pad_to_next_power_two(x):
    len_power_two = int(pow(2, math.ceil(math.log(len(x),2))))
    x = numpy.append(x, numpy.zeros(len_power_two - len(x)))
    return x

def bin2hertz(bin_number):
    return float(bin_number) * fs / (WINDOWSIZE)
def hertz2bin(freq):
    return float(freq) * (WINDOWSIZE) / fs


#def lorentzian(p, x):
#    """ curve based on wikipedia
#        http://en.wikipedia.org/wiki/Cauchy_distribution
#            "in physics" section
#    """
#    return abs(p[2]) * ( p[0]**2 / ( (x-p[1])**2 + p[0]**2) )

#def lorentzian(p, x):
#    """ from Important Fourier-transform pairs in NMR spectroscopy
#    """
#    return 2 * p[0] / (
#        1 + (2*numpy.pi*p[0])**2 * (x-p[1])**2)

#def lorentzian(p, x):
#    return p[2] * (p[0]**2 /
#        (p[0]**2 + 4*(p[1] - x)**2))
      
def lorentzian(x, p0, p1, p2):
    return p2 / (
        1. + p0**2 * (x - p1)**2)

def fit_lorentzian(ffta, freq_low, freq_high, f0a, plot=False,
        add_plot=False):
    show = False
    bin_low = hertz2bin(freq_low)
    bin_high = hertz2bin(freq_high)
    peak_area = ffta[ bin_low : bin_high ]

    w = numpy.array( [
        bin2hertz(bin_low+i) for i, a in enumerate(peak_area)
        ] )
    y = numpy.array(peak_area)

    initial_guess = numpy.array([1., w.mean(), 1.])
    p, pcov = scipy.optimize.curve_fit(
        lorentzian,
        w, y,
        initial_guess,
        )
    #print p

    w_eval = w
    predicted = lorentzian(w_eval, *p)
    #logplot = False
    #pylab.figure()
    #if logplot:
    #    pylab.semilogy(w, y, '.', label="FFT")
    #    pylab.semilogy(w_eval, predicted, label="Lorentzian fit")
    #    pylab.show()
    #else:
    #    pylab.plot(w, y, '.', label="FFT")
    #    pylab.plot(w_eval, predicted, label="Lorentzian fit")
    #    pylab.show()

    ss_err = ((y - predicted)**2).sum()
    ss_tot = ((y-y.mean())**2).sum()
    rsquared = 1.-(ss_err/ss_tot)
    try:
        variance = pcov[0][0]
        #print variance
    except:
        return None, 0, 0, 0
    freq = p[1]

    decay = 2*numpy.pi / abs(p[0])

    if rsquared < defs.LONG_LORENTZIAN_RSQUARED_MIN:
        #print "bail from rsquared", rsquared
        return freq, 0, 0, 0

    if plot:
        logplot = True
        pylab.figure()
        if logplot:
            pylab.semilogy(w, y, label="FFT")
            pylab.semilogy(w_eval, predicted, label="Lorentzian fit")
            #pylab.semilogy(w, resi, label="residuals")
        else:
            pylab.plot(w, y, label="FFT")
            pylab.plot(w_eval, predicted, label="Lorentzian fit")
            #pylab.plot(w, resi, label="residuals")
        pylab.title("Searching for mode around %.5g" % (f0a))
        #pylab.xlabel("frequency relative to w_n")
        pylab.xlabel("frequency")
        pylab.ylabel("power")
        pylab.legend()
        if show:
            pylab.show()
    if add_plot:
        low = min(w_eval)
        high = max(w_eval)
        pylab.axvspan(low, high, color='c', alpha=0.3,
           label="stiff")
        pylab.plot(w_eval, numpy.log(predicted),
        #pylab.plot(w_eval, (predicted),
            label="Lorentzian fit",
            color="red")
    return freq, decay, rsquared, variance

def mode_B2freq(base, mode, B):
    return mode * base * math.sqrt(1.0 + B * mode**2)

def test():
    global fs
    fs = 1000
    seconds = 2.0
    t = numpy.linspace(0, seconds, fs*seconds)
    f = 200.
    w = 2 * numpy.pi * f
    a = 10.0
    sig = 7*numpy.cos(w*t) * numpy.exp(-a*t)
    #pylab.plot(t, sig)
    
    fft = scipy.fftpack.fft(sig)
    fft_positive = abs(fft[0:len(fft)/2])
    fft_normalized = fft_positive / float(len(sig))
    fft_power = fft_normalized**2
    
    #pylab.plot(fft_power)
    
    freq_low = 180
    freq_high = 220
    f0a = f
    global WINDOWSIZE
    WINDOWSIZE = len(sig)
    
    freq, decay = fit_lorentzian(fft_power, freq_low, freq_high, f0a,
        False, False)
        #True, False)
    print freq, decay
    
    pylab.show()

#test()
#exit(1)


def calc_harmonics(wav_filename, f_0=None, B=None, plot=False):
    wav_filename = os.path.realpath(os.path.expanduser(wav_filename))

    if f_0 is None:
        detected_freqs, adjusted_freqs, stats, final = estimate_f0_B.estimate_f0_B(
            [wav_filename])
        f_0 = final.f0
        B = final.B
        print "Estimating f_0 and B from single file, but not good!"

    global fs
    global WINDOWSIZE
    fs, rawwav = scipy.io.wavfile.read(wav_filename)
    wav = rawwav / float(numpy.iinfo(rawwav.dtype).max)

    wav = truncate_to_maximum_length(wav, SECONDS_MAXIMUM * fs)
    wav = remove_DC_offset(wav)
    
    #print len(wav)
    wav = zero_pad_to_next_power_two(wav)
    #print len(wav)
    
    buf = wav
    
    ZERO_PADDING = 4
    WINDOWSIZE = ZERO_PADDING * len(buf)
    
    fft = scipy.fftpack.fft(buf, WINDOWSIZE)
    fft_positive = abs(fft[0:len(fft)/2])
    fft_normalized = fft_positive / float(WINDOWSIZE)
    fft_power = fft_normalized**2
    #fft_examine = fft_normalized
    fft_examine = fft_power
    
    freqs = numpy.array(
        [ bin2hertz(i) for i, y in enumerate(fft_examine) ]
        )
    
    if plot:
        pylab.figure()
        # avoid the 0 DC offset term
        pylab.plot(
            [ f for f, m in zip(freqs[1:], fft_examine[1:]) if m > 0.0],
            [ numpy.log(m) for f, m in zip(freqs[1:], fft_examine[1:]) if m > 0.0],
            )
        pylab.title("Overall power\n%s" % (wav_filename))
    
    #search_radius = defs.PEAK_SPREAD_HERTZ
    search_radius = defs.LONG_PEAK_AREA_HERTZ

    
    print "f_0: %.3f \t B: %.3g" % (f_0, B)

    decays = []
    add_plot = plot
    plot = False
    for n in range(1,NODES_MAXIMUM+1):
        #if add_plot:
        if False:
            pylab.axvline( n*f_0,
                color="pink",
                #linewidth=3.0,
                alpha=0.8,
                label="ideal",
                )
            pylab.axvline( mode_B2freq(f_0, n, B/4),
                color="purple",
                #linewidth=3.0,
                alpha=0.8,
                label="experimental B/4",
                )
        freq_center = mode_B2freq(f_0, n, B)
        freq_low  = freq_center - search_radius
        freq_high = freq_center + search_radius
        plot = False
        freq, alpha, rsquared, variance = fit_lorentzian( fft_examine,
            freq_low, freq_high, freq_center,
            plot=plot, add_plot=add_plot)

        if alpha == 0:
            continue
        w = 2*numpy.pi*freq
        Q = w / (2*alpha)
        drop = 0
        decay = classes.Decay(freq, w, n, alpha, Q, rsquared, variance, drop)
        decays.append(decay)
    if add_plot:
        pylab.show()
    return decays
    

if __name__ == "__main__":
    import sys
    freq = None
    try:
        freq = float(sys.argv[2])
    except:
        freq = None
    decays = calc_harmonics(sys.argv[1], freq, B=0, plot=True)
    for d in decays:
        print d.n, d.alpha, d.rsquared, d.variance

