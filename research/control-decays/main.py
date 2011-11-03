#!/usr/bin/env python

import time

import numpy
import scipy.io.wavfile

import comedi_interface
from comedi_interface import CHANNEL_RELAY as RELAY

import alsa_interface
from defs_measure import RATE, PROCESS_BUFFER_SIZE

def wait(seconds, audio_in_queue):
    lefts = []
    rights = []
    for i in range(int(seconds*RATE/PROCESS_BUFFER_SIZE)):
        while audio_in_queue.empty():
            time.sleep(0.1)
        while not audio_in_queue.empty():
            left, right = audio_in_queue.get()
            lefts.append(left)
            rights.append(right)
    return lefts, rights




def main():
    ### init
    comedi = comedi_interface.Comedi()
    comedi.send_all(0)
    audio = alsa_interface.Audio()
    freq_queue, audio_in_queue = audio.begin()

    #freq_queue.put(0)
    
    if True:
        freq_queue.put(440)
        _, _ = wait(0.5, audio_in_queue) # better safe than sorry
        comedi.send(RELAY, 1)
        power_lefts, power_rights = wait(2.0, audio_in_queue)
        
        # turn off signal
        freq_queue.put(0)
        comedi.send(RELAY, 0)
        decay_lefts, decay_rights = wait(10.0, audio_in_queue)
    
    ### clean up
    audio.end()
    audio.close()

    left_all = numpy.array(decay_lefts).flatten()
    right_all = numpy.array(decay_rights).flatten()
    scipy.io.wavfile.write("test-left.wav", RATE,
        left_all)
    scipy.io.wavfile.write("test-right.wav", RATE,
        right_all)



if __name__ == "__main__":
    main()

