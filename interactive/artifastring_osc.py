#!/usr/bin/env python

DEBUG_OSC = False
#DEBUG_OSC = True

import time
import os
import sys
sys.path.append('build/swig')
import curses

import artifastring_interactive
import artifastring_process
import midi_pos
from artifastring_process import COMMANDS

import liblo


class ArtifastringOsc(artifastring_interactive.InteractiveViolin):
    def __init__(self, *args):
        artifastring_interactive.InteractiveViolin.__init__(self, *args)

        try:
            self.server = liblo.Server(8888)
        except liblo.ServerError, err:
            print str(err)
            sys.exit()
        self.server.add_method(None, None, self.callback)

    def keypress_extra(self, c):
        if c == 'b':
            pass

    def extra_main_loop(self):
        self.server.recv(0)

    def callback(self, path, args):
        if DEBUG_OSC:
            print "received:", path, args

        def scale(val, minin, maxin, minout, maxout):
            relval = (val - minin) / (maxin-minin)
            return relval*maxout + minout

        if path.startswith("/st"):
            st = self.params.violin_string
            if path == '/st_g':
                st = 0
            elif path == '/st_d':
                st = 1
            elif path == '/st_a':
                st = 2
            elif path == '/st_e':
                st = 3
            if st != self.params.violin_string:
                self.turn_off_current_string()
                # new
                self.params.violin_string = st
                self.commands_pipe_master.send( (COMMANDS.BOW, self.params) )
            #print "finger\t%.2f\t%.2f" %( x, y)
            fp = scale(args[0], 0.0, 1.0, 0.0, 0.4) - 0.05
            if fp < 0:
                fp = 0
            #print "f\t%.2f\t%.2f" %( x, y)
            text = "fp: %.2f" %( fp)
            if DEBUG_OSC:
                print text
            else:
                self.set_message(text + "             ")
            self.params.finger_position = fp
            self.commands_pipe_master.send( (COMMANDS.FINGER, self.params) )

        if path.startswith("/bow"):
            x, y = args

            #print "bow\t%.2f\t%.2f" %( x, y)
            #print "\t%.2f\t%.2f" %( scale(x, 0.0, 0.25, 0.05, 0.20), y)
            #print "\t%.2f\t%.2f" %( scale(y, 0.0, 0.25, 0.05, 0.20), y)
            vb = scale(x, 0.0, 1.0, 0.0, 4.0) - 2.0
            Fb = 2.0-scale(y, 0.0, 1.0, 0.0, 2.0)
            text = "vb: %.2f\tFb: %.2f" %( vb, Fb)
            if DEBUG_OSC:
                print text
            else:
                self.set_message(text + "             ")
            self.params.force = Fb
            self.params.velocity = vb
            self.commands_pipe_master.send( (COMMANDS.BOW, self.params) )


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


    try:
        p, audio_stream = artifastring_interactive.make_audio_stream()
    except:
        p = None
        audio_stream = None

    artifastring_init = artifastring_process.ArtifastringInit(
        instrument_type, instrument_number)

    vln = ArtifastringOsc(artifastring_init, stdscr)
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

    if p is not None:
        audio_stream.close()
        p.terminate()


if __name__ == "__main__":
    if DEBUG_OSC:
        main(None)
    else:
        curses.wrapper(main)


