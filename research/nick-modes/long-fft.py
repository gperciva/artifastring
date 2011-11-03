#!/usr/bin/env python

import sys
import math
import os.path
sys.path.append("../shared")

import dsp
import numpy
import scipy.fftpack
import scipy.signal
import scipy.io.wavfile
import pylab

FREQ_WIDTH = 10
ZEROPADDING = 4
NORMALIZE_DB = False
SHORT = False
SHORT = 4096*2
#SHORT = 96000*4

#WINDOW="boxcar"
#WINDOW="halfexponential"

WINDOW="hamming"
#WINDOW="hanning"
#WINDOW="gaussian"

LONG_LORENTZIAN_RSQUARED_MIN = 0.0

def zero_pad_to_next_power_two(x):
    len_power_two = int(pow(2, math.ceil(math.log(len(x),2))))
    x = numpy.append(x, numpy.zeros(len_power_two - len(x)))
    return x

def bin2hertz(bin_number, sample_rate, N):
    return bin_number * sample_rate / float(N)
def hertz2bin(freq, sample_rate, N):
    return freq / sample_rate * float(N)


def get_freqs_fft(signal, sample_rate):
    signal = zero_pad_to_next_power_two(signal)
    if WINDOW is "gaussian":
        window = scipy.signal.gaussian(len(signal), len(signal)/8)
    elif WINDOW is "halfexponential":
        seconds = numpy.arange(0, len(signal)) / float(sample_rate)
        a = -0.1
        window = numpy.exp(seconds * a)
    else:
        window = scipy.signal.get_window(WINDOW, len(signal))

    fft = scipy.fftpack.fft(signal*window, ZEROPADDING*len(signal))
    fft_abs = numpy.abs(fft[:len(fft)/2+1])
    fft_normalized = fft_abs
    #fft_normalized = fft_abs / (sum(window))
    fft_phase = numpy.angle(fft[:len(fft)/2+1])
    #fft_db = stft.amplitude2db(fft_normalized)
    #fft_db = fft_normalized
    freqs = numpy.array([ bin2hertz(i, sample_rate, len(fft))
        for i in range(len(fft_normalized)) ])
    return freqs, fft_normalized, fft_phase, ZEROPADDING*len(signal)


def process(wav_filename, expected_peak_freq):
    sample_rate, data_unnormalized = scipy.io.wavfile.read(wav_filename)
    data = (numpy.array(data_unnormalized, dtype=numpy.float64)
        / float(numpy.iinfo(data_unnormalized.dtype).max))

    # expermental: remove some data
    #data = data[0.2*len(data):0.5*len(data)]
    if SHORT:
        data = data[:SHORT]

    freqs, fft, phase, fft_length = get_freqs_fft(data, sample_rate)
    fft_db = dsp.amplitude2db(fft)
    if NORMALIZE_DB:
        fft_db -= max(fft_db)
    
    filename = "%s-freqs.txt" % (os.path.splitext(wav_filename)[0] )
    numpy.savetxt( filename, numpy.vstack( (freqs, fft_db)).transpose() )

    low_freq = expected_peak_freq - FREQ_WIDTH
    high_freq = expected_peak_freq + FREQ_WIDTH
    low_bin  = hertz2bin(low_freq, sample_rate, fft_length)
    high_bin = hertz2bin(high_freq, sample_rate, fft_length)
    freqs  = freqs [low_bin:high_bin]
    fft_db = fft_db[low_bin:high_bin]
    phase  = phase [low_bin:high_bin]
    return freqs, fft_db, phase


def lorentzian(x, p0, p1, p2):
    if any([p0, p1, p2]) < 0:
        return 1e9*numpy.ones(len(x))
    global noise_floor
    return (p2 / (
          1. + p0**2 * (x - p1)**2)
        + noise_floor
        )

def lorentzian_two(x, p0, p1, p2, p3, p4, p5):
    if any([p0, p1, p2, p3, p4, p5]) < 0:
        return 1e9*numpy.ones(len(x))
    global noise_floor
    return (p2 / (
          1. + p0**2 * (x - p1)**2)
        + p5 / (
          1. + p3**2 * (x - p4)**2)
        + noise_floor)


