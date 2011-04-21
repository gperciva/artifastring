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


