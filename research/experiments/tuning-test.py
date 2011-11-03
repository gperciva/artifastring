#!/usr/bin/env python

import math

import artifastring_instrument
import monowav

import scipy
import aubio.aubiowrapper

windowsize = 2048
HOPSIZE=512
pitch_obj = aubio.aubiowrapper.new_aubio_pitchdetection(
    windowsize, HOPSIZE, 1, 44100,
    aubio.aubiowrapper.aubio_pitch_yinfft,
    aubio.aubiowrapper.aubio_pitchm_freq
    )
fvec = aubio.aubiowrapper.new_fvec(HOPSIZE, 1)




violin = artifastring_instrument.ArtifastringInstrument()
#wavfile = monowav.MonoWav("artifastring-test.wav")
tuningfile = open('data-tuning.txt', 'w')

FS = 44100.0
hundred_ms = int(0.1 * FS)
hopsize = 512


pc = violin.get_physical_constants(2)
orig_tension = pc.T / 2.0
pc.T = orig_tension
violin.set_physical_constants(2, pc)

bp = 0.1
bf = 1.0
bv = 0.4
violin.bow(2, bp, bf, bv)
out = monowav.shortArray(HOPSIZE)

seconds = 0.0
def wait_pitch():
    violin.wait_samples(out, hopsize)
    global seconds
    seconds += hopsize/44100.0
    for i in xrange(HOPSIZE):
        aubio.aubiowrapper.fvec_write_sample(
            fvec,
            out[i],
            0,
            i)
    pitch = aubio.aubiowrapper.aubio_pitchdetection(
        pitch_obj, fvec)
    return pitch

for i in range(87):
    _ = wait_pitch()

i = 0
while True:
    if i % 5 == 0:
        pc.T = orig_tension + 0.1*i
        if pc.T > 4*orig_tension:
            break
    i += 1
    violin.set_physical_constants(2, pc)
    pitch = wait_pitch()
    tuningfile.write("%.8g\t%.8g\t%.8g\n" % (seconds, pc.T, pitch))
tuningfile.close()



