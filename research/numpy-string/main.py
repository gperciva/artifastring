#!/usr/bin/env python

### this stuff ***must*** come before anything else!
import sys
THESIS = ' '.join(sys.argv[1:])

if len(THESIS) == 0:
    print "need THESIS type"
    exit(1)


import numpy
import scipy.io.wavfile

import sys
import defs
from defs import *
import numpy_string
import os.path

HACK_INVESTIGATE_UNIT = False


if defs.THESIS is not "":
    filename = defs.THESIS.replace(" ", "-")
else:
    filename = "string-out"
filename = os.path.join(numpy_string.DATA_DIR, filename)


num_samples = int(SECONDS * FS + 0.1) # I **HATE** floating point

# used in 2-pluck case
pull_low     = num_samples/2 + 0.00*FS
pull_high    = num_samples/2 + numpy_string.PLUCK_SAMPLES - 0.00*FS
release_low  = num_samples/2 + numpy_string.PLUCK_SAMPLES + 0.01*FS
release_high = num_samples - 0.00*FS


def play():
    vln = numpy_string.Violin(num_samples)
    outs = numpy.empty(num_samples)
    if PLAY_MULTIPLE:
        if TEST_BOW:
            #vln.finger(0.5, K_finger)
            vln.finger(1.0 - 0.25, K_finger)
            #vln.bow(0.12, 1.0, 0.4)
            vln.bow(0.12, 0.8, 0.4)
            for i in range(num_samples/4):
                outs[i] = vln.tick()
            vln.bow(0.12, 0.8, -0.4)
            for i in range(num_samples/4):
                outs[i+num_samples/4] = vln.tick()
            vln.bow(0.12, 0.0, 0.4)
            for i in range(num_samples/4):
                outs[i+2*(num_samples/4)] = vln.tick()
            vln.bow(0.12, 0.8, 0.4)
            for i in range(num_samples/4):
                outs[i+3*(num_samples/4)] = vln.tick()
        else:
            vln.finger(defs.xf, K_finger, R_finger)
            if ONLY_TWO:
                vln.pluck(defs.xp, K_pluck, R_pluck)
                for i in range(num_samples/2):
                    outs[i] = vln.tick()

                vln.finger(defs.xf, K_finger, R_finger)
                vln.pluck(defs.xp, K_pluck, R_pluck)
                for i in range(num_samples/2):
                    outs[i+num_samples/2] = vln.tick()
            else:
                vln.pluck(defs.x0, K_pluck, R_pluck)
                for i in range(num_samples/2):
                    outs[i] = vln.tick()
            
                vln.finger(1.0 - 0.109, K_finger, R_finger)
                vln.pluck(defs.x0, K_pluck, R_pluck)
                for i in range(num_samples/5):
                    outs[i+num_samples/5] = vln.tick()
                
                vln.finger(1.0 - 1.0/4.0, K_finger, R_finger)
                vln.pluck(defs.x0, K_pluck, R_pluck)
                for i in range(num_samples/5):
                    outs[i+2*(num_samples/5)] = vln.tick()
                
                vln.finger(1.0 - 1.0/3.0, K_finger, R_finger)
                vln.pluck(defs.x0, K_pluck, R_pluck)
                for i in range(num_samples/5):
                    outs[i+3*(num_samples/5)] = vln.tick()
                
                vln.finger(1.0 - 1.0/2.0, K_finger, R_finger)
                vln.pluck(defs.x0, K_pluck, R_pluck)
                for i in range(num_samples/5):
                    outs[i+4*num_samples/5] = vln.tick()
    else:
        if TEST_BOW:
            if MAIN_TWO_BOWS:
                vln.finger(defs.xf, K_finger, R_finger)
                vln.bow(defs.bow_position, defs.bow_force_first, defs.bow_velocity)
                samples_first = int(SECONDS_FIRST * FS)
                for i in range(samples_first):
                    val = vln.tick()
                    outs[i] = val
                vln.bow(defs.bow_position, defs.bow_force_second,
                    defs.bow_velocity_second)
                samples_second = int(SECONDS_SECOND * FS)
                for i in range(samples_first, samples_second+samples_first):
                    outs[i] = vln.tick()
            else:
                vln.finger(defs.xf, K_finger, R_finger)
                vln.bow(defs.bow_position, defs.bow_force, defs.bow_velocity)

                for i in range(num_samples):
                    val = vln.tick()
                    if val is None:
                        print "breaking on sample", i
                        #outs /= max(outs)
                        break
                    else:
                        outs[i] = val
        else:
            #vln.finger(0.5, K_finger)
            #vln.finger(1.0 - 0.47, K_finger)
    
            #vln.finger(1.0 - 0.25, K_finger)
            vln.finger(defs.xf, K_finger, R_finger)
            vln.pluck(defs.xp, K_pluck, R_pluck)
            for i in range(num_samples):
                val = vln.tick()
                if val is None:
                    #outs /= max(outs)
                    break
                else:
                    outs[i] = val
    
    
    #outs /= max(outs)
    if not NO_AUDIO:
        scipy.io.wavfile.write(filename+".wav", FS,
            #numpy.array(outs*(2**14-1), dtype=numpy.int16))
            numpy.array(SCALE_WAV_OUTPUT*outs*2**15, dtype=numpy.int16))
    if defs.WRITE_PLUCK_PULL_RELEASE:
        pulling = outs[ pull_low : pull_high]
        release = outs[ release_low : release_high]
        scipy.io.wavfile.write("%s-pulling.wav" % filename, FS,
            numpy.array(SCALE_WAV_OUTPUT*pulling*2**15, dtype=numpy.int16))
        scipy.io.wavfile.write("%s-release.wav" % filename, FS,
            numpy.array(SCALE_WAV_OUTPUT*release*2**15, dtype=numpy.int16))

    return vln

