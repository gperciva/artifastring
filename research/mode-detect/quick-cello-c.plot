


plot \
  './out/cello-c-I.predicted.modes.txt' u ($0+1):2 w l ls 1, './out/cello-c-I.detected.modes.txt' u 1:2 ls 1, \
  './out/cello-c-II.predicted.modes.txt' u ($0+1):2 w l ls 2, './out/cello-c-II.detected.modes.txt' u 1:2 ls 2, \
  './out/cello-c-III.predicted.modes.txt' u ($0+1):2 w l ls 3, './out/cello-c-III.detected.modes.txt' u 1:2 ls 3


pause(-1)

