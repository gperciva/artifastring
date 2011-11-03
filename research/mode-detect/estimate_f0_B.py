#!/usr/bin/env python

import sys
import os.path
import glob

import math
import numpy
import scipy

import defs
import expected_frequencies
import calc_noise
import stft
import partials
import stiff_ideal_conflict
import plots

import pylab
import matplotlib.cm

import adjust_B


class StringFreqsB():
    def __init__(self, f0, B, highest_mode):
        self.f0 = f0
        self.B = B
        self.highest_mode = highest_mode

class StringFreqsB_stats():
    def __init__(self):
        self.basename = None
        self.num_files = None
        self.rsquared = None
        self.highest_mode_detected = None
        self.highest_mode_stiff_ideal = None
        self.highest_mode_stiff_ideal_adjusted = None
        self.delta_fn = None


### estimating B
def estimate_B(xs, ys, weights, initial_bin_f0, initial_B):
    xs = numpy.array(xs)
    ys = numpy.array(ys)
    weights = 1.

    def residuals(p, y, x):
        return (y - (partials.mode_B2freq(p[0], x, abs(p[1])) / x) )
    def residuals_weighted(p, y, x):
        return ((y - (partials.mode_B2freq(p[0], x, abs(p[1])) /
        x) ))*weights

    initial_guess = [initial_bin_f0, initial_B]
    fit, cov, infodict, mesg, ier = scipy.optimize.leastsq( 
        residuals, initial_guess,
        args=(ys,xs), full_output=1)

    ss_err = (infodict['fvec']**2).sum()
    ss_tot = ((ys-ys.mean())**2).sum()
    rsquared = 1. - (ss_err / ss_tot)

    return fit[0], abs(fit[1]), rsquared


def get_bin_f0_B(bin_initial_estimate, fft_buffers,
        noise_cutoff, bin_spread_below, bin_spread_above, fs):
    ### gradually discover/refine estimates of bin_f0 and B
    bin_f0 = bin_initial_estimate
    B = 1e-4
    limit = defs.TOTAL_HARMONICS
    for i in range(defs.B_INITIAL_PARTIALS, defs.TOTAL_HARMONICS):
        #print fft_buffers.shape
        bin_f0, B, rsquared, ok = align_with_B(i, bin_f0, B, fft_buffers,
            noise_cutoff, bin_spread_below, bin_spread_above,
            fs)
        limit = stiff_ideal_conflict.find_limit(bin_f0, B,
            bin_spread_below, bin_spread_above)
        #print B, rsquared, limit
        if i > limit:
            #print "warning: exceeding lim?", i, limit
            ok = False
        if defs.B_PRINT_INDIVIDUAL_BS:
            print "%i\t%.4f\t%.5e\t\t%i\t%i" % (
                i, bin_f0, B, ok, 0)
        if ok is False:
            limit = i
            break

    rows, columns = fft_buffers.shape
    partialss = []
    idealss = []
    for j in range(rows):
        fft = fft_buffers[j]
        #harmonics, ideal_harmonics = partials.get_freqs_mags(defs.TOTAL_HARMONICS, bin_f0, B,
        harmonics, ideal_harmonics = partials.get_freqs_mags(limit, bin_f0, B,
            fft, bin_spread_below, bin_spread_above,
            only_peaks=True, Bsearch=True)
        harmonics = [ h for h in harmonics if h.mag > noise_cutoff[h.fft_bin] ]
        ideal_harmonics = [ h for h in ideal_harmonics if h.mag > noise_cutoff[h.fft_bin] ]
        partialss.extend(harmonics)
        idealss.extend(ideal_harmonics)

    #if True:
    if False:
        pylab.figure()
        for j in range(rows):
            fft = fft_buffers[j]
            pylab.plot(stft.amplitude2db(fft), color="orange")

        xs = [ h.fft_bin for h in partialss]
        #if h.n > defs.B_MIN_HARMONIC_FIT_TO ]
        ys = [ h.mag for h in partialss]
        #if h.n > defs.B_MIN_HARMONIC_FIT_TO ]
        pylab.plot(xs, stft.amplitude2db(ys), 'p',
            color="blue")
        pylab.plot(stft.amplitude2db(noise_cutoff), color="black")
        #ns = [ h.n for h in partialss if h.n > defs.B_MIN_HARMONIC_FIT_TO ]
        #pylab.plot( ns,
        #    [ h.fft_bin - partials.mode_B2freq(bin_f0, h.n, B)
        #    for h in partialss if h.n > defs.B_MIN_HARMONIC_FIT_TO ],
        #    '.')
        pylab.show()

    if defs.B_PLOT_FIT:
        ns = [ h.n for h in partialss if h.n > defs.B_MIN_HARMONIC_FIT_TO ]
        ys = [ h.fft_bin / h.n for h in partialss if h.n >
            defs.B_MIN_HARMONIC_FIT_TO ]
        omit_ns = [ h.n for h in partialss if h.n <= defs.B_MIN_HARMONIC_FIT_TO ]
        omit_ys = [ h.fft_bin / h.n for h in partialss if h.n <=
            defs.B_MIN_HARMONIC_FIT_TO ]
        plots.plot_B_fit(ns, ys, omit_ns, omit_ys, bin_f0, B, fs, idealss)
        pylab.show()

    return bin_f0, B, rsquared, partialss, limit

