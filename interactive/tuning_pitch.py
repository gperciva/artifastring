#!/usr/bin/env python



def expected_pitch(instrument_number, which_string):
    # tuned to equal temperament
    if instrument_number == 0:
        if which_string == 3:
            return 659.3
        if which_string == 2:
            return 440.0
        if which_string == 1:
            return 293.7
        if which_string == 0:
            return 196.0
    if instrument_number == 1:
        if which_string == 3:
            return 440.0
        if which_string == 2:
            return 293.7
        if which_string == 1:
            return 196.0
        if which_string == 0:
            return 130.8
    if instrument_number == 2:
        if which_string == 3:
            return 220.0
        if which_string == 2:
            return 146.8
        if which_string == 1:
            return 98.0
        if which_string == 0:
            return 65.4



