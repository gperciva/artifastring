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

import artifastring_process
ARTIFASTRING_SAMPLE_RATE = artifastring_process.ARTIFASTRING_SAMPLE_RATE

import quality_judgements
import tuning_pitch

import curses
import numpy
import math

import multiprocessing
import time
import scipy.io.wavfile

import aubio.aubiowrapper

# for Vivi?
import actions_file
#import vivi_defines
#import dynamics
import midi_pos
#HOPSIZE = vivi_defines.HOPSIZE

HOPSIZE = 512
NUM_AUDIO_BUFFERS = 2

TUNING_SETTLE_BUFFERS = 10
# for pitch and buffers
PRINT_EXTRA_DISPLAY = 1

class Parameters():
    def __init__(self, st=0, fp=0, bp=.12, f=1.0, v=0.24, T=1.0):
        self.violin_string = st
        self.finger_position = fp
        self.bow_position = bp
        self.force = f
        self.velocity = v
        # HACK: kind-of.  Tension isn't really a normal "playing
        # parameter", but it _is_ still something under a
        # musician's control.
        self.tension_relative = T

from artifastring_process import COMMANDS


class InteractiveViolin():
    def __init__(self, artifastring_init, stdscr, train_dirname=None):
        self.artifastring_init = artifastring_init
        self.stdscr = stdscr

        self.row = 5
        self.params = Parameters()

        self.commands_pipe_master, commands_pipe_client = multiprocessing.Pipe()
        self.audio_pipe_master, audio_pipe_client = multiprocessing.Pipe()
        self.violin_process = multiprocessing.Process(
            target=artifastring_process.violin_process,
            args=(artifastring_init,
                commands_pipe_client,
                audio_pipe_client,
                )
            )
        #self.violin_process.daemon = False

        self.tuning = -1
        #self.unsafes = numpy.zeros(20)
        #self.unsafe_index = 0

        self.train_info = quality_judgements.training_init(
            train_dirname, artifastring_init)

        self.violin_process.start()
        time.sleep(0.1)

        if self.stdscr is not None:
            self.stdscr.clear()
            self.stdscr.nodelay(1)
            self.print_help()
        #self.stdscr.addstr(20, 50, str("%s" % audio_queue))

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

    def copy_params(self):
        change = Parameters()
        change.violin_string = self.params.violin_string
        change.finger_position = self.params.finger_position
        change.bow_position = self.params.bow_position
        change.force = self.params.force
        change.velocity = self.params.velocity
        change.tension_relative = self.params.tension_relative
        return change

    def turn_off_current_string(self):
        string_off = self.copy_params()
        string_off.force = 0
        string_off.velocity = 0
        self.commands_pipe_master.send( (COMMANDS.BOW, string_off) )

    def change_tension(self, alter):
        change = self.copy_params()
        change.tension_relative = alter
        self.commands_pipe_master.send( (COMMANDS.TENSION, change) )

    def keypress_extra(self, c):
        pass

    def keypress(self, c):
        if c == 'q':
            return False
        if c == 's':
            self.turn_off_current_string()
            # new
            self.params.violin_string += 1
            if self.params.violin_string > 3:
                self.params.violin_string = 0
        if c == 'a':
            self.turn_off_current_string()
            # new
            self.params.violin_string -= 1
            if self.params.violin_string < 0:
                self.params.violin_string = 3
        if c == 'f':
            if self.params.finger_position == 0.0:
                self.params.finger_position = 0.02
            else:
                self.params.finger_position *= 1.1
        if c == 'd':
            if self.params.finger_position < 0.02:
                self.params.finger_position = 0.00
            else:
                self.params.finger_position /= 1.1
        if c == 't':
            self.params.bow_position *= 1.01
        if c == 'g':
            self.params.bow_position /= 1.01
        if c == 'y':
            self.params.force *= 1.1
        if c == 'h':
            self.params.force /= 1.1
        if c == 'u':
            self.params.velocity *= 1.1
        if c == 'j':
            self.params.velocity /= 1.1

        if c == 'm':
            self.tuning = TUNING_SETTLE_BUFFERS

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
            self.change_tension(alter)
            skip_violin_print = True

        ### TODO: icky hard-coding categories
        if c >= '1' and c <= '7':
            skip_violin_print = True
            self.snapshot(c)
            self.stdscr.addstr(self.row, 0, str("file written"))

        if c == ord('b'):
            self.params.force /= 1.1
        if c == 'l':
            if self.params.force > 0:
                self.store_force = self.params.force
                self.params.force = 0
            else:
                self.params.force = self.store_force
        if c == 'm':
            midi = midi_pos.pos2midi(self.params.finger_position)
            midi = round(midi)
            self.params.finger_position = midi_pos.midi2pos(midi)
            self.stdscr.addstr(23, 20, str("midi: %i" % midi))
        if c == 'n':
            midi = midi_pos.pos2midi(self.params.finger_position)
            midi = round(midi) + 1
            if midi > 12:
                midi = 0
            self.params.finger_position = midi_pos.midi2pos(midi)
            self.stdscr.addstr(23, 20, str("midi: %i  " % midi))

        self.keypress_extra(c)



        self.commands_pipe_master.send( (COMMANDS.FINGER, self.params) )
        self.commands_pipe_master.send( (COMMANDS.BOW, self.params) )
        if not skip_violin_print:
            self.stdscr.addstr(self.row, 0, str(
                "%i\t%.3f\t%.3f\t%.3f\t%.3f" % (
                self.params.violin_string, self.params.finger_position,
                self.params.bow_position, self.params.force, self.params.velocity)))
            # next line
            self.row += 1
            if self.row > 20:
                self.row = 5
            self.stdscr.addstr(self.row, 0, str(" "*40))
            self.stdscr.move(self.row, 0)
        return True

    def print_tension(self, tension):
        if self.stdscr is not None:
            self.stdscr.addstr(23, 5, str("T=%.3f" % tension))
    #def print_unsafe(self):
    #    if self.stdscr is not None:
    #        unsafe = self.unsafes.mean()
    #        self.stdscr.addstr(23, 30, str("unsafe %.1f" % unsafe))

    def snapshot(self, cat_key):
        basename = quality_judgements.get_train_basename(
            self.train_info, self.artifastring_init, self.params)
        actions_out = actions_file.ActionsFile(basename+".actions")
        finger_midi = midi_pos.pos2midi(self.params.finger_position)
        actions_out.comment(
            "basic\tst %i\tdyn %i\tfinger_midi %.3f\tinst %i %i" % (
            self.params.violin_string, 0, finger_midi,
            self.artifastring_init.instrument_type,
            self.artifastring_init.instrument_number,
            ))
        actions_out.finger(0, self.params.violin_string,
            self.params.finger_position)

        complete = numpy.empty(0, dtype=numpy.int16)
        complete_forces = numpy.empty(0, dtype=numpy.int16)

        seconds = 0.4
        bow_pos_along = 0.1
        num_hops = int(math.ceil(seconds * ARTIFASTRING_SAMPLE_RATE / HOPSIZE))
        for j in xrange(num_hops):
            arr, forces = self.audio_pipe_master.recv()
            complete = numpy.append(complete, arr)
            complete_forces = numpy.append(complete_forces, forces)
            self.audio_pipe_master.send( (arr, forces) )
            seconds = float(j)*HOPSIZE/ARTIFASTRING_SAMPLE_RATE

            actions_out.bow(seconds, self.params.violin_string,
                self.params.bow_position,
                self.params.force,
                self.params.velocity,
                bow_pos_along,
                )
            bow_pos_along += self.params.velocity/float(
                ARTIFASTRING_SAMPLE_RATE)
        # do one more action for "good luck"
        seconds = (j+1)*HOPSIZE/float(
            ARTIFASTRING_SAMPLE_RATE)
        actions_out.bow(seconds, self.params.violin_string,
            self.params.bow_position,
            self.params.force,
            self.params.velocity,
            bow_pos_along
            )



        scipy.io.wavfile.write(basename+".wav",
            ARTIFASTRING_SAMPLE_RATE, complete)
        scipy.io.wavfile.write(basename+".forces.wav",
            ARTIFASTRING_SAMPLE_RATE/4, complete_forces)
        actions_out.close()

        quality_judgements.append_to_mf(self.train_info, self.params,
            basename, cat_key)
        #self.stdscr.addstr(22, 10, str("wrote to %s" % mf_filename))
        self.snapshot_post(basename)

    def snapshot_post(self, filename):
        pass


    def set_message(self, text):
        self.stdscr.addstr(23, 20, str("%s" % text))

    def extra_main_loop(self):
        pass

    def main_loop(self):
        windowsize = 2048

        for i in range(NUM_AUDIO_BUFFERS):
            arr = numpy.zeros(HOPSIZE, dtype=numpy.int16)
            forces = numpy.zeros(
                HOPSIZE/artifastring_process.HAPTIC_DOWNSAMPLE_FACTOR,
                dtype=numpy.int16)
            self.audio_pipe_master.send( (arr, forces) )

        self.commands_pipe_master.send( (COMMANDS.BOW, self.params) )

        pitch_obj = aubio.aubiowrapper.new_aubio_pitchdetection(
            windowsize, HOPSIZE, 1,
            ARTIFASTRING_SAMPLE_RATE,
            aubio.aubiowrapper.aubio_pitch_yinfft,
            aubio.aubiowrapper.aubio_pitchm_freq,
            )
        fvec = aubio.aubiowrapper.new_fvec(HOPSIZE, 1)
        show_pitch = 0
        time_unit = 0.5*HOPSIZE/float(
            ARTIFASTRING_SAMPLE_RATE)

        # wait for a complete queue before progressing
        #time.sleep(1)
        #while not self.output_audio_queue.full():
        #    if PRINT_EXTRA_DISPLAY:
        #        self.stdscr.addstr(20, 60, str("in %i" %
        #            self.input_audio_queue.qsize()))
        #        self.stdscr.addstr(21, 60, str("out %i" %
        #            self.output_audio_queue.qsize()))
        #    time.sleep(time_unit)

        while True:
            self.extra_main_loop()
        #    if PRINT_EXTRA_DISPLAY:
        #        self.stdscr.addstr(20, 60, str("in %i" %
        #            self.input_audio_queue.qsize()))
        #        self.stdscr.addstr(21, 60, str("out %i" %
        #            self.output_audio_queue.qsize()))

            if self.stdscr is not None:
                c = self.stdscr.getch()
                if c != -1:
                    if not self.keypress( chr(c) ):
                        break

   
            while self.commands_pipe_master.poll():
                client_message = self.commands_pipe_master.recv()
                if client_message[0] == COMMANDS.TENSION:
                    self.print_tension( client_message[1] )
                #if client_message[0] == COMMANDS.UNSAFE:
                    #self.unsafes[self.unsafe_index] = client_message[1]
                    #self.unsafe_index += 1
                    #if self.unsafe_index >= len(self.unsafes):
                    #    self.unsafe_index = 0
                    #self.print_unsafe()


            if self.audio_pipe_master.poll():
                arr, forces = self.audio_pipe_master.recv()
            else:
                time.sleep(time_unit)
                continue

            if PRINT_EXTRA_DISPLAY:
                for i in xrange(HOPSIZE):
                    aubio.aubiowrapper.fvec_write_sample(
                       fvec, float(arr[i]), 0, i)

                pitch = aubio.aubiowrapper.aubio_pitchdetection(
                        pitch_obj, fvec)
                show_pitch -= 1
                if self.stdscr is not None:
                    if show_pitch <= 0:
                        self.stdscr.addstr(23, 50, str("%.1f" % pitch))
                        show_pitch = 20

                expected = tuning_pitch.expected_pitch(
                    self.artifastring_init.instrument_type,
                    self.params.violin_string)
                delta_pitch = expected - pitch
                adjust = delta_pitch / expected
                if self.stdscr is not None:
                    self.stdscr.addstr(14, 50, str("%.1f Hz   " % delta_pitch))
                    self.stdscr.addstr(16, 50, str("%.4f" % adjust))
                if abs(delta_pitch) < 0.5:
                    self.tuning = -1

                if self.stdscr is not None:
                    self.stdscr.addstr(15, 50, str("%i" % self.tuning))
                if self.tuning > 0:
                    self.tuning -= 1
                    if self.tuning == 0:
                        alter = 1.0 + adjust
                        self.change_tension(alter)
                        self.tuning = TUNING_SETTLE_BUFFERS
            self.audio_pipe_master.send( (arr, forces) )
        self.audio_pipe_master.send(None)
        self.violin_process.join()
 
def main(stdscr):
    try:
        instrument_type = int(sys.argv[1])
    except:
        instrument_type = 0
    try:
        instrument_number = int(sys.argv[2])
    except:
        instrument_number = 0

    try:
        st = int(sys.argv[3])
    except:
        st = 0
    try:
        dyn = int(sys.argv[4])
    except:
        dyn = 0
    try:
        finger = int(sys.argv[5])
    except:
        finger = 0
    try:
        text_message = " ".join(sys.argv[6:])
    except:
        text_message = ""

    artifastring_init = artifastring_process.ArtifastringInit(
        instrument_type, instrument_number)

    vln = InteractiveViolin(artifastring_init, stdscr)
    vln.turn_off_current_string()
    vln.params.violin_string = st
    #vln.params.bow_position = dynamics.get_distance(dyn)
    #vln.params.velocity = dynamics.get_velocity(dyn)
    vln.params.finger_position = midi_pos.midi2pos(finger)
    vln.commands_pipe_master.send( (COMMANDS.BOW, vln.params) )

    vln.dyn = dyn

    if stdscr is not None:
        vln.set_message(text_message)

    time.sleep(0.5)
    vln.main_loop()


if __name__ == "__main__":
    curses.wrapper(main)
    #main(None)

