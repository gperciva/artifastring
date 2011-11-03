#!/usr/bin/env python

import os
import os.path
import sys

import pickle

import numpy
import pylab

import defs
import classes

import stft
import partials
import estimate_f0_B
import calc_noise

import write_data
import plots
import tables


def use_harmonic(h, noise_cutoff, fft_amplitude, bin_f0, B,
        bin_spread_below, bin_spread_above):
    if h.mag < noise_cutoff[h.fft_bin]:
        return False
    return True

def calc_harmonics(wav_filename, f0=None, B=None,
        limit=defs.TOTAL_HARMONICS):
    if f0 is None:
        raise Exception("need f0 and B; run another program")

    # eliminate $HOME ~ and symlinks
    wav_filename = os.path.realpath(os.path.expanduser(wav_filename))
    basename = os.path.splitext(os.path.basename(wav_filename))[0]
    shared_dirname = os.path.abspath(
        os.path.join(os.path.dirname(wav_filename), '..'))

    dest_dir = os.path.join(shared_dirname, "spectrum", basename)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    window_buffers, sample_rate = stft.get_buffers_from_file(wav_filename)

    freqs = [ stft.bin2hertz(i, sample_rate)
        for i in range(stft.WINDOWSIZE/2+1) ]

    ### get noise for tuning off low harmonics
    initial_noise_floor, initial_noise_freqs, _, _, _ = calc_noise.get_noise(wav_filename)
    noise_cutoff = stft.db2amplitude(
        stft.amplitude2db(initial_noise_floor)
        +defs.STFT_MIN_DB_ABOVE_NOISE)

    bin_f0 = stft.hertz2bin(f0, sample_rate)
    # radius of search area for peaks
    bin_spread_below = int(
        stft.hertz2bin(defs.STFT_PEAK_SPREAD_BELOW_HERTZ*f0,
            sample_rate))
    bin_spread_above = int(
        stft.hertz2bin(defs.STFT_PEAK_SPREAD_ABOVE_HERTZ*f0,
            sample_rate))
    bin_spread_below = 3
    bin_spread_above = 3

    if defs.STFT_DUMP_TEXT:
        write_data.write_Bs(dest_dir, sample_rate, f0, B, limit,
            bin_spread_below, bin_spread_above)
        write_data.write_ideals(dest_dir, f0, limit)


    # store the peaks
    harmonics = [None]*limit

    spectrums = []
    table_info = tables.save_fft(basename)
    if table_info:
        harms_freqs = []
        harms_mags = []

    if defs.ONLY_N_WINDOWS:
        window_buffers = window_buffers[:defs.ONLY_N_WINDOWS]
    for window_number, window_buffer in enumerate(window_buffers):
        #print '-------- window --- %i' % window_number
        #fft_amplitude = stft.stft(window_buffer)
        fft_amplitude = stft.stft_amplitude(window_buffer)
        if window_number == 0:
            write_data.write_spectrum(dest_dir, window_number,
                freqs, stft.amplitude2db(fft_amplitude))
        if defs.STFT_DUMP_TEXT:
            write_data.write_spectrum(dest_dir, window_number,
            freqs, stft.amplitude2db(fft_amplitude))
        spectrums.append(fft_amplitude)

        # get harmonic peaks, and disable harmonics if can't do
        harms, _ = partials.get_freqs_mags(
            limit, bin_f0, B, fft_amplitude,
            bin_spread_below, bin_spread_above,
            only_peaks=False)
        if defs.STFT_PLOT_PARTIALS:
            plots.plot_partials(fft_amplitude, sample_rate, harms,
                bin_f0, B, bin_spread_below, bin_spread_above
                )
        if defs.STFT_DUMP_TEXT:
            dump_freqs = numpy.zeros(limit)
            dump_mags = numpy.zeros(limit)
        if table_info:
            harm_freqs = []
            harm_mags = []

        for h in harms:
            i = h.n-1
            if harmonics[i] is None:
                #print stft.bin2hertz(h.fft_bin, sample_rate), h.mag, noise_cutoff[h.fft_bin]
                harmonics[i] = classes.HarmonicSignal(h.n)
                #if use_harmonic(h, noise_cutoff, fft_amplitude,
                #        bin_f0, B,
                #        bin_spread_below, bin_spread_above,
                #        ):
                #    harmonics[i] = classes.HarmonicSignal(h.n)
                #else:
                #    #print "disable harmonic ", n
                #    harmonics[i] = False
            if harmonics[i] is not False:
                if h.mag == 0:
                    continue
                if defs.STFT_DUMP_TEXT:
                    dump_freqs[i] = stft.bin2hertz(h.fft_bin, sample_rate)
                    dump_mags[i] = h.mag
                if table_info:
                    harm_freqs.append(stft.bin2hertz(h.fft_bin, sample_rate))
                    harm_mags.append(h.mag)
                harmonics[i].mags.append(h.mag)
                harmonics[i].frame_numbers.append(window_number)
            #print harmonics[i]
        if table_info:
            harms_freqs.append(harm_freqs)
            harms_mags.append(harm_mags)

        if defs.STFT_DUMP_TEXT:
            #print dump_mags
            write_data.write_harms(dest_dir, window_number,
               dump_freqs, dump_mags, harmonics)

        if (defs.STFT_PLOT_FIRST_N > 0) and (window_number < defs.STFT_PLOT_FIRST_N):
            plots.plot_stft_first_n(window_number,
                defs.STFT_PLOT_FIRST_N,
                fft_amplitude, sample_rate, harms, wav_filename,
                bin_f0, B, bin_spread_below, bin_spread_above
                )
            if window_number >= defs.STFT_PLOT_FIRST_N - 1:
                pylab.show()
    dh = float(defs.HOPSIZE) / sample_rate
    if defs.STFT_DUMP_ALL:
        write_data.write_stft_all(dest_dir, spectrums, freqs, dh)
    table_info = tables.save_fft(basename)
    if table_info:
        for ti in table_info:
            write_data.write_stft_3d(basename, spectrums, freqs, dh,
                ti, harms_freqs, harms_mags, sample_rate)

    # clean up harmonics
    harmonics = filter(lambda x: x is not False, harmonics)
    for h in harmonics:
        h.mags = numpy.array(h.mags)
        h.frame_numbers = numpy.array(h.frame_numbers)
        #pylab.plot(stft.amplitude2db(h.mags))
        #pylab.show()

    return harmonics, dh


