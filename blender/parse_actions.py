
def process_bow(violin, splitline, frame):
    string_number = int(splitline[2])
    bow_bridge_distance = float(splitline[3])
    bow_force = float(splitline[4])
    bow_velocity = float(splitline[5])
    bow_along = float(splitline[6])
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
        splitline = line.split()
        seconds = float(splitline[1])
        frame = int(seconds * fps)+1 # we start counting at 1

        # to allow lifting bow
        if frame != prev_frame:
            if prev_bow != None:
                process_bow(violin, prev_bow, prev_frame)
                prev_bow = None

        action_text = splitline[0]
        if action_text == 'b':
            # skip over the tons of bowing
            # TODO: take average of them instead of skipping?
            if frame == prev_frame:
                prev_bow = splitline
            else:
                process_bow(violin, splitline, frame)
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
            violin.pluck_action(string_number, pluck_position, frame)
            prev_frame = frame
        elif action_text == 'c':
            camera_number = int(splitline[2])
            violin.camera_action(camera_number, frame)
        elif action_text == 'w':
            pass
        else:
            print ("ERROR: unrecognized command: %s" % action_text)
    seconds_end = float(lines[-1].split()[1])
    frame_end = int(seconds_end * fps)
    return frame_end

