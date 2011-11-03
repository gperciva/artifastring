


plot \
  './out/viola-g-I.predicted.modes.txt' u ($0+1):2 w l ls 1, './out/viola-g-I.detected.modes.txt' u 1:2 ls 1, \
  './out/viola-g-II.predicted.modes.txt' u ($0+1):2 w l ls 2, './out/viola-g-II.detected.modes.txt' u 1:2 ls 2


pause(-1)

