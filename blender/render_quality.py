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

def setup(quality, fps):
    ### unified settings
    render = bpy.context.scene.render
    render.fps = fps

    render.image_settings.file_format = 'TARGA'
    render.parts_x = 1
    render.parts_y = 1
    # HDTV 720p resolution
    render.resolution_x = 1280
    render.resolution_y = 720
    if quality==2:
        render.resolution_percentage = 100
    elif quality == 1:
        render.resolution_percentage = 50
    else:
        # VGA resolution
        render.resolution_percentage = 50
    # other options
    if quality < 2:
        render.use_antialiasing = False
        render.use_color_management = False
        render.use_compositing = False
        render.use_envmaps = False
        render.use_motion_blur = False
        render.use_raytrace = False
        render.use_sequencer = False
        render.use_shadows = False
        render.use_sss = False
        render.use_textures = False
        render.use_simplify = True

    bpy.context.scene.use_gravity = False

