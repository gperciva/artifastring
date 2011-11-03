#!/usr/bin/env python

import sys

sys.path.append('../../build/swig')
sys.path.append('../../build/.libs')

import pickle

import artifastring_instrument
import monowav

import os.path
import time
import math
import numpy
import scipy.io.wavfile
import scipy.fftpack
sys.path.append('../mode-detect/')

import pylab

def test_ns():
    return [ i for i in range(5, 101, 5) ]

def test_N(violin, N, inst, st):
    violin.reset()
    pc = violin.get_physical_constants(st)
    pc.N = N
    violin.set_physical_constants(st, pc)
    seconds = 5.0
    num_samples = int(seconds*44100.0)
    violin.pluck(st, 0.47, 4.0)
    wavfile = monowav.MonoWav(
        str("out/pluck-modes-%i-%i-%i.wav" % (inst, st, N)))
    buf = wavfile.request_fill(num_samples)
    artifastring_instrument.wait_samples_c(violin, buf, num_samples)

def get_modes(inst_text, st_text):
    consts_basename = "%s-%s-%s" % (
        inst_text, st_text, 'I')
    decay_pickle_filename = os.path.join(
        "../mode-detect/out/", consts_basename + ".mode-decays.pickle")
    pickle_file = open(decay_pickle_filename, 'rb')
    decays = pickle.load(pickle_file)
    pickle_file.close()
    return decays


def construct_plucks(violin, inst, st):
    inst_text, st_text = get_st_text(inst, st)
    decays = get_modes(inst_text, st_text)
    pc = violin.get_physical_constants(st)
    for i in range(artifastring_instrument.MODAL_DECAY_MODES):
        artifastring_instrument.floatArray_setitem(pc.modes, i, decays[i])
    violin.set_physical_constants(st, pc)

    out = open("out/times-%i-%i.txt" % (inst, st), 'w')
    out.write("#modes\tseconds\n")
    for n in test_ns():
        before = time.clock()
        test_N(violin, N=n, inst=inst, st=st)
        after = time.clock()
        out.write( "%i\t%g\n" % (n, after-before))
    out.close()

def zero_pad_to_next_power_two(x):
    len_power_two = int(pow(2, math.ceil(math.log(len(x),2))))
    x = numpy.append(x, numpy.zeros(len_power_two - len(x)))
    return x

def bin2hertz(bin_number, sample_rate, N):
    return bin_number * sample_rate / float(N)

def get_freqs_fft(signal, sample_rate):
    signal = zero_pad_to_next_power_two(signal)
    fft = scipy.fftpack.fft(signal / (2**15))
    fft_abs = abs(fft[:len(signal)/2])
    fft_normalized = fft_abs / (len(signal)/2)
    #fft_db = stft.amplitude2db(fft_normalized)
    #fft_db = fft_normalized
    freqs = [ bin2hertz(i, sample_rate, len(signal))
        for i in range(len(fft_normalized)) ]
    return freqs, fft_normalized

def get_aligned_samples(filename1, filename2):
    sample_rate, samples1 = scipy.io.wavfile.read(filename1)
    sample_rate, samples2 = scipy.io.wavfile.read(filename2)
    samples1 = numpy.array(samples1, dtype=numpy.float64) / float(2**15)
    samples2 = numpy.array(samples2, dtype=numpy.float64) / float(2**15)
    #pylab.plot(samples1)
    #pylab.show()
    max1index = numpy.argmax(samples1)
    max2index = numpy.argmax(samples2)
    #samples1 = samples1[max1index:]
    #samples2 = samples2[max2index:]
    #minlen = min(len(samples1), len(samples2))
    #samples1 = samples1[:minlen]
    #samples2 = samples2[:minlen]
    shift_index = max2index - max1index
    #print max1index, max2index, shift_index
    if shift_index > 0:
        samples1 = samples1[:-shift_index]
        samples2 = samples2[shift_index:]
    elif shift_index < 0:
        samples1 = samples1[-shift_index:]
        samples2 = samples2[:shift_index]
    return sample_rate, samples1, samples2