def peak_F1(dts, dataorig, wn):
    datafft = dataorig[PLOT_SAMPLE_MIN:]
    fft_N = 4*len(datafft)
    fft = scipy.fftpack.fft(datafft, fft_N)[:len(datafft)/2]
    freqs = numpy.linspace(0, FS/2, fft_N/2)

    peak_bin = fft.argmax()
    F1_freq = freqs[peak_bin]

    mode1_f = wn[1] / (2*numpy.pi)
    ratio = F1_freq / mode1_f
    #print "F1_freq:\t", F1_freq
    #print "ratio:\t", ratio
    return F1_freq, ratio

if not HACK_INVESTIGATE_UNIT: 
    vln = play()
    vln.plotting.main_filename = filename
    if PLOTS:
        vln.plotting.plot()
    dts, F1s = vln.plotting.get_dts_F1()
    peak, ratio = peak_F1(dts, F1s, numpy_string.wn)
    fn = numpy_string.wn / (2*numpy.pi)
    #print "max delta v0h: %.3f" % (vln.debug_max_dv0h)
    #print "modes hz:\t", fn[0], fn[1], fn[2]
    #print "f1 hz:\t", peak
    #print "ratio:\t", ratio
else:
    out = open("ratios.txt", "w")
    out.write("T\tL\tpl\tratio\n")
    #print "T\tL\tpl\tratio\twn0\twn1\twn2"

    def try_pluck(T, L, pl, out):
        numpy_string.T = T
        numpy_string.L = L
        numpy_string.pl = pl
        numpy_string.set_constants()
        vln = play()
        dts, F1s = vln.plotting.get_dts_F1()
        ratio = peak_F1(dts, F1s, numpy_string.wn)
        out.write("%g\t%g\t%g\t%g\n" % (
        #print "%g\t%g\t%g\t%g\t%g\t%g\t%g" % (
            T, L, pl, ratio,
            #numpy_string.wn[0], numpy_string.wn[1], numpy_string.wn[2],
            ))

    samples = 2
    total = samples**3
    done = 0
    for T in numpy.linspace(1, 1000, samples):
        for L in numpy.linspace(0.1, 10.0, samples):
            for pl in numpy.linspace(1e-4, 1e-3, samples):
                try_pluck(T, L, pl, out)
                done += 1
                print "completed %i/%i" % (done, total)
    out.close()

