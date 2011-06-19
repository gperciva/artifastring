import bpy
import mathutils

import math

import abstract_object
import utils

class Bow(abstract_object.AbstractObject):
    def __init__(self, violin):
        abstract_object.AbstractObject.__init__(self)
        self.violin = violin

        self.size = self.violin.string_length

        self.obj = bpy.data.objects["bow"]
        # normalized "coordinate system" of bow
        self.frog, self.tip, self.winding = self.get_bow_points()
        self.along_hair_towards_frog = self.get_along_hair_towards_frog()
        self.away_from_string = self.get_away_from_string()
        self.towards_lh_fingers = self.get_towards_lh_fingers()

        self.set_visible(False)


    ### get axis information from model
    def get_bow_points(self):
        bow_obj = bpy.data.objects["bow"]
        #only do this once, for efficency
        vertex_groups = utils.getVertGroups(bow_obj)
        frog = utils.mean_of_vertex_group(bow_obj, vertex_groups, "hair-frog")
        tip  = utils.mean_of_vertex_group(bow_obj, vertex_groups, "hair-point")
        wind = utils.mean_of_vertex_group(bow_obj, vertex_groups, "wrapping")
        return frog, tip, wind

    def get_along_hair_towards_frog(self):
        frog_tip = self.tip - self.frog
        frog_tip.normalize()
        return frog_tip

    def get_away_from_string(self):
        intersect_point = mathutils.geometry.intersect_point_line(
            self.winding, self.frog, self.tip)[0]
        intersect_line  = self.winding - intersect_point
        intersect_line.normalize()
        return intersect_line

    def get_towards_lh_fingers(self):
        lh_fingers = self.away_from_string.cross(self.along_hair_towards_frog)
        return lh_fingers


    ### action
    def move(self, violin, string_number, bow_bridge_distance,
            bow_force, bow_along, frame):
        # TODO: iffy?  want to disable linear interpolation for
        # the next keyframe.
        if frame > 0:
            self.obj.keyframe_insert("rotation_euler", frame=frame-1)
            self.obj.keyframe_insert("location", frame=frame-1)
        string_contact = violin.string_contact(
            string_number, bow_bridge_distance)

        hair_along = self.frog.lerp(self.tip, bow_along)
        distance_along = hair_along.dot(self.along_hair_towards_frog)

        bow_hair_extra_away = -hair_along.project(self.violin.away_from_string)

        angle = self.violin.string_angles[string_number]
        rotation = angle * violin.away_from_bridge

        # TODO: this is iffy
        origin_transpose = mathutils.Vector((0,0,0))
        origin_transpose += (distance_along * violin.towards_frog
            * math.cos(angle) * -1)
        origin_transpose += (distance_along * violin.away_from_string
            * math.sin(angle) * -1)

        bow_loc = string_contact + origin_transpose
        bow_loc += bow_hair_extra_away
        if bow_force < 0:
            bow_loc += 0.1*self.size * violin.away_from_string

        # set properties
        self.obj.rotation_euler = rotation
        self.obj.location = bow_loc
        # animation
        self.obj.keyframe_insert("location", frame=frame)
        self.obj.keyframe_insert("rotation_euler", frame=frame)


    def debug(self):
        print()
        print("----- Bow debug")
        print("\ttip:\n", self.tip)
        print("\tfrog:\n", self.frog)
        print("\twinding:\n", self.winding)
        print()
        print("\talong_hair_towards_frog:\n", self.along_hair_towards_frog)
        print("\taway from string:\n", self.away_from_string)
        print("\ttowars_lh_fingers:\n", self.towards_lh_fingers)


