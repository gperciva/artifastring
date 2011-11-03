#!/usr/bin/env python

import os.path
import sys
import glob

import numpy
import pylab

import expected_frequencies
import defs

import stft
import partials

try:
    dirname = sys.argv[1]
except:
    print "Need dirname, and optional maximum frequency"
try:
    min_freq = float(sys.argv[2])
    max_freq = float(sys.argv[3])
except:
    max_freq = 0
    max_freq = -1

HOPSIZE=defs.HOPSIZE
#SAMPLE_RATE=48000

#MAX_SECONDS = 3.0
#MAX_SECONDS = 0.5
MAX_SECONDS = 15

AXIS_Y_TOP = 0
AXIS_Y_BOTTOM = -160

def write_plot(base_filename):
    filenames = glob.glob(os.path.join(
        base_filename, "spectrum-*.txt"))
    basename = base_filename.split('/')[-2]
    wav_filename = os.path.split(
        os.path.dirname(base_filename)
        )[-1]
    base_freq = expected_frequencies.get_freq_from_filename(wav_filename)
    filenames.sort()
    Bs = numpy.loadtxt(os.path.join(base_filename, 'Bs.txt'))
    SAMPLE_RATE, base_freq, B, limit, below, above = Bs
    limit = int(limit)
    num_harms = None
    for i, filename in enumerate(filenames):
        seconds = i*HOPSIZE / float(SAMPLE_RATE)
        if seconds > MAX_SECONDS:
            print "Reached time cutoff of %.1f" % MAX_SECONDS
            return
        print i, filename
        fft = numpy.loadtxt(filename)
        harms = numpy.loadtxt(filename.replace("spectrum-", "harms-"))
        #noise = numpy.loadtxt(os.path.join(
        #    base_filename, "noise-floor.txt"))
        outfilename = filename.replace("spectrum-","").replace(".txt", ".png")
        freqs_estimate_int = [ i*base_freq for
            i in range(1,limit+1)]
        freqs_estimate_B = [ partials.mode_B2freq(base_freq, i, B) for
            i in range(1,limit+1)]

        # DEBUG for g string only
        for j, freq in enumerate(freqs_estimate_int):
            if j == 0:
                pylab.axvline(freq, color="y", label="ideal freq.")
            else:
                pylab.axvline(freq, color="y")
        for j, freq in enumerate(freqs_estimate_B):
            low = stft.bin2hertz( stft.hertz2bin(freq, SAMPLE_RATE)
                - below, SAMPLE_RATE)
            high = stft.bin2hertz( stft.hertz2bin(freq,
                SAMPLE_RATE) + above, SAMPLE_RATE)
            if j == 0:
                pylab.axvspan(low, high, color="c", alpha=0.3,
                    label="search range")
            else:
                pylab.axvspan(low, high, color="c", alpha=0.3)

        pylab.plot(fft[:,0], fft[:,1])
        pylab.plot(harms[:,0], harms[:,1], 'ro', label="peaks")
        #pylab.semilogy(noise[:,0], noise[:,1], 'g-')

        if num_harms is None:
            num_harms = len(harms[:,0])

        #pylab.xlim([0, (num_harms+3)*base_freq])
        if max_freq > 0:
            pylab.xlim([min_freq, max_freq])
        pylab.ylim([AXIS_Y_BOTTOM, AXIS_Y_TOP])
        pylab.xlabel("Frequency [Hz]")
        pylab.ylabel("Amplitude [dB]")
        pylab.title("Evolution of harmonics: %s\n%.3fs seconds" % (
            basename, seconds))
        #pylab.legend(bbox_to_anchor=(1.05, 1), loc=2)
        pylab.legend()
        pylab.savefig(outfilename)
        pylab.close()
        #pylab.show()

write_plot(dirname)

