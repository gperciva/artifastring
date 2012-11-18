#!/bin/bash

cd build/
../actions/unit.py
# warm up
/usr/bin/time -o benchmarks.txt -f "%U" ./actions2wav unit.actions
/usr/bin/time -a -o benchmarks.txt -f "%U" ./actions2wav unit.actions

rm benchmarks.txt
# actual times
#{ TIMEFORMAT="%E" time ./actions2wav unit.actions ; } 2>> benchmarks.txt
/usr/bin/time -o benchmarks.txt -f "%U" ./actions2wav unit.actions
/usr/bin/time -a -o benchmarks.txt -f "%U" ./actions2wav unit.actions
/usr/bin/time -a -o benchmarks.txt -f "%U" ./actions2wav unit.actions


cd ..
cat build/benchmarks.txt

