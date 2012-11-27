#!/usr/bin/env python

import os.path

FREQS = {
    'cello': { 'C': 65.2, 'G': 97.8, 'D': 146.7, 'A': 220.0},
    'viola': { 'C': 130.4, 'G': 195.6, 'D': 293.3, 'A': 440.0},
    'violin': { 'G': 195.6, 'D': 293.3, 'A': 440.0, 'E': 660.0},
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


