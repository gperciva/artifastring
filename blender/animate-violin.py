import Blender
import math

# TODO: most of this file isn't used any more; clean up.

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

def pos(st, along):
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
	return pos


############# general geometry
def centerY(bow_string):
	return bow_string*1.0

def centerZ(bow_string):
	if bow_string == 1 or bow_string == 2:
		return 0.5
	else:
		return 0.0


def finger(splitline):
	finger_string_num = int( splitline[2] )
	if finger_string_num >= 0:
		finger_string = str( finger_string_num )
		#print finger_string
		finger = Blender.Object.Get('Finger'+'-'+finger_string)
		#finger.LocX = float( splitline[3] ) * 33.0 - 16.5
		along = 1.0 - float(splitline[3])
		fp = pos(finger_string_num, along)
		finger.LocX = fp[0]
		finger.LocY = fp[1]
		finger.LocZ = fp[2]

def raisePlucks():
#	for i in range(4):
#		pluck = Blender.Object.Get('Pluck'+'-'+str(i))
#		center_z = centerZ( i )
#		if pluck.LocZ < (center_z + 4.0):
#			pluck.LocZ += 0.25
#		center_z = centerZ( i )
	pluck = Blender.Object.Get('Pluck')
	steps = thisFrame - Blender.pluckFrame
	# oh god ick; I can't do simple math any more?!
	pluck.LocY = Blender.pluckInit
	for i in range(int(steps)):
		delta = (Blender.pluckTargetY - pluck.LocY)
		pluck.LocY += delta*0.1
	if pluck.LocY > Blender.pluckTargetY:
		pluck.LocY = Blender.pluckTargetY
#	print "pluck %f %f %i" % (Blender.pluckInit, Blender.pluckTargetY, Blender.pluckFrame)
#	print "delta:", delta
#	print "pluck new:", pluck.LocY

def raiseBow():
	if not Blender.useBow:
		#bow = Blender.Object.Get('Bow')
		bow = Blender.Object.Get('arco')
		bow.layers = []
#	else:
#		bow.layers = range(1,21)
#		bow.RotX = -0.5*math.pi
#		bow.RotY = 0.0
#		bow.RotZ = 0.0
#		bow.LocX = 20.0
#		bow.LocZ = 0.5 + 2.0 # off the string to begin with
#		bow.LocY = -37.5 + 1.5 + 2.0 # origin, and almost at frog




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
	contact = pos(pluck_string_num, pluck_pos)
#	print pluck
#	print contact
	#pluck.LocX = 16.5 - 33.0 * pluck_pos
	#pluck.LocZ = centerZ( pluck_string_num )
	pluck.LocX = contact[0]
	pluck.LocY = contact[1]
	pluck.LocZ = contact[2]
	Blender.pluckInit = pluck.LocY
	Blender.pluckTargetY = pluck.LocY + 0.1
	Blender.pluckFrame = seconds_action * float(fps)
#	print "pluck target: ", Blender.pluckTargetY
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

	#bow = Blender.Object.Get('Bow')
	bow = Blender.Object.Get('arco')
	bow.layers = range(1,21)
	angle = string_angle(bow_string_num)

	#bow.RotY = angle

#	h = 75*(0.5 - bow_along)
	h = 0.75*(0.5 - (bow_along + 0.01))
	# NEW COORDINATE SYSTEM:
	# X: along bow       (positive is frog)
	# Y: off string-ish  (positive is off)
	# Z: away from bridge-ish   (positive is fingerboard)
	bow.RotX = angle
	contact = pos(bow_string_num, bow_bridge_distance)
#	print contact
	bow.LocX = contact[0] + h*math.cos(angle)
	bow.LocY = contact[1] + h*math.sin(angle) + 0.015
	bow.LocZ = contact[2]
#	bow.LocX = 16.5 - 33.0 * bow_bridge_distance
#	bow.LocY = centerY(bow_string) + h*math.sin(angle)
#	bow.LocZ = centerZ(bow_string) - h*math.cos(angle)


#raiseBow()
if not Blender.useBow:
	raisePlucks() # do before any new plucks, though!

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

	# oh god ick
	if not Blender.useBow:
		raisePlucks() # do before any new plucks, though!

