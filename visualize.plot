# uncomment the DEBUG line in violin_string.h, then redirect
# output to blah.txt

FILENAME = 'blah.txt'

SCALE_SLIP = 1e-1
SCALE_F0 = 1e0
SCALE_F1 = 1e-16
SCALE_result = 1e1

title_slip = sprintf("slip (0 or 1)")
title_f0 = sprintf("F0 * %g", SCALE_F0)
title_f1 = sprintf("F1 * %g", SCALE_F1)
title_res = sprintf("result * %g", SCALE_result)

plot FILENAME \
	   using 1:($2*SCALE_SLIP) title title_slip w lines, \
	'' using 1:($3*SCALE_F0) title title_f0 w points pt 7 ps 1, \
	'' using 1:($4*SCALE_F1) title title_f1 w dots, \
	'' using 1:($5*SCALE_result) title title_res w lines

pause -1

