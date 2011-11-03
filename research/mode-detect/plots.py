#!/usr/bin/env python

import numpy
import pylab
import matplotlib.cm

import stft
import partials
import defs

### add individual bits
def plot_fft(fft, sample_rate):
    freqs = [ stft.bin2hertz(i, sample_rate) for i in xrange(len(fft)) ]
    pylab.plot(
        [ f for f, m in zip(freqs, fft) if m > 0.0 ],
        [ stft.amplitude2db(m) for f, m in zip(freqs, fft) if m > 0.0 ],
        '.-',
        alpha=0.9,
        label="fft above noise")

def plot_peaks(partials, sample_rate):
    pylab.plot( [
            stft.bin2hertz(f.fft_bin, sample_rate)
            for f in partials],
        [stft.amplitude2db(f.mag) for f in partials],
        'o', color="red",
        label="detected peaks")

def plot_resynth(harmonics, fft, sample_rate):
    freqs = [ stft.bin2hertz(i, sample_rate) for i in xrange(len(fft)) ]
    synth_min_cutoff = 0.5 * min(numpy.where(fft>0, fft, 1))
    length = len(fft)
    for i, sp in enumerate(harmonics):
        synthesized_peak = partials.qifft_synthesize(sp.fft_bin,
            sp.mag, sp.curvature_a, length)
        synthesized_peak = numpy.where(
            synthesized_peak > synth_min_cutoff,
            synthesized_peak, 0)
        if i == 0:
            pylab.plot(
                [ f for f, m in zip(freqs, synthesized_peak) if m > 0.0 ],
                stft.amplitude2db(
                    numpy.array(
                    [ m for f, m in zip(freqs, synthesized_peak) if m > 0.0 ],
                    )),
                '.-', color="yellow", alpha=0.8,
                label="resynthesized peak")
        else:
            pylab.plot(
                [ f for f, m in zip(freqs, synthesized_peak) if m > 0.0 ],
                stft.amplitude2db(
                    numpy.array(
                    [ m for f, m in zip(freqs, synthesized_peak) if m > 0.0 ],
                    )),
                '.-', color="yellow", alpha=0.8)


def plot_ideal_lines(bin_f0, num_harmonics, sample_rate):
    ideal_freqs = numpy.array(
        [stft.bin2hertz( partials.mode_B2freq( bin_f0, i+1, 0), sample_rate)
            for i in xrange(num_harmonics) ]
            )
    for i, line in enumerate(ideal_freqs):
        if i == 0:
            pylab.axvline( line,
                color="pink",
                #linewidth=3.0,
                alpha=0.8,
                label="ideal",
                )
        else:
            pylab.axvline( line,
                color="pink",
                #linewidth=3.0,
                alpha=0.8,
                #label="ideal",
                )

def plot_stiff_area(bin_f0, B, bin_spread_below, bin_spread_above, stiff_partials, sample_rate):
    stiff_bins = numpy.array(
        [ partials.mode_B2freq( bin_f0, i+1, B)
            for i in xrange(len(stiff_partials)) ]
            )
    for i, est in enumerate(stiff_bins):
        low = stft.bin2hertz(est - bin_spread_below, sample_rate)
        high = stft.bin2hertz(est + bin_spread_above, sample_rate)
        if i == 0:
            pylab.axvspan(low, high, color='c', alpha=0.3,
                label="stiff")
        else:
            pylab.axvspan(low, high, color='c', alpha=0.3)


### main plots

def plot_partials(fft, sample_rate, stiff_partials,
        bin_f0, B, bin_spread_below, bin_spread_above
        ):
    plot_fft(fft, sample_rate)
    plot_stiff_area(bin_f0, B, bin_spread_below, bin_spread_above, stiff_partials, sample_rate)
    plot_ideal_lines(bin_f0, len(stiff_partials), sample_rate)
    plot_resynth(stiff_partials, fft, sample_rate)
    plot_peaks(stiff_partials, sample_rate)
    pylab.legend()
    pylab.show()


