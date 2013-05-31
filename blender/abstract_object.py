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


class AbstractObject():
    def __init__(self):
        self.visible = None
        self.obj = None

    def set_visible(self, visible, frame=0):
        if self.visible != visible:
            self.visible = visible
            self.obj.hide = not visible
            self.obj.hide_render = not visible
            self.obj.keyframe_insert("hide", frame=frame)
            self.obj.keyframe_insert("hide_render", frame=frame)


