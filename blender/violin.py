import bpy
import mathutils

import math
import collections

import bow
import pluck
import finger

import utils

STRINGS=['g', 'd', 'a', 'e']
StringEnds = collections.namedtuple("StringEnds", "bridge, nut")

class Violin():
    def __init__(self):
        self.obj = bpy.data.objects["violin"]
        ### coordinates in violin-space
        ### (can't change parents during animation, so no string-space coords)
        self.string_coords    = self.get_string_coords()

        ### normalized "coordinate system" of violin
        self.away_from_bridge = self.get_away_from_bridge()
        self.towards_frog     = self.get_towards_frog()
        self.away_from_string = self.get_away_from_string()

        ### other stup
        self.string_length    = self.get_string_length()
        self.string_angles    = self.get_string_angles()

        ### pluck
        self.pluck = pluck.Pluck(self)

        ### bow
        self.bow = bow.Bow(self)

        ### fingers
        self.fingers = list(map(lambda x: finger.Finger(self, x),
                            range(len(STRINGS))))

        ### initialize positions
        self.bow_action(0, 0, 0, 0, 1)
        for i in range(len(STRINGS)):
            self.finger_action(i, 0.0, 1)


    ### get axis information from model
    def get_string_coords(self):
        """ gets the coordinates of the strings at bridge and nut,
            using relative coordinates to the violin body. """
        string_coords = []
        for i, st in enumerate(STRINGS):
            string_object = self.get_string_obj(i)
            # only do this once per string, for efficency
            vertex_groups = utils.getVertGroups(string_object)
            # support two naming schemes
            if "bridge-mark" in string_object.vertex_groups:
                bridge = utils.mean_of_vertex_group(string_object,vertex_groups,
                    "bridge-mark")
                nut    = utils.mean_of_vertex_group(string_object,vertex_groups,
                    "nut-mark")
            else:
                bridge = utils.mean_of_vertex_group(string_object,vertex_groups,
                    st+"-bridge-mark")
                nut    = utils.mean_of_vertex_group(string_object,vertex_groups,
                    st+"-nut-mark")
            bridge *= string_object.matrix_local
            nut    *= string_object.matrix_local
            string_coords.append( StringEnds(bridge, nut) )
        return string_coords

    def get_string_length(self):
        e_length = self.string_coords[0].bridge - self.string_coords[0].nut
        return e_length.length


    def get_away_from_bridge(self):
        away_from_bridge = mathutils.Vector((0,0,0))
        # find mean vector
        for st_coords in self.string_coords:
            away_from_bridge += (st_coords.nut - st_coords.bridge)
        away_from_bridge.normalize()
        return away_from_bridge

    def get_towards_frog(self):
        e_bridge_violin_coords = self.string_coords[0].bridge
        g_bridge_violin_coords = self.string_coords[3].bridge
        towards_frog = e_bridge_violin_coords - g_bridge_violin_coords
        towards_frog.normalize()
        return towards_frog
    
    def get_away_from_string(self):
        away_from_string = self.away_from_bridge.cross(self.towards_frog)
        away_from_string.normalize()
        return away_from_string


    ### convenience functions
    def get_string_obj(self, index):
        st_char = STRINGS[index]
        return bpy.data.objects[st_char+"-string"]

    def string_contact(self, string_number, along):
        contact = self.string_coords[string_number].bridge.lerp(
            self.string_coords[string_number].nut, along)
        return contact

    def get_string_angles(self):
        # TODO: iffy calculations
        g_a = self.string_coords[2].bridge - self.string_coords[0].nut
        d_ang = self.towards_frog.angle(g_a) - math.pi/2
        d_ang = -1*d_ang

        # TODO: ouch hard-coding!
        g_ang = d_ang - 0.3

        #e_a = self.string_coords[3].bridge - self.string_coords[2].nut
        e_d = self.string_coords[3].bridge - self.string_coords[1].nut
        a_ang = self.towards_frog.angle(e_d) - math.pi/2
        #a_ang = e_a.angle(e_d)
        e_ang = a_ang + 0.3

        angles = [g_ang, d_ang, a_ang, e_ang]
#        print (angles)
        return angles


    ### actions
    def finger_action(self, string_number, finger_position, frame):
        self.fingers[string_number].move(finger_position, frame)

    def pluck_action(self, string_number, pluck_position, frame):
        self.pluck.set_visible(True, frame)
        self.bow.set_visible(False, frame)
        self.pluck.move(string_number, pluck_position, frame)

    def bow_action(self, string_number, bow_bridge_distance,
            bow_force, bow_along, frame):
        self.pluck.set_visible(False, frame)
        self.bow.set_visible(True, frame)
        self.bow.move(self, string_number, bow_bridge_distance,
            bow_force, bow_along, frame)



    def debug(self):
        print()
        print("----- Violin debug")
        print("\tbridges:")
        for sc in self.string_coords:
            print("", sc[0])
        print("\tnuts:")
        for sc in self.string_coords:
            print("", sc[1])
        print()
        print("\taway from bridge:\n", self.away_from_bridge)
        print("\ttowards frog:\n", self.towards_frog)
        print("\taway from string:\n", self.away_from_string)


