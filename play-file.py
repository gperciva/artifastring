#!/usr/bin/env python

##
# Copyright 2010 Graham Percival
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

import sys
import violin_instrument
import monowav

def actions(violin, params):
	if params[0] == 'f':
		violin.finger( int(params[2]), float(params[3]))
	elif params[0] == 'p':
		violin.pluck( int(params[2]), float(params[3]),
			float(params[4]))
	elif params[0] == 'b':
		violin.bow( int(params[2]), float(params[3]),
			float(params[4]), float(params[5]))
	elif params[0] == 'w':
		# do nothing -- it's a "wait" command
		pass
	else:
		print "ERROR: unrecognized command!  ", params


def parseFile(lines, wavfile):
	violin = violin_instrument.ViolinInstrument()
	total_samples = 0

	for i, line in enumerate(lines):
		# is a comment
		if (line[0] == '#'):
			continue
		splitline = line.split()

		# advance time
		action_time = float( splitline[1] )
		delta_samples = 44100.0*action_time - total_samples
		delta_samples = int(delta_samples)
		if delta_samples > 0:
#			print "advancing", delta_samples, "samples"
			buf = wavfile.request_fill(delta_samples)
			violin.wait_samples(buf, delta_samples)
			total_samples += delta_samples
		elif delta_samples == 0:
			pass
		else:
			print "ERROR: move backwards in time? line", i
		actions(violin,splitline)

def main():
	filename = sys.argv[1]
	lines = open(filename).readlines()
	outfilename = filename.split('.')[0] + '.wav'
	wavfile = monowav.MonoWav( outfilename )
	parseFile(lines, wavfile)

main()

