#!/usr/bin/env python

import os
import numpy
import scipy.io.wavfile

from defs import *
import defs
import numpy_string
import scipy.signal
import scipy.stats
import pylab

K_finger = 1e5
K_pluck = 1e4
R_finger = 30
num_samples = int(0.5 * FS)
pull_low     = num_samples + 0.00*FS
pull_high    = num_samples + numpy_string.PLUCK_SAMPLES - 0.00*FS
release_low  = num_samples + numpy_string.PLUCK_SAMPLES + 0.00*FS
release_high = 2*num_samples - 0.00*FS

b, a = scipy.signal.iirdesign(wp = 40.0*2*numpy.pi/FS,
    ws = 20.0*2*numpy.pi/FS, gpass=3, gstop=24, ftype='butter')
#w, h = scipy.signal.freqz(b, a)
#pylab.plot(w, abs(h))
#pylab.show()

if not os.path.exists("out-plucks"):
    os.makedirs("out-plucks")

def spectral_flatness(buf):
    fft = scipy.fftpack.fft(buf)
    fft_power = abs(fft[:len(fft)/2+1])**2

    low_bin = 50.0 / (FS/2) * len(fft_power)
    high_bin = 5000.0 / (FS/2) * len(fft_power)
    #print low_bin, high_bin
    fft_power = fft_power[low_bin:high_bin]
    flatness = (scipy.stats.gmean(fft_power) / fft_power.mean() )

    #return max(fft_power) / fft_power.mean()
    #pylab.figure()
    #pylab.plot(buf)
    #pylab.figure()
    #pylab.plot(10*numpy.log(fft_power))
    #pylab.show()
    return flatness

def spectral_centroid(buf):
    fft = scipy.fftpack.fft(buf)
    fft_mag = abs(fft[:len(fft)/2])
    #low_bin = 30.0/(FS/2) * len(fft_power)
    #fft_power = fft_power[low_bin:]
    freqs = numpy.arange(0, len(fft_mag)) * (FS/2) / len(fft_mag)
    centroid = sum(fft_mag*freqs) / sum(fft_mag)
    return centroid

def pluck(x1, R_pluck):
    filename = "out-plucks/pluck-%.3f-%04f.wav" % (x1, R_pluck)
    outs = numpy.empty(2*num_samples)

    vln = numpy_string.Violin()
    vln.finger(1.0 - x1, K_finger, R_finger)

    vln.pluck(0.2, K_pluck, R_pluck)
    for i in range(num_samples):
        outs[i] = vln.tick()
    vln.pluck(0.2, K_pluck, R_pluck)
    for i in range(num_samples):
        outs[num_samples + i] = vln.tick()

    # calc before normalizing
    #release = outs[ release_low : release_high]
    #release_ambitus = sum(release**2) / len(release)

    scipy.io.wavfile.write(filename, FS,
        numpy.array(SCALE_WAV_OUTPUT*outs*2**15, dtype=numpy.int16))
    #outs /= (max(abs(outs)) * 2)
    #scipy.io.wavfile.write(filename, FS,
    #    numpy.array(outs*2**15, dtype=numpy.int16))
    #outs = scipy.signal.lfilter(b, a, outs)

    outs = scipy.signal.lfilter(b, a, outs)



    pulling = outs[ pull_low : pull_high]
    release = outs[ release_low : release_high]

    pull_flatness = spectral_flatness(pulling)
    pull_centroid = spectral_centroid(pulling)

    #if True:
    if False:
        print "------ ", R_pluck
        print "flatness:", pull_flatness
        print "centroid:", pull_centroid
        #pylab.figure()
        #pylab.plot(outs)
        pylab.figure()
        pylab.plot(pulling)
        pylab.title("pulling %.2f" % R_pluck)
        #pylab.figure()
        #pylab.plot(release)
        #pylab.title("release %.2f" % R_pluck)


    pull_ambitus = numpy.sqrt(sum(pulling**2) / len(pulling))
    #pull_late_data = pulling[0.01*FS : ]
    #pull_late = numpy.sqrt(sum(pull_late_data**2)) / len(pull_late_data)
    release_ambitus = numpy.sqrt(sum(release**2) / len(release))
    #print K_pluck, pull_ambitus, release_ambitus
    #print pull_flatness
    #score = release_ambitus / pull_flatness
    #print score
    #score = pull_ambitus / (release_ambitus**2)
    score = pull_ambitus

    #pylab.figure()
    #pylab.subplot(211)
    #pylab.title("%i" % K_pluck)
    #pylab.plot(pulling)
    #pylab.subplot(212)
    #pylab.plot(release)
    return pull_flatness, score
    #return pull_ambitus, release_ambitus, score


#R_values = numpy.append(numpy.array([0]),
#    numpy.logspace(0, 4, 10))
#R_values = numpy.logspace(-1, 1, 10)
R_values = numpy.append(numpy.linspace(0, 2, 11),
    numpy.linspace(4, 10, 4))
x1s = numpy.append(numpy.linspace(0, 0.25, 8),
    numpy.linspace(0.25, 0.50, 4))

out = open("out-plucks/objective-R.txt", "w")
#for x1 in [0.0, 0.109, 0.251, 0.333, 0.5]:
#for x1 in [0.0, 0.109, 0.251, 0.333, 0.5]:
#for x1 in [0.0, 0.109, 0.251, 0.333, 0.5]:
#for x1 in [0.0, 0.251, 0.5]:
#for x1 in [0.109]:
for x1 in x1s:
    for R in R_values:
    #for R in [0.0, 1.0, 10.0, 30.0, 100.0, 1000.0, 10000.0]:
    #for R in numpy.linspace(0, 100, 10):
    #for K in numpy.logspace(-1, 2.0, 10):
    #for K in numpy.logspace(3, 4.0, 4):
        score1, score2 = pluck(x1, R)
        #print "%.3f\t%i\t%.3g\t%.3g\t%.3g" % (x1, K, score1, score2, score3),
        #print score2 / score3 * 1000
        text = "%.3f\t%.2f\t%.3g\t%.3g" % (x1, R, score1, score2)
        out.write(text + "\n")
        #print "%.3f\t%.2f\t%.3g" % (x1, R, score3)
#for x1 in [0.0, 0.5]:
#    for K in [1e1, 1e5]:
    out.write("\n")
out.close()

pylab.show()


