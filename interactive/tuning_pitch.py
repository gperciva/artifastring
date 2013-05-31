#!/usr/bin/env python


##
# Copyright 2010--2013 Graham Percival
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



