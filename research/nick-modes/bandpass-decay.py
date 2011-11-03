#!/usr/bin/env python

import scipy
import scipy.signal
import scipy.io.wavfile
import numpy
import pylab


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    bl, al = scipy.signal.butter(order, low, btype='low')
    #bh, ah = scipy.signal.butter(order, high, btype='high')
    bh = ah = 0
    return bl, al, bh, ah

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    #zi = scipy.signal.lfiltic(b, a, data, data)
    #y, zf = scipy.signal.lfilter(b, a, data, zi=zi)
    y = 0
    return y



wav_filename = "cello-c-old-01.wav"

sample_rate, data_unnormalized = scipy.io.wavfile.read(wav_filename)
data = (numpy.array(data_unnormalized, dtype=numpy.float64)
            / float(numpy.iinfo(data_unnormalized.dtype).max))


# Sample rate and desired cutoff frequencies (in Hz).
fs = float(sample_rate)
#fs = 10000.0
lowcut = 60.0
highcut = 90.0

# Plot the frequency response for a few different orders.
pylab.figure()
#for order in [3, 6, 9]:
for order in [31]:
    bl, al, bh, ah = butter_bandpass(lowcut, highcut, fs, order=order)
    wl, hl = scipy.signal.freqz(bl, al, worN=2000)
    pylab.plot((fs * 0.5 / numpy.pi) * wl, abs(hl),
        label="order = %d" % order)

pylab.show()







