#!/usr/bin/env python

import partials

REPLACEMENTS_B = {
    'violin-d-jen': 1.55e-04,

#    'violin-d-colin': 1.55e-04,
}
NOTES_REMOVING = {
}
NOTES_DECAYS = {
    'viola-g-wcams': 'a',
}

def adjust(basename, lim, f0, B):
    try:
        new_B = REPLACEMENTS_B[basename]
        detected_fn = partials.peak_stiff(f0, lim, B)
        adjusted_fn = partials.peak_stiff(f0, lim, new_B)
        delta_fn = abs(adjusted_fn - detected_fn)
        return new_B, delta_fn
    except:
        return None, None

def notes_removing(basename):
    try:
        text = NOTES_REMOVING[basename]
        return "(%s)" % text
    except:
        return ""

def notes_decays(basename):
    try:
        text = NOTES_DECAYS[basename]
        return "(%s)" % text
    except:
        return ""

