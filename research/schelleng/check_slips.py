#!/usr/bin/env python

#EXAMINE_ONLY = True
EXAMINE_ONLY = False
DISABLE_MULTI = False
#DISABLE_MULTI = True

import os
import sys
sys.path.append('../../build/swig')
sys.path.append('../../build/.libs')
sys.path.append('../shared')
import artifastring_instrument
ARTIFASTRING_SAMPLE_RATE = artifastring_instrument.ARTIFASTRING_INSTRUMENT_SAMPLE_RATE
HAPTIC_SAMPLE_RATE = artifastring_instrument.HAPTIC_SAMPLE_RATE

import scipy.io.wavfile
import midi_pos

import scipy.fftpack
import numpy

import dsp

import scipy
import pylab
import expected_frequencies

NUM_PROCESSES = 3

import multiprocessing
fs = artifastring_instrument.ARTIFASTRING_INSTRUMENT_SAMPLE_RATE
DIRNAME = str(fs)
if not os.path.exists(DIRNAME):
    os.makedirs(DIRNAME)


#STEPS_POSITIONS = 40
STEPS_FORCE = 20
#STEPS_VELOCITY = 10
#forces = numpy.linspace(0.25, 2.0, STEPS_FORCE)
#positions = numpy.linspace(0.05, 0.20, STEPS_POSITIONS)
forces = numpy.linspace(0.01, 3.0, STEPS_FORCE)
# max force 2N for violin E string
# max force 3N for violin E string


#velocities = numpy.linspace(0.001, 1.0, STEPS_VELOCITY)
#velocities = [0.001, 0.3, 4.0]


#positions = numpy.linspace(0.085, 0.115, STEPS_POSITIONS)
#positions = list(positions)
#positions.append( 1.0 / 9)
#positions.append( 1.0 / 11)
#positions.sort()

def make_zoomed_positions(mode_low, mode_high, num_between):
    positions = []
    for x in range(mode_low,mode_high):
        low = 1.0 / (x+1)
        mid = 1.0 / (x + 0.5)
        high = 1.0 / (x)
        poses = numpy.linspace(low, mid, num_between)
        positions += list(poses)
        poses = numpy.linspace(mid, high, num_between)
        positions += list(poses)
    positions = list(set(positions))
    positions.sort()
    return positions

#positions = make_zoomed_positions(5,6,40)
#positions.append(1.0/5.5)
#positions.sort()

#positions = make_zoomed_positions(5,8,9)
positions = list(set(
    make_zoomed_positions(5, 10, 21)
    ))
positions.sort()

#print positions
#exit(1)


def note(st, fp, bp, force, bv, basename):
    #print bp, force, bv

    violin = artifastring_instrument.ArtifastringInstrument()
    #violin.reset()
    violin.finger(st, fp)
    violin.bow(st, bp, force, bv)
    
    samples = 1.0 * ARTIFASTRING_SAMPLE_RATE
    ### let string settle
    if True:
        buf = numpy.empty(samples, dtype=numpy.int16)
        forces = numpy.empty(samples/artifastring_instrument.HAPTIC_DOWNSAMPLE_FACTOR,
            dtype=numpy.int16)
        violin.wait_samples_forces_python(buf, forces)
    samples = 1.0 * ARTIFASTRING_SAMPLE_RATE
    ### part we care about
    #violin.set_string_logfile(st, str("%s-%i.log" % (basename, st)))
    if True:
        buf = numpy.empty(samples, dtype=numpy.int16)
        forces = numpy.empty(samples/artifastring_instrument.HAPTIC_DOWNSAMPLE_FACTOR,
            dtype=numpy.int16)
        violin.wait_samples_forces_python(buf, forces)

    #scipy.io.wavfile.write(basename+".wav",
    #    ARTIFASTRING_SAMPLE_RATE, buf)
    num_skips = violin.get_num_skips(st)
    return num_skips
    #violin.set_string_logfile(st, "")


