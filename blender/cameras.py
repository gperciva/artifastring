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
import mathutils

def cycle_cameras(cycle_seconds, frame_end, fps):
    num_cameras = len(bpy.data.cameras) -1 # don't count the active camera
    for i in range( int((frame_end/fps)/cycle_seconds) ):
        frame_num = i*cycle_seconds*fps
        now = i % num_cameras
        prev = (i-1) % num_cameras

        set_camera(now, prev, frame_num)


def set_camera(camera_number, prev, frame_num):
    cameras = list(filter(lambda obj_key: obj_key.startswith("Camera.0"),
        bpy.data.objects.keys()))
    cameras.sort() # just in case
    camera_locations = list(
        map(lambda cam: mathutils.Vector(bpy.data.objects.get(cam).location),
            cameras))
    camera_rotations = list(
        map(lambda cam: mathutils.Euler(bpy.data.objects.get(cam).rotation_euler),
            cameras))

    if frame_num > 0:
        bpy.context.scene.camera.rotation_euler = camera_rotations[prev]
        bpy.context.scene.camera.location = camera_locations[prev]
        bpy.context.scene.camera.keyframe_insert("rotation_euler", frame = (frame_num-1))
        bpy.context.scene.camera.keyframe_insert("location", frame = (frame_num-1))
    
    bpy.context.scene.camera.rotation_euler = camera_rotations[camera_number]
    bpy.context.scene.camera.location = camera_locations[camera_number]
    bpy.context.scene.camera.keyframe_insert("rotation_euler", frame = frame_num)
    bpy.context.scene.camera.keyframe_insert("location", frame = frame_num)


