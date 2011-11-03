#!/usr/bin/env python

import partials

REPLACEMENTS_B = {
#    'violin-d-jen': 1.55e-04,

#    'violin-d-colin': 1.55e-04,
}
REPLACEMENTS_B_DECAYFIT_ONLY = {
#    'violin-d-jen': 1.55e-04,

#    'violin-d-colin': 1.55e-04,
#    'violin-d-graham': 1.55e-04,
}
NOTES_B = {
    'violin-d-colin': 'a',
    'violin-g-jen': 'a',
    'viola-c-wcams': 'a',

    'viola-d-wcams': 'b',
    #'violin-d-colin': 'b',
    #'violin-g-graham': 'b',

    #'viola-a-graham': 'c',
    #'viola-a-wcams': 'c',

    #'cello-c-glasgow': 'd',
}

def adjust_decayfit_only(basename, B):
    try:
        new_B = REPLACEMENTS_B_DECAYFIT_ONLY[basename]
        return new_B
    except:
        return B

def adjust(basename, lim, f0, B):
    try:
        new_B = REPLACEMENTS_B[basename]
        detected_fn = partials.peak_stiff(f0, lim, B)
        adjusted_fn = partials.peak_stiff(f0, lim, new_B)
        delta_fn = abs(adjusted_fn - detected_fn)
        return new_B, delta_fn
    except:
        return None, None

def notes_B(basename):
    try:
        text = NOTES_B[basename]
        return "(%s)" % text
    except:
        return ""