def note_multi(st, fp, bp, force1, force2, bv, basename):
    #print bp, force, bv

    violin = artifastring_instrument.ArtifastringInstrument()
    #violin.reset()
    violin.finger(st, fp)
    violin.bow(st, bp, force1, bv)
    
    samples = 1.0 * ARTIFASTRING_SAMPLE_RATE
    ### let string settle
    if True:
        buf = numpy.empty(samples, dtype=numpy.int16)
        forces = numpy.empty(samples/artifastring_instrument.HAPTIC_DOWNSAMPLE_FACTOR,
            dtype=numpy.int16)
        violin.wait_samples_forces_python(buf, forces)
    samples = 1.0 * ARTIFASTRING_SAMPLE_RATE
    ### part we care about
    violin.bow(st, bp, force2, bv)
    #violin.set_string_logfile(st, str("%s-%i.log" % (basename, st)))
    if True:
        buf = numpy.empty(samples, dtype=numpy.int16)
        forces = numpy.empty(samples/artifastring_instrument.HAPTIC_DOWNSAMPLE_FACTOR,
            dtype=numpy.int16)
        violin.wait_samples_forces_python(buf, forces)

    #scipy.io.wavfile.write(basename+".wav",
    #    ARTIFASTRING_SAMPLE_RATE, buf)
    num_skips = violin.get_num_skips(st)
    return num_skips
    #violin.set_string_logfile(st, "")



def bin2hertz(bin_number, sample_rate, N):
    return bin_number * (sample_rate/2) / float(N/2+1)

def get_freqs_fft(signal, sample_rate):
    #signal = zero_pad_to_next_power_two(signal)
    fft = scipy.fftpack.fft(signal)
    fft_abs = abs(fft[:len(signal)/2+1])
    fft_normalized = fft_abs / (len(signal)/2)
    #fft_db = stft.amplitude2db(fft_normalized)
    #fft_db = fft_normalized
    freqs = [ bin2hertz(i, sample_rate, len(signal))
        for i in range(len(fft_normalized)) ]
    return freqs, fft_normalized

def get_freqs_db(signal, sample_rate):
    freqs, fft_abs = get_freqs_fft(signal, sample_rate)
    fft_db = 20*scipy.log10(fft_abs)
    return freqs, fft_db

def analyze_file(st, basename, f0):
    sample_rate, data = scipy.io.wavfile.read(basename+".wav")
    freqs, fft_db = get_freqs_db(data, sample_rate)

    #flatness = dsp.spectral_flatness(data)
    #flatness_low = dsp.spectral_flatness_limited(data, 20, f0*1.5, sample_rate)
    #flatness_low = dsp.spectral_flatness_limited(data, 20, f0*4.5, sample_rate)
    one = dsp.f0_snr(data, f0, sample_rate)

    #buf = data
    #window = scipy.signal.gaussian(len(buf), len(buf)/8)
    #fft = scipy.fftpack.fft(buf*window)
    #fft_power = abs(fft[:len(fft)/2+1])**2
    two = dsp.spectral_flatness_limited(data, 20, f0*4.5, sample_rate)

    three = abs(
        f0 - dsp.scf_limited(data, f0*0.9, f0*1.9, sample_rate)) / f0

    #centroid = dsp.spectral_centroid(data, sample_rate)
    #print "results:", flatness, centroid
    #pylab.plot(freqs, fft_db, label=basename)
    #return flatness, flatness_low, centroid
    return one, two, three
    #return flatness, f0_snr, centroid

