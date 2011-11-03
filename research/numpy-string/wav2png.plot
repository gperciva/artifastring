
set terminal png size 800,600

#set xrange [0.1:0.5]
#set yrange [-2.5:2.5]
set yrange [-1.0:1.0]

set nokey
unset colorbox
unset cbtics
unset xtics
unset ytics
unset title
unset xlabel
unset ylabel
set border 0
set lmargin 0
set rmargin 0
set tmargin 0
set bmargin 0

set output OUTPUT
plot INPUT \
  w l linecolor rgb "blue" lw 2

