
all:
	echo "do nothing?"

clean:
	rm -f out-disp/*
	rm -f *.txt
	rm -f out.wav

png:
	echo "make png INPUT=foo.wav OUTPUT=foo.png"
	sox $(INPUT) make-png-tmp-bad.dat
	grep -v '^;' make-png-tmp-bad.dat > make-png-tmp.dat
	rm make-png-tmp-bad.dat
	gnuplot -e "OUTPUT='$(OUTPUT)'; INPUT='make-png-tmp.dat'" wav2png.plot
	rm make-png-tmp.dat

# done in phd-dissertation now
#thesis:
#	rsync -r data/ ~/src/phd-dissertation/python-data/


