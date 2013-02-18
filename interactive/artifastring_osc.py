#!/usr/bin/env python

DEBUG_OSC = False
#DEBUG_OSC = True

import time
import sys
sys.path.append('build/swig')
import curses

import artifastring_interactive
import artifastring_process
import midi_pos
from artifastring_process import COMMANDS

import liblo

OLD_BEHAVIOUR = True
#OLD_BEHAVIOUR = False

SOUNDPLANE = False
SOUNDPLANE = True


class ArtifastringOsc(artifastring_interactive.InteractiveViolin):
    def __init__(self, *args):
        artifastring_interactive.InteractiveViolin.__init__(self, *args)

        #self.active = [False, False, False, False]

        try:
            if SOUNDPLANE:
                self.server = liblo.Server(3123)
            else:
                self.server = liblo.Server(8888)
        except liblo.ServerError, err:
            print str(err)
            sys.exit()

    def start_server(self):
        if SOUNDPLANE:
            self.server.add_method("/t3d/tch", "iffff",
                self.soundplane_callback_tch)
            self.server.add_method("/t3d/alv", None,
                self.soundplane_callback_alv)
        elif OLD_BEHAVIOUR:
            self.server.add_method(None, None, self.old_callback)
        else:
            self.server.add_method(None, None, self.callback)

    def keypress_extra(self, c):
        if c == 'b':
            pass

    def extra_main_init(self):
        self.start_server()

    def extra_main_loop(self):
        #for st in range(4):
        #    if self.active[st]:
        #        self.params.force = 0.0
        #        self.commands_pipe_master.send( (COMMANDS.BOW, self.params) )
        #        self.active[st] = False
        while self.server.recv(0):
            pass

    def soundplane_callback_alv(self, path, args):
        if len(args) > 0:
            return
        self.params.force = 0.0
        self.commands_pipe_master.send( (COMMANDS.BOW, self.params) )

    def inst_force(self, z):
        if self.artifastring_init.instrument_type == 0:
            return 4*z
        elif self.artifastring_init.instrument_type == 1:
            return 8*z
        elif self.artifastring_init.instrument_type == 2:
            return 12*z

    def soundplane_callback_tch(self, path, args):
        i, x, y, z, m = args
        #print "%i\t%.3f\t%.3f\t%.3f" % (i, x, y, z)
        #Fb = self.inst_force(z)

        def scale(val, minin, maxin, minout, maxout):
            relval = (val - minin) / (maxin-minin)
            return relval*maxout + minout
        #self.active[st] = True
        if x > 0.25:
            st = int(5*y)
            if st > 3:
                return
            fp = 0.9 - scale(x, 0.25, 1.0, 0.0, 1.0)
            if fp < 0:
                fp = 0
            #Fb = scale(z, 0.0, 1.0, 0.0, 5.0)
            Fb = self.inst_force(z)
            self.params.violin_string = st
            self.params.force = Fb
            self.params.finger_position = fp
        else:
            xb = x
            vb = 1.0 - 2*y
            self.params.bow_position = xb
            self.params.velocity = vb

        self.commands_pipe_master.send( (COMMANDS.BOW, self.params) )
        self.commands_pipe_master.send( (COMMANDS.FINGER, self.params) )


    def callback(self, path, args):
        if DEBUG_OSC:
            print "received:", path, args
        if path.startswith("/bow"):
            st, xb, Fb, vb = args
            self.violin_string = st
            self.params.bow_position = xb
            self.params.force = Fb
            self.params.velocity = vb
            self.commands_pipe_master.send( (COMMANDS.BOW, self.params) )
        elif path.startswith("/finger"):
            st, fp = args
            self.violin_string = st
            self.params.finger_position = xb
            self.commands_pipe_master.send( (COMMANDS.FINGER, self.params) )


    def old_callback(self, path, args):
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
            #fp = scale(args[0], 0.0, 1.0, 0.0, 0.4) - 0.05
            fm = scale(args[0], 0.0, 1.0, 0.0, 8.0) - 0.5
            if fm < 0:
                fm = 0
            fp = midi_pos.midi2pos(fm)
            #if fp < 0:
            #    fp = 0
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
            #vb = scale(x, 0.0, 1.0, 0.0, 4.0) - 2.0
            vb = x - 0.5
            Fb = 4.0-scale(y, 0.0, 1.0, 0.0, 4.0)
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


