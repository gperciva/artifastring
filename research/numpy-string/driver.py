#!/usr/bin/env python

import os


THESIS_TYPES = [
###### these are approved
### section 2.1.2
    #"pluck finger begin-release violin-g",
    #"pluck finger forces violin-g",
    #"pluck finger movie begin violin-g",
    #"pluck finger movie middle violin-g",
    #"pluck finger movie-long violin-g",

### section 2.1.3
#    "bow finger movie begin violin-g",
#    "bow finger movie middle violin-g",
#    "bow harmonic light violin-g",
#    "bow harmonic normal violin-g",

### section 2.2.1
#    "pluck finger two-plucks undamped violin-g",
#    "pluck finger two-plucks damped violin-g",
#    "pluck open one-pluck-force violin-g",
#    "pluck open two-pluck-force violin-g", # no plural
#    "pluck finger-force-one violin-g",
#    "pluck finger-force-two violin-g", # no plural
#    "pluck beating unit",
    #"pluck release-force two violin-g",
    #"pluck release-force three violin-g",
    #"pluck release-force four violin-g",

### section 2.2.2
    #"bow slip-single freq-low violin-e",
    #"bow slip-single freq-moderate violin-e",
    #"bow slip-single freq-high violin-e",
    #"bow slip-change negative only violin-g",
    #"bow slip-change both violin-g",
    #"bow slip-change no skips safety violin-e",
    #"bow slip-change both safety violin-e",


###### under consideration
### section 2.1.2

### section 2.1.3

### section 2.2.2

### section 3.4.1
    #"ns 32 finger cello-c",
    #"ns 40 finger cello-c",
    #"ns 48 finger cello-c",
    #"ns 64 finger cello-c",
    #"ns 32 finger violin-e",
    #"ns 40 finger violin-e",
    #"ns 48 finger violin-e",
    #"ns 64 finger violin-e",
    #"ns 32 bow cello-c",
    #"ns 40 bow cello-c",
    #"ns 48 bow cello-c",
    #"ns 64 bow cello-c",
    #"ns 32 bow violin-e",
    #"ns 40 bow violin-e",
    #"ns 48 bow violin-e",
    #"ns 64 bow violin-e",



###### not verified
#    "pluck decay open violin-g",
#    "pluck decay first violin-g",
#
#    "bow rational moderate violin-g",
#    "bow rational none violin-g",
#    "bow frequency low violin-e",
#    "bow frequency normal violin-e",
#    "bow frequency high violin-e",
#
#    "bow harmonic light violin-g",
#    "bow harmonic normal violin-g",
#
#    "pluck total forces two violin-g",
#    "pluck total forces three violin-g",
#
#    "finger freqs triple violin-g",
#    "finger freqs single violin-g",
#
#    "finger beating single violin-g",
#    "finger beating double violin-g",
#    "finger beating triple violin-g",
#    "finger unit string violin-g",
#
##    "multi pluck two violin-g",
##    "multi pluck three violin-g",
#
#
    "NULL violin-g"
]

for i, thesis in enumerate(THESIS_TYPES):
    cmd = "./main.py %s" % (thesis)
    print cmd
    #if not thesis.startswith("ns "):
    #    continue
    os.system(cmd)
    print "**************** completed %i / %i." % (i+1, len(THESIS_TYPES))




