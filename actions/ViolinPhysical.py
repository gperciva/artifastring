#!/usr/bin/env python

# this sets the maximum time before "updates" to the actions
VIDEO_FPS = 25.0
BOW_LENGTH = 0.75


def semitones(num):
    return 1.0 - 1.0 / (1.05946309**num)


class ViolinPhysical:
    """Creates an .actions file (for both sound synthesis and
       visualization in Blender."""

    def __init__(self, filename_base):
        """ Constructor """
        self.seconds_action = 0.0
        self.seconds_target = 0.0

        self.actions = open(filename_base+'.actions', 'w')
        self.actions.write('# type\tseconds\tparams...\n')

        self.bow_bridge_distance = 0.0
        self.bow_force = 0.0
        self.bow_velocity = 0.0
        self.bow_pos_along = 0.0
        self.bow_string = 1
        self.bow_accel = 0.0


    def __del__(self):
        """ Destructor, calls self.end() if necessary. """
        if self.actions:
            self.end()

    def end(self):
        """ Write file and stop. """
        self.wait(0.2)
        self.actions.close()
        self.actions = None

    def finger(self, vln_string, finger_pos):
        """ Places finger on string. """
        vln_string_n = self.whichToNum(vln_string)
        Kf = 1.0
        self.actions.write("f\t%g\t%i\t%g\t%f\n" %
            (self.seconds_action, vln_string_n, finger_pos, Kf) )

    def bow(self, vln_string, bridge_distance, force,
            velocity, starting_bow_pos=-1):
        """ Moves bow; velocity is assumed to be constant
            until changed. """
        which_string_num = self.whichToNum(vln_string)
        if (which_string_num != self.bow_string):
            self.bowStop()
        self.bow_string = self.whichToNum(vln_string)
        self.bow_bridge_distance = bridge_distance
        self.bow_force = force
        self.bow_velocity = velocity
        self.bow_acccel = 0
        if starting_bow_pos >= 0:
            self.bow_pos_along = starting_bow_pos
        self.actions.write(
            'b\t%g\t%i\t%g\t%g\t%g\t%g\n' %(
            self.seconds_action,
            self.bow_string,
            self.bow_bridge_distance,
            self.bow_force,
            self.bow_velocity,
            self.bow_pos_along
            ) )

    def accel(self, vln_string, bridge_distance, force,
            velocity, accel, starting_bow_pos=-1):
        """ Moves bow; velocity is assumed to be constant
            until changed. """
        which_string_num = self.whichToNum(vln_string)
        if (which_string_num != self.bow_string):
            self.bowStop()
        self.bow_string = self.whichToNum(vln_string)
        self.bow_bridge_distance = bridge_distance
        self.bow_force = force
        self.bow_velocity = velocity
        self.bow_accel = accel
        if starting_bow_pos >= 0:
            self.bow_pos_along = starting_bow_pos
        self.actions.write(
            'a\t%g\t%i\t%g\t%g\t%g\t%g\t%g\n' %(
            self.seconds_action,
            self.bow_string,
            self.bow_bridge_distance,
            self.bow_force,
            self.bow_velocity,
            self.bow_accel,
            self.bow_pos_along
            ) )

    def bowStop(self):
        """ Sets bow velocity and force to 0.0.
            Called automatically when string is plucked. """
        self.bow_force = 0.0
        self.bow_velocity = 0.0
        self.actions.write(
            'b\t%g\t%i\t%g\t%g\t%g\t%g\n' %(
            self.seconds_action,
            self.bow_string,
            self.bow_bridge_distance,
            self.bow_force,
            self.bow_velocity,
            self.bow_pos_along
            ) )

    def comment(self, text):
        """ Adds a comment to the .actions file. """
        self.actions.write('#' + text + '\n')


    def pluck(self,which_string, finger_ratio_from_nut,
            pluck_ratio_from_bridge, pluck_force=1.0):
        """ Plucks a string. """
        if (self.bow_force != 0.0):
            self.bowStop()
        self.finger(which_string, finger_ratio_from_nut)
        string_num = self.whichToNum(which_string)
        self.actions.write("p\t%g\t%i\t%g\t%g\n" %
            (self.seconds_action, string_num,
             pluck_ratio_from_bridge, pluck_force) )

    def whichToNum(self,which_string):
        """ Internal function which maps strings like
            'vl_A' to a string number. """
        if (which_string >=0) and (which_string <= 3):
            return which_string
        if which_string == 'vl_E':
            string_num = 3
        elif which_string == 'vl_A':
            string_num = 2
        elif which_string == 'vl_D':
            string_num = 1
        elif which_string == 'vl_G':
            string_num = 0
        else:
            string_num = -1
        return string_num

    def wait(self, seconds):
        if (self.bow_velocity == 0.0):
            # bow not moving
            self.seconds_target += seconds
            self.actions.write('w\t%g\n' %(
                self.seconds_target))
            self.seconds_action += seconds
        else:
            # bow moving, split up into frames
            self.seconds_target += seconds
            delta_frames = int((self.seconds_target
                  - self.seconds_action)
                * VIDEO_FPS)
            for i in range(delta_frames):
                self.seconds_action += 1.0 / VIDEO_FPS
                self.bow_pos_along += self.bow_velocity / BOW_LENGTH / VIDEO_FPS
                if ((self.bow_pos_along > 1.0) or
                    (self.bow_pos_along < 0.0)):
                    print "ERROR: run out of bow, %g seconds!" % self.seconds_action
                if self.bow_accel == 0:
                    self.actions.write(
                    'b\t%g\t%i\t%g\t%g\t%g\t%g\n' %(
                    self.seconds_action,
                    self.bow_string,
                    self.bow_bridge_distance,
                    self.bow_force,
                    self.bow_velocity,
                    self.bow_pos_along
                    ) )
                else:
                    self.actions.write(
                    'a\t%g\t%i\t%g\t%g\t%g\t%g\t%g\n' %(
                    self.seconds_action,
                    self.bow_string,
                    self.bow_bridge_distance,
                    self.bow_force,
                    self.bow_velocity,
                    self.bow_accel,
                    self.bow_pos_along
                    ) )
            remaining_time = seconds - float(delta_frames) / VIDEO_FPS
            self.bow_pos_along += self.bow_velocity / BOW_LENGTH * remaining_time

            self.seconds_action += remaining_time
            if self.bow_accel == 0:
                self.actions.write(
                'b\t%g\t%i\t%g\t%g\t%g\t%g\n' %(
                self.seconds_action,
                self.bow_string,
                self.bow_bridge_distance,
                self.bow_force,
                self.bow_velocity,
                self.bow_pos_along
                ) )
            else:
                self.actions.write(
                'a\t%g\t%i\t%g\t%g\t%g\t%g\t%g\n' %(
                self.seconds_action,
                self.bow_string,
                self.bow_bridge_distance,
                self.bow_force,
                self.bow_velocity,
                self.bow_accel,
                self.bow_pos_along
                ) )
#            self.actions.write('w\t%g\n' %(
#                self.seconds_action))


