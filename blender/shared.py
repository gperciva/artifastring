# TODO: should be I really be storing data in Blender ?
import Blender


# G D A E: bridge xyz, fingerboard xyz
# TODO: use vertex groups instead of hard-coded values
Blender.strings = [
  [ [ 0.016, 0.109, 0.172], [ 0.008, 0.057, 0.507], ],
  [ [ 0.005, 0.113, 0.172], [ 0.003, 0.059, 0.507], ],
  [ [-0.005, 0.113, 0.172], [-0.003, 0.059, 0.507], ],
  [ [-0.016, 0.109, 0.172], [-0.008, 0.057, 0.507], ],
]
# TODO: find a better way of making sure that the fingers
#       go on top of strings.
#       (i.e. using pos(st, along) , or constraits, or something?)
FINGER_X_OFFSET = -0.0005
FINGER_Y_OFFSET =  0.0004
BOW_Y_OFFSET = 0.015

def pos(st, along, finger=False):
	" 'along' is the distance away from the bridge."
	pos = [0,0,0]
#	print "bridge:     \t", Blender.strings[st][0]
#	print "fingerboard:\t", Blender.strings[st][1]
	for i in range(3):
		# linear interpolation
		x0 = 0.0
		y0 = Blender.strings[st][0][i]
		x1 = 1.0
		y1 = Blender.strings[st][1][i]
		x = along
		pos[i] = y0 + (((x-x0)*y1 - (x-x0)*y0) / (x1-x0))
	if finger:
		pos[0] += FINGER_X_OFFSET
		pos[1] += FINGER_Y_OFFSET
	else:
		pos[1] += BOW_Y_OFFSET
	return pos




