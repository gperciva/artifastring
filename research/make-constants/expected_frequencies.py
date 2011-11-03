#!/usr/bin/env python

import os.path

FREQS = {
    'cello': { 'c': 65.2, 'g': 97.8, 'd': 146.7, 'a': 220.0},
    'viola': { 'c': 130.4, 'g': 195.6, 'd': 293.3, 'a': 440.0},
    'violin': { 'g': 195.6, 'd': 293.3, 'a': 440.0, 'e': 660.0},
    }

def get_freq_from_filename(wav_filename):
    #print wav_filename
    instrument = os.path.basename(wav_filename).split('-')[0]
    string_text = os.path.basename(wav_filename).split('-')[1]
    #print instrument
    #print string_text
    try:
        freq = FREQS[instrument][string_text]
    except:
        #for inst in FREQS.iterkeys():
        #    print inst
        print "Don't recognize the instrument or string"
        # HACK: remove
        return 220.0
        exit(0)
    return freq