def align_with_B(num_harmonics, bin_f0, B, ffts,
        noise_cutoff,
        bin_spread_below, bin_spread_above, sample_rate):
    rows, columns = ffts.shape
    partialss = []
    idealss = []
    for j in range(rows):
        fft = ffts[j]
        harmonics, ideal_harmonics = partials.get_freqs_mags(num_harmonics, bin_f0, B,
            fft, bin_spread_below, bin_spread_above,
            only_peaks=True, Bsearch=True)
        if harmonics is None:
            return bin_f0, B, None, False

        harmonics = [ h for h in harmonics if h.mag > noise_cutoff[h.fft_bin] ]
        ideal_harmonics = [ h for h in ideal_harmonics if h.mag > noise_cutoff[h.fft_bin] ]
        partialss.extend(harmonics)
        idealss.extend(ideal_harmonics)

    #ns = [ h.n for h in partialss if h.n > 1 ]
    #ys = [ h.fft_bin / h.n for h in partialss if h.n > 1 ]
    ns = [ h.n for h in partialss if h.n >
        defs.B_MIN_HARMONIC_FIT_TO ]
    ys = [ h.fft_bin / h.n for h in partialss if h.n >
        defs.B_MIN_HARMONIC_FIT_TO ]
    ns_orig = list(ns)
    ys_orig = list(ys)
    ns = []
    ys = []
    weights = []
    #for i, h in enumerate(partialss):
    #    if h.n <= defs.B_MIN_HARMONIC_FIT_TO:
    #        continue
        #if stiff_ideal_conflict.does_confict(bin_f0, B,
        #    bin_spread_below, bin_spread_above, h.n):
        #    #print "bail from conflict"
        #    continue
    #    ns.append( h.n )
    #    ys.append( h.fft_bin / h.n)
    #    weights.append( h.mag - noise_cutoff[h.fft_bin] )
    ns = ns_orig
    ys = ys_orig
    bin_f0, B, rsquared = estimate_B(ns, ys,
        weights,
        initial_bin_f0=bin_f0, initial_B=B)

    if defs.B_PLOT_FIT_INDIVIDUAL:
        omit_ns = [ h.n for h in partialss if h.n <= defs.B_MIN_HARMONIC_FIT_TO ]
        omit_ys = [ h.fft_bin / h.n for h in partialss if h.n <=
            defs.B_MIN_HARMONIC_FIT_TO ]
        plots.plot_B_fit(ns, ys, omit_ns, omit_ys, bin_f0, B,
            sample_rate, idealss)

        pylab.show()

    ok = True
    nums_per = []
    #print '----'
    for n in range(1,num_harmonics+1):
        nums = len( [h.n for h in partialss if h.n == n])
        nums_per.append(nums)
        #print nums,
    if nums_per[num_harmonics-1] < 4:
        #ok = False
        #print "bail", num_harmonics
        pass

    return bin_f0, B, rsquared, ok


