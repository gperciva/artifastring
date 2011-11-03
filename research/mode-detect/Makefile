
all:
	echo "do something"

test-glasgow-violin:
	./quick-b-check.py ~/media/phd-data/glasgow/fixed-wav/violin-

test-glasgow-cello:
	./quick-b-check.py ~/media/phd-data/glasgow/fixed-wav/cello-

clean:
	rm -f *.png
	rm -f *_modes.h
	rm -f *.pyc
	rm -f split-png/*
	rm -f glasgow/spectrum/*/*.txt
	rm -f glasgow/fixed-wav/*.txt
	rm -f glasgow/spectrum/*/*.png
	rm -f glasgow/png/*
	rm -f vancouver/spectrum/*/*.txt
	rm -f vancouver/spectrum/*/*.png
	rm -f vancouver/png/*
	rm -rf spectrum/*
	find . -name "*.pickle" -delete

