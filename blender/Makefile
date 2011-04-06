# change this if you have blender 2.49 in a special location,
# such as
#BLENDER_BIN=$HOME/blender-2.49/blender
# instead of using the normal blender on the PATH
BLENDER_BIN=blender

# if you change this, you need to change the value in
# setup.py as well.
# TODO: make the fps controllable on the command-line
FPS=25

TEMP_DIR=/tmp/vivi-movie/



all: mpeg

unit.actions:
	python ../actions/unit.py

prep: unit.actions
	mkdir -p $(TEMP_DIR)
	rm -f $(TEMP_DIR)/*.jpg $(TEMP_DIR)/*.tga

test: prep
	$(BLENDER_BIN) -b blank.blend -P setup.py \
		-o $(TEMP_DIR)/#### \
		-k \
		-c_unit.actions \
		-s 0 -e 3 -a > log-render.txt

quality-test: prep
	$(BLENDER_BIN) -b blank.blend -P setup.py \
		-o $(TEMP_DIR)/#### \
		-c_unit.actions \
		-s 0 -e 3 -a > log-render.txt

images: prep
	$(BLENDER_BIN) -b blank.blend -P setup.py \
		-o $(TEMP_DIR)/#### \
		-k \
		-c_unit.actions \
		-a > log-render.txt

quality-images: prep
	$(BLENDER_BIN) -b blank.blend -P setup.py \
		-o $(TEMP_DIR)/#### \
		-c_unit.actions \
		-a > log-render.txt

unit.wav.mp3: unit.actions
	../build/src/actions2wav unit.actions
	lame unit.wav

quality-avi: quality-images unit.wav.mp3
	mencoder "mf://$(TEMP_DIR)/*.tga" -mf fps=$(FPS):type=tga \
		-ovc lavc \
		-vf scale=640:512 \
		-audiofile unit.wav.mp3 -oac copy \
		-o unit.avi

avi: images unit.wav.mp3
	mencoder "mf://$(TEMP_DIR)/*.tga" -mf fps=$(FPS):type=tga \
		-ovc lavc \
		-vf scale=640:512 \
		-audiofile unit.wav.mp3 -oac copy \
		-o unit.avi

#mencoder "mf://$(TEMP_DIR)/*.jpg" -mf fps=$(FPS):type=jpg
mpeg: images unit.wav.mp3
	mencoder "mf://$(TEMP_DIR)/*.tga" -mf fps=$(FPS):type=tga \
		-of mpeg \
		-mpegopts format=mpeg1:tsaf:muxrate=2000 \
    -ovc lavc \
    -lavcopts \
	vcodec=mpeg1video:vbitrate=1152:keyint=15:mbd=2 \
		-vf scale=640:512 \
		-audiofile unit.wav.mp3 -oac copy \
		-o unit.mpeg