def get_residuals_shifted(samples1, samples2, n):
    if n > 0:
        samples1 = samples1[:-n]
        samples2 = samples2[n:]
    elif n < 0:
        samples1 = samples1[-n:]
        samples2 = samples2[:n]
    delta = samples2 - samples1 
    #delta = delta[2000:4000]
    #pylab.plot(delta)
    #pylab.show()
    sumsqr = sum(delta**2)
    #print delta.dtype
    #print delta
    #print delta**2
    #print sum(delta**2)
    #print sumsqr, len(delta)
    #return
    rms = math.sqrt( sumsqr / float(len(delta)) )
    #print n, '\t', sumsqr, '\t', len(delta), '\t', rms
    #pylab.plot(samples2[2000:4000], label="2")
    #pylab.plot(samples1[2000:4000], label="1")
    #pylab.plot(delta[2000:4000])
    #pylab.plot(delta)
    #pylab.show()
    #return rms, samples1, samples2
    return rms


def construct_delta(filename1, filename2):
    num = os.path.basename(filename1).split('-')[2]
    sample_rate, samples1, samples2 = get_aligned_samples(filename1, filename2)

    rmss = []
    ns = numpy.arange(-20, 21)
    for n in ns:
        rms = get_residuals_shifted(samples1, samples2, n)
        #print n, rms
        rmss.append( rms )
    rms = sorted(rmss)[0]


    #rms, samples1, samples2 = rmss[0]
    #pylab.plot(ns, rmss)
    #pylab.show()
    #exit(1)
    delta = samples1 - samples2
    #pylab.figure()
    #pylab.plot(samples2, label=filename2)
    #pylab.plot(samples1, label=filename1)
    #pylab.plot(delta, label="residual "+num)
    freqs0, delta_fft = get_freqs_fft(delta, sample_rate)
    #pylab.figure()

    #rms = math.sqrt(sum(delta**2)/float(len(delta)))
    #print os.path.basename(filename1), '\t', rms
    #return rms
    #return

    #pylab.plot(delta)
    #pylab.plot(freqs0, delta_fft,
    #    label=os.path.basename(filename1))
    #print "%.3g\t%.3g\t%.3g\t%.3g" % (
    #    sum(delta_fft), rms, sum(delta_fft**2), sum(delta**2)
    #    )
    #pylab.show()
    return sum(delta_fft), sum(delta_fft**2), rms

    #freqs1, fft_db1 = get_freqs_fft_db(samples1, sample_rate)
    #freqs2, fft_db2 = get_freqs_fft_db(samples2, sample_rate)

    #delta = fft_db2 - fft_db1
    #pylab.plot(freqs2, fft_db2,
    #    label=os.path.basename(filename2))
    #pylab.plot(freqs1, fft_db1,
    #    label=os.path.basename(filename1))

    #pylab.figure()
    #pylab.plot(freqs1, delta,
    #    label=os.path.basename(filename1))

    #freqs, fft_db = get_freqs_fft_db(delta, sample_rate)
    #pylab.plot(freqs, fft_db,
    #    label=os.path.basename(filename1))
    #pylab.title(filename1)
    pylab.xlabel("freq bins")
    pylab.ylabel("magnitude dB")

def do_string(violin, inst, st):
    construct_plucks(violin, inst, st)

    rms_file = open("out/rmss-%i-%i.txt" % (inst, st), 'w')
    rms_file.write("#modes\trms\n")
    final_n = max(test_ns())
    for n in test_ns():
        df, dfs, rms = construct_delta(
            str("out/pluck-modes-%i-%i-%i.wav" % (inst, st, n)),
            str("out/pluck-modes-%i-%i-%i.wav" % (inst, st, final_n)))
        rms_file.write( str("%i\t%g\t%g\t%g\n" %(n, df, dfs, rms)) )
        print "%i\t%.2g\t%.2g\t%.2g" % (n, df, dfs, rms)
    rms_file.close()

def do_inst(inst):
    violin = artifastring_instrument.ArtifastringInstrument(inst)
    for st in range(4):
        do_string(violin, inst, st)

def get_st_text(inst, st):
    if inst==0:
        inst_text = 'violin'
    elif inst==1:
        inst_text = 'viola'
    elif inst==2:
        inst_text = 'cello'
    if inst == 0:
        if st==0:
            st_text = 'g'
        elif st==1:
            st_text = 'd'
        elif st==2:
            st_text = 'a'
        elif st==3:
            st_text = 'e'
    elif inst==1 or inst==2:
        if st==0:
            st_text = 'c'
        elif st==1:
            st_text = 'g'
        elif st==2:
            st_text = 'd'
        elif st==3:
            st_text = 'a'
    return inst_text, st_text

def main():
    do_inst(0)
    do_inst(2)


main()


