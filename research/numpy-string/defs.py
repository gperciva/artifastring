#!/usr/bin/env python

""" Definitions to control the simulation and output """

### this stuff ***must*** come before anything else!
import sys
THESIS = ' '.join(sys.argv[1:])

if len(THESIS) == 0:
    print "need THESIS type"
    exit(1)


#THESIS = "pluck begin release"
#THESIS = "pluck decay open"

#THESIS = "pluck decay first"
#THESIS = "pluck decay two plucks undamped"
#THESIS = "pluck decay two plucks damped"

#THESIS = "pluck open one"
#THESIS = "pluck open two"

#THESIS = "pluck total forces two"
#THESIS = "pluck total forces three"


#THESIS = "finger freqs triple"
#THESIS = "finger freqs double"
#THESIS = "finger freqs single"

#THESIS = "finger beating single"
#THESIS = "finger beating double"
#THESIS = "finger beating triple"
#THESIS = "finger unit string"

#THESIS = "multi pluck two"
#THESIS = "multi pluck three"


#THESIS = "bow skipping 48000"
#THESIS = "bow skipping 66150"

#THESIS = "bow unstable"

#THESIS = "cello c 16"
#THESIS = "cello c 24"
#THESIS = "cello c 24 finger"
#THESIS = "cello c 32"
#THESIS = "cello c 32 finger"
#THESIS = "cello c 40"
#THESIS = "cello c 40 finger"
#THESIS = "cello c 64"
#THESIS = "cello c 64 finger"

#THESIS = "violin e 16"
#THESIS = "violin e 24"
#THESIS = "violin e 32"
#THESIS = "violin e 40"
#THESIS = "violin e 24 finger"
#THESIS = "violin e 32 finger"
#THESIS = "violin e 40 finger"
#THESIS = "violin e 64 finger"

#THESIS = ""

FS = 44100

### plotting
#PLOTS = True
PLOTS = False

N = 40

SECONDS = 1.6 # 0.100 for pluck, plus over 65536 samples
xp = 0.2
xf = 0.0

Wp = 0.012
Wf = 0.01
K_finger = 1e5
K_pluck = 1e4
#R_finger = 1e1
R_finger = 30
R_pluck = 1

#A_noise = 0.0
A_noise = 0.02


MAIN_TWO_BOWS = False
WRITE_X3N_Y3N = False
INFINITE_SPRING = False
SINGLE_FINGER_FORCE = False
DOUBLE_FINGER_FORCE = False
SINGLE_PLUCK_DOUBLE_FINGER_FORCE = False
SINGLE_PLUCK_FORCE = False
FOUR_PLUCK_FORCES = False

PLOT_FINAL_OUTPUT = False
PLOT_FINAL_OUTPUT_TIME = False
PLOT_FORCES = False
PLOT_MODE_DISPLACEMENTS = False
PLOT_DISPLACEMENTS = False
PLOT_DISP_BOW = False
PLOT_BOW_STATES = False
WRITE_DISPLACEMENTS = False
WRITE_DISPLACEMENTS_EXTRA = False
WRITE_PLUCK_PULL_RELEASE = False

DISPLACEMENTS_ALONG_STRING = 200
PLOT_MIN_FREQ = 0
PLOT_MAX_FREQ = 2000
PLOT_SAMPLE_MIN = 0
PLOT_SAMPLE_MAX = 0
#PLOT_SAMPLE_MIN = int(FS*0.1)
#PLOT_SAMPLE_MAX = int(FS*0.1546)
DISPLACEMENTS_SAMPLE_RATE = FS
PLOT_FINAL_OUTPUT_FFT_NO_WINDOW = False

PLOT_FINAL_OUTPUT_FFT = False
PLOT_FORCES_FFT = False
PLOT_HIST_BOW = False
PLOT_BOW_COMBO = False
PLOT_BOW_SLIPSTATES = False
PLOT_VELOCITY_UNDER_FINGER = False

