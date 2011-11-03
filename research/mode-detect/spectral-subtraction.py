#!/usr/bin/env python

import sys

import numpy
numpy.seterr(under='ignore')
import scipy.io
import scipy.fftpack
import scipy.signal
import pylab


import defs
import stft

import calc_noise



def spectral_subtraction(wav_filename, noise_filename):
    sample_rate, wav_data = scipy.io.wavfile.read(wav_filename)
    wav_data = wav_data / float(numpy.iinfo(wav_data.dtype).max)
    hopsize = len(wav_data)

    ##noise, freqs, means, mins, stds = calc_noise.get_noise(
    ##    #wav_filename, noise_filename, recalc=True)
    #    wav_filename, noise_filename, recalc=False,
    #    bins=len(wav_data))

    sample_rate, noise_data = scipy.io.wavfile.read(noise_filename)
    noise_data = noise_data / float(numpy.iinfo(noise_data.dtype).max)
    smallsize = int(len(noise_data) / hopsize)
    noise_data = noise_data[:hopsize*smallsize]
    noise_data = noise_data.reshape(smallsize, hopsize)
    #window = scipy.signal.get_window("blackmanharris", hopsize)
    window = scipy.signal.get_window("hamming", hopsize)
    noise_data *= window
    noise_ffts = scipy.fftpack.fft(noise_data, axis=1)
    noise_ffts_abs = abs(noise_ffts)
    noise_power = noise_ffts_abs**2


    #mins = numpy.min(noise_ffts_abs, axis=0)
    #mins_full = mins
    #mins = mins[:len(mins)/2+1]
    means_power = numpy.mean(noise_power, axis=0)
    #means_abs = numpy.abs(means) [:len(means)/2+1]

    noise_db = stft.amplitude2db( means_power[:len(means_power)/2+1]/hopsize )
    freqs = [float(i)*(sample_rate) / hopsize for i in range(len(noise_db))]

    #for i in range(len(means_abs)):
    #    print means_abs[i]
    #print means_abs
    #print means_abs.shape
    #pylab.semilogy(mins)
    pylab.plot(freqs, noise_db, label="noise means")

    fft = scipy.fftpack.fft(wav_data*window)
    #fft = scipy.fftpack.fft(wav_data)
    fft_abs = abs(fft)[:len(fft)/2+1]
    #fft_power = fft_abs**2
#    print len(fft)
#    print len(mins)

    fft_db = stft.amplitude2db( fft_abs / hopsize )
    #pylab.semilogy(abs(fft[:len(fft)/2+1]))
    #pylab.semilogy(fft_abs, label="sig orig")
    #pylab.semilogy(fft_abs - mins, label="sig min")
    pylab.plot(freqs, fft_db, label="sig orig")

    #reconstructed = fft - mins_full
    #reconstructed = fft
    #reconstructed = numpy.zeros(len(fft), dtype=complex)
    #for i in range(len(reconstructed)):
    theta = numpy.angle(fft)
    alpha = 1.0
    beta = 0.1
    r = numpy.zeros(len(fft))
    for i in range(len(fft)):
        r[i] = (abs(fft[i])**2 - alpha * means_power[i])
        if r[i] < 0:
            r[i] = beta * means_power[i]
        else:
            r[i] = numpy.sqrt(r[i])
        #print r_orig[i], means_full[i], r[i]

    reconstructed = ( r * numpy.cos(theta)
        + r * numpy.sin(theta)*1j);

    rec_abs = abs(reconstructed)[:len(reconstructed)/2+1]
    #print r_abs

    rec_db = stft.amplitude2db( rec_abs / hopsize )
    pylab.plot(freqs, rec_db,
        label="reconstructed")
    pylab.legend()

    reconstructed_sig = scipy.fftpack.ifft(reconstructed )

    reconstructed_sig /= window
    reconstructed_sig = numpy.real(reconstructed_sig)

    #pylab.figure()
    #pylab.plot(reconstructed_sig)


    # FIXME: don't normalize
    #reconstructed_sig /= max(reconstructed_sig)

    big = numpy.int16(reconstructed_sig * numpy.iinfo(numpy.int16).max)
    #pylab.figure()
    #pylab.plot(big)

    scipy.io.wavfile.write("foo.wav", sample_rate, big)

    pylab.show()



if __name__ == "__main__":
    wav_filename = sys.argv[1]
    noise_filename = sys.argv[2]
    spectral_subtraction(wav_filename, noise_filename)


