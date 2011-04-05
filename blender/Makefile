FPS=25

all: images mpeg

prep:
	mkdir -p /tmp/vivi-movie/
	rm -f /tmp/vivi-movie/*.jpg /tmp/vivi-movie/*.tga

test: prep
	blender -b blank.blend -P setup.py \
		-o /tmp/vivi-movie/#### \
		-c_unit.actions \
		-s 0 -e 3 -a > foo.txt

#		-a > foo.txt &

longtest: prep
	blender -b blank.blend -P setup.py \
		-o /tmp/vivi-movie/#### \
		-c_unit.actions \
		-s 0 -e 25 -a > foo.txt


images: prep
	blender -b blank.blend -P setup.py \
		-o /tmp/vivi-movie/#### \
		-c_unit.actions \
		-a > foo.txt

#		-s 0 -e 9 -a > foo.txt &

avi:
	mencoder "mf:///tmp/vivi-movie/*.tga" -mf fps=$(FPS):type=tga \
		-ovc lavc \
		-vf scale=640:512 \
		-audiofile violin-1-delay.wav.mp3 -oac copy \
		-o violin-1.avi

#mencoder "mf:///tmp/vivi-movie/*.jpg" -mf fps=$(FPS):type=jpg
mpeg:
	mencoder "mf:///tmp/vivi-movie/*.tga" -mf fps=$(FPS):type=tga \
		-of mpeg \
		-mpegopts format=mpeg1:tsaf:muxrate=2000 \
    -ovc lavc \
    -lavcopts \
	vcodec=mpeg1video:vbitrate=1152:keyint=15:mbd=2 \
		-vf scale=640:512 \
		-audiofile violin-1-delay.wav.mp3 -oac copy \
		-o violin-1.mpeg