RELEASE_FORCES_THREE = False

NO_POSITIVE_SLIPPING = False
NO_SLIPPING_SKIPS = False

PLAY_MULTIPLE = False
ONLY_TWO = False
TEST_BOW = False
NO_AUDIO = False
PLOT_EXTRA_HARMONIC_LINES_AT_QUARTERS = False

SCALE_WAV_OUTPUT = 1e-1

PLOTS_SHOW = False
#PLOTS_SHOW = True

if THESIS.startswith("pluck"):
    DOUBLE_FINGER_FORCE = True
    if "finger" in THESIS:
        xf = 1.0 - 0.109
    elif "open" in THESIS:
        xf = 1.0

    if "begin-release" in THESIS:
        WRITE_DISPLACEMENTS_EXTRA = True
        NO_AUDIO = True
    elif "forces" in THESIS:
        PLOTS = True
        PLOT_FINAL_OUTPUT = True
        PLOT_FINAL_OUTPUT_TIME = True
        PLOT_FINAL_OUTPUT_FFT = True
        PLOT_FORCES = True
        PLOT_FORCES_FFT = True
        PLOT_TIME_SAMPLE_MIN = int(FS*0.1)
        PLOT_TIME_SAMPLE_MAX = int(FS*0.125)
        PLOT_SAMPLE_MIN = int(FS*0.1)
        PLOT_SAMPLE_MAX = int(FS*1.6)
    elif "movie" in THESIS:
        NO_AUDIO = True
        PLOTS = True
        PLOT_DISPLACEMENTS = True
        WRITE_DISPLACEMENTS = True
        DISPLACEMENTS_SAMPLE_RATE = FS
        if "begin" in THESIS:
            PLOT_SAMPLE_MIN = int(FS*0.1)
            PLOT_SAMPLE_MAX = int(FS*0.1046)
            PLOT_TIME_SAMPLE_MIN = int(FS*0.1)
            PLOT_TIME_SAMPLE_MAX = int(FS*0.1046)
        if "middle" in THESIS:
            PLOT_DISPLACEMENTS = False
            WRITE_DISPLACEMENTS = True
            PLOT_SAMPLE_MIN = int(FS*1.0)
            PLOT_SAMPLE_MAX = int(FS*1.0046)
            PLOT_TIME_SAMPLE_MIN = int(FS*1.0)
            PLOT_TIME_SAMPLE_MAX = int(FS*1.0046)
        if "long" in THESIS:
            WRITE_DISPLACEMENTS = False
            PLOT_SAMPLE_MAX = int(FS*0.3)
            DISPLACEMENTS_SAMPLE_RATE = FS/5
    elif "two-plucks" in THESIS:
        SECONDS = 1.0
        PLAY_MULTIPLE = True
        ONLY_TWO = True
        if "undamped" in THESIS:
            R_pluck = 0
            R_finger = 0
        PLOTS = True
        PLOT_FINAL_OUTPUT = True
        PLOT_FINAL_OUTPUT_TIME = False
        PLOT_FINAL_OUTPUT_FFT = True
        PLOT_FINAL_OUTPUT_FFT_NO_WINDOW = True
        PLOT_TIME_SAMPLE_MIN = int(FS*0.5)
        PLOT_TIME_SAMPLE_MAX = int(FS*0.6)
        PLOT_SAMPLE_MIN = int(FS*0.5)
        PLOT_SAMPLE_MAX = int(FS*0.6)
        PLOT_MIN_FREQ = 0
        PLOT_MAX_FREQ = 5000
    elif "pluck-force" in THESIS: # no plural
        xp = 0.5
        if "one" in THESIS:
            SINGLE_PLUCK_FORCE = True

        PLOTS = True
        PLOT_FINAL_OUTPUT = True
        PLOT_FINAL_OUTPUT_TIME = False
        PLOT_FINAL_OUTPUT_FFT = True
        PLOT_TIME_SAMPLE_MIN = int(FS*0.1)
        PLOT_TIME_SAMPLE_MAX = int(FS*1.6)
        PLOT_SAMPLE_MIN = int(FS*0.1)
        PLOT_SAMPLE_MAX = int(FS*1.6)
    elif "finger-force" in THESIS: # no plural
        xf = 0.5
        if "one" in THESIS:
            SINGLE_FINGER_FORCE = True

        PLOTS = True
        PLOT_FINAL_OUTPUT = True
        PLOT_FINAL_OUTPUT_TIME = True
        PLOT_FINAL_OUTPUT_FFT = True
        PLOT_TIME_SAMPLE_MIN = int(FS*0.1)
        PLOT_TIME_SAMPLE_MAX = int(FS*1.6)
        PLOT_SAMPLE_MIN = int(FS*0.1)
        PLOT_SAMPLE_MAX = int(FS*1.6)
    elif "beating" in THESIS:
        xf = 0.5
        R_finger = 0
        N = 3
        INFINITE_SPRING = True
        SINGLE_FINGER_FORCE = True
        SINGLE_PLUCK_FORCE = True

        PLOTS = True
        PLOT_FINAL_OUTPUT = True
        PLOT_FINAL_OUTPUT_TIME = True
        PLOT_FINAL_OUTPUT_FFT = True
        PLOT_FORCES = True
        PLOT_FORCES_FFT = True
        PLOT_TIME_SAMPLE_MIN = int(FS*0.1)
        PLOT_TIME_SAMPLE_MAX = int(FS*0.12)
        PLOT_SAMPLE_MIN = int(FS*0.1)
        PLOT_SAMPLE_MAX = int(FS*1.6)
    elif "release-force" in THESIS: # no plural
        xf = 0.5
        xp = 0.2
        if "three" in THESIS:
            RELEASE_FORCES_THREE = True
            R_finger = 14
        if "four" in THESIS:
            FOUR_PLUCK_FORCES = True
        PLOTS = True
        PLOT_FINAL_OUTPUT = True
        PLOT_FINAL_OUTPUT_TIME = False
        PLOT_FINAL_OUTPUT_FFT = True
        PLOT_TIME_SAMPLE_MIN = int(FS*0.1)
        PLOT_TIME_SAMPLE_MAX = int(FS*0.12)
        PLOT_SAMPLE_MIN = int(FS*0.1)
        PLOT_SAMPLE_MAX = int(FS*1.6)
        PLOT_MAX_FREQ = 5000
        ### FIXME
        #PLOTS = True
        #PLOT_DISPLACEMENTS = True
        #WRITE_DISPLACEMENTS = True
        #DISPLACEMENTS_SAMPLE_RATE = FS/5
        #if "begin" in THESIS:
        #    PLOT_SAMPLE_MIN = int(FS*0.0)
        #    PLOT_SAMPLE_MAX = int(FS*0.1)
        #    PLOT_TIME_SAMPLE_MIN = int(FS*0.0)
        #    PLOT_TIME_SAMPLE_MAX = int(FS*0.1)


