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


def process_bow_or_accel(violin, splitline, frame):
    string_number = int(splitline[2])
    bow_bridge_distance = float(splitline[3])
    bow_force = float(splitline[4])
    bow_velocity = float(splitline[5])
    bow_along = float(splitline[-1])  # 'b' is 6, 'a' is 7
    print ("%i\t%.3f" % (string_number, bow_along))
    violin.bow_action(string_number, bow_bridge_distance,
        bow_force, bow_along, frame)


def load_keyframes(violin, filename, fps):
    lines = open(filename).readlines()
    prev_frame = 0

    # used in case we stop bowing
    prev_bow = None

    for line in lines:
        if line[0] == '#':
            # comment line
            continue
        if len(line) < 2:
            # blank line
            continue
        splitline = line.split()
        seconds = float(splitline[1])
        seconds_end = seconds
        frame = int(seconds * fps)+1 # we start counting at 1

        # to allow lifting bow
        if frame != prev_frame:
            if prev_bow != None:
                process_bow_or_accel(violin, prev_bow, prev_frame)
                prev_bow = None

        action_text = splitline[0]
        if action_text == 'b' or action_text == 'a':
            # skip over the tons of bowing
            # TODO: take average of them instead of skipping?
            if frame == prev_frame:
                prev_bow = splitline
            else:
                process_bow_or_accel(violin, splitline, frame)
                prev_frame = frame
        elif action_text == 'f':
           # print ("FINGER:", splitline)
            string_number = int(splitline[2])
            finger_position = float(splitline[3])
            violin.finger_action(string_number, finger_position, frame)
            prev_frame = frame
        elif action_text == 'p':
            #print (splitline)
            string_number = int(splitline[2])
            pluck_position = float(splitline[3])
            # pluck lifts off the string 0.1 seconds later
            begin_lift_frame = int((seconds+0.1) * fps)+1 # we start counting at 1
            violin.pluck_action(string_number, pluck_position,
                frame, begin_lift_frame)
            prev_frame = frame
        elif action_text == 'c':
            camera_number = int(splitline[2])
            violin.camera_action(camera_number, frame)
        elif action_text == 'w':
            pass
        else:
            print ("ERROR: unrecognized command: %s" % action_text)
    frame_end = int(seconds_end * fps)
    return frame_end