def fit_area(freqs, fft_db, plot=False, add_plot=False):
    w = freqs
    y = dsp.db2amplitude(fft_db)
    #y = fft_db
    #w = numpy.array( [
    #    bin2hertz(bin_low+i) for i, a in enumerate(peak_area)
    #    ] )
    #y = numpy.array(peak_area)

    global noise_floor
    #noise_floor = scipy.stats.gmean(y)
    noise_floor = min(y)
    mag_est = max(y) - noise_floor

    initial_guess = numpy.array([1.0, w.mean(), mag_est
        ])
    print "initial:", initial_guess
    p, pcov = scipy.optimize.curve_fit(
        lorentzian,
        w, y,
        initial_guess,
        )
    print "fit:", p
    freq = p[1]
    mag = p[2]
    decay = 2*numpy.pi / abs(p[0])
    print "Fit only:\t%.1f\t%.2g\t%.3g" % (
        freq, mag, decay)

    predicted = lorentzian(w, *p)
    rem = y - predicted
    #if False:
    if True:
        pylab.plot(w, dsp.amplitude2db(y), label="FFT")
        pylab.plot(w, dsp.amplitude2db(predicted),
            label="Lorentzian fit")
        pylab.plot(w, dsp.amplitude2db(rem),
            label="residual")
        #pylab.plot(w, y, label="FFT")
        #pylab.plot(w, predicted,
        #    label="Lorentzian fit")
        pylab.show()

    #double_guess = numpy.array([ p[0], p[1], p[2], p[0], p[1],
    #    p[2]/100.0])
    double_guess = numpy.array([ p[0], p[1], p[2],
        1.2, 96.3, 200.0])
    #print "double guess:"
    #print double_guess
    p, pcov = scipy.optimize.curve_fit(
        lorentzian_two,
        w, y,
        double_guess
        )
    print "fit two:"
    print p

    predicted = lorentzian_two(w, *p)
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
    #try:
    #    variance = pcov[0][0]
    #except:
    #    print "bail from variance"
    #    return None, 0, 0, 0
    variance = 0
    freq = p[1]
    mag = p[2]

    decay = 2*numpy.pi / abs(p[0])

    print "Fit first:\t%.1f\t%.2g\t%.3g" % (
        freq, mag, decay)
    print "Fit second :\t%.1f\t%.2g\t%.3g" % (
        p[4], p[5], 2*numpy.pi / abs(p[3]))

    #if rsquared < LONG_LORENTZIAN_RSQUARED_MIN:
    #    print "bail from rsquared", rsquared
    #    return freq, 0, 0, 0
    rem = y - predicted

    if plot:
        logplot = True
        pylab.figure()
        if logplot:
            pylab.plot(w, dsp.amplitude2db(y), label="FFT")
            pylab.plot(w, dsp.amplitude2db(predicted),
                label="Lorentzian fit")
            pylab.plot(w, dsp.amplitude2db(rem),
                label="residual")
            #pylab.semilogy(w, resi, label="residuals")
        else:
            pylab.plot(w, y, label="FFT")
            pylab.plot(w, predicted, label="Lorentzian fit")
            #pylab.plot(w, resi, label="residuals")
        #pylab.xlabel("frequency relative to w_n")
        pylab.xlabel("frequency")
        pylab.ylabel("power")
        pylab.legend()
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



if __name__ == "__main__":
    try:
        filename = sys.argv[1]
        expected_peak_freq = float(sys.argv[2])
    except:
        print "Need a filename and expected freq"
        exit(1)

    freq, fft_db, phase = process(filename, expected_peak_freq)

    
    if False:
    #if True:
        pylab.figure()
        pylab.plot(freq, fft_db)
    
        pylab.xlabel("freq (hz)")
        pylab.ylabel("magnitude (dB)")
        pylab.title(filename)
        #pylab.xlim([min(freq),max(freq)])
        #pylab.xlim([95,97])
        #pylab.ylim([0,100])
        pylab.show()

    #fit_area(freq, fft_db, plot=True, add_plot=False)
    
    #pylab.figure()
    #pylab.plot(freq, phase)
    #pylab.xlabel("freq (hz)")
    #pylab.ylabel("phase")
    #pylab.title(filename)

    pylab.show()
    
    