elif THESIS.startswith("bow"):
    TEST_BOW = True
    bow_position = 0.1
    bow_force = 0.5
    bow_velocity = 0.5

    if "movie" in THESIS:
        xf = 1.0 - 0.109

        bow_position = 0.1
        bow_force = 1.0
        bow_velocity = 0.5

        PLOTS = True
        PLOT_DISPLACEMENTS = True
        WRITE_DISPLACEMENTS = True
        if "begin" in THESIS:
            NO_AUDIO = True
            SECONDS = 0.02
            PLOT_TIME_SAMPLE_MIN = int(FS*0.0)
            PLOT_TIME_SAMPLE_MAX = int(FS*SECONDS)
            PLOT_SAMPLE_MIN = int(FS*0.0)
            PLOT_SAMPLE_MAX = int(FS*SECONDS)
        elif "middle" in THESIS:
            SECONDS = 1.0
            START = 0.9
            END = 0.92
            PLOT_TIME_SAMPLE_MIN = int(FS*START)
            PLOT_TIME_SAMPLE_MAX = int(FS*END)
            PLOT_SAMPLE_MIN = int(FS*START)
            PLOT_SAMPLE_MAX = int(FS*END)

    elif "harmonic" in THESIS:
        xf = 1.0 - 0.25
        bow_position = 0.1
        bow_force = 0.5
        bow_velocity = 0.3

        if "light" in THESIS:
            K_finger = 1000
            R_finger = 0.1
        PLOTS = True
        PLOT_DISPLACEMENTS = True
        PLOT_EXTRA_HARMONIC_LINES_AT_QUARTERS = True
        WRITE_DISPLACEMENTS = True
        PLOT_SAMPLE_MIN = int(FS*1.0)
        PLOT_SAMPLE_MAX = int(FS*1.01)
        PLOT_TIME_SAMPLE_MIN = int(FS*1.0)
        PLOT_TIME_SAMPLE_MAX = int(FS*1.01)
        #DISPLACEMENTS_SAMPLE_RATE = FS/5

    elif "rational" in THESIS:
        xf = 1.0 - 0.2
        bow_velocity = 0.5
        if "moderate" in THESIS:
            bow_position = 0.2
            bow_force = 0.25
        elif "weak" in THESIS:
            bow_position = 0.195
            bow_force = 0.25
        SECONDS = 2.6

        PLOTS = True
        PLOT_FINAL_OUTPUT = True
        PLOT_FINAL_OUTPUT_TIME = False
        PLOT_FINAL_OUTPUT_FFT = True
        PLOT_SAMPLE_MIN = int(FS*1.0)
        PLOT_SAMPLE_MAX = int(FS*2.6)
        PLOT_TIME_SAMPLE_MIN = int(FS*1.0)
        PLOT_TIME_SAMPLE_MAX = int(FS*1.1)
        PLOT_MAX_FREQ = 10000

    elif "frequency" in THESIS:
        xf = 0.0
        bow_velocity = 0.3
        bow_position = 0.1
        bow_force = 0.5
        SECONDS = 2.6

        if "low" in THESIS:
            # top mode: 26409 Hz
            FS = 55000
        elif "high" in THESIS:
            FS = 110000
        else:
            FS = 66150

        PLOTS = True
        PLOT_FINAL_OUTPUT = True
        PLOT_FINAL_OUTPUT_TIME = False
        PLOT_FINAL_OUTPUT_FFT = True
        PLOT_BOW_SLIPSTATES = True

        PLOT_SAMPLE_MIN = int(FS*1.0)
        PLOT_SAMPLE_MAX = int(FS*2.6)
        PLOT_TIME_SAMPLE_MIN = int(FS*1.0)
        PLOT_TIME_SAMPLE_MAX = int(FS*2.6)
        PLOT_MAX_FREQ = 10000


    elif "slip-single" in THESIS:
        xf = 0.0
        bow_position = 0.12
        bow_force = 0.25
        bow_velocity = 0.1
        SECONDS = 2.0

        if "low" in THESIS:
            FS = 55000
        elif "moderate" in THESIS:
            FS = 66150
        elif "high" in THESIS:
            FS = 110000
        else:
            FS = 88200

        PLOTS = True
        PLOT_BOW_SLIPSTATES = True
        PLOT_FINAL_OUTPUT = True
        PLOT_FINAL_OUTPUT_TIME = False
        PLOT_FINAL_OUTPUT_FFT = True
        PLOT_SAMPLE_MIN = int(FS*1.0)
        PLOT_SAMPLE_MAX = int(FS*2.0)
        PLOT_TIME_SAMPLE_MIN = int(FS*1.0)
        PLOT_TIME_SAMPLE_MAX = int(FS*1.01)

    elif "slip-change" in THESIS:
        xf = 0.0
        bow_position = 0.12
        MAIN_TWO_BOWS = True
        bow_velocity = 0.5
        bow_force_first = 1.0

        SECONDS_FIRST = 1.0
        SECONDS_SECOND = 2.0

        A_noise = 0.0

        bow_velocity_second = 0.1
        bow_force_second = 0.01

        if "negative only" in THESIS:
            NO_POSITIVE_SLIPPING = True
        elif "both" in THESIS:
            pass
        if "safety" in THESIS:
            FS = 88200
            SECONDS_SECOND = 0.15
            PLOTS = True
            PLOT_FINAL_OUTPUT = True
            PLOT_FINAL_OUTPUT_TIME = True
            PLOT_BOW_SLIPSTATES = True
            PLOT_SAMPLE_MIN = int(FS*0.95)
            PLOT_SAMPLE_MAX = int(FS*1.15)
            PLOT_TIME_SAMPLE_MIN = int(FS*0.95)
            PLOT_TIME_SAMPLE_MAX = int(FS*1.15)
            if "no skips" in THESIS:
                NO_SLIPPING_SKIPS = True
            elif "both" in THESIS:
                SECONDS_SECOND = 1.0
                pass

        SECONDS = SECONDS_FIRST + SECONDS_SECOND

        #PLOTS = True
        #PLOT_BOW_SLIPSTATES = True
        #PLOT_FINAL_OUTPUT = True
        #PLOT_FINAL_OUTPUT_TIME = False
        #PLOT_FINAL_OUTPUT_FFT = True
        #PLOT_SAMPLE_MIN = int(FS*1.0)
        #PLOT_SAMPLE_MAX = int(FS*1.18576)
        #PLOT_TIME_SAMPLE_MIN = int(FS*1.0)
        #PLOT_TIME_SAMPLE_MAX = int(FS*1.18576)