def get_harmonics(wav_filename, f0=None, B=None, limit=None, recalc=False):
    pickle_filename = wav_filename + ".stft.pickle"
    if os.path.exists(pickle_filename) and not recalc:
        print "Reading from", pickle_filename
        pickle_file = open(pickle_filename, 'rb')
        (harmonics, hop_rate) = pickle.load(pickle_file)
        pickle_file.close()
    else:
        if f0 is None:
            _, _, _, final = estimate_f0_B.estimate_f0_B(
                [wav_filename])
            f0 = final.f0
            B = final.B
            limit = final.highest_mode
        print "Using f0, B, limit:\t%.1f\t%.3g\t%i" % (
            f0, B, limit)
        (harmonics, hop_rate) = calc_harmonics(wav_filename,
            f0, B, limit)
        pickle_file = open(pickle_filename, 'wb')
        pickle.dump( (harmonics, hop_rate), pickle_file, -1)
        pickle_file.close()
        print "Wrote to", pickle_filename

    return harmonics, hop_rate

if __name__ == "__main__":
    try:
        filename = os.path.realpath(os.path.expanduser(
            sys.argv[1]))
    except:
        print "need filename"
        exit(1)
    try:
        f0 = float(sys.argv[2])
        B = float(sys.argv[3])
        limit = int(sys.argv[4])
    except:
        f0 = None
        B = None
        limit = None
    get_harmonics(filename, f0, B, limit, recalc=True)


