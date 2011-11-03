#!/usr/bin/env python
import numpy
import scipy.io.wavfile
import scipy.fftpack
import scipy.signal

import defs

WINDOWSIZE = defs.ZEROPADDING_FACTOR * defs.BUFFER_WINDOWSIZE


### convenience functions
def amplitude2db(power):
    return 20.0 * scipy.log10( power )

def db2amplitude(db):
    return 10.0**(db/20.0)

def hertz2bin(freq, sample_rate):
    return freq*(WINDOWSIZE/2+1) / (float(sample_rate)/2)

def bin2hertz(bin_number, sample_rate):
    return bin_number * (sample_rate/2) / (float(WINDOWSIZE)/2+1)

### file IO
def get_buffers_from_file(wav_filename, num_buffers=None, bins=None):
    sample_rate, data_unnormalized = scipy.io.wavfile.read(wav_filename)
    windowsize = defs.BUFFER_WINDOWSIZE
    hopsize = defs.HOPSIZE
    if bins is not None:
        windowsize = bins
        hopsize = hopsize

    if num_buffers:
        data_unnormalized = data_unnormalized[0:(
            windowsize + (num_buffers-1) * hopsize)]
    data = data_unnormalized / float(numpy.iinfo(data_unnormalized.dtype).max)

    # split into overlapping windows
    window_buffers = []
    for window_index in range(
            (len(data)/hopsize - windowsize/hopsize)+1):
        index_start = window_index*hopsize
        index_end = window_index*hopsize + windowsize
        window = data[ index_start : index_end ]
        window_buffers.append(window)
    return window_buffers, sample_rate


def get_long_buffer_from_file(wav_filename, num_buffers=None, bins=None):
    sample_rate, data_unnormalized = scipy.io.wavfile.read(wav_filename)
    windowsize = defs.LONG_WINDOWSIZE
    data_unnormalized = data_unnormalized[0:(
        windowsize + (num_buffers-1) * 1)]
    data = data_unnormalized / float(numpy.iinfo(data_unnormalized.dtype).max)

    # split into overlapping windows
    return data, sample_rate


### FFT stuff
def stft_amplitude(window_buffer, zeropadding=defs.ZEROPADDING_FACTOR):
    #window_function = scipy.signal.gaussian(len(window_buffer),
    #    len(window_buffer)/8)
    #window_function = scipy.signal.get_window("hanning",
    #    len(window_buffer))
    window_function = scipy.signal.get_window("hamming",
        len(window_buffer))
    buf = window_buffer*window_function
    N = zeropadding*len(buf)
    fft = scipy.fftpack.fft(buf, N)
    fft_abs = abs(fft[:N/2+1])
    ### see test-normalization.py
    fft_normalized = fft_abs / (sum(window_function)/2)
    return fft_normalized

def fft_amplitude(window_buffer, sample_rate):
    #seconds = numpy.arange(0, len(window_buffer)) / float(sample_rate)
    #a = -10.0
    #window_function = numpy.exp(seconds * a)
    zeropadding = 2
    window_function = scipy.signal.get_window("hamming",
        len(window_buffer))

    buf = window_buffer*window_function
    #import pylab
    #pylab.plot(buf)
    #pylab.show()
    N = zeropadding*len(buf)
    fft = scipy.fftpack.fft(buf, N)
    fft_abs = abs(fft[:N/2+1])
    fft_normalized = fft_abs / (sum(window_function)/2)
    return fft_normalized






