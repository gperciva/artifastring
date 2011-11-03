#!/usr/bin/env python

import os
import sys
sys.path.append("../shared")

import dsp
import numpy
numpy.seterr(under='ignore')
import scipy.io.wavfile
import scipy.fftpack
import scipy.signal
import pylab
import math

#HOPSIZE = 1024
HOPSIZE = 4096*2
#HOPSIZE = 65536*2
ZEROPADDING = 4

#WINDOW="boxcar"
WINDOW="hamming"
#WINDOW="hanning"
#WINDOW="gaussian"
#WINDOW="blackmanharris"
#WINDOW="bartlett"
#WINDOW="triang"
#WINDOW="tukey"

FREQ_WIDTH = 20


def tukeywin(window_length, alpha=0.5):
    '''The Tukey window, also known as the tapered cosine window,
can be regarded as a cosine lobe of width \alpha * N / 2
    that is convolved with a rectangle window of width (1 - \alpha
/ 2). At \alpha = 1 it becomes rectangular, and
    at \alpha = 0 it becomes a Hann window.

    We use the same reference as MATLAB to provide the same
results in case users compare a MATLAB output to this function
    output

    Reference
    ---------
    http://www.mathworks.com/access/helpdesk/help/toolbox/signal/tukeywin.html

    '''
    # Special cases
    if alpha <= 0:
        return numpy.ones(window_length) #rectangular window
    elif alpha >= 1:
        return numpy.hanning(window_length)

    # Normal case
    x = numpy.linspace(0, 1, window_length)
    w = numpy.ones(x.shape)

    # first condition 0 <= x < alpha/2
    first_condition = x<alpha/2
    w[first_condition] = 0.5 * (1 + numpy.cos(2*numpy.pi/alpha * (x[first_condition] - alpha/2) ))

    # second condition already taken care of

    # third condition 1 - alpha / 2 <= x <= 1
    third_condition = x>=(1 - alpha/2)
    w[third_condition] = 0.5 * (1 + numpy.cos(2*numpy.pi/alpha * (x[third_condition] - 1 + alpha/2))) 

    return w

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

def bin2hertz(bin_number, sample_rate, N):
    return float(bin_number) * (sample_rate/2) / (N/2+1)
def hertz2bin(freq, sample_rate, N):
    return float(freq) / (sample_rate/2) * (N/2+1)


def freq_stuffs(freqs, ffts_power, sample_rate, FFT_LENGTH,
        expected_peak_freq):
    low_bin = hertz2bin(expected_peak_freq - FREQ_WIDTH,
        sample_rate, FFT_LENGTH)
    high_bin = hertz2bin(expected_peak_freq + FREQ_WIDTH,
        sample_rate, FFT_LENGTH)

    ex_freqs = freqs[low_bin:high_bin]
    ex_power = ffts_power[:,low_bin:high_bin]

    for i in range(ex_power.shape[0]):
        ex = ex_power[i]

        bin_highest = ex.argmax()
        interp_bin, yp, a = quadratic_interpolation(bin_highest, ex)
        interp_freq = (  (low_bin + interp_bin)
            * (sample_rate/2) / (FFT_LENGTH/2+1)
            )
        #print "%.2f\t%.2f\t%.4f" % (interp_freq, yp, a)

        #fit_gaussian(ex_freqs, ex)
        fit_lorentzian(ex_freqs, numpy.sqrt(ex))
        #if i > 4:
        #    exit(1)
        #pylab.plot(ex)
        #pylab.show()


def stft(wav_filename, expected_peak_freq):
    sample_rate, wav_data = scipy.io.wavfile.read(wav_filename)
    wav_data = wav_data / float(numpy.iinfo(wav_data.dtype).max)
    smallsize = int(len(wav_data) / HOPSIZE)
    wav_data = wav_data[:HOPSIZE*smallsize]
    wav_data = wav_data.reshape(smallsize, HOPSIZE)

    if WINDOW is "gaussian":
        window = scipy.signal.gaussian(HOPSIZE, HOPSIZE/8)
    if WINDOW is "chebwin":
        window = scipy.signal.chebwin(HOPSIZE, 2.0)
    if WINDOW is "tukey":
        window = tukeywin(HOPSIZE)
    else:
        window = scipy.signal.get_window(WINDOW, HOPSIZE)
    wav_data *= window

    FFT_LENGTH = ZEROPADDING*HOPSIZE
    ffts = scipy.fftpack.fft(wav_data, FFT_LENGTH,  axis=1)
    ffts_abs = abs(ffts)
    ffts_normalized = ffts_abs
    #ffts_normalized = ffts_abs / (sum(window))
    ffts_power = ffts_normalized**2
    freqs = numpy.array([
        bin2hertz(i, sample_rate, FFT_LENGTH)
        for i in xrange(ffts_power.shape[1])
        ])

    #freq_stuffs(freqs, ffts_power, sample_rate, FFT_LENGTH, expected_peak_freq)
    return freqs, ffts_power