def read_results(st, basename, plot=False):

    research_data = numpy.loadtxt(
        str("%s-%i.log" % (basename, st)))
    slips = research_data[:,4]

    dslips = slips[1:] - slips[:-1]
    ones = numpy.where( dslips == 1)
    ones = ones[0]
    dones = ones[1:] - ones[:-1]

    ft = numpy.zeros(len(slips))
    prev = 0
    for i, one in enumerate(ones[:-1]):
        ft[prev:one] = float(ARTIFASTRING_SAMPLE_RATE) / dones[i]
        prev = one
    ft = ft[:one]
    dts = [ float(x)/ARTIFASTRING_SAMPLE_RATE for x, y in enumerate(ft) ]

    mean_slip_freq = scipy.mean(ft)

    if plot:
        pylab.plot(dts, ft)
        pylab.ylim([100, 4000])
        pylab.ylabel("Freqency of slips (Hz)")
        pylab.xlabel("time (seconds)")

    #hopsize = 2048
    #slips = slips[:hopsize*int(len(slips)/hopsize)]
    #slips = slips.reshape( (-1, hopsize) )
    #print slips.shape

    #slips = slips[18]
    #pylab.plot(slips)
    #freqs, fft_normalized = get_freqs_fft(slips, 44100)

    #pylab.figure()
    #pylab.semilogy(freqs, fft_normalized)
        pylab.show()
    return mean_slip_freq

#fp = 0.251
fp = 0.0
string_midi = 76
expected_midi = midi_pos.pos2midi(fp) + string_midi
expected_freq = midi_pos.midi2freq(expected_midi)
#print "Expected frequency: %.1f" % expected_freq

#print "Searching positions:\n", positions
#print "Searching forces:\n", forces
#print "Searching vels:\n", velocities

def test_slips(st, vel):
    STEPS_FORCE = 30
    #STEPS_VELOCITIES = 30
    forces = numpy.linspace(0.01, 1.0, STEPS_FORCE)
    #velocities = numpy.linspace(0.01, 2.0, STEPS_VELOCITIES)
    filename = "slips-%i-%.3f.txt" % (ARTIFASTRING_SAMPLE_RATE, vel)
    out = open(filename, 'w')
    for i, force in enumerate(forces):
        for j, bp in enumerate(positions):
        #for j, vel in enumerate(velocities):
            basename = "%s-s%i-p%.3f-f%.3f-v%.3f" % (
                "%s/bow" % DIRNAME, st, bp, force, vel)
            fp = 0
            num_skips = note(st, fp, bp, force, vel, basename)
            out.write("%g\t%g\t%i\n" % (
                bp, force, num_skips))
        out.write("\n")
    out.close()

def test_slips_multi(st, vel):
    STEPS_FORCE = 10
    #STEPS_VELOCITIES = 30
    force1 = 1.5
    forces = numpy.linspace(0.01, 0.1, STEPS_FORCE)
    #velocities = numpy.linspace(0.01, 2.0, STEPS_VELOCITIES)
    filename = "multi-slips-%i-%.3f.txt" % (ARTIFASTRING_SAMPLE_RATE, vel)
    out = open(filename, 'w')
    for i, force in enumerate(forces):
        for j, bp in enumerate(positions):
        #for j, vel in enumerate(velocities):
            basename = "%s-s%i-p%.3f-f%.3f-v%.3f" % (
                "%s/bow" % DIRNAME, st, bp, force, vel)
            fp = 0
            num_skips = note_multi(st, fp, bp, force1, force, vel, basename)
            out.write("%g\t%g\t%i\n" % (
                bp, force, num_skips))
        out.write("\n")
    out.close()


def handle_file(queue, i, j, basename, f0):
    results = analyze_file(st, basename, f0)
    queue.put( (i, j, results) )

