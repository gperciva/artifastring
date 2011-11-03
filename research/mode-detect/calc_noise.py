#!/usr/bin/env python

import os
import os.path
import sys
import glob

import scipy.io.wavfile
import scipy.fftpack
import scipy.signal
import scipy.optimize

import scipy
import scipy.stats
import pylab

import pickle

import numpy

import defs
import stft

def get_noise_filename(wav_filename):
    noise_filename = "-".join(wav_filename.split("-")[:-1]) + "-noise.wav"
    noise_filename = noise_filename.replace("fixed-wav", "noise")
    if not os.path.exists(noise_filename):
        dirname = os.path.dirname(wav_filename)
        dirname = dirname.replace("fixed-wav", "noise")
        basename = os.path.basename(wav_filename)
        noise_filename =  "-".join(basename.split("-")[0:2])
        noise_cands = glob.glob(
            os.path.join(dirname, noise_filename + "*.wav"))
        if len(noise_cands) == 1:
            noise_filename = noise_cands[0]
        else:
            # deal with Nick's filenames
            noise_filename = "_".join(wav_filename.split("_")[:-3]) + "_noise.wav"
            if not os.path.exists(noise_filename):
                raise Exception("Can't find noise filename:\t%s"%noise_filename)
    return noise_filename

def get_noise(wav_filename, noise_filename=None, recalc=False,
        bins=None):
    if noise_filename is None:
        noise_filename = get_noise_filename(wav_filename)
    pickle_filename = noise_filename + ".pickle"
    if os.path.exists(pickle_filename) and not recalc:
        pickle_file = open(pickle_filename, 'rb')
        noise = pickle.load(pickle_file)
        pickle_file.close()
    else:
        noise = calc_noise(noise_filename, bins=bins)
        pickle_file = open(pickle_filename, 'wb')
        pickle.dump( noise, pickle_file, -1)
        pickle_file.close()
    return noise

def calc_noise(wav_filename, bins=None):
    window_buffers, sample_rate = stft.get_buffers_from_file(wav_filename)

    bins = numpy.empty([
        stft.WINDOWSIZE/2 + 1,
        len(window_buffers),
        ])
    for i, window_buffer in enumerate(window_buffers):
        fft_amplitude = stft.stft_amplitude(window_buffer)
        bins[:,i] = fft_amplitude
    print bins.shape

    freqs = [ stft.bin2hertz(i, sample_rate)
        for i in range(stft.WINDOWSIZE/2 + 1) ]
    #for i, window_buffer in enumerate(window_buffers):
    #    pylab.plot(freqs,
    #        stft.amplitude2db(bins[:,i]),
    #        color="blue")

    noise = numpy.empty(len(bins[:,0]))
    means = numpy.empty(len(bins[:,0]))
    mins = numpy.empty(len(bins[:,0]))
    stds = numpy.empty(len(bins[:,0]))
    for i, bin_spot in enumerate(bins):
        detected_noise = scipy.percentile(bin_spot,
            defs.NOISE_PERCENTILE_BELOW)
        #noise[i] = stft.db2amplitude(stft.amplitude2db(detected_noise))
        noise[i] = detected_noise
        means[i] = scipy.mean(bin_spot)
        mins[i] = bin_spot.min()
        stds[i] = scipy.std(bin_spot, ddof=1)
        #if i == 100:
        #   numpy.savetxt("noise.csv", bin_spot, delimiter=', ')

    #return noise, freqs, variance
    return noise, freqs, means, mins, stds

if __name__ == "__main__":
    #noise = get_noise("noise/viola-a-noise.wav")
    #noise = get_noise("noise/viola-c-noise.wav")
    wav_filename = sys.argv[1]
    try:
        noise_filename = sys.argv[2]
    except:
        noise_filename = None
    noise, freqs, means, mins, stds = get_noise(wav_filename,
                        noise_filename, recalc=True)
    #get_noise("sine-440-3s.wav")

    #print variance
    pylab.plot(freqs, stft.amplitude2db(noise), color="red")
    #pylab.plot(freqs, stft.amplitude2db(means), color="green")
    #pylab.plot(freqs, stft.amplitude2db(mins), color="blue")
    #pylab.semilogx(freqs, stft.amplitude2db(noise), color="red")
    #pylab.title(wav_filename)
    #pylab.figure()
    #pylab.plot(freqs, stds)
    pylab.show()

    #if False:
    if True:
        data = numpy.vstack( (freqs, stft.amplitude2db(noise)) ).transpose()
        save_filename = wav_filename + ".txt"
        numpy.savetxt( save_filename, data)

