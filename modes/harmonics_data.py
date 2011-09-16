#!/usr/bin/env python

import os.path
import glob
import pickle
import math

import numpy
import pylab
import matplotlib

import marsyas_interface

# interactive pylab graph?
SHOW_DECAY = 0

# dirs
PLUCKS_DIR = "split-wav"
PNG_OUTPUT_DIR = "split-png"

# the middle-to-end of a file is more likely to be pure noise
NOISE_BEGIN_PERCENT = 0.50
NOISE_END_PERCENT = 0.95

# beginnings of notes aren't always trustworthy
SKIP_PERCENT_BEGIN = 0.30
SKIP_PERCENT_END = 0.0
MIN_HOPS_AFTER_NOISE = 20


class HarmonicsData():
    tnss = None
    tsss = None
    def __init__(self, basename):
        pickle_filename = basename + '.pickle'
        if os.path.exists(pickle_filename):
            pickle_file = open(pickle_filename, 'rb')
            (self.tnss, self.tsss) = pickle.load(pickle_file)
            pickle_file.close()
        else:
            (self.tnss, self.tsss) = self.generate_data(basename)
            pickle_file = open(pickle_filename, 'wb')
            pickle.dump( (self.tnss, self.tsss), pickle_file, -1)
            pickle_file.close()

    def get_freq_from_filename(self, wav_filename):
        if "violin-g" in wav_filename:
            frequency = 196.0
        elif "violin-d" in wav_filename:
            frequency = 293.0
        elif "violin-a" in wav_filename:
            frequency = 440.0
        elif "violin-e" in wav_filename:
            frequency = 660.0
        elif "cello-a" in wav_filename:
            frequency = 220.0
        elif "cello-d" in wav_filename:
            frequency = 146.7
        elif "cello-g-finger-a" in wav_filename: # do these before the open string!
            frequency = 111.0
        elif "cello-g-finger-c" in wav_filename:
            frequency = 130.8
        elif "cello-g" in wav_filename:
            frequency = 97.8
        elif "cello-c" in wav_filename:
            frequency = 65.2
        else:
            print "Need a frequency!"
            sys.exit(1)
        return frequency


    # truncate list when it falls below the noise floor
    def truncate_list_below_noise_floor(self, values):
        cutoff_index = -1
        noise_start = int(NOISE_BEGIN_PERCENT * len(values))
        noise_end = int(NOISE_END_PERCENT * len(values))
        noise_values = values[noise_start:noise_end]
        median = numpy.median(noise_values)
        std = numpy.std(noise_values)
        noise_floor = median + 10*std
        for i, value in enumerate(values):
            if value < noise_floor:
                cutoff_index = i
                break
        return values[:cutoff_index]

    def truncate_beginning_ending(self, values):
        if not len(values):
            return values
        while max(values) in values[1:]:
            skip_index = values[1:].index(max(values))
            values = values[skip_index+1:]
        skip_index_begin = int(SKIP_PERCENT_BEGIN * len(values))
        skip_index_end = int(SKIP_PERCENT_END * len(values))
        if skip_index_end == 0:
            return values[skip_index_begin:]
        return values[skip_index_begin:-skip_index_end]
    
    
    # get list of sample (hop) times
    # list of times = ts; list of list of times = tss
    def get_tss(self, hop_rate, harmonics):
        tss = []
        for i in range(len(harmonics)):
            ts = [x*hop_rate for x in xrange(len(harmonics[i]))]
            tss.append(ts)
        return tss

    #we want the decay envelopes, so normalize them to begin at 1.0
    def normalize_list(self, values):
        ### TODO: I'm uncertain about which we want here
        #maximum = values[0]
        maximum = max(values)
        return [ x/maximum for x in values ]

    def only_keep_until_short(self, values):
        cutoff = -1
        for i, harm in enumerate(values):
            if len(harm) < MIN_HOPS_AFTER_NOISE:
                cutoff = i
                break
        if cutoff > 0:
            return values[:cutoff]
        return values

    def remove_after_zero(self, values):
        if 0 in values:
            index = values.index(0)
            return values[:index]
        return values

    def fit_to_exponential(self, arg):
        xs, ys = arg
        ys_log = map(math.log, ys)
        # http://en.wikipedia.org/wiki/Simple_linear_regression#Linear_regression_without_the_intercept_term
        gradient = (
            sum(map(lambda (x,y): x*y, zip(xs, ys_log))) /
            sum(map(lambda x: x*x, xs)))
        tn = -1.0 / (2*gradient)
        return tn


    def plot_decays(self, tss, tns, harmonics, png_filename, instrument_string):
        pylab.figure()
        for i in range(len(harmonics)):
            ts = tss[i]
            tn = tns[i]
            color = matplotlib.cm.jet(float(i)/len(harmonics))
            pylab.semilogy(ts, harmonics[i],
                '.', color=color, label="harmonic %i" % (i+1))
            # Demoucron, p. 60
            test_formula = map(lambda t: math.exp(-t/(2*tn)), ts)
            pylab.semilogy(ts, test_formula,
                '-', color=color, label="predict %i" % (i+1))
        if len(harmonics) < 10:
            pylab.legend()
        pylab.xlabel("Time (seconds)")
        pylab.ylabel("Relative strength of harmonic")
        pylab.title("Decay envelopes and linear-fit lines, %s" %
            instrument_string)
        pylab.savefig(png_filename.replace(".png", "-decays.png"))
        if SHOW_DECAY:
            pylab.show()
 


    def generate_data(self, basename):
        filenames = glob.glob(
            os.path.join(PLUCKS_DIR, basename + '*.wav'))
        filenames.sort()
#        filenames = filenames[7:10]
        tnss = []
        tsss = []
        for wav_filename in filenames:
            print "Processing", wav_filename
            frequency = self.get_freq_from_filename(wav_filename)
            harmonics, hop_rate = marsyas_interface.get_harmonics(
                wav_filename, frequency)

            harmonics = map(self.truncate_list_below_noise_floor, harmonics)
            harmonics = map(self.remove_after_zero, harmonics)
            harmonics = map(self.truncate_beginning_ending, harmonics)
            ### remove harmonics that are less than the noise floor
            ### and have extremely few samples
            harmonics = self.only_keep_until_short(harmonics)

            harmonics = map(self.normalize_list, harmonics)

#            for i, h in enumerate(harmonics):
#                print len(h),
#            print

            tss = self.get_tss(hop_rate, harmonics)
            tns = map(self.fit_to_exponential, zip(tss, harmonics))
            tnss.append(tns)
            tsss.append(tss)

            png_filename = os.path.join(PNG_OUTPUT_DIR,
                os.path.basename(wav_filename).replace(".wav", ".png"))
            instrument_string = os.path.basename(wav_filename)
            self.plot_decays(tss, tns, harmonics, png_filename, instrument_string)
        return tnss, tsss


