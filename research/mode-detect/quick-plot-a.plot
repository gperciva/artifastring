


plot \
  './out/violin-a-I.predicted.modes.txt' u ($0+1):2 w l ls 1, './out/violin-a-I.detected.modes.txt' u 1:2 ls 1, \
  './out/violin-a-II.predicted.modes.txt' u ($0+1):2 w l ls 2, './out/violin-a-II.detected.modes.txt' u 1:2 ls 2, \
  './out/violin-a-III.predicted.modes.txt' u ($0+1):2 w l ls 3, './out/violin-a-III.detected.modes.txt' u 1:2 ls 3, \
  './out/violin-a-IV.predicted.modes.txt' u ($0+1):2 w l ls 4, './out/violin-a-IV.detected.modes.txt' u 1:2 ls 4, \
  './out/violin-a-V.predicted.modes.txt' u ($0+1):2 w l ls 5, './out/violin-a-V.detected.modes.txt' u 1:2 ls 5


pause(-1)

