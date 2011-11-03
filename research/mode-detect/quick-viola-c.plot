


plot \
  './out/viola-c-I.predicted.modes.txt' u ($0+1):2 w l ls 1, './out/viola-c-I.detected.modes.txt' u 1:2 ls 1, \
  './out/viola-c-II.predicted.modes.txt' u ($0+1):2 w l ls 2, './out/viola-c-II.detected.modes.txt' u 1:2 ls 2


pause(-1)

