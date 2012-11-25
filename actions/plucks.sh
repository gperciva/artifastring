#!/bin/sh

inst=0
for num in 0 1 2 3 4
do
	./actions2wav benchmark.actions $inst $num
	mv benchmark.wav $inst-$num.wav
done

inst=1
for num in 0 1
do
	./actions2wav benchmark.actions $inst $num
	mv benchmark.wav $inst-$num.wav
done

inst=2
for num in 0 1 2
do
	./actions2wav benchmark.actions $inst $num
	mv benchmark.wav $inst-$num.wav
done


