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


import bpy
import abstract_object

import math

class Pluck(abstract_object.AbstractObject):
    def __init__(self, violin):
        abstract_object.AbstractObject.__init__(self)
        self.violin = violin

        self.base_size = 0.01*self.violin.string_length

        self.obj = self.make_pluck()
        self.set_visible(False)

    def make_pluck(self):
        bpy.ops.mesh.primitive_cone_add(radius=self.base_size,
            depth=3*self.base_size)
        obj = bpy.context.active_object
        obj.name = "pluck"
        pluck_material = bpy.data.materials.new("pluck_material")
        pluck_material.diffuse_color = (1.0, 0.0, 0.5)
        obj.active_material = pluck_material
        # TODO: bad rotation!
        obj.rotation_euler = math.pi * self.violin.towards_frog
        # parent on violin, due to animation ?
        obj.parent = self.violin.obj
        return obj


    def move(self, string_number, pluck_position, frame, lift_frame):
        loc = self.violin.string_contact(string_number, pluck_position)
        loc += 1.5*self.base_size * self.violin.away_from_string
        # set properties and animation
        self.obj.location = loc
        self.obj.keyframe_insert("location", frame=frame)
        # extra
        self.pluck_raise(lift_frame)

    def pluck_raise(self, frame_start):
        off_target = 10*self.base_size
        for i in range(1,10):
            off_string = off_target * (1.0 - 0.9**i)
            #self.pluck_action(string_number, pluck_position, frame_start+i, off_string)
            # animation
            self.obj.location += off_string * self.violin.away_from_string
            self.obj.keyframe_insert("location", frame=frame_start+i)


