#!/usr/bin/env python

import pstats
p = pstats.Stats("profile.txt")

p.strip_dirs().sort_stats('time').print_stats(10)
#p.strip_dirs().sort_stats('cumulative').print_stats(10)
#p.strip_dirs().sort_stats('calls').print_stats(10)