elif THESIS.startswith("ns "):
    xf = 1.0 - 0.109
    if "bow" in THESIS:
        TEST_BOW = True
        bow_position = 0.12
        bow_force = 0.2
        bow_velocity = 0.2
        if "cello" in THESIS:
            bow_force = 1.5

    FS = 96000
    xp = 0.2
    SECONDS = 1.6 # 0.1 for pluck, plus over 65536 samples

    if "16" in THESIS:
        N = 16
    elif "24" in THESIS:
        N = 24
    elif "32" in THESIS:
        N = 32
    elif "40" in THESIS:
        N = 40
    elif "48" in THESIS:
        N = 48
    elif "64" in THESIS:
        N = 64
    else:
        print "fail: explain cello c THESIS"
        exit(1)

    PLOTS = True
    PLOT_FINAL_OUTPUT = True
    PLOT_FINAL_OUTPUT_FFT = True
    PLOT_SAMPLE_MIN = int(FS*0.1)
    PLOT_SAMPLE_MAX = int(FS*1.6)
    PLOT_TIME_SAMPLE_MIN = int(FS*0.1)
    PLOT_TIME_SAMPLE_MAX = int(FS*0.11)

    PLOT_MIN_FREQ = 0
    if "cello-c" in THESIS:
        PLOT_MAX_FREQ = 5000
    elif "violin-e" in THESIS:
        PLOT_MAX_FREQ = 30000
    SCALE_WAV_OUTPUT = 1e-1

    if "bow" in THESIS:
        SECONDS = 1.8
        PLOT_SAMPLE_MIN = int(FS*1.0)
        PLOT_SAMPLE_MAX = int(FS*1.7)