def process_string_velocity(st, f0, vel):
    ### make files
    pool = multiprocessing.Pool(processes=NUM_PROCESSES)
    for i, force in enumerate(forces):
        for j, bp in enumerate(positions):
            basename = "%s-s%i-p%.3f-f%.3f-v%.3f" % (
                "%s/bow" % DIRNAME, st, bp, force, vel)
            fp = 0
            if not EXAMINE_ONLY:
                if DISABLE_MULTI:
                    note(st, fp, bp, force, vel, basename)
                else:
                    pool.apply_async(note, args=(
                        st, fp, bp, force, vel, basename))
    pool.close()
    pool.join()

    ### analyze files
        
    pool = multiprocessing.Pool(processes=NUM_PROCESSES)
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    grid = numpy.zeros( (len(forces), len(positions), 3))
    for i, force in enumerate(forces):
        for j, bp in enumerate(positions):
            basename = "%s-s%i-p%.3f-f%.3f-v%.3f" % (
                "%s/bow" % DIRNAME, st, bp, force, vel)
            #print basename
            if DISABLE_MULTI:
                handle_file(queue, i, j, basename, f0)
            else:
                pool.apply_async(handle_file, args=(
                    queue, i, j, basename, f0))
    pool.close()
    pool.join()

    while not queue.empty():
        i, j, results = queue.get()
        for k in range(3):
            if k != k:
                grid[i][j][k] = 1.0
            else:
                grid[i][j][k] = results[k]

    
    out = open('%s/grid-%i-s%i-v%.3f.txt' % (DIRNAME, fs, st, vel), 'w')
    for i, force in enumerate(forces):
        for j, bp in enumerate(positions):
            out.write("%g\t%g\t%g\t%g\t%g\n" % (force, bp,
                grid[i][j][0], grid[i][j][1], grid[i][j][2]))
        out.write("\n")
    out.close()

    #sfm_narrow_sum = 0.0
    #for i, force in enumerate(forces):
    #    for j, bp in enumerate(positions):
    #        sfm_narrow_sum += grid[i][j][1]
    #out = open('%s/quality-%i-s%i-v%.3f.txt' % (DIRNAME, fs, st, vel), 'w')
    #out.write("%g\n" % sfm_narrow_sum)
    #out.close()


#test_slips(3, 0.5)
test_slips_multi(0, 0.5)
exit(1)

#print analyze_file(0, "22050/bow-s0-p0.152-f0.231-v0.100", 196)
#print analyze_file(0, "22050/bow-s0-p0.152-f0.894-v0.100", 196)
#print analyze_file(0, "22050/bow-s0-p0.152-f2.000-v0.100", 196)
#print analyze_file(0, "66150/bow-s0-p0.143-f0.890-v0.100", 196)
#print analyze_file(0, "22050/bow-s0-p0.143-f0.894-v0.100", 196)
#print analyze_file(0, "22050/bow-s0-p0.143-f0.894-v0.400", 196)
#exit(1)

inst_text = 'violin'
#STRINGS = [ (3, 'e'), (2, 'a'), (1,'d'), (0, 'g') ]
STRINGS = [ (3, 'e') ]
#STRINGS = [ (0, 'g') ]
for st, st_text in STRINGS:
    print "Processing %s %s" % (inst_text, st_text)
    expected_freq = expected_frequencies.FREQS[inst_text][st_text]
    highest_freq = 41*expected_freq
    if highest_freq < artifastring_instrument.ARTIFASTRING_INSTRUMENT_SAMPLE_RATE/2:
        process_string_velocity(st, expected_freq, 0.10)
        process_string_velocity(st, expected_freq, 0.40)
    else:
        print "Skipping %s string %.1f Hz" % (st_text, highest_freq)

#st_text = 'g'
#st = 0
#expected_freq = expected_frequencies.FREQS[inst_text][st_text]
#process_string_velocity(st, expected_freq, 0.10)


#process_string_velocity(st, expected_freq, 0.40)
#process_string_velocity(st, 0.10)

#analyze_file(3, "66150/bow-s3-p0.155-f0.452-v0.400", 3000)
#analyze_file(3, "66150/bow-s3-p0.167-f2.000-v0.400", 3000)
#analyze_file(3, "441000/bow-s3-p0.150-f0.010-v0.100", 660)
#analyze_file(3, "441000/bow-s3-p0.167-f2.000-v0.100", 3000)

#pylab.legend()
#pylab.show()

