#!/usr/bin/env python

import sys

import os.path
import glob
import pickle
import tables

import numpy
import pylab
import matplotlib
import stft

import scipy
import scipy.stats

import stft_interface
import estimate_f0_B

import defs
import classes

import partials

import decay_exponential

class HarmonicsStats:
    def __init__(self):
        self.num_files = 0
        self.num_harms_original = 0
        self.num_harms_max_no_above_noise = 0
        self.num_harms_num_no_above_noise = 0
        self.num_harms_no_fit = 0
        self.num_harms_no_rsquared = 0
        self.num_harms_no_variance = 0
        self.num_harms_no_drop = 0
        self.num_harms_end = 0
        self.highest_harm = 0


def get_noise_top(signal, fraction):
    noise_begin_x = fraction * len(signal)
    noise_top_percentile = scipy.percentile(signal[noise_begin_x:],
        defs.NOISE_PERCENTILE_BELOW)
    return noise_top_percentile

def get_noise_mean(signal, fraction):
    return signal[-1]
    noise_begin_x = fraction * len(signal)
    noise_top_mean = scipy.mean(signal[noise_begin_x:])
    return noise_top_mean


def num_above_noise(signal, noise_top):
    begin_above = None
    for i, hm in enumerate(signal):
        noise_top_extra = stft.db2amplitude(
            stft.amplitude2db(noise_top)
            + defs.HARMONIC_DB_ABOVE_NOISE_TOP)
        if hm < noise_top_extra:
            begin_above = i
            break
    return begin_above