### old stuffs

elif THESIS.startswith("pluck decay"):
    if "open" in THESIS:
        xf = 0.0
        SECONDS = 5.0
    elif "first" in THESIS:
        xf = 1.0 - 0.109
        SECONDS = 5.0
    elif "two plucks" in THESIS:
        xf = 1.0 - 0.109
        SECONDS = 1.0
        PLAY_MULTIPLE = True
        ONLY_TWO = True
        if "undamped" in THESIS:
            R_pluck = 0
            R_finger = 0
    else:
        print "ERROR: bad THESIS type?"
    xp = 0.2
    PLOTS = False


elif THESIS.startswith("pluck open"):
    xp = 0.5
    xf = 0.0
    if "one" in THESIS:
        DOUBLE_FINGER_FORCE = True
        # "double" uses only one force for the pluck
    elif "two" in THESIS:
        # "triple" still uses two forces for the pluck
        DOUBLE_FINGER_FORCE = False

    SCALE_WAV_OUTPUT = 1e-1
    PLOT_FINAL_OUTPUT = True
    PLOT_FINAL_OUTPUT_FFT = True
    PLOT_SAMPLE_MIN = int(FS*0.1)
    PLOT_SAMPLE_MAX = int(FS*1.6)

elif THESIS.startswith("pluck total forces"):
    xf = 0.75
    xp = 0.5

    xf = 0.5
    xp = 0.25
    if "two" in THESIS:
        SINGLE_PLUCK_DOUBLE_FINGER_FORCE = True
    elif "three" in THESIS:
        SINGLE_PLUCK_DOUBLE_FINGER_FORCE = False

    SCALE_WAV_OUTPUT = 1e-1
    PLOT_FINAL_OUTPUT = True
    PLOT_FINAL_OUTPUT_FFT = True
    PLOT_SAMPLE_MIN = int(FS*0.1)
    PLOT_SAMPLE_MAX = int(FS*1.6)
    #PLOT_MAX_FREQ = 1500



