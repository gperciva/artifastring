


plot \
  './out/violin-d-I.predicted.modes.txt' u ($0+1):2 w l ls 1, './out/violin-d-I.detected.modes.txt' u 1:2 ls 1, \
  './out/violin-d-II.predicted.modes.txt' u ($0+1):2 w l ls 2, './out/violin-d-II.detected.modes.txt' u 1:2 ls 2, \
  './out/violin-d-III.predicted.modes.txt' u ($0+1):2 w l ls 3, './out/violin-d-III.detected.modes.txt' u 1:2 ls 3, \
  './out/violin-d-IV.predicted.modes.txt' u ($0+1):2 w l ls 4, './out/violin-d-IV.detected.modes.txt' u 1:2 ls 4, \
  './out/violin-d-V.predicted.modes.txt' u ($0+1):2 w l ls 5, './out/violin-d-V.detected.modes.txt' u 1:2 ls 5


pause(-1)

