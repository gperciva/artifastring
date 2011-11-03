#!/usr/bin/env python

SHOW_F0_SNR = False
#SHOW_F0_SNR = True

import scipy.signal
import scipy.fftpack
import scipy.stats

import partials
import pylab

import numpy
numpy.seterr(all='ignore')

def spectral_flatness(buf):
    window = scipy.signal.get_window("blackmanharris", len(buf))
    fft = scipy.fftpack.fft(buf*window)
    fft_power = abs(fft[:len(fft)/2+1])**2
    flatness = (scipy.stats.gmean(fft_power) / fft_power.mean() )
    return flatness

def spectral_flatness_limited(buf, low, high, fs):
    #window = scipy.signal.get_window("blackmanharris", len(buf))
    window = scipy.signal.gaussian(len(buf), len(buf)/8)
    fft = scipy.fftpack.fft(buf*window)
    fft_power = abs(fft[:len(fft)/2+1])**2
    low_bin = float(low) / (fs/2) * (len(fft_power)-1)
    high_bin = float(high) / (fs/2) * (len(fft_power)-1)
    fft_power = fft_power[low_bin:high_bin]

    flatness = (scipy.stats.gmean(fft_power) / fft_power.mean() )

    if False:
    #if True:
        pylab.figure()
        pylab.semilogy(fft_power)
        print flatness
        pylab.show()
    return flatness


### copied from:
#### http://leohart.wordpress.com/2006/01/29/hello-world/
# Not to be confused with functions to be used on the Windows OS
# These window functions are similar to those found in the Windows
# toolbox of MATLAB
# Note that numpy has a couple of Window functions already:
# See: hamming, bartlett, blackman, hanning, kaiser
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
    


def f0_snr(buf, f0, fs):
    window = scipy.signal.gaussian(len(buf), len(buf)/8)
    fft = scipy.fftpack.fft(buf*window)
    fft_abs = abs(fft[:len(fft)/2+1])
    cutoff_low_bin = float(20.0) / (fs/2) * (len(fft_abs)-1)
    cutoff_bin = 1.95*float(f0) / (fs/2) * (len(fft_abs)-1)
    low_bin = float(f0*0.95) / (fs/2) * (len(fft_abs)-1)
    high_bin = float(f0*1.05) / (fs/2) * (len(fft_abs)-1)

    freqs = numpy.array([ float(i) / (fs/2) * (len(fft_abs)-1) for
        i in range(len(fft_abs)) ])
    cutoff_bin = int(cutoff_bin)
    fft_abs = fft_abs[:cutoff_bin]
    freqs = freqs[:cutoff_bin]

    fft_power = fft_abs**2
    examine = fft_abs[low_bin:high_bin]**2

    # multiply the FREQUENCY domain with a window to ensure
    # that the maximum will be close to 660.
    examine *= tukeywin(len(examine))

    peak_index_within = numpy.argmax(examine)
    peak_index = low_bin + peak_index_within

    while not (fft_power[peak_index-1] < fft_power[peak_index] > fft_power[peak_index+1]):
        # find the next-highest peak, whatever it is
        peak_index += 1


    if False:
        pylab.plot(examine)
        pylab.semilogy(peak_index_within,
            examine[peak_index_within], 'o')
        pylab.figure()
        pylab.plot(fft_power)
        pylab.semilogy(peak_index,
            fft_power[peak_index], 'o')
        pylab.show()


    try:
        peak_bin, peak_mag, curvature_a = partials.quadratic_interpolation(
            peak_index, fft_abs)
    except:
        print "PROBLEM"
        pylab.plot(examine)
        pylab.semilogy(peak_index_within,
            examine[peak_index_within], 'o')
        pylab.figure()
        pylab.semilogy(fft_power)
        pylab.semilogy(peak_index,
            fft_power[peak_index], 'o')
        pylab.show()
        exit(1)


    #print peak_bin, peak_mag, curvature_a
    length = len(fft_power)
    synth = partials.qifft_synthesize(peak_bin, peak_mag, curvature_a, length)
    residual = fft_abs - synth

    synth_min = min(fft_abs)
    residual.clip(synth_min)

    consider_orig = fft_abs[cutoff_low_bin:]
    freqs_orig = freqs[cutoff_low_bin:]

    #consider_residual = fft_abs[cutoff_low_bin:low_bin]
    #freqs_residual = freqs[cutoff_low_bin:low_bin]
    consider_residual = numpy.append(
    #    #residual[cutoff_low_bin:low_bin],
    #    #residual[high_bin:])
        fft_abs[cutoff_low_bin:low_bin],
        fft_abs[high_bin:])
    freqs_residual = numpy.append(
        freqs[cutoff_low_bin:low_bin],
        freqs[high_bin:])
    #consider_residual = residual[cutoff_low_bin:low_bin]
    flatness_orig = (scipy.stats.gmean(consider_orig)
        / consider_orig.mean() )
    flatness_residual= (scipy.stats.gmean(consider_residual)
        / consider_residual.mean() )

    #mean = scipy.stats.gmean(consider)
    #print mean

    value = flatness_orig / flatness_residual
    #print
    #print flatness_orig, flatness_residual, peak_mag
    def rms(sig):
        return numpy.sqrt( numpy.mean( sig**2 ) )
    energy_orig = rms( consider_orig )
    energy_sig = rms( fft_abs[low_bin:high_bin] )
    energy_residual = rms( consider_residual )
    #print energy_sig, energy_orig, energy_residual
    value = energy_residual / energy_sig
    #print value

    if SHOW_F0_SNR:
        pylab.semilogy(freqs, fft_abs, '-')
        pylab.semilogy(peak_bin, peak_mag, 'o')
        #pylab.semilogy(synth)
        pylab.semilogy(freqs_orig, consider_orig)
        pylab.semilogy(freqs_residual, consider_residual)
        #pylab.axhline(mean)
        pylab.show()

    return value


def scf_limited(buf, low, high, fs):
    window = scipy.signal.get_window("blackmanharris", len(buf))
    fft = scipy.fftpack.fft(buf*window)
    fft_mag = abs(fft[:len(fft)/2+1])
    freqs = scipy.arange(0, len(fft_mag)) * (fs/2) / (len(fft_mag)-1)

    low_bin = float(low) / (fs/2) * (len(fft_mag)-1)
    high_bin = float(high) / (fs/2) * (len(fft_mag)-1)

    freqs = freqs[low_bin:high_bin]
    fft_mag = fft_mag[low_bin:high_bin]
    centroid = sum(fft_mag*freqs) / sum(fft_mag)
    return centroid

def spectral_centroid(buf, fs):
    window = scipy.signal.get_window("blackmanharris", len(buf))
    fft = scipy.fftpack.fft(buf*window)
    fft_mag = abs(fft[:len(fft)/2+1])
    freqs = scipy.arange(0, len(fft_mag)) * (fs/2) / (len(fft_mag)-1)
    centroid = sum(fft_mag*freqs) / sum(fft_mag)
    return centroid

def amplitude2db(power):
    return 20.0 * scipy.log10( power )

def power2db(power):
    return 10.0 * scipy.log10( power )

def db2amplitude(db):
    return 10.0**(db/20.0)

def db2power(db):
    return 10.0**(db/10.0)