def parabola(x, p0, p1, p2):
    a = p1
    p = p0
    b = p2
    return a * (x - p)**2 + b

def fit_gaussian(freqs, fft_power, plot=False):
    w = freqs
    y = numpy.log(fft_power)
    initial_guess = numpy.array([w.mean(), w.max(),
        1.0])
    p, pcov = scipy.optimize.curve_fit(
        parabola,
        w, y,
        initial_guess,
        )
    predicted = parabola(w, *p)

    ss_err = ((y - predicted)**2).sum()
    ss_tot = ((y-y.mean())**2).sum()
    rsquared = 1.-(ss_err/ss_tot)

    #print "Fit first:\t%.1f\t%.2g\t%.3g" % (
    #    p[0], p[1], p[2])
    print "%.2f\t%.4g\t%.4g" % (
        p[0], p[1], p[2])
    if plot:
        #pylab.plot(w, dsp.amplitude2db(y), label="FFT")
        #pylab.plot(w, dsp.amplitude2db(predicted),
        #    label="Lorentzian fit")
        pylab.plot(w, y, 'o-', label="FFT")
        pylab.plot(w, predicted,
            'o-', label="Lorentzian fit")
        pylab.show()

    return p

def lorentzian(x, p0, p1, p2, p3):
    if any([p0, p1, p2, p3]) < 0:
        return 1e9*numpy.ones(len(x))
    return (p2 / (
          1. + p0**2 * (x - p1)**2)
        + p3
        )

def fit_lorentzian(freqs, fft_db, plot=False, add_plot=False):
    w = freqs
    y = dsp.db2amplitude(fft_db)
    #y = fft_db
    #w = numpy.array( [
    #    bin2hertz(bin_low+i) for i, a in enumerate(peak_area)
    #    ] )
    #y = numpy.array(peak_area)

    #noise_floor = scipy.stats.gmean(y)
    noise_floor = min(y)
    mag_est = max(y) - noise_floor

    initial_guess = numpy.array([1.0, w.mean(), mag_est,
        noise_floor
        ])
    #print "initial:", initial_guess
    p, pcov = scipy.optimize.curve_fit(
        lorentzian,
        w, y,
        initial_guess,
        )
    #print "fit:", p
    predicted = lorentzian(w, *p)
    #if plot:
    #    #pylab.plot(w, dsp.amplitude2db(y), label="FFT")
    #    #pylab.plot(w, dsp.amplitude2db(predicted),
    #    #    label="Lorentzian fit")
    #    pylab.plot(w, y, label="FFT")
    #    pylab.plot(w, predicted,
    #        label="Lorentzian fit")
    #    pylab.show()
#

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

    #print "Fit first:\t%.1f\t%.2g\t%.3g" % (
    print "%.2f\t%.3g\t%.4g" % (
        freq, mag, decay)

    #if rsquared < LONG_LORENTZIAN_RSQUARED_MIN:
    #    print "bail from rsquared", rsquared
    #    return freq, 0, 0, 0

    if plot:
        logplot = True
        pylab.figure()
        if logplot:
            pylab.plot(w, dsp.amplitude2db(y), label="FFT")
            pylab.plot(w, dsp.amplitude2db(predicted),
                label="Lorentzian fit")
            #pylab.semilogy(w, resi, label="residuals")
        else:
            pylab.plot(w, y, label="FFT")
            pylab.plot(w, predicted, label="Lorentzian fit")
            #pylab.plot(w, resi, label="residuals")
        #pylab.xlabel("frequency relative to w_n")
        pylab.xlabel("frequency")
        pylab.ylabel("power")
        pylab.legend()
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



if __name__ == "__main__":
    try:
        wav_filename = sys.argv[1]
        expected_peak_freq = float(sys.argv[2])
    except:
        print "Need a filename and expected freq"
        exit(1)

    freqs, ffts_power = stft(wav_filename, expected_peak_freq)
    #for i in range(ffts_power.shape[0]):
    #    fft_power = ffts_power[i]
    #    fit_gaussian(freqs, fft_power, plot=False)
    #    exit(1)

    basenametemp = os.path.basename(os.path.splitext(wav_filename)[0])
    out = open('fft-3d-%s-%s.txt' %
        (basenametemp, WINDOW), 'w')
    for i in range(ffts_power.shape[0]):
        for j in range(ffts_power.shape[1]/2):
            #if freqs[j] > 250:
            #    continue
            out.write('%g\t%g\t%g\n' % (
                i*HOPSIZE/44100.0,
                freqs[j],
                dsp.power2db(ffts_power[i][j])))
        out.write('\n')

        #if i > 10:
        #    out.close()
        #    exit(1)
    out.close()