elif THESIS.startswith("finger freqs"):
    #xf = 0.109
    #xp = 0.2
    #xf = 0.0
    #xf = 1.0 - 0.3333333333
    #xp = 0.3333333333
    xf = 1.0 - 0.25
    xp = 0.25

    PLOTS = False
    PLAY_MULTIPLE = True
    ONLY_TWO = True

    INFINITE_SPRING = False
    if "single" in THESIS:
        SINGLE_FINGER_FORCE = True
        DOUBLE_FINGER_FORCE = False
    elif "double" in THESIS:
        SINGLE_FINGER_FORCE = False
        DOUBLE_FINGER_FORCE = True
    else:
        SINGLE_FINGER_FORCE = False
        DOUBLE_FINGER_FORCE = False

    #PLOT_FINAL_OUTPUT = False
    #PLOT_FORCES = False
    #PLOT_MODE_DISPLACEMENTS = False
    #PLOT_DISPLACEMENTS = True
    #WRITE_DISPLACEMENTS = True
    #WRITE_DISPLACEMENTS_EXTRA = True
    #DISPLACEMENTS_ALONG_STRING = 200

    PLOT_MIN_FREQ = 0
    PLOT_MAX_FREQ = 2000
    PLOT_SAMPLE_MIN = int(FS*0.1)
    PLOT_SAMPLE_MAX = int(FS*0.16)
    DISPLACEMENTS_SAMPLE_RATE = FS
    SCALE_WAV_OUTPUT = 1e-1

elif THESIS == "finger freqs single":
    xf = 0.109
    SECONDS = 1.6 # 0.1 for pluck, plus over 65536 samples

    INFINITE_SPRING = False
    SINGLE_FINGER_FORCE = True

    PLOT_FINAL_OUTPUT = True
    PLOT_FORCES = True
    PLOT_MODE_DISPLACEMENTS = False
    PLOT_DISPLACEMENTS = True
    WRITE_DISPLACEMENTS = False
    WRITE_DISPLACEMENTS_EXTRA = False

    PLOT_MIN_FREQ = 0
    PLOT_MAX_FREQ = 2000
    PLOT_SAMPLE_MIN = int(FS*0.1)
    PLOT_SAMPLE_MAX = int(FS*0.125)
    DISPLACEMENTS_SAMPLE_RATE = FS/5
    SCALE_WAV_OUTPUT = 1e-1
