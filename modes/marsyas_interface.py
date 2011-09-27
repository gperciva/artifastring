#!/usr/bin/evn python
import marsyas

NUM_HARMONICS = 40
HOPSIZE = 256
WINDOWSIZE = 2048

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


def get_harmonics(wav_filename, base_frequency):
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
    net.updControl("HarmonicStrength/harms/mrs_real/harmonicsWidth", 0.00)
    net.updControl("HarmonicStrength/harms/mrs_real/base_frequency", base_frequency)
    net.updControl("HarmonicStrength/harms/mrs_natural/type", 1)
    
    harmonics = []
    for i in range(num_harmonics):
        harmonics.append([])

    count = 0
    while net.getControl("SoundFileSource/src/mrs_bool/hasData").to_bool():
        # update time
        net.tick()
        count += 1
        # get data
        output = net.getControl("mrs_realvec/processedData").to_realvec()
        # omit beginning (inaccurate due to ShiftInput "filling up"
        if count >= (WINDOWSIZE / HOPSIZE):
            for i in range(num_harmonics):
                harmonics[i].append(output[i])

    return harmonics, HOPSIZE/sample_rate
  

