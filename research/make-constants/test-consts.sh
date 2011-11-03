
# violins
./actions2wav bow-violin-strings.actions 0 0
cp bow-violin-strings.wav test-0.wav
./actions2wav bow-violin-strings.actions 0 1
cp bow-violin-strings.wav test-1.wav
./actions2wav bow-violin-strings.actions 0 2
cp bow-violin-strings.wav test-2.wav
./actions2wav bow-violin-strings.actions 0 3
cp bow-violin-strings.wav test-3.wav

# yes, viola is icky
./actions2wav bow-violin-strings.actions 1 0
cp bow-violin-strings.wav test-4.wav

# cello
./actions2wav bow-cello-strings.actions 2 0
cp bow-cello-strings.wav test-5.wav
./actions2wav bow-cello-strings.actions 2 1
cp bow-cello-strings.wav test-6.wav

