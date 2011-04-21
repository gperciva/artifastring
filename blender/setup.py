import Blender
import math
import Blender.Library


# some computers need this, some don't.  No clue why.  :(
import sys
sys.path.append('.')

fast_render = False
# get command-line options in a bad way
import sys
for arg in sys.argv:
	if arg[0:3] == '-c_':
		action_filename = arg[3:]
	if arg[0:6] == '-k': # argument not used elsewhere
			     # it's short for "kwality".  ;-)
		fast_render = True


scene = Blender.Scene.GetCurrent()
### Remove cube
#cube = Blender.Object.Get('Cube')
#scene.objects.unlink(cube)

### Setup background color
world = Blender.World.Get()
world[0].setHor( [0.8,0.8,0.9] )

### Get violin and arco
#Blender.Library.Open("violin-and-bow.blend")
#Blender.Library.Load('violin', 'Object', 0)
#Blender.Library.Load('arco', 'Object', 0)
#Blender.Library.Update()
#Blender.Library.Close()
#

## must do this after adding violin and bow!
import shared


### setup arco
bow = Blender.Object.Get('bow')
#bow.RotX = 0.0 *math.pi/180.0
#bow.RotY = 90.0 *math.pi/180.0
#bow.RotZ = 180.0 *math.pi/180.0
#
Blender.useBow = False
# make invisible for now
bow.layers = []

#violin = Blender.Object.Get('violin')
#violin.makeParent([bow])


### setup pluck
pluck = Blender.Mesh.Primitives.Cone(3, 0.01, 0.01)
scene.objects.new(pluck,'Pluck')
pluck = Blender.Object.Get('Pluck')
#
pluck.RotX = -90 * math.pi/180.0
Blender.pluckInit = pluck.LocY
Blender.pluckTargetY = pluck.LocY
Blender.pluckFrame = 0

mat = Blender.Material.New('pluckMat')
mat.rgbCol = [1.0, 0.0, 0.5]
pluck.getData(mesh=True).materials += [mat]

# make invisible for now
pluck.layers = []


### setup fingers
for i in range(4):
	finger = Blender.Mesh.Primitives.Cone(20, 0.008, 0.008)
	scene.objects.new(finger,'Finger'+'-'+str(i))
	# gets it as an object, rather than mesh ?
	finger = Blender.Object.Get('Finger'+'-'+str(i))
	mat = Blender.Material.New('fingerMat')
	mat.rgbCol = [1.0, 0.5, 0.0]
	#mat.emit = 0.5
	finger.getData(mesh=True).materials += [mat]


	finger.RotX = -90 * math.pi/180.0
	finger.setLocation( shared.pos(i, 1.0, finger=True) )

### setup camera
#camera = Blender.Object.Get('Camera')
#camera.LocX = 0.291
#camera.LocY = 0.608
#camera.LocZ = 0.040
#
#camera.RotX = -30.5 * math.pi/180.0
#camera.RotY = 113.5 * math.pi/180.0
#camera.RotZ = 29.7 * math.pi/180.0


### setup lamp
# TODO: add more lamps?
#lamp = Blender.Object.Get('Lamp')
#lamp.LocX = 2.5
#lamp.LocY = 8.0
#lamp.LocZ = -0.7


### add animation script
Blender.Text.Load("animate-violin.py")
scene.addScriptLink("animate-violin.py", "FrameChanged")
Blender.actions_lines = open(action_filename).readlines()
Blender.actions_index = 0



### rendering
context = scene.getRenderingContext()
context.fps = 25

context.sFrame = 1
end_time = float( Blender.actions_lines[-1].split()[1] )
context.eFrame = int(end_time * context.fps)


context.mode = 0
context.imageType = Blender.Scene.Render.TARGA
#context.imageType = Blender.Scene.Render.JPEG

if fast_render:
	context.sizePreset(Blender.Scene.Render.PREVIEW)
else:
	## actual good, but ok-time, output.  Takes about 5 seconds per frame
	context.rayTracing = True
	context.gammaCorrection = True
	context.shadow = True
	context.environmentMap = True
	context.sizePreset(Blender.Scene.Render.FULL)
	## these takes ridiculously long
	#context.oversampling = True
	#context.motionBlur = True



