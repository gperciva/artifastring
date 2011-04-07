import Blender
import math

# some computers need this, some don't.  No clue why.  :(
import sys
sys.path.append('.')

import shared

## general time
thisFrame = Blender.Get('curframe')
fps = Blender.Scene.GetCurrent().getRenderingContext().fps
current_time = float(thisFrame) / fps


def get_splitline():
	line = Blender.actions_lines[Blender.actions_index]
	while (line[0] == '#'):
		Blender.actions_index += 1
		line = Blender.actions_lines[Blender.actions_index]
	splitline = line.split()
	return splitline


def finger(splitline):
	finger_string_num = int( splitline[2] )
	finger_string = str( finger_string_num )
	finger = Blender.Object.Get('Finger'+'-'+finger_string)
	along = 1.0 - float(splitline[3])
	finger.setLocation( shared.pos(finger_string_num, along, finger=True) )

def raisePlucks():
	pluck = Blender.Object.Get('Pluck')
	steps = int(thisFrame - Blender.pluckFrame)
	delta_y = 0.1
	pluck.LocY = (Blender.pluckInit+delta_y) - delta_y*(0.9**steps)

def pluck(splitline):
	# disable bow
	Blender.useBow = False
	bow = Blender.Object.Get('arco')
	bow.layers = []

	seconds_action = float(splitline[1])
	pluck_string_num = int( splitline[2] )
	pluck_pos = float( splitline[3] )

	pluck_string = str( pluck_string_num )
	pluck = Blender.Object.Get('Pluck')
	pluck.setLocation( shared.pos(pluck_string_num, pluck_pos) )

	Blender.pluckInit = pluck.LocY
	Blender.pluckFrame = seconds_action * float(fps)
	# make visible
	pluck.layers = range(1,21)



####################### bowing stuff
def string_angle(bow_string):
	angle = 0.0
	if bow_string == 0:
		#angle = 5.5  # in radians
		angle = -20.0 *math.pi/180.0
	elif bow_string == 1:
		#angle = 5.0
		angle = -7.0 *math.pi/180.0
	elif bow_string == 2:
		#angle = 5.0
		angle = 7.0 *math.pi/180.0
	else:
		#angle = 5.0
		angle = 20.0 *math.pi/180.0
	return angle

def bow(splitline):
	Blender.useBow = True
	# disable plucks
	pluck = Blender.Object.Get('Pluck')
	pluck.layers = []

	bow_string_num = int( splitline[2] )
	bow_bridge_distance = float( splitline[3] )
	bow_along = float( splitline[6] )

	bow = Blender.Object.Get('arco')
	bow.layers = range(1,21)

	angle = string_angle(bow_string_num)
	# TODO: bad hack for bow_along; replace with a proper
	# distances based on vertex locations (maybe by
	# making a VertexGroup for the bow hair?)
	h = 0.75*(0.5 - (bow_along + 0.01))
	# NEW COORDINATE SYSTEM:
	# X: along bow       (positive is frog)
	# Y: off string-ish  (positive is off)
	# Z: away from bridge-ish   (positive is fingerboard)
	bow.RotX = angle
	contact = shared.pos(bow_string_num, bow_bridge_distance)
	bow.LocX = contact[0] + h*math.cos(angle)
	bow.LocY = contact[1] + h*math.sin(angle)
	bow.LocZ = contact[2]

# TODO: we need this in both places, but it's icky
if not Blender.useBow:
	raisePlucks()

splitline = get_splitline()
seconds_action = float(splitline[1])
while (seconds_action < current_time):
	if (splitline[0] == 'f'):
		finger(splitline)
	if (splitline[0] == 'p'):
		pluck(splitline)
	if (splitline[0] == 'b'):
		bow(splitline)

	Blender.actions_index += 1
	splitline = get_splitline()
	seconds_action = float(splitline[1])

	if not Blender.useBow:
		raisePlucks()

