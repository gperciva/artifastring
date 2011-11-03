#!/usr/bin/env python
import os
import os.path
import scipy.signal
import stft

def write_noise(dest_dir, freqs, noise_floor):
    out = open(os.path.join(dest_dir,'noise-floor.txt'), 'w')
    for i in range(len(noise_floor)):
        out.write('%g\t%g\n' % (freqs[i], noise_floor[i]))
    out.close()

def write_spectrum(dest_dir, count, freqs, fft_power):
    out = open(os.path.join(dest_dir,'spectrum-%05i.txt' % count), 'w')
    for i in range(len(fft_power)):
        out.write('%g\t%g\n' % (freqs[i], fft_power[i]))
    out.close()

def write_harms(dest_dir, count, harm_freqs, mags, harmonics_enable):
    out = open(os.path.join(dest_dir,'harms-%05i.txt' % count), 'w')
    for harm_index in range(len(harm_freqs)):
        if harmonics_enable[harm_index]:
            if mags[harm_index] > 0.0:
                out.write('%g\t%g\n' % (harm_freqs[harm_index],
                    stft.amplitude2db(mags[harm_index])))
    out.close()

def write_stft_all(dest_dir, spectrums, freqs, dh):
    out = open(os.path.join(dest_dir, 'all-harms.txt'), 'w')
    for i, fft_amplitude in enumerate(spectrums):
        for j, freq in enumerate(freqs):
            amplitude = fft_amplitude[j]
            seconds = i*dh
            out.write("%g\t%g\t%g\n" % (freq, amplitude, seconds))
    out.close()

def write_Bs(dest_dir, sample_rate, f0, B, limit,
        bin_spread_below, bin_spread_above):
    out = open(os.path.join(dest_dir, 'Bs.txt'), 'w')
    out.write("%g\t%g\t%g\t%g\t%g\t%g\n" % (sample_rate, f0, B,
        limit, bin_spread_below, bin_spread_above))
    out.close()

def write_ideals(dest_dir, f0, limit):
    out = open(os.path.join(dest_dir, 'ideal-harmonics.txt'), 'w')
    harms = [i*f0 for i in range(1, limit+5)]
    for i, h in enumerate(harms):
        out.write("%i\t%g\n" % (i, h))
    out.close()

def write_stft_3d(basename, spectrums, freqs, dh, info,
        harms_freqs, harms_mags, sample_rate):
    print "writing %s" % info[0]
    add_filename = info[0]
    max_seconds = info[1]
    min_freq = info[2]
    max_freq = info[3]
    print "min, max freq, seconds:", min_freq, max_freq, max_seconds
    out = open(os.path.join("out", basename+"."+add_filename+".txt"), 'w')

    # log scale
    #mag_scale = max(max(harms_mags))
    mag_scale = 1.0
    #print mag_scale

    #import pylab
    #pylab.plot(freqs)
    max_time_bin = int(max_seconds / dh)
    min_freq_bin = int(stft.hertz2bin(min_freq, sample_rate))
    max_freq_bin = int(stft.hertz2bin(max_freq, sample_rate))
    #pylab.show()
    print "min, max, time bins:", min_freq_bin, max_freq_bin, max_time_bin
    total_points_x = 10000
    total_points_z = 10000
    downsample_factor_x = int((max_freq_bin-min_freq_bin) / total_points_x)
    downsample_factor_z = int(max_time_bin / total_points_z)
    print "downsample factors:", downsample_factor_x, downsample_factor_z

    print max_seconds, max_time_bin
    #print max_freq_bin / downsample_factor_x,
    #print max_time_bin / downsample_factor_z

    #import pylab
    #pylab.plot(freqs)
    if downsample_factor_x > 1:
        fft_freqs = [ freqs[i*downsample_factor_x]
            for i in range(max_freq_bin/downsample_factor_x) ]
    else:
        fft_freqs = freqs
    #fft_freqs = [ scipy.mean(freqs[i:i+downsample_factor_x])
    #    for i in range(len(freqs)/downsample_factor_x) ]
    #scipy.signal.decimate(
    #    freqs[min_freq_bin:max_freq_bin],
    #    downsample_factor_x, ftype='iir')
    #pylab.plot(fft_freqs)
    #pylab.show()
    rows = 0
    donerows = False
    for i, fft_amplitude in enumerate(spectrums[:max_time_bin]):
        if downsample_factor_z > 0:
            if (i % downsample_factor_z) != 0:
                continue
        if downsample_factor_x > 1:
            fft = [ scipy.mean(fft_amplitude[j*downsample_factor_x
                    :(j+1)*downsample_factor_x])
                for j in range(len(fft_amplitude)/downsample_factor_x) ]
        else:
            fft = fft_amplitude
        #fft = scipy.signal.decimate(fft_amplitude[min_freq_bin:max_freq_bin],
        #    downsample_factor_x, ftype='fir')
        j = 0
        k = 0
        while j < len(fft_freqs):
            fft_freq = fft_freqs[j]
            #print i, k
            if k < len(harms_freqs[i]):
                harm_freq = harms_freqs[i][k]
            else:
                harm_freq = 1e100
            if fft_freq < harm_freq:
                freq = fft_freq
                mag = fft[j] / mag_scale
                j += 1
            else:
                freq = harm_freq
                if k < len(harms_freqs[i]):
                    mag = harms_mags[i][k] / mag_scale
                else:
                    mag = -1
                k += 1
            if freq < min_freq or freq > max_freq:
                continue

            #amplitude = fft[j]
            seconds = i*dh
            out.write("%g\t%g\t%g\n" % (
                freq, seconds, stft.amplitude2db(mag)))
            if not donerows:
                rows += 1
        # define end of matrix
        out.write("\n")
        donerows = True
    out.close()
    print "rows:", rows


