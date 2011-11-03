#!/usr/bin/env python
import math

import os
import os.path
import sys
sys.path.append("swig/python/")
sys.path.append("lib/")
import marsyas

DIRNAME = "spectrum/"
import numpy

NUM_HARMONICS = 30
HOPSIZE = 512
    # needed for cello C string: 4096
    # sr: 48000
    # FFT bin width: sr / (windowsize/2) = 23.4
    # looking for modes of 65.0 Hz
    # and we want some "spikiness" to the spectrum.  :)
WINDOWSIZE = 4096

END_COUNT = 0

# create a MarSystem from a recursive list specification
def create(net):
    msm = marsyas.MarSystemManager()
    composite = msm.create("Gain/id") # will be overwritten
    if (len(net) == 2):
        composite = msm.create(net[0])
        msyslist = map(create,net[1])
        msyslist = map(composite.addMarSystem,msyslist)
    else:
        composite = msm.create(net)
    return composite

# we're not using this function, but I've left it here for historical 
def get_B():
    # hard-code A string for now
    T = 49.0
    l = 0.325
    d = 0.52e-3
    E = 4.0e9
    Q = E
    B = (math.pi**3) * Q * (d**4) / (64.0 * (l**2) * T)
    return B


def get_harmonics(wav_filename, base_frequency, B=0.0):
    dest_dir = os.path.join(DIRNAME,
        os.path.basename(wav_filename.replace(".wav", "")))
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    global NUM_HARMONICS
    num_harmonics = NUM_HARMONICS
    # Create top-level patch
    net = create(["Series/extract_network",
            ["SoundFileSource/src",
             "ShiftInput/shift",
             "Windowing/win",
             "Spectrum/spec",
             "PowerSpectrum/pspec",
             "HarmonicStrength/harms",
        ]])
    # setup processing
    net.updControl("SoundFileSource/src/mrs_string/filename", wav_filename)
    sample_rate = net.getControl("SoundFileSource/src/mrs_real/osrate").to_real()
    harmonics_maximum = int( (sample_rate/2)/base_frequency ) - 3
    if num_harmonics > harmonics_maximum:
        # reduce for nyquist
        num_harmonics = harmonics_maximum
    net.updControl("Windowing/win/mrs_string/type", "Hanning")
    net.updControl("mrs_natural/inSamples", HOPSIZE)
    net.updControl("ShiftInput/shift/mrs_natural/winSize", WINDOWSIZE)
    
    net.updControl("HarmonicStrength/harms/mrs_natural/harmonicsSize", num_harmonics)
    net.updControl("HarmonicStrength/harms/mrs_real/harmonicsWidth",
        0.001)
    net.updControl("HarmonicStrength/harms/mrs_real/base_frequency", base_frequency)
    net.updControl("HarmonicStrength/harms/mrs_natural/type", 1)
    #B = get_B()
    net.updControl("HarmonicStrength/harms/mrs_real/inharmonicity_B", B)
    
    harmonics = []
    for i in range(num_harmonics):
        harmonics.append([])

    count = 0

    while net.getControl("SoundFileSource/src/mrs_bool/hasData").to_bool():
        # update time
        net.tick()
        count += 1
        if END_COUNT > 0 and count > END_COUNT:
            return harmonics, HOPSIZE/sample_rate
        # get data
        output = net.getControl("mrs_realvec/processedData").to_realvec()

        # omit beginning (inaccurate due to ShiftInput "filling up"
        if count >= (WINDOWSIZE / HOPSIZE):
            binfreq = float(sample_rate) / WINDOWSIZE
            freq_cutoff = (num_harmonics+5) * base_frequency
            fftbin_cutoff = freq_cutoff / binfreq
            fft = net.getControl("PowerSpectrum/pspec/mrs_realvec/processedData").to_realvec()
            fftbin_cutoff = int(min(fftbin_cutoff, fft.getRows()))

            out = open(os.path.join(dest_dir,'spectrum-%05i.txt' % count), 'w')
            for i in range(fftbin_cutoff):
                out.write('%g\t%g\n' % (i*binfreq, fft[i]))
            out.close()

            harms = net.getControl("mrs_realvec/processedData").to_realvec()
            harms_size = min(num_harmonics+5, output.getRows()) 
            out = open(
                os.path.join(dest_dir,'harms-%05i.txt' % count), 'w')
            for i in range(len(harms)):
                n = i+1
                freq = n *base_frequency * math.sqrt(1.0 + B*n**2)
                out.write('%g\t%g\n' % (freq, harms[i]))
            out.close()

            for i in range(num_harmonics):
                harmonics[i].append(output[i])

    return harmonics, HOPSIZE/sample_rate

if __name__ == "__main__":
    #get_harmonics("pluck.wav", 196.0)
    get_harmonics(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]))
    #get_harmonics("split-wav/violin-e-01.wav", 660.0)
    #get_harmonics("split-wav/violin-a-01.wav", 440.0)
    #get_harmonics("split-wav/cello-a-01.wav", 220.0)
    #get_harmonics("split-wav/cello-c-01.wav", 65.0)

