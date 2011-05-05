# change this if you have blender 2.57 in a special location,
BLENDER_BIN=blender

# if you change this, you need to change the value in
# setup-2.5.py as well.
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
	$(BLENDER_BIN) -noaudio \
		-b fast-violin.blend -P setup-2.5.py \
		-o $(TEMP_DIR)/#### \
		-s 1 -e 2 -a > log-render.txt


gui: prep
	$(BLENDER_BIN) -noaudio \
		fast-violin.blend -P setup-2.5.py

show:
	comix $(TEMP_DIR)/*

low: prep
	$(BLENDER_BIN) -noaudio \
		-b fast-violin.blend -P setup-2.5.py \
		-o $(TEMP_DIR)/#### \
		-a > log-render.txt


quality-test: prep
	$(BLENDER_BIN) -noaudio \
		-b violin-and-bow.blend -P setup-2.5.py \
		-o $(TEMP_DIR)/#### \
		-s 1 -e 2 -a > log-render.txt

quality-gui: prep
	$(BLENDER_BIN) -noaudio \
		violin-and-bow.blend -P setup-2.5.py


images: prep
	$(BLENDER_BIN) -noaudio \
		-b fast-violin.blend -P setup-2.5.py \
		-o $(TEMP_DIR)/#### \
		-k \
		-c_unit.actions \
		-a > log-render.txt

quality-images: prep
	$(BLENDER_BIN) -noaudio \
		-b violin-and-bow.blend -P setup-2.5.py \
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
mpeg: low unit.wav.mp3
	mencoder "mf://$(TEMP_DIR)/*.tga" -mf fps=$(FPS):type=tga \
		-of mpeg \
		-mpegopts format=mpeg1:tsaf:muxrate=2000 \
		-ovc lavc \
		-lavcopts \
			vcodec=mpeg1video:vbitrate=1152:keyint=15:mbd=2 \
		-vf scale=640:480 \
		-audiofile unit.wav.mp3 -oac copy \
		-o unit.mpeg