def estimate_f0_B(filenames):
    ### ASSUME: all filenames are of the same instrument-string
    wav_filename = filenames[0]
    basename='-'.join(os.path.basename(wav_filename).split('-')[0:3])
    if basename.startswith("test-440f"):
        return 440.0, 0, 1, 1, 1, 1

    ### get initial f0 estimate
    base_frequency_estimate = expected_frequencies.get_freq_from_filename(
        wav_filename)
    ### get noise
    initial_noise_floor, initial_noise_freqs, _, _, _ = calc_noise.get_noise(wav_filename)
    noise_cutoff = stft.db2amplitude(
        stft.amplitude2db(initial_noise_floor)+defs.B_MINIMUM_HARMONIC_SNR)

    #### get FFT frames from audio files
    sample_rate = None
    freqs = None
    estimate_B_buffers_list = []
    for wav_i, wav_filename in enumerate(filenames):
        #print wav_filename
        #window_buffer, sample_rate = stft.get_long_buffer_from_file(wav_filename,
        window_buffers, sample_rate = stft.get_buffers_from_file(wav_filename,
            (defs.B_NUM_BUFFERS_ESTIMATE))
        if freqs is None:
            freqs = [ stft.bin2hertz(i, sample_rate)
                for i in range(stft.WINDOWSIZE/2+1) ]

        estimate_B_buffers_this_list = []
        #fft_amplitude = stft.fft_amplitude(window_buffer, sample_rate)
        #estimate_B_buffers_this_list.append(fft_amplitude)
        for window_number in range(defs.B_NUM_BUFFERS_ESTIMATE):
            window_buffer = window_buffers[window_number]
            fft_amplitude = stft.stft_amplitude(window_buffer)
            estimate_B_buffers_this_list.append(fft_amplitude)
        estimate_B_buffers_list.extend(estimate_B_buffers_this_list)

    estimate_B_buffers = numpy.array(estimate_B_buffers_list)
    
    ### radius of search area for peaks
    # used with STFT only
    bin_initial_estimate = stft.hertz2bin(base_frequency_estimate,
        sample_rate)
    #bin_initial_estimate = (base_frequency_estimate
    #    * fft_amplitude.shape[0] / (sample_rate/2)
    #    )
    #print bin_initial_estimate
    bin_spread_below = int(math.ceil(abs(
        stft.hertz2bin(
            (1.0-defs.B_PEAK_SPREAD_BELOW_HERTZ)*base_frequency_estimate,
            sample_rate) - bin_initial_estimate)))
    bin_spread_above = int(math.ceil(
        stft.hertz2bin(
            (1.0+defs.B_PEAK_SPREAD_ABOVE_HERTZ)*base_frequency_estimate,
            sample_rate) - bin_initial_estimate))
    #bin_spread_below = int(round(bin_initial_estimate *
    #    defs.B_PEAK_SPREAD_BELOW_HERTZ))
    #bin_spread_above = int(round(bin_initial_estimate *
    #    defs.B_PEAK_SPREAD_BELOW_HERTZ))
    #bin_spread_below_main = int(
    #    stft.hertz2bin(defs.STFT_PEAK_SPREAD_BELOW_HERTZ*base_frequency_estimate,
    #        sample_rate))
    #bin_spread_above_main = int(
    #    stft.hertz2bin(defs.STFT_PEAK_SPREAD_ABOVE_HERTZ*base_frequency_estimate,
    #        sample_rate))

    ### actual estimate
    bin_f0, B, rsquared, harmonics, limit = get_bin_f0_B(
        bin_initial_estimate,
        estimate_B_buffers, noise_cutoff,
        #estimate_B_buffers, numpy.zeros(defs.LONG_WINDOWSIZE+1),
        bin_spread_below, bin_spread_above, sample_rate)

    highest_harmonic = 0
    for h in harmonics:
        if highest_harmonic < h.n:
            highest_harmonic = h.n
    limit = min(limit, highest_harmonic)
    # HACK: remove limit
    #limit = defs.TOTAL_HARMONICS
    #print "limit to:", limit

    #harmonics_enable = [True]*defs.TOTAL_HARMONICS
    harmonics_enable = [True]*limit

    bins_estimate = [ partials.mode_B2freq(bin_f0, i, B) for
        i in range(1,len(harmonics_enable)+1) ]
    bins_naive = [ i*bin_f0 for
        i in range(1,len(harmonics_enable)+1) ]

    if defs.B_PLOT:
        pylab.figure()
        pylab.plot(initial_noise_freqs,
            stft.amplitude2db(initial_noise_floor), color='black')
        #pylab.plot(initial_noise_freqs,
        #   stft.amplitude2db(initial_noise_floor)+defs.B_MINIMUM_HARMONIC_SNR,
        #   color='black')
        pylab.xlabel("Frequency (seconds)")
        pylab.ylabel("Power (/ dB)")

        for i in range(estimate_B_buffers.shape[0]):
            #color = matplotlib.cm.spring(float(wav_i)/len(filenames))
            #color = matplotlib.cm.RdYlGn(
            #color = matplotlib.cm.spring(
            #    float(i)/len(estimate_B_buffers_this_list))
            pylab.plot(freqs,
                stft.amplitude2db(estimate_B_buffers[i,:]),
                #color=color,
                color="orange",
                alpha=0.5,
                label=basename,
                )


        for est in bins_estimate:
            low = stft.bin2hertz(est - bin_spread_below, sample_rate)
            high = stft.bin2hertz(est + bin_spread_above, sample_rate)
            if True:
                pylab.axvspan(low, high, color='c', alpha=0.3)
            else:
                pylab.axvline(stft.bin2hertz(est, sample_rate),
                    color='cyan', alpha=0.3,
                    #linewidth=2.0
                    )
        for naive in bins_naive:
            freq = stft.bin2hertz(naive, sample_rate)
            pylab.axvline(freq, color='grey', alpha=0.2,
                #linewidth=2.0
                )
        for j, harm in enumerate(harmonics):
            if harm.mag == 0:
                continue
            fn = stft.bin2hertz(harm.fft_bin, sample_rate)
            mag = stft.amplitude2db(harm.mag)
            #pylab.plot(fn, mag, 'o',
            #    color='green'
            #    )
        pylab.xlabel("Frequency")
        pylab.ylabel("Decibels")
    if defs.B_DUMP_HARMS:
        t_fns = []
        t_mags = []
        for j, harm in enumerate(harmonics):
            if harm.mag == 0:
                continue
            fn = stft.bin2hertz(harm.fft_bin, sample_rate)
            mag = stft.amplitude2db(harm.mag)
            t_fns.append(fn)
            t_mags.append(mag)
        data = numpy.vstack((t_fns, t_mags)).transpose()
        numpy.savetxt("B-harms.txt", data)


    if defs.B_PLOT:
        pylab.show()

    f0 = stft.bin2hertz(bin_f0, sample_rate)
    stiff_ideal_limit = stiff_ideal_conflict.find_limit(bin_f0, B,
        bin_spread_below, bin_spread_above)
    lim = min(stiff_ideal_limit, limit)
    detected_freqs = StringFreqsB(f0, B, lim)
    stats = StringFreqsB_stats()
    stats.num_files = len(filenames)
    stats.rsquared = rsquared
    stats.highest_mode_detected = limit
    stats.highest_mode_stiff_ideal = stiff_ideal_limit
    stats.basename = basename


    adjusted_B, delta_fn = adjust_B.adjust(basename, limit, f0, B)
    if adjusted_B is not None:
        stiff_ideal_lim_adjusted = stiff_ideal_conflict.find_limit(
            bin_f0, adjusted_B,
            bin_spread_below, bin_spread_above)
        lim = min(stiff_ideal_lim_adjusted, limit)

        adjusted_freqs = StringFreqsB(f0, adjusted_B, lim)
        adjusted_freqs.delta_fn = delta_fn
        stats.highest_mode_stiff_ideal_adjusted = stiff_ideal_lim_adjusted
        stats.delta_fn = delta_fn
        final = StringFreqsB(f0, adjusted_B,
            min(stats.highest_mode_detected,
                stats.highest_mode_stiff_ideal,
                stiff_ideal_lim_adjusted))
    else:
        adjusted_freqs = None
        final = StringFreqsB(f0, B,
            min(stats.highest_mode_detected,
                stats.highest_mode_stiff_ideal))
    return detected_freqs, adjusted_freqs, stats, final