class HarmonicsData():
    def __init__(self, dirname, basename, recalc=False, plot=False):
        dirname = os.path.realpath(os.path.expanduser(
                    "~/media/phd-data/%s/fixed-wav" % dirname
                    ))
        pickle_filename = os.path.join(dirname, basename+".pickle")
        if os.path.exists(pickle_filename) and not recalc:
            pickle_file = open(pickle_filename, 'rb')
            (self.decays, self.f0, self.B, self.stats) = pickle.load(pickle_file)
            pickle_file.close()
        else:
            (self.decays, self.f0, self.B, self.stats) = self.generate_data(
                dirname, basename, plot_harms=plot)
            pickle_file = open(pickle_filename, 'wb')
            pickle.dump( (self.decays, self.f0, self.B, self.stats),
                pickle_file, -1)
            pickle_file.close()

    def get_data(self):
        return self.decays, self.f0, self.B, self.stats

    def generate_data(self, dirname, basename, plot_harms=False):
        #png_dirname = os.path.join(dirname, 'png')
        #if not os.path.exists(png_dirname):
        #    os.makedirs(png_dirname)

        if defs.ONLY_FILES_CONTAINING:
            search_filename = '%s*%s*wav' % (
                basename, defs.ONLY_FILES_CONTAINING)
        else:
            search_filename = basename + '*.wav'
        filenames = glob.glob(
            os.path.join(dirname, search_filename))
        filenames = filter(lambda x: "noise" not in x, filenames)
        filenames.sort()

        if defs.ONLY_N_FILES > 0:
            filenames = filenames[:defs.ONLY_N_FILES]
        _, _, _, final = estimate_f0_B.estimate_f0_B(filenames)
        f0 = final.f0
        B = final.B
        limit = final.highest_mode

        stats = HarmonicsStats()
        stats.num_files = len(filenames)

        decays = []
        for wav_filename_count, wav_filename in enumerate(filenames):
            basename = os.path.basename(wav_filename)
            #print "Processing", wav_filename
            pickle_filename = wav_filename+".stft.pickle"
            if os.path.exists(pickle_filename):
                pickle_file = open(pickle_filename, 'rb')
                harmonics, hop_rate = pickle.load(pickle_file)
                pickle_file.close()
                #print "... read pickle"
            else:
                #print "... calculating new"
                #frequency = expected_frequencies.get_freq_from_filename(
                #    wav_filename, f0, B)
                harmonics, hop_rate = stft_interface.get_harmonics(
                    wav_filename, f0, B, limit)
                pickle_file = open(pickle_filename, 'wb')
                pickle.dump( (harmonics, hop_rate), pickle_file, -1)
                pickle_file.close()
                #print "... wrote pickle"

            nums = tables.save_partials(os.path.splitext(basename)[0])
            if nums:
                dest_dir = "out/"
                for num in nums:
                    h = harmonics[num]
                    #print h.n
                    data = numpy.vstack( (
                            h.frame_numbers*hop_rate,
                            stft.amplitude2db(h.mags)
                        )).transpose()
                    filename = dest_dir + '/partials-%s-%i.txt' % (
                        basename, num)
                    numpy.savetxt( filename, data)
                    print "Wrote to %s" % filename
            
            for i, h in enumerate(harmonics):
                stats.num_harms_original += 1
                if len(h.mags) < 2:
                    stats.num_harms_max_no_above_noise += 1
                    continue

                #if h.n > 0:
                #    pylab.figure()
                #    pylab.semilogy(h.mags, '.')
                #    pylab.title("mode %i" % h.n)
                #    pylab.show()
                #N = 16
                #b, a = scipy.signal.butter(N, 0.25)
                #b = scipy.signal.firwin(N, 0.25)
                #a = 1.0
                #zi = scipy.signal.lfiltic(b, a, h.mags[0:N],
                #    h.mags[0:N])
                #h.mags, zf = scipy.signal.lfilter(b, a, h.mags,
                #    zi=zi)
                #pylab.semilogy(h.mags)
                #pylab.show()

                #if defs.HARMONICS_PRINT_SUMMARY:
                #    print "n: %i\tbegin" %(h.n)
                noise_mean = get_noise_mean(h.mags, 0.9)
                #noise_top = get_noise_top(h.mags, 0.9)
                #frames_above = num_above_noise(h.mags, noise_top)
                frames_above = num_above_noise(h.mags, noise_mean)
                #print h.n, "above:", frames_above
                noise_top_extra_min = stft.db2amplitude(
                    stft.amplitude2db(noise_mean)
                    + defs.HARMONIC_MAX_DB_ABOVE_NOISE_TOP)
                if max(h.mags) < noise_top_extra_min:
                #    print "bail noise_top_extra"
                #    # FIXME: special
                    stats.num_harms_max_no_above_noise += 1
                    continue
                #print h.n, frames_above
                if frames_above < defs.HARMONIC_MIN_HOPS_ABOVE_NOISE:
                    stats.num_harms_num_no_above_noise += 1
                    #print "not enough above noise top", frames_above
                    continue
                ### experiment: only take beginning
                #h.frame_numbers = h.frame_numbers[:frames_above]
                #h.mags = h.mags[:frames_above]

                ### experiment: test the derivative
                #dh_mags = numpy.zeros(len(h.mags)-1)
                #for i in range(0, len(h.mags)-1):
                    # subtraction on log scale
                    #dh_mags[i] = (h.mags[i+1] / h.mags[i]) * (
                    #    1.0 + h.mags[i])
                #    dh_mags[i] = (h.mags[i+1] - h.mags[i])
                #ddh_mags = numpy.zeros(len(dh_mags))
                #for i in range(0, len(dh_mags)-1):
                #    ddh_mags[i] = dh_mags[i+1] - dh_mags[i]
                #dh_mags = (h.mags[1:] - h.mags[:-1])
                #sub = (dh_mags > 0)
                ##print dh_mags * sub
                #num_below_zero = (dh_mags * sub).sum()
                #print "bad: %.3g" % (float(num_below_zero) / len(dh_mags) )
                ##pylab.plot(dh_mags)
                ##pylab.show()
                #print "%.3g\t%.3g\t%.3g\t%.3g" % (
                #   scipy.std(dh_mags), scipy.median(dh_mags),
                #   scipy.std(ddh_mags), scipy.median(ddh_mags))
                #if h.n in defs.HARMONICS_FIT_PLOT_N:
                #if False:
                #    #pylab.plot(h.mags, '-o')
                #    pylab.plot(dh_mags, '-')
                #    pylab.plot(ddh_mags, '-*')
                #    #pylab.xlim([0, 30])
