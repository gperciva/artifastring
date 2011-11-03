#!/usr/bin/env python

#import os
import os.path
import sys
import glob

import numpy
import scipy.stats
import pylab
import matplotlib.cm

import defs
import estimate_f0_B

INDIVIDUAL_DETAILS = 1
PLOT_FREQS = 1

try:
    dirname = sys.argv[1]
except:
    print "Give dirname and optionally base filename"

inst_strings = {}

filenames = glob.glob(
    os.path.realpath(os.path.expanduser(dirname)) + '*.wav')
filenames.sort()

for i, wav_filename in enumerate(filenames):
    basename = os.path.basename(wav_filename)
    key = '-'.join(basename.split('-')[:-1])
    inst_strings.setdefault(key, []).append(wav_filename)

for key in sorted(inst_strings):
    #print '------', key
    filenames = inst_strings[key]
    filenames.sort()
    if defs.ONLY_N_FILES > 0:
        filenames = filenames[:defs.ONLY_N_FILES]
    f0, B, num_harmonics, rsquared = estimate_f0_B.estimate_f0_B(filenames)
    print "%s\t%.1f\t%.4e\t%i\t%.4e" % (
            key,
            f0, B, num_harmonics, rsquared)

if defs.PLOT_B:
    pylab.show()

exit(0)

data_f0 = {}
data_B = {}
data_num = {}

if PLOT_FREQS:
    pylab.figure()

exit(0)

for i, wav_filename in enumerate(filenames):
    if INDIVIDUAL_DETAILS:
        print "%s\t%.1f\t%.4e\t%i" % (
            basename,
            f0, B, num_harmonics)
    basename = os.path.basename(wav_filename)
    key = '-'.join(basename.split('-')[:-1])
    data_f0.setdefault(key, []).append(f0)
    data_B.setdefault(key, []).append(B)
    data_num.setdefault(key, []).append(num_harmonics)
    if PLOT_FREQS:
        n = numpy.arange(1, num_harmonics)
        predicted = stft_interface.mode_B2freq(f0, n, B)
        pylab.plot(n, predicted, '.-',
            alpha = 0.9,
            c = "blue")
            #c = matplotlib.cm.spring(float(i)/len(filenames)))

        ne = numpy.arange(num_harmonics, 30)
        predicted_e = stft_interface.mode_B2freq(f0, ne, B)
        pylab.plot(ne, predicted_e, '-',
            alpha = 0.6,
            c = "green")
            #c = matplotlib.cm.hot(float(i)/len(filenames)))


#print "#name\tf0 mean\tf0 std\tB mean\tB std\tnum mean\tnum std"
print "# name\t\tf0 mean\tf0 std\tB mean\tB std\tnh mean\tnh std"
for key in data_f0:
    f0_mean = scipy.mean(data_f0[key])
    f0_std = scipy.std(data_f0[key])
    B_mean = scipy.mean(data_B[key])
    B_std = scipy.std(data_B[key])
    num_mean = scipy.mean(data_num[key])
    num_std = scipy.std(data_num[key])
    print "%s\t%.1f\t%.1f\t%.1e\t%.1e\t%.1f\t%.1f" % (
        key, f0_mean, f0_std, B_mean, B_std, num_mean, num_std)

if PLOT_FREQS:
    pylab.title( os.path.basename(dirname) )
    pylab.xlabel("Mode number")
    pylab.ylabel("Frequency")
    pylab.show()