def process(dirname):
    dirname = os.path.realpath(os.path.expanduser(dirname))
    if dirname.endswith('.wav'):
        filenames = [ dirname ]
    else:
        filenames = glob.glob(
            os.path.expanduser(dirname) + '*.wav')
    filenames.sort()

    if defs.ONLY_N_FILES > 0:
        filenames = filenames[:defs.ONLY_N_FILES]

    return estimate_f0_B(filenames)

def get_header():
    return "name\t$f_0$\t$B$\t$R^2$\tstiff-ideal limit\tnotes"
    #return "name\tnum files\t$f_0$\tB\t$R^2$\thighest detected\tstiff-ideal limit\tadjusted B (and delta fn)\tfinal limit"

def get_info(detected_freqs, adjusted_freqs, stats, final):
    if adjusted_freqs  is not None:
        adjusted_string = str("%.4e %.4f" % (
            adjusted_freqs.B, stats.delta_fn))
        #lim = adjusted_freqs.highest_mode
    else:
        adjusted_string = ""
        #lim = detected_freqs.highest_mode
    notes = adjust_B.notes_B(stats.basename)
    #text = str("%i\t%.1f\t%.2e\t%.2f\t%i\t%i\t%s\t%i" % (
    text = str("%.4f\t%.5e\t%.3f\t%i\t%s" % (
            #stats.num_files,
            detected_freqs.f0, detected_freqs.B,
            stats.rsquared,
            #stats.highest_mode_detected,
            stats.highest_mode_stiff_ideal,
            #adjusted_string,
            #final.highest_mode,
            notes,
            ))
    return text


if __name__ == "__main__":
    try:
        dirname = os.path.realpath(os.path.expanduser(sys.argv[1]))
    except:
        print "Give dirname and optionally base filename"
    detected_freqs, adjusted_freqs, stats, final = process(dirname)
    print get_header()
    print os.path.basename(dirname) + "\t",
    print get_info(detected_freqs, adjusted_freqs, stats, final)
    if defs.B_PLOT:
        pylab.show()


