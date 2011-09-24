#!/usr/bin/env python

##
# Copyright 2010--2011 Graham Percival
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

import sys
import violin_instrument
import monowav
import curses
import numpy
import math

import pyaudio
import aubio.aubiowrapper

class InteractiveViolin():
    violin = None
    audio_stream = None

    violin_string = 0
    finger_position = 0.0
    bow_position = 0.08
    force = 1.0
    velocity = 0.4

    stdscr = None
    row = 5
    instrument_number = 0

    cats = [0]*7

    def __init__(self, instrument_number, stdscr, audio_stream):
        self.instrument_number = instrument_number
        self.stdscr = stdscr
        self.audio_stream = audio_stream

        self.violin = violin_instrument.ViolinInstrument(
            self.instrument_number)
        self.stdscr.nodelay(1)
        self.print_help()

    def print_help(self):
        helpstr = [[
            "q: quit",
            "s: string++",
            "a: string--",
            "f: finger++",
            "d: finger--"
        ], [
            "t: pos++",
            "g: pos--",
            "y: force++",
            "h: force--",
        ], [
            "u: velocity++",
            "j: velocity--",
        ], [
            "z,x: tension+",
            "c,v: tension-",
        ]]
        for row, line in enumerate(helpstr):
            for i, text in enumerate(line):
                self.stdscr.addstr(row, 16*i, text)

    def keypress(self, c):
        if c == 'q':
            return False
        if c == 's':
            # turn off previous
            self.violin.bow(self.violin_string, 
                self.bow_position, 0.0, 0.0)
            # new
            self.violin_string += 1
            if self.violin_string > 3:
                self.violin_string = 0
            self.violin.bow(self.violin_string, 
                self.bow_position, self.force, self.velocity)
        if c == 'a':
            # turn off previous
            self.violin.bow(self.violin_string, 
                self.bow_position, self.force, 0.0) # leave force to deaden
            # new
            self.violin_string -= 1
            if self.violin_string < 0:
                self.violin_string = 3
            self.violin.bow(self.violin_string, 
                self.bow_position, self.force, self.velocity)
        if c == 'f':
            if self.finger_position == 0.0:
                self.finger_position = 0.02
            else:
                self.finger_position *= 1.1
            self.violin.finger(self.violin_string, self.finger_position)
        if c == 'd':
            if self.finger_position < 0.02:
                self.finger_position = 0.00
            else:
                self.finger_position /= 1.1
            self.violin.finger(self.violin_string, self.finger_position)
        if c == 't':
            self.bow_position *= 1.01
        if c == 'g':
            self.bow_position /= 1.01
        if c == 'y':
            self.force *= 1.1
        if c == 'h':
            self.force /= 1.1
        if c == 'u':
            self.velocity *= 1.1
        if c == 'j':
            self.velocity /= 1.1

        skip_violin_print = False
        if c == 'z' or c == 'x' or c == 'c' or c == 'v':
            if c == 'z':
                alter = 1.0/1.1
            if c == 'x':
                alter = 1.0/1.01
            if c == 'c':
                alter = 1.01
            if c == 'v':
                alter = 1.1

            pc = self.violin.get_physical_constants(
                self.violin_string)
            pc.T *= alter
            self.violin.set_physical_constants(
                self.violin_string, pc)
            self.stdscr.addstr(self.row, 0, str("T=%.3f" % pc.T))
            skip_violin_print = True
        if c >= '1' and c <= '7':
            skip_violin_print = True
            self.snapshot(int(c))
            self.stdscr.addstr(self.row, 0, str("file written"))

        if c == ord('b'):
            self.force /= 1.1
        if not skip_violin_print:
            self.stdscr.addstr(self.row, 0, str(
                "%i\t%.3f\t%.3f\t%.3f\t%.3f" % (
                self.violin_string, self.finger_position,
                self.bow_position, self.force, self.velocity)))
        # next line
        self.row += 1
        if self.row > 20:
            self.row = 5
        self.stdscr.addstr(self.row, 0, str(" "*40))
        self.stdscr.move(self.row, 0)
        return True

    def snapshot(self, cat):
        prev_num = self.cats[cat-1]
        num = prev_num + 1
        self.cats[cat-1] += 1

        finger_midi = 12.0*math.log(1.0 /
            (1.0 - self.finger_position)) / math.log(2.0)
        filename = "audio_%i_%.3f_%.3f_%.3f_%.3f_%i.wav" % (
            self.violin_string,
            finger_midi,
            self.bow_position,
            self.force,
            self.velocity,
            num)
        wavfile = monowav.MonoWav(filename)
        num_samples = int(0.2 * 44100)
        buf = wavfile.request_fill( num_samples )
        self.violin.wait_samples(buf, num_samples)

        mf_file = open('collection.mf', 'a')
        mf_file.write(str("%s\t%.1f\n" % (filename, cat)) )
        mf_file.close()

    def main_loop(self):
        hopsize = 512
        windowsize = 2048

        buf = monowav.shortArray(hopsize)
        arr = numpy.zeros(hopsize, dtype=numpy.int16)
    
        pitch_obj = aubio.aubiowrapper.new_aubio_pitchdetection(
            windowsize, hopsize, 1, 44100,
            aubio.aubiowrapper.aubio_pitch_yinfft,
            aubio.aubiowrapper.aubio_pitchm_freq,
            )
        fvec = aubio.aubiowrapper.new_fvec(hopsize, 1)
        show_pitch = 0
 
        self.violin.bow(self.violin_string, self.bow_position,
            self.force, self.velocity)
        while True:
            c = self.stdscr.getch()
            if c != -1:
                if not self.keypress( chr(c) ):
                    break
                self.violin.bow(self.violin_string, self.bow_position,
                    self.force, self.velocity)
    
            self.violin.wait_samples(buf, hopsize)
    
            for i in xrange(hopsize):
                arr[i] = buf[i]
                aubio.aubiowrapper.fvec_write_sample(
                    fvec, buf[i], 0, i)
            self.audio_stream.write( arr.tostring() )

            pitch = aubio.aubiowrapper.aubio_pitchdetection(
                pitch_obj, fvec)
            show_pitch -= 1
            if show_pitch <= 0:
                self.stdscr.addstr(23, 50, str("%.1f" % pitch))
                show_pitch = 20
    

def main(stdscr):
    try:
        instrument_number = int(sys.argv[1])
    except:
        instrument_number = 0

    p = pyaudio.PyAudio()
    audio_stream = p.open(
        rate = 44100,
        channels = 1,
        format = pyaudio.paInt16,
        output = True
    )

    vln = InteractiveViolin(instrument_number, stdscr, audio_stream)
    vln.main_loop()

    audio_stream.close()
    p.terminate()

if __name__ == "__main__":
    curses.wrapper(main)

