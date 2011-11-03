


plot \
  './out/violin-e-I.predicted.modes.txt' u ($0+1):2 w l ls 1, './out/violin-e-I.detected.modes.txt' u 1:2 ls 1, \
  './out/violin-e-II.predicted.modes.txt' u ($0+1):2 w l ls 2, './out/violin-e-II.detected.modes.txt' u 1:2 ls 2, \
  './out/violin-e-III.predicted.modes.txt' u ($0+1):2 w l ls 3, './out/violin-e-III.detected.modes.txt' u 1:2 ls 3, \
  './out/violin-e-IV.predicted.modes.txt' u ($0+1):2 w l ls 4, './out/violin-e-IV.detected.modes.txt' u 1:2 ls 4, \
  './out/violin-e-V.predicted.modes.txt' u ($0+1):2 w l ls 5, './out/violin-e-V.detected.modes.txt' u 1:2 ls 5


pause(-1)