elif THESIS.startswith("finger beating"):
    xf = 0.5
    SECONDS = 1.6 # 0.1 for pluck, plus over 65536 samples

    INFINITE_SPRING = False
    if "single" in THESIS:
        SINGLE_FINGER_FORCE = True
        DOUBLE_FINGER_FORCE = False
    elif "double" in THESIS:
        SINGLE_FINGER_FORCE = False
        DOUBLE_FINGER_FORCE = True
    else:
        SINGLE_FINGER_FORCE = False
        DOUBLE_FINGER_FORCE = False

    PLOT_FINAL_OUTPUT = True
    PLOT_FORCES = True
    PLOT_MODE_DISPLACEMENTS = False
    PLOT_DISPLACEMENTS = False
    WRITE_DISPLACEMENTS = False
    WRITE_DISPLACEMENTS_EXTRA = False

    PLOT_MIN_FREQ = 200
    PLOT_MAX_FREQ = 1250
    PLOT_SAMPLE_MIN = int(FS*0.1)
    PLOT_SAMPLE_MAX = int(FS*0.6)
    DISPLACEMENTS_SAMPLE_RATE = FS/5
    SCALE_WAV_OUTPUT = 1e-1
elif THESIS.startswith("finger unit string"):
    print "ZZZZZZZZZZZZZZZZZ: change string in constants.py"
    xf = 0.5
    SECONDS = 1.6 # 0.1 for pluck, plus over 65536 samples

    N = 3
    INFINITE_SPRING = True
    SINGLE_FINGER_FORCE = True

    PLOT_FINAL_OUTPUT = True
    PLOT_FORCES = True
    PLOT_MODE_DISPLACEMENTS = True
    PLOT_DISPLACEMENTS = False
    WRITE_DISPLACEMENTS = False
    WRITE_DISPLACEMENTS_EXTRA = False

    PLOT_MIN_FREQ = 0
    PLOT_MAX_FREQ = 2000
    #PLOT_MIN_FREQ = 400
    #PLOT_MAX_FREQ = 1800
    PLOT_SAMPLE_MIN = int(FS*0.1)
    PLOT_SAMPLE_MAX = int(FS*0.12)
    DISPLACEMENTS_SAMPLE_RATE = FS/5
    SCALE_WAV_OUTPUT = 1e-3

elif THESIS.startswith("bow skipping"):
    TEST_BOW = True
    if "48000" in THESIS:
        FS = 48000
    elif "66150" in THESIS:
        FS = 66150
    else:
        print "zzzzzzzzz not suitable THESIS"
    xf = 0.0

    bow_position = 0.1
    bow_force = 0.3
    bow_velocity = 0.3

    #bow_position = 0.06
    #bow_force = 0.4
    #bow_velocity = 1.0

    # really bad example
    #xf = 1.0 - 0.5
    #bow_position = 0.06
    #bow_force = 0.1
    #bow_velocity = 0.31623

    SECONDS = 1.0
    #zzz

    INFINITE_SPRING = False
    SINGLE_FINGER_FORCE = False

    PLOT_BOW_COMBO = True

    PLOT_FINAL_OUTPUT = False
    PLOT_HIST_BOW = False
    PLOT_BOW_STATES = False
    PLOT_FORCES = False
    PLOT_MODE_DISPLACEMENTS = False
    PLOT_DISPLACEMENTS = False
    WRITE_DISPLACEMENTS = False
    WRITE_DISPLACEMENTS_EXTRA = False

    PLOT_MIN_FREQ = 0
    PLOT_MAX_FREQ = 1250
    PLOT_SAMPLE_MIN = 0
    PLOT_SAMPLE_MAX = int(FS*0.1)
    SCALE_WAV_OUTPUT = 1e-1