#
#                    pylab.show()
                    #exit(1)

                #num_harms_above_noise += 1
                ts = hop_rate * h.frame_numbers
                if h.n == defs.HARMONICS_FIT_PLOT_N:
                    show=True
                    plot=False
                    plot_last=True
                else:
                    show=False
                    plot=False
                    plot_last=defs.HARMONICS_FIT_PLOT
                fit, rsquared, variance = decay_exponential.fit_best_exponential(
                    ts, h.mags, noise_mean=noise_mean,
                    show=show, plot=plot, plot_last=plot_last)
                if fit is None:
                    stats.num_harms_no_fit += 1
                    print "bail from no fit"
                    continue
                #alpha = fit[2]
                alpha = fit[1]

                #drop_amplitude = fit[0] / noise_mean
                drop_amplitude = max(h.mags) / noise_mean
                drop_db = stft.amplitude2db(drop_amplitude)
                #print drop_db
                #if drop_db < defs.HARMONIC_MIN_DROP_DB:
                #    stats.num_harms_no_drop += 1
                #    continue
                if rsquared < defs.HARMONIC_FIT_MIN_RSQUARED:
                    stats.num_harms_no_rsquared += 1
                    continue
                #if variance > defs.HARMONIC_FIT_MAX_VARIANCE:
                #    stats.num_harms_no_variance += 1
                #    continue
                #if variance > 1.0:
                #    continue



                freq = partials.mode_B2freq(f0, h.n, B)
                w = 2*numpy.pi*freq
                Q = w / (2*alpha)
                decay = classes.Decay(freq, w, h.n, alpha, Q,
                    rsquared, variance, drop_db)
                decays.append(decay)
                stats.num_harms_end += 1
                if defs.HARMONICS_PRINT_SUMMARY:
                    print "n: %i\t%.1f\tdecay: %.2f\tr-squared: %.2f\tvariance: %.2f\tdrop: %.2f db" % (
                        h.n, freq, alpha, rsquared, variance, drop_db)
                        
            #print "%s\t%i\t%i\t%i\t%i\t%i" % (
            #print "%s\t%i | \t%i\t%i\t%i\t| %i" % (
            #    basename,
            #    num_harms_original,
            #    num_harms_no_above_noise,
            #    num_harms_no_fit,
            #    #num_harms_no_rsquared,
            #    num_harms_no_drop,
            #    num_harms_end,
            #    )
        print "dropped:", stats.num_harms_max_no_above_noise, stats.num_harms_num_no_above_noise,

        def dot_color(d):
            #rs = 1.0/d.variance
            #if rs > 10.:
            #    rs = 10.
            #rs = 10*d.rsquared
            rs = d.drop/10.0

            rss = rs/10.0
            dot = '.'
            markersize = 5 + 5.0*(rss)
            color = matplotlib.cm.winter(1.-rss)
            return dot, color, markersize

        if defs.HARMONICS_PLOT_DECAYS or plot_harms:
            pylab.figure()
            for d in decays:
                #dot, color, markersize = dot_color(d.rsquared)
                dot, color, markersize = dot_color(d)
                pylab.plot(d.n, d.alpha,
                    dot, color=color,
                    markersize=markersize,
                    linewidth=0,
                    )
            pylab.xlabel("mode")
            pylab.ylabel("decay rates")
            pylab.xlim([0, max([d.n for d in decays])+1])
            #pylab.legend()

        if defs.HARMONICS_PLOT_Q:
            pylab.figure()
            #print "# n, loss factor, weight"
            for d in decays:
                #print "%i, %.2e, %.2e" %(d.n, 1./d.Q, d.rsquared)
                #dot, color, markersize = dot_color(1.0/d.variance)
                dot, color, markersize = dot_color(d)
                #if d.variance > 10 or d.rsquared < 0.25:
                #if d.rsquared < 0.3:
                #    dot = 'x'
                #    color = 'red'
                #else:
                #    print d.variance
                pylab.plot(d.n, d.Q,
                    dot, color=color,
                    markersize=markersize,
                    linewidth=0,
                    )
            pylab.xlabel("mode")
            pylab.ylabel("Q")
            pylab.xlim([0, max([d.n for d in decays])+1])
            #pylab.legend()

        if defs.HARMONICS_PLOT_LOSS:
            pylab.figure()
            #print "# n, loss factor, weight"
            for d in decays:
                #print "%i, %.2e, %.2e" %(d.n, 1./d.Q, d.rsquared)
                #dot, color, markersize = dot_color(1.0/d.variance)
                dot, color, markersize = dot_color(d)
                #if d.variance > 10 or d.rsquared < 0.25:
                #if d.rsquared < 0.3:
                #    dot = 'x'
                #    color = 'red'
                #else:
                #    print d.variance
                pylab.plot(d.n, 1.0/d.Q,
                    dot, color=color,
                    markersize=markersize,
                    linewidth=0,
                    )
            pylab.xlabel("mode")
            pylab.ylabel("loss")
            pylab.xlim([0, max([d.n for d in decays])+1])
            #pylab.legend()

        ns = [ h.n for h in decays ]
        stats.highest_harm = max(ns)

        if (defs.HARMONICS_PLOT_DECAYS or defs.HARMONICS_PLOT_Q
                or defs.HARMONICS_PLOT_LOSS or plot_harms):
            pylab.show()
        return decays, f0, B, stats


def get_ts(hop_rate, values):
    ts = numpy.array([x*hop_rate for x in xrange(len(values))])
    return ts

if __name__ == "__main__":
    if len(sys.argv) > 1:
        harms = HarmonicsData("yvr", sys.argv[1],
            #recalc=True, plot=True)
            recalc=True, plot=False)
        #harms = HarmonicsData(sys.argv[1], sys.argv[2])
        exit(0)


