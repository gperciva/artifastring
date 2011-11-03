#!/usr/bin/env python

import pyaudio
import numpy

#RATE = 96000
#ALSA_BUFFER_SIZE = 2048
#PROCESS_BUFFER_SIZE = 8192

RATE = 44100
ALSA_BUFFER_SIZE = 1024
PROCESS_BUFFER_SIZE = 4096

ALSA_BUFFER_SIZE_MULTIPLIER = 2

# don't change these!  portaudio and/or pyaudio is really finicky
# about sample formats :(
#FORMAT = pyaudio.paFloat32
#FORMAT_NUMPY = numpy.float32
FORMAT_ALSA = pyaudio.paInt16
FORMAT_NUMPY = numpy.int16


