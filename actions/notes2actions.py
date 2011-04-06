#!/usr/bin/env python

### Very bad, and old+unused, file.
# Vivi does a much better job of producing an .actions file based
# on a .notes file from LilyPond.  I wrote this in the very early
# days; I'm only including it here to give people an idea of the
# overall structure in case they want to try out stuff before I
# release Vivi in a few days.
#
# THIS IS NOT AN EXAMPLE OF MY REAL PROGRAMMING SKILL.
#
# in fact, I consider this file to be under the CRAPL.
#   http://matt.might.net/articles/crapl/

import sys

import ViolinPhysical
from ViolinPhysical import semitones
violin = ''
bp = 0.08
dtc = 1.0/1000.0

sixteenth = 0.15544 # 30 seconds / 193 16th notes.
#sixteenth = 0.20


tempo = 30.0/12.0

def suzuki(which_string, factor, direction):
	force = 1.5
	force_target = 0.5
	velocity = 0.0
	accel = 20.0 * direction
	target_velocity = 0.5
	duration = sixteenth * factor
	current_time = 0.0
	while ((velocity*direction < target_velocity) and
			(current_time < duration/2.0)):
		force -= (force-force_target)/50.0
		velocity += accel * dtc
		violin.bow(which_string, bp, force, velocity, 0.6-direction*0.2)
		violin.wait(dtc)
		current_time += dtc
	flat = duration - 2.0*current_time
	violin.wait(flat)
	current_time += flat
	while ((velocity*direction > 0 ) and
			(current_time < duration)):
		velocity -= 2.0 * accel * dtc
		if (velocity*duration) < 0:
			velocity = 0
		violin.bow(which_string, bp, force, velocity)
		violin.wait(dtc)
		current_time += dtc
	violin.wait( duration - current_time );

def six(note):
	if (note < 4):
		which_string = 'vl_D'
	else:
		which_string = 'vl_A'
	if (note%4 == 0):
		violin.finger(which_string, semitones(0))
	elif (note%4 == 1):
		violin.finger(which_string, semitones(2))
	elif (note%4 == 2):
		violin.finger(which_string, semitones(4))
	elif (note%4 == 3):
		violin.finger(which_string, semitones(5))
	else:
		print "ERROR: bad note"
	suzuki(which_string, 1, 1)
	suzuki(which_string, 1, -1)
	suzuki(which_string, 1, 1)
	suzuki(which_string, 1, -1)
	suzuki(which_string, 1.5, 1)
	violin.wait(sixteenth*0.5)
	suzuki(which_string, 1.5, -1)
	violin.wait(sixteenth*0.5)
	violin.bow(which_string, bp, 1.0, 0.0)

def change_string(old_string, new_string, duration):
	force_was = 0.49
	steps = int(duration / dtc)
	#lighten = -force_was / steps
	linear = 0.0
	old_force = force_was
	new_force = 0.0
	
	violin.comment("begin fade-off string")
	#old_force = 0.1
	#violin.bow(old_string, bp, old_force, 0.0)
	violin.bow(old_string, bp, old_force, 0.0)
	violin.wait(dtc)
	#return
	
	for i in range(steps-1):
		violin.comment("top loop")
		#delta = -old_force / 2.0
		if (old_force > 0.20):
			delta = -old_force / 8.0
		else:
			if linear == 0.0:
				linear = -old_force / (steps-1-i)
				lighten = linear
				violin.comment("change linear: "+str(lighten))
	#		#delta = -old_force / 10.0
			delta = lighten
		lighten = delta
		violin.comment("change: "+str(lighten))
		old_force += lighten
		if (old_force < 0):
			old_force = 0.0
		#new_force += delta
		violin.bow(old_string, bp, old_force, 0.0)
#		violin.bow(new_string, bp, new_force, 0.0)
		violin.wait(dtc)
	violin.bow(old_string, bp, 0.0, 0.0)

def get_naive_string(pitch):
	if (pitch < 62):
		return 0
	elif (pitch < 69):
		return 1
	elif (pitch < 76):
		return 2
	else:
		return 3

def get_finger_naive(pitch):
	which_string = get_naive_string(pitch)
	finger_semitones = pitch - (55 + 7*which_string)
	position = semitones(finger_semitones)
	return which_string, position


def write_actions(notes):
	bow_dir = 1
	for i, note in enumerate(notes):
		time = note[0]
		pitch = note[1]
		dur = note[2]

		which_string, position = get_finger_naive(pitch)
		if (i+1 < len(notes)):
			next_string, next_pos = get_finger_naive(notes[i+1][1])
		else:
			next_string = which_string

		violin.finger(which_string, position)
		if dur == '16':
			suzuki(which_string, 1, bow_dir)
		elif dur == '8':
			suzuki(which_string, 1.5, bow_dir)
			if which_string == next_string:
				violin.wait(sixteenth*0.5)
			else:
#				violin.waitSeconds(sixteenth*0.25)
				change_string(which_string,
					next_string, sixteenth*0.5)
		bow_dir *= -1
	violin.end()


def main():
	filename = sys.argv[1]
	lines = open(filename).readlines()
	global violin
	violin = ViolinPhysical.ViolinPhysical(filename.split('.')[0])
	notes = []
	for line in lines:
		splitline = line.split('\t')
		time = float(splitline[0])
		pitch = float(splitline[1])
		dur = splitline[2].rstrip()
		notes.append( (time, pitch, dur) )
	write_actions(notes)
	
if __name__ == "__main__":
	main()


