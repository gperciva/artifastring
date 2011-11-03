


plot \
  './out/viola-d-I.predicted.modes.txt' u ($0+1):2 w l ls 1, './out/viola-d-I.detected.modes.txt' u 1:2 ls 1, \
  './out/viola-d-II.predicted.modes.txt' u ($0+1):2 w l ls 2, './out/viola-d-II.detected.modes.txt' u 1:2 ls 2


pause(-1)

