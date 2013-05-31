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

#import bpy
import mathutils

###### convenience functions
def getVertGroups(obj):
    ### find index of name
    groups = {}
    for g in obj.vertex_groups:
        groups[g.name] = []
    ### find all vertices matching those groups
    for v in obj.data.vertices:
        for g in v.groups:
            groups[ obj.vertex_groups[g.group].name ].append(v.index)
    return groups

def mean_of_vertex_group(object, group_list, group_name):
    vertex_indices = group_list[group_name]
    means = mathutils.Vector((0, 0, 0))
    for index in vertex_indices:
        coords = object.data.vertices[index].co
        for j in range(len(coords)):
            means[j] += coords[j] / len(vertex_indices)
    return means


