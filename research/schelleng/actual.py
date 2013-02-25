#1/usr/bin/env python

import sys
sys.path.append('../shared')
import dsp

import scipy.signal
import scipy.fftpack

import os.path

import defs

#ADSR_A_SECONDS = 0.050
#ADSR_S_SECONDS = 0.200

ADSR_A_SECONDS = 0.500
ADSR_S_SECONDS = 0.500
#ADSR_A_SECONDS = 1.0
#ADSR_S_SECONDS = 1.0

### for accel attacks?
ADSR_A_SECONDS = 0.2
#ADSR_D_SECONDS = 0.05
ADSR_S_SECONDS = 0.2

NUM_FEATURES = 8



import artifastring_instrument
ARTIFASTRING_SAMPLE_RATE = artifastring_instrument.ARTIFASTRING_INSTRUMENT_SAMPLE_RATE
HAPTIC_SAMPLE_RATE = artifastring_instrument.HAPTIC_SAMPLE_RATE
HAPTIC_DOWNSAMPLE_FACTOR = 2
HOPSIZE = artifastring_instrument.NORMAL_BUFFER_SIZE

import numpy
import scipy.io.wavfile

import marsyas_util


def notes(shared, actions, basename, num_notes):
    filenames = []
    for i in range(num_notes):
        filename = note(shared[0], actions, basename+"-%i"%i)
        filenames.append(filename)
    return (filenames, actions)

def note(inst, actions, basename):
    ### MUST start with this!
    inst.reset()

    st = actions['st']
    xb = actions['xb']
    fb = actions['fb']
    fb2 = actions['fb2']
    vb = actions['vb']
    ba = actions['ba']
    fp = actions['fp']
    inst.finger(st, fp)
    inst.bow(st, xb, fb, vb)
    #inst.bow_accel(st, xb, fb, vb, ba)
    #print "%.3f\t%.3f" % (xb, fb)
    if fb2:
        #if fb2 > fb:
        #    return basename + ".wav"
        fb2 = fb * fb2
    
    samples = ADSR_A_SECONDS * ARTIFASTRING_SAMPLE_RATE
    ### let string settle
    if True:
        if fb2 is not None:
            init_samples = 0.05
            samples = init_samples * ARTIFASTRING_SAMPLE_RATE
            #buft = numpy.empty(HOPSIZE, dtype=numpy.int16)
            #forcest = numpy.empty(HOPSIZE/HAPTIC_DOWNSAMPLE_FACTOR,
            #    dtype=numpy.int16)
            #num_hops = int(samples / HOPSIZE)
            #force_adjust = (fb - fb2) / float(num_hops)
            ##print '----', fb, fb2
            #for i in range(num_hops):
            #    #print fb, samples
            #    inst.wait_samples_forces_python(buft, forcest)
            #    samples -= HOPSIZE
            #    fb -= force_adjust
            #    inst.bow(st, xb, fb, vb)
            #print fb2, samples
            buft = numpy.empty(samples, dtype=numpy.int16)
            forcest = numpy.empty(samples/HAPTIC_DOWNSAMPLE_FACTOR,
                dtype=numpy.int16)
            #inst.bow(st, xb, fb, vb)
            inst.wait_samples_forces_python(buft, forcest)
            inst.bow(st, xb, fb2, vb)


            samples = (ADSR_A_SECONDS-init_samples) * ARTIFASTRING_SAMPLE_RATE
            buft = numpy.empty(samples, dtype=numpy.int16)
            forcest = numpy.empty(samples/HAPTIC_DOWNSAMPLE_FACTOR,
                dtype=numpy.int16)
            inst.wait_samples_forces_python(buft, forcest)
        else:
            buft = numpy.empty(samples, dtype=numpy.int16)
            forcest = numpy.empty(samples/HAPTIC_DOWNSAMPLE_FACTOR,
                dtype=numpy.int16)
            inst.wait_samples_forces_python(buft, forcest)

    #samples = ADSR_D_SECONDS * ARTIFASTRING_SAMPLE_RATE
    #inst.bow_accel(st, xb, fb*0.3, vb, ba)
    ### let string settle
    #if True:
    if False:
        buft = numpy.empty(samples, dtype=numpy.int16)
        forcest = numpy.empty(samples/HAPTIC_DOWNSAMPLE_FACTOR,
            dtype=numpy.int16)
        inst.wait_samples_forces_python(buft, forcest)

    samples = ADSR_S_SECONDS * ARTIFASTRING_SAMPLE_RATE
    ### part we care about
    if True:
        buf = numpy.empty(samples, dtype=numpy.int16)
        forces = numpy.empty(samples/HAPTIC_DOWNSAMPLE_FACTOR,
            dtype=numpy.int16)
        inst.wait_samples_forces_python(buf, forces)

    scipy.io.wavfile.write(basename+".wav",
        ARTIFASTRING_SAMPLE_RATE, buf)
    return basename + ".wav"




