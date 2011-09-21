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

import pyaudio

class InteractiveViolin():
    violin = violin_instrument.ViolinInstrument(0)
    audio_stream = None

    violin_string = 0
    finger_position = 0.0
    bow_position = 0.12
    force = 1.0
    velocity = 0.4

    stdscr = None
    row = 5

    def __init__(self, stdscr, audio_stream):
        self.stdscr = stdscr
        self.audio_stream = audio_stream
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
            "j: velocity--"
        ]]
        for self.row, line in enumerate(helpstr):
            for i, text in enumerate(line):
                self.stdscr.addstr(self.row, 16*i, text)

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
        if c == 'd':
            if self.finger_position < 0.02:
                self.finger_position = 0.02
            else:
                self.finger_position /= 1.1
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

        if c == ord('b'):
            self.force /= 1.1
        self.stdscr.addstr(self.row, 0, str(
            "%i\t%.3f\t%.3f\t%.3f\t%.3f" % (
                self.violin_string, self.finger_position,
                self.bow_position, self.force, self.velocity)))
        # next line
        self.row += 1
        if self.row > 20:
            self.row = 5
        return True
    
    
    def main_loop(self):
        buf = monowav.shortArray(256)
        arr = numpy.zeros(256)
    
    
        while True:
            c = self.stdscr.getch()
            if c != -1:
    #            stdscr.addstr(self.row, 0, str(c))
                if not self.keypress( chr(c) ):
                    break
    
            self.violin.finger(self.violin_string, self.finger_position)
            self.violin.bow(self.violin_string, self.bow_position,
                self.force, self.velocity)
            self.violin.wait_samples(buf, 256)
    
            for i in range(256):
                arr[i] = buf[i]
            self.audio_stream.write( arr.astype(numpy.int16).tostring() )
    
    

def main(stdscr):
    p = pyaudio.PyAudio()
    audio_stream = p.open(
        rate = 44100,
        channels = 1,
        format = pyaudio.paInt16,
        output = True
    )

    vln = InteractiveViolin(stdscr, audio_stream)
    vln.main_loop()

    audio_stream.close()
    p.terminate()

if __name__ == "__main__":
    curses.wrapper(main)

