import Blender
import math
import Blender.Library

# get action filename in a bad way
import sys
for arg in sys.argv:
	if arg[0:3] == '-c_':
		action_filename = arg[3:]


scene = Blender.Scene.GetCurrent()

cube = Blender.Object.Get('Cube')
scene.objects.unlink(cube)


Blender.Library.Open("violin-and-bow.blend")
Blender.Library.Load('violin', 'Object', 0)
Blender.Library.Load('arco', 'Object', 0)
Blender.Library.Update()
Blender.Library.Close()

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
#       (i.e. using pos(st, along) )
ST_X_OFFSET = -0.0005
ST_Y_OFFSET =  0.0004

bow = Blender.Object.Get('arco')
bow.RotX = 0.0 *math.pi/180.0
bow.RotY = -90.0 *math.pi/180.0
bow.RotZ = 180.0 *math.pi/180.0


for i in range(4):
	finger = Blender.Mesh.Primitives.Cone(20, 0.008, 0.008)
	scene.objects.new(finger,'Finger'+'-'+str(i))
	finger = Blender.Object.Get('Finger'+'-'+str(i))

	finger.LocX = Blender.strings[i][1][0] + ST_X_OFFSET
	finger.LocY = Blender.strings[i][1][1] + ST_Y_OFFSET # anchor point
	finger.LocZ = Blender.strings[i][1][2]
	finger.RotX = -90 * math.pi/180.0
	mat = Blender.Material.New('fingerMat')
	mat.rgbCol = [1.0, 0.5, 0.0]
	#mat.emit = 0.5
	finger.getData(mesh=True).materials += [mat]

pluck = Blender.Mesh.Primitives.Cone(3, 0.01, 0.01)
scene.objects.new(pluck,'Pluck')
pluck = Blender.Object.Get('Pluck')

pluck.RotX = -90 * math.pi/180.0
Blender.pluckInit = pluck.LocY
Blender.pluckTargetY = pluck.LocY
Blender.pluckFrame = 0

mat = Blender.Material.New('pluckMat')
mat.rgbCol = [1.0, 0.0, 0.5]

pluck.getData(mesh=True).materials += [mat]

# make invisible for now
pluck.layers = []


camera = Blender.Object.Get('Camera')
camera.LocX = 0.291
camera.LocY = 0.608
camera.LocZ = 0.040

camera.RotX = -30.5 * math.pi/180.0
camera.RotY = 113.5 * math.pi/180.0
camera.RotZ = 29.7 * math.pi/180.0



lamp = Blender.Object.Get('Lamp')
lamp.LocX = 2.5
lamp.LocY = 8.0
lamp.LocZ = -0.7

Blender.Text.Load("animate-violin.py")
scene.addScriptLink("animate-violin.py", "FrameChanged")

context = scene.getRenderingContext()
context.sFrame = 1

Blender.actions_lines = open(action_filename).readlines()

Blender.actions_index = 0
end_time = float( Blender.actions_lines[-1].split()[1] )

context.fps = 25
context.eFrame = int(end_time * context.fps)

context.mode = 0
context.imageType = Blender.Scene.Render.TARGA
#context.imageType = Blender.Scene.Render.JPEG

### good output  (for fast/low quality, comment these out
###               and switch the size to .PREVIEW)

## these takes ridiculously long
##context.oversampling = True
##context.motionBlur = True

## actual good, but ok-time, output.  Takes about 5 seconds per frame
#context.rayTracing = True
#context.gammaCorrection = True
#context.shadow = True
#context.environmentMap = True
#context.sizePreset(Blender.Scene.Render.FULL)
context.sizePreset(Blender.Scene.Render.PREVIEW)


Blender.useBow = False
bow = Blender.Object.Get('arco')
bow.layers = []


# colors 
world = Blender.World.Get()
world[0].setHor( [0.8,0.8,0.9] )