def make_net(expected_f0):
    spec = ["Series/series", [
          "SoundFileSource/src",
          "ShiftInput/si",
          "Windowing/window",
          "Spectrum/spec",
          "PowerSpectrum/ps",
          "RemoveObservations/ro",
          ["Fanout/fanout", [
            "HarmonicStrength/hsRel",
            "HarmonicStrength/hsAbs",
            "Centroid/centroid",
            "SpectralFlatnessAllBands/sfab",
          ]],
        ]]
    net = marsyas_util.create(spec)
    spect_cutoff = 0.34

    #net.updControl("mrs_natural/inSamples", 2048)
    #net.updControl("ShiftInput/si/mrs_natural/winSize", 4096)
    net.updControl("mrs_natural/inSamples", 4096)
    net.updControl("ShiftInput/si/mrs_natural/winSize", 8192)

    net.updControl("RemoveObservations/ro/mrs_real/highCutoff", spect_cutoff)

    net.updControl("Fanout/fanout/HarmonicStrength/hsRel/mrs_natural/harmonicsSize", 3)
    net.updControl("Fanout/fanout/HarmonicStrength/hsRel/mrs_real/harmonicsWidth",
        0.001)
    # magnitude / energy_rms
    net.updControl("Fanout/fanout/HarmonicStrength/hsRel/mrs_natural/type", 0)

    net.updControl("Fanout/fanout/HarmonicStrength/hsRel/mrs_real/base_frequency",
        float(expected_f0))
        #float(expected_f0)*spect_cutoff)
    net.updControl("Fanout/fanout/HarmonicStrength/hsRel/mrs_real/inharmonicity_B", 4e-5)

    net.updControl("Fanout/fanout/HarmonicStrength/hsAbs/mrs_natural/harmonicsSize", 3)
    net.updControl("Fanout/fanout/HarmonicStrength/hsAbs/mrs_real/harmonicsWidth",
        0.001)
    # log(magnitude)
    net.updControl("Fanout/fanout/HarmonicStrength/hsAbs/mrs_natural/type", 2)

    net.updControl("Fanout/fanout/HarmonicStrength/hsAbs/mrs_real/base_frequency",
        float(expected_f0))
        #float(expected_f0)*spect_cutoff)
    net.updControl("Fanout/fanout/HarmonicStrength/hsAbs/mrs_real/inharmonicity_B", 4e-5)

    notempty = net.getControl("SoundFileSource/src/mrs_bool/hasData")
    return net, notempty

def make_shared(inst_type, inst_num, expected_f0):
    inst = artifastring_instrument.ArtifastringInstrument(
            inst_type, inst_num)
    net, notempty = make_net(expected_f0)
    return inst, net, notempty


#def bin2hertz(bin_number, sample_rate, N):
#    return bin_number * (sample_rate/2) / float(N/2+1)
#
#def get_freqs_fft(signal, sample_rate):
#    #signal = zero_pad_to_next_power_two(signal)
#    fft = scipy.fftpack.fft(signal)
#    fft_abs = abs(fft[:len(signal)/2+1])
#    fft_normalized = fft_abs / (len(signal)/2)
#    #fft_db = stft.amplitude2db(fft_normalized)
#    #fft_db = fft_normalized
#    freqs = [ bin2hertz(i, sample_rate, len(signal))
#        for i in range(len(fft_normalized)) ]
#    return freqs, fft_normalized
#
#def get_freqs_db(signal, sample_rate):
#    freqs, fft_abs = get_freqs_fft(signal, sample_rate)
#    fft_db = 20*scipy.log10(fft_abs)
#    return freqs, fft_db

def analyze_file(net, notempty, filename):
    if not os.path.exists(filename):
        return None
    net.updControl("SoundFileSource/src/mrs_string/filename", filename)
    vals = []
    for i in range(NUM_FEATURES):
        vals.append([])
    while notempty.to_bool():
        net.tick()
        output = net.getControl("mrs_realvec/processedData").to_realvec()
        for i in range(NUM_FEATURES):
            vals[i].append(output[i])
    for i in range(NUM_FEATURES):
        vals[i] = vals[i][1:-1]

    #sample_rate, data = scipy.io.wavfile.read(filename)
    #freqs, fft_db = get_freqs_db(data, sample_rate)
    #one = dsp.spectral_flatness_limited(data, 20, 5000, sample_rate)

    return vals

def analyze_files(shared, filenames):
    net = shared[1]
    notempty = shared[2]
    vals = []
    means = []
    stds = []
    #sfms = []
    for i in range(NUM_FEATURES):
        vals.append([])
        means.append(0)
        stds.append(0)
    for filename in filenames:
        #val, sfm = analyze_file(net, notempty, filename)
        val = analyze_file(net, notempty, filename)
        if val is None:
            continue
        for i in range(NUM_FEATURES):
            vals[i].extend( val[i] )
        #sfms.append(sfm)
    for i in range(NUM_FEATURES):
        means[i] = numpy.mean(vals[i])
        stds[i] = numpy.std(vals[i])
    #return means, stds, numpy.mean(sfms), numpy.std(sfms)
    return means, stds


def process(shared, actions, basename, num_notes):
    filenames, actions = notes(shared, actions, basename, num_notes)
    #means, stds, sfmm, sfmstd = analyze_files(shared, filenames)
    means, stds = analyze_files(shared, filenames)
    #return (filenames, actions, means, stds, sfmm, sfmstd)
    return (filenames, actions, means, stds)


