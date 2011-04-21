# TODO: should be I really be storing data in Blender ?
import Blender

print "imported shared"

#bow_mesh = bow.getData(mesh=True)
#hair_frog_index = bow.getData(mesh=True).getVertsFromGroup("hair-frog")[0]
#hair_tip_index = bow.getData(mesh=True).getVertsFromGroup("hair-tip")[0]
STRINGS = ['e', 'a', 'd', 'g']

#violin = Blender.Object.Get('violin')
#violin_mesh = violin.getData(mesh=True)
string_coords = []

def mean_of_vertex_group(mesh, object_matrix, group_name):
	means = [0, 0, 0]
	vertex_indices = string_mesh.getVertsFromGroup(group_name)
	for index in vertex_indices:
		global_coords = mesh.verts[index].co * object_matrix
		for j in range(len(global_coords)):
			means[j] += global_coords[j] / len(vertex_indices)
	return means


for st in STRINGS:
	string_object = Blender.Object.Get(st+'-string')
	string_mesh = string_object.getData(mesh=True)

	nut = mean_of_vertex_group(string_mesh, string_object.matrix, "nut-mark")
	bridge = mean_of_vertex_group(string_mesh, string_object.matrix, "bridge-mark")

	string_coords.append( (bridge, nut) )


print "bridges"
for i in string_coords:
	print i[0]
print "nuts"
for i in string_coords:
	print i[1]

#print hair_frog_index
#print bow_mesh.verts[hair_frog_index].co
#print bow_mesh.verts[hair_frog_index].co[0]
#print bow_mesh.verts[hair_frog_index].co[1]
#print bow_mesh.verts[hair_frog_index].co[2]


# G D A E: bridge xyz, fingerboard xyz
# TODO: use vertex groups instead of hard-coded values
#Blender.strings = [
#  [ [ 0.016, 0.109, 0.172], [ 0.008, 0.057, 0.507], ],
#  [ [ 0.005, 0.113, 0.172], [ 0.003, 0.059, 0.507], ],
#  [ [-0.005, 0.113, 0.172], [-0.003, 0.059, 0.507], ],
#  [ [-0.016, 0.109, 0.172], [-0.008, 0.057, 0.507], ],
#]
# TODO: find a better way of making sure that the fingers
#       go on top of strings.
#       (i.e. using pos(st, along) , or constraits, or something?)
FINGER_X_OFFSET = -0.0005
FINGER_Y_OFFSET =  0.0004
#BOW_Y_OFFSET = 0.015
BOW_Y_OFFSET = 0.0

def pos(st, along, finger=False):
	" 'along' is the distance away from the bridge."
	pos = [0,0,0]
	for i in range(3):
		# linear interpolation
		x0 = 0.0
		y0 = string_coords[st][0][i]
		x1 = 1.0
		y1 = string_coords[st][1][i]
		x = along
		pos[i] = y0 + (((x-x0)*y1 - (x-x0)*y0) / (x1-x0))
	if finger:
		pos[0] += FINGER_X_OFFSET
		pos[1] += FINGER_Y_OFFSET
	else:
		pos[1] += BOW_Y_OFFSET
	return pos