elif THESIS.startswith("bow unstable"):
    print "zzzzzzzzzzzzzzzzzzzzz not working"
    TEST_BOW = True
    FS = 44100
    xf = 0.0

    SECONDS = 1.0
    NO_POSITIVE_SLIPPING = True
    #NO_POSITIVE_SLIPPING = False

    bow_position = 0.05
    bow_force = 0.1
    bow_velocity = 0.1

    PLOT_BOW_COMBO = True
    SCALE_WAV_OUTPUT = 1e-1


elif THESIS.startswith("multi pluck"):
    xf = 0.5
    xf = 1.0 - 0.109
    #xf = 0.25
    #xf = 0.0
    #SECONDS = 1.6 # 0.1 for pluck, plus over 65536 samples
    SECONDS = 1.0

    R_pluck = 1e1

    INFINITE_SPRING = False
    SINGLE_FINGER_FORCE = False

    PLAY_MULTIPLE = True
    ONLY_TWO = True

    PLOTS = False
    PLOT_FINAL_OUTPUT = False
    PLOT_FORCES = False
    PLOT_MODE_DISPLACEMENTS = False
    #PLOT_DISPLACEMENTS = True
    PLOT_DISPLACEMENTS = False
    WRITE_DISPLACEMENTS = False
    WRITE_DISPLACEMENTS_EXTRA = False

    PLOT_MIN_FREQ = 0
    PLOT_MAX_FREQ = 1250
    DISPLACEMENTS_SAMPLE_RATE = FS/50
    PLOT_SAMPLE_MIN = int(FS*0.78)
    PLOT_SAMPLE_MAX = int(FS*0.92)
    SCALE_WAV_OUTPUT = 5e-2

elif "bad pluck" in THESIS:
    xf = 1.0 - 0.159104
    xp = 0.3
    SECONDS = 1.0

elif "finger-R-decay" in THESIS:
    FS = 22050
    SECONDS = 8.0
    SCALE_WAV_OUTPUT = 1e-1
    xf = 1.0 - 0.109
    xp = 0.2

    PLOTS = True
    PLOT_DISPLACEMENTS = True
    WRITE_DISPLACEMENTS = True
    DISPLACEMENTS_SAMPLE_RATE = FS
    PLOT_SAMPLE_MIN = int(FS*0.1)
    PLOT_SAMPLE_MAX = int(FS*0.11)
    PLOT_TIME_SAMPLE_MIN = int(FS*0.1)
    PLOT_TIME_SAMPLE_MAX = int(FS*0.11)

    if "10" in THESIS:
        R_finger = 10
    elif "300" in THESIS:
        R_finger = 300
    elif "30" in THESIS:
        R_finger = 30
    print "set R_finger to:", R_finger

else:
    print "Selecting null THESIS type"
    #xf = 0.333
    SECONDS = 1.6 # 0.1 for pluck, plus over 65536 samples
    SECONDS = 0.4
    #N = 16
    FS = 44100
    #FS = 22050
    #PLOTS = True
    PLOTS = False
    #PLOTS_SHOW = True
    #xf = 1.0 - 0.109

    INFINITE_SPRING = False
    SINGLE_FINGER_FORCE = False
    DOUBLE_FINGER_FORCE = False
    #DOUBLE_FINGER_FORCE = True

    PLOT_FINAL_OUTPUT = True
    PLOT_FORCES = False
    PLOT_MODE_DISPLACEMENTS = False
    PLOT_DISPLACEMENTS = False
    WRITE_DISPLACEMENTS = False
    WRITE_DISPLACEMENTS_EXTRA = False

    PLOT_MIN_FREQ = 0
    PLOT_MAX_FREQ = 1250
    DISPLACEMENTS_SAMPLE_RATE = FS/100
    PLOT_SAMPLE_MIN = int(FS*0.0)
    PLOT_SAMPLE_MAX = int(FS*0.3)
    #SCALE_WAV_OUTPUT = 1.0
    SCALE_WAV_OUTPUT = 1e-1



