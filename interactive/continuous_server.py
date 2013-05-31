#!/usr/bin/env python

##
# Copyright 2010--2013 Graham Percival
# This file is part of Artifastring.
#
# Artifastring is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# Artifastring is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with Artifastring.  If not, see
# <http://www.gnu.org/licenses/>.
##

import numpy

import artifastring_instrument
import liblo

HOPSIZE=64


import os
### portaudio should use plughw
os.environ['PA_ALSA_PLUGHW'] = '1'
import pyaudio

def make_audio_stream():
    pyaudio_obj = pyaudio.PyAudio()
    audio_stream = pyaudio_obj.open(
        rate = artifastring_instrument.ARTIFASTRING_INSTRUMENT_SAMPLE_RATE,
        channels = 1,
        format = pyaudio.paInt16,
        input=False,
        output = True,
        #output_device_index = 0,
        frames_per_buffer=HOPSIZE,
        )
    return pyaudio_obj, audio_stream



class ArtifastringContinuousOsc():
    def __init__(self, inst_type, inst_num):
        self.inst = artifastring_instrument.ArtifastringInstrument(
            inst_type, inst_num)
        self.Fb = [0.0,0.0,0.0,0.0]
        self.xb = [0.125,0.125,0.125,0.125]
        self.vb = [0.4,0.4,0.4,0.4]
        self.fp = [0.0,0.0,0.0,0.0]
        #self.active = [False, False, False, False]

        try:
            self.server = liblo.Server(3123)
        except liblo.ServerError, err:
            print str(err)
            exit()
        #self.server.add_method(None, None, self.callback)
        self.server.add_method("/t3d/tch", "iffff", self.callback)

        try:
            self.pyaudio_obj, self.audio_stream = make_audio_stream()
        except:
            print "AUDIO PROBLEM"

    def __del__(self):
        self.audio_stream.close()
        self.pyaudio_obj.terminate()


    # @liblo.make_method("/t3d/tch", "iffff")
    def callback(self, path, args):
        #if not path.startswith("/t3d/tch"):
        #    return
        i, x, y, z, m = args
        #print "%i\t%.3f\t%.3f\t%.3f" % (i, x, y, z)
        st = int(5*y)
        if st > 3:
            return
        Fb = self.inst_force(z)
        fp = 0.90 - x
        if fp < 0:
            fp = 0

        self.Fb[st] = Fb
        self.fp[st] = fp
        #self.active[st] = True
        #print "%i\t%.3f\t%.3f\t%.3f\t\t%i\t%.2f\t%.3f" % (i, x, y, z, st, Fb, fp)


    def inst_force(self, z):
        return 4*z


    def start(self):
        arr = numpy.zeros(HOPSIZE, dtype=numpy.int16)
        forces = numpy.zeros(HOPSIZE, dtype=numpy.int16)
        i = 0
        while True:
            while self.server.recv(0):
                pass
            print "here %i" % i
            i += 1
            for st in range(4):
                #print st, self.Fb[st]
                self.inst.bow(st, self.xb[st], self.Fb[st], self.vb[st])
                self.Fb[st] = 0.0
            self.inst.wait_samples_forces_python(arr, forces)
            self.audio_stream.write( arr.tostring(), HOPSIZE)

if __name__ == "__main__":
    art = ArtifastringContinuousOsc(0,0)
    art.start()
    