def plot_stft_first_n(window_number, n_windows,
                fft_amplitude, sample_rate, harms, wav_filename,
                bin_f0, B, bin_spread_below, bin_spread_above
        ):
    #if window_number % 2 == 0:
    count = window_number+1
    color = matplotlib.cm.gnuplot(float(count)/(n_windows+1))
    #label = "%.3f seconds" % (float(count) * stft.HOPSIZE/sample_rate)

    bin_freqs = [ stft.bin2hertz(bin_num, sample_rate)
        for bin_num, amplitude in enumerate(fft_amplitude) ]
    harms_freqs = [ 
        stft.bin2hertz(h.fft_bin, sample_rate)
        for h in harms if h.mag > 0]
    harms_mags = [
        stft.amplitude2db(h.mag)
        for h in harms if h.mag > 0]

    plot_ideal_lines(bin_f0, len(harms), sample_rate)
    plot_stiff_area(bin_f0, B, bin_spread_below, bin_spread_above, harms, sample_rate)
    pylab.plot(bin_freqs, stft.amplitude2db(fft_amplitude),
        '-',
        color=color,
        label="fft",
        )
    pylab.plot(harms_freqs, harms_mags, 'o',
        color=color,
        label="harmonics",
        )

    #for est in bins_estimate:
    #    low = stft.bin2hertz(est - bin_spread, sample_rate)
    #    high = stft.bin2hertz(est + bin_spread, sample_rate)
    #    pylab.axvspan(low, high, color='c', alpha=0.3)
    if window_number >= n_windows - 1:
        import calc_noise
        initial_noise_floor, initial_noise_freqs, _, _, _ = calc_noise.get_noise(
            wav_filename)
        pylab.plot(initial_noise_freqs,
            stft.amplitude2db(initial_noise_floor),
            label="initial noise floor",
            color="black",
            )
    #    #pylab.legend()
    #    #pylab.xlim([0, 3000])

def plot_B_fit(ns, ys, omit_ns, omit_ys, bin_f0, B, sample_rate, idealss):
    x = numpy.arange(1, max(ns)+1)
    predicted = partials.mode_B2freq(bin_f0, x, B) / x

    ideal_below = partials.mode_B2freq(bin_f0, x, 0) / x
    ideal_above = ((partials.mode_B2freq(bin_f0, x+1, 0)
        ) / x / bin_f0)
    below_bins = int(stft.hertz2bin(bin_f0*defs.B_PEAK_SPREAD_BELOW_HERTZ, sample_rate))
    above_bins = int(stft.hertz2bin(bin_f0*defs.B_PEAK_SPREAD_ABOVE_HERTZ, sample_rate))
    ideal_above_safe = ((partials.mode_B2freq(bin_f0, x+1, 0)
            - below_bins
            - above_bins
        ) / x / bin_f0)
    ideal_above_semi_stiff = ((partials.mode_B2freq(bin_f0, x+1, B/4.0)
        ) / x / bin_f0)
    ideal_above_above = ((partials.mode_B2freq(bin_f0, x+2, 0)
            - above_bins
        ) / x / bin_f0)

    ideal_ns = numpy.array([ h.n for h in idealss ])
    ideal_ys = [ h.fft_bin / h.n for h in idealss ]
    ideal_ns_next = ideal_ns-1
    ideal_ys_next = [ h.fft_bin / (h.n-1) for h in idealss ]

    ysa = numpy.array(ys)
    pylab.figure()
    pylab.plot(ns, ysa, '.')

    numpy.savetxt("ns_ys.txt",
        numpy.vstack((
            numpy.array(ns), stft.bin2hertz(numpy.array(ysa),
            sample_rate)
        )).transpose())
    pylab.plot(ideal_ns, ideal_ys, '.',
        color="green")
    pylab.plot(ideal_ns_next, ideal_ys_next, '.',
        color="green")
    pylab.plot(x, predicted, '-')
    numpy.savetxt("ns_predicted.txt",
        numpy.vstack((
            numpy.array(x), stft.bin2hertz(numpy.array(predicted),
            sample_rate)
        )).transpose())
    pylab.plot(x, ideal_below, '-', color="orange")
    pylab.plot(x, ideal_above_safe, '-', color="pink")
    pylab.plot(x, ideal_above, '-', color="orange")
    #pylab.plot(x, ideal_above_above, '-', color="orange")
    #pylab.plot(x, ideal_above_semi_stiff, '-', color="orange")

    pylab.plot( omit_ns, omit_ys, 'rx')
    numpy.savetxt("omit_ns_ys.txt",
        numpy.vstack((
            numpy.array(omit_ns),
            stft.bin2hertz(numpy.array(omit_ys), sample_rate)
        )).transpose())
    #pylab.plot(xs, weights, 'o')
    pylab.xlim(0)
    pylab.ylim([0.99*min(ys), 1.01*max(ys)])

