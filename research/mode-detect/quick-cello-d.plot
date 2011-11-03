


plot \
  './out/cello-d-I.predicted.modes.txt' u ($0+1):2 w l ls 1, './out/cello-d-I.detected.modes.txt' u 1:2 ls 1, \
  './out/cello-d-II.predicted.modes.txt' u ($0+1):2 w l ls 2, './out/cello-d-II.detected.modes.txt' u 1:2 ls 2, \
  './out/cello-d-III.predicted.modes.txt' u ($0+1):2 w l ls 3, './out/cello-d-III.detected.modes.txt' u 1:2 ls 3


pause(-1)

