


plot \
  './out/cello-g-I.predicted.modes.txt' u ($0+1):2 w l ls 1, './out/cello-g-I.detected.modes.txt' u 1:2 ls 1, \
  './out/cello-g-II.predicted.modes.txt' u ($0+1):2 w l ls 2, './out/cello-g-II.detected.modes.txt' u 1:2 ls 2, \
  './out/cello-g-III.predicted.modes.txt' u ($0+1):2 w l ls 3, './out/cello-g-III.detected.modes.txt' u 1:2 ls 3


pause(-1)

