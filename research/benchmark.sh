#!/bin/bash

INST=0
cd build/
../actions/benchmark.py
# warm up
touch benchmarks.txt
/usr/bin/time -a -o benchmarks.txt -f "%U" ./actions2wav benchmark.actions $INST
/usr/bin/time -a -o benchmarks.txt -f "%U" ./actions2wav benchmark.actions $INST

rm benchmarks.txt
echo "VIOLIN TIMES" > benchmarks.txt
# actual times
#{ TIMEFORMAT="%E" time ./actions2wav benchmark.actions ; } 2>> benchmarks.txt
/usr/bin/time -a -o benchmarks.txt -f "%U" ./actions2wav benchmark.actions $INST
/usr/bin/time -a -o benchmarks.txt -f "%U" ./actions2wav benchmark.actions $INST
/usr/bin/time -a -o benchmarks.txt -f "%U" ./actions2wav benchmark.actions $INST


INST=2
# warm up
/usr/bin/time -o /dev/null -f "%U" ./actions2wav benchmark.actions $INST
/usr/bin/time -o /dev/null -f "%U" ./actions2wav benchmark.actions $INST

echo "CELLO TIMES" >> benchmarks.txt
# actual times
#{ TIMEFORMAT="%E" time ./actions2wav benchmark.actions ; } 2>> benchmarks.txt
/usr/bin/time -a -o benchmarks.txt -f "%U" ./actions2wav benchmark.actions $INST
/usr/bin/time -a -o benchmarks.txt -f "%U" ./actions2wav benchmark.actions $INST
/usr/bin/time -a -o benchmarks.txt -f "%U" ./actions2wav benchmark.actions $INST



cd ..
cat build/benchmarks.txt

