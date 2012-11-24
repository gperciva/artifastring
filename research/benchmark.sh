#!/bin/bash

INST=0
cd build/
../actions/unit.py
# warm up
touch benchmarks.txt
/usr/bin/time -a -o benchmarks.txt -f "%U" ./actions2wav unit.actions $INST
/usr/bin/time -a -o benchmarks.txt -f "%U" ./actions2wav unit.actions $INST

rm benchmarks.txt
echo "VIOLIN TIMES" > benchmarks.txt
# actual times
#{ TIMEFORMAT="%E" time ./actions2wav unit.actions ; } 2>> benchmarks.txt
/usr/bin/time -a -o benchmarks.txt -f "%U" ./actions2wav unit.actions $INST
/usr/bin/time -a -o benchmarks.txt -f "%U" ./actions2wav unit.actions $INST
/usr/bin/time -a -o benchmarks.txt -f "%U" ./actions2wav unit.actions $INST


INST=2
# warm up
/usr/bin/time -o /dev/null -f "%U" ./actions2wav unit.actions $INST
/usr/bin/time -o /dev/null -f "%U" ./actions2wav unit.actions $INST

echo "CELLO TIMES" >> benchmarks.txt
# actual times
#{ TIMEFORMAT="%E" time ./actions2wav unit.actions ; } 2>> benchmarks.txt
/usr/bin/time -a -o benchmarks.txt -f "%U" ./actions2wav unit.actions $INST
/usr/bin/time -a -o benchmarks.txt -f "%U" ./actions2wav unit.actions $INST
/usr/bin/time -a -o benchmarks.txt -f "%U" ./actions2wav unit.actions $INST



cd ..
cat build/benchmarks.txt

