


plot \
  './out/cello-a-I.predicted.modes.txt' u ($0+1):2 w l ls 1, './out/cello-a-I.detected.modes.txt' u 1:2 ls 1, \
  './out/cello-a-II.predicted.modes.txt' u ($0+1):2 w l ls 2, './out/cello-a-II.detected.modes.txt' u 1:2 ls 2, \
  './out/cello-a-III.predicted.modes.txt' u ($0+1):2 w l ls 3, './out/cello-a-III.detected.modes.txt' u 1:2 ls 3


pause(-1)

