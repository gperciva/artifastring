#!/usr/bin/env python
import ViolinPhysical
from ViolinPhysical import semitones

def pluckWait(vln, st, finger, pos, seconds, force = 1.0):
    vln.pluck(st, finger, pos, force)
    vln.wait(seconds)

def main():
    violin = ViolinPhysical.ViolinPhysical('benchmark')
    violin.comment("")
    violin.comment(" This will produce bad sound output")
    violin.comment("   it's just a simple test; the main Vivi")
    violin.comment("   output is much better.  :)")

    # pluck position (default)
    #   - lowest value is pp-0.05
    pp = 0.25
    bp = 0.12

    violin.wait(0.5)
    violin.comment(" open strings arco")
    force = 1.2
    violin.bow('vl_A', bp, force, 1.0, 0.1)
    violin.wait(0.5)
    violin.bow('vl_D', bp, force, -1.0)
    violin.wait(0.5)
    force = 2.2
    violin.bow('vl_G', bp, force, 1.0)
    violin.wait(0.5)
    force = 0.8
    violin.bow('vl_E', bp, force, -0.5)
    violin.wait(1.0)
    violin.bow('vl_E', bp, 0.0, 0.0)
    violin.wait(0.5)

    violin.comment(" scale pizz")
    pluckWait(violin, 'vl_D', 0.0, pp, 0.25);
    pluckWait(violin, 'vl_D', semitones(2), pp, 0.25);
    pluckWait(violin, 'vl_D', semitones(4), pp, 0.25);
    pluckWait(violin, 'vl_D', semitones(5), pp, 0.25);
    pluckWait(violin, 'vl_D', semitones(7), pp, 0.25);
    pluckWait(violin, 'vl_A', 0.0, pp, 0.25); # repeated note
    pluckWait(violin, 'vl_A', semitones(2), pp, 0.25);
    pluckWait(violin, 'vl_A', semitones(4), pp, 0.25);
    pluckWait(violin, 'vl_A', semitones(5), pp, 0.25);
    violin.wait(1.0);

    violin.comment(" scale arco")
    force = 1.0
    velocity = 1.0
    violin.finger('vl_D', 0.0);
    violin.bow('vl_D', bp, force, velocity, 0.1);
    violin.wait(0.25);
    violin.finger('vl_D', semitones(2));
    violin.bow('vl_D', bp, force, -velocity);
    violin.wait(0.25);
    violin.finger('vl_D', semitones(4));
    violin.bow('vl_D', bp, force, velocity);
    violin.wait(0.25);
    violin.finger('vl_D', semitones(5));
    violin.bow('vl_D', bp, force, -velocity);
    violin.wait(0.25);
    violin.finger('vl_D', semitones(7));
    violin.bow('vl_D', bp, force, velocity);
    violin.wait(0.25);
    # repeated note
    force = 0.8
    violin.finger('vl_A', semitones(0));
    violin.bow('vl_A', bp, force, -velocity);
    violin.wait(0.25);
    violin.finger('vl_A', semitones(2));
    violin.bow('vl_A', bp, force, velocity);
    violin.wait(0.25);
    violin.finger('vl_A', semitones(4));
    violin.bow('vl_A', bp, force, -velocity);
    violin.wait(0.25);
    violin.finger('vl_A', semitones(5));
    violin.bow('vl_A', bp, force, velocity/2);
    violin.wait(0.5);

    violin.bow('vl_A', bp, 0.0, 0.0);
    violin.wait(1.0);

    violin.comment('scale done')


    violin.comment(" pizz chord")
    pluckWait(violin, 'vl_G', 0.0, pp+0.2, 0.0);
    pluckWait(violin, 'vl_D', 0.0, pp+0.15, 0.0);
    pluckWait(violin, 'vl_A', semitones(1), pp+0.1, 0.0);
    pluckWait(violin, 'vl_E', semitones(3), pp+0.05, 0.0);
    violin.wait(1.0);

    pluckWait(violin, 'vl_G', 0.0, pp+0.2, 0.03);
    pluckWait(violin, 'vl_D', 0.0, pp+0.15, 0.03);
    pluckWait(violin, 'vl_A', semitones(2), pp+0.1, 0.03);
    pluckWait(violin, 'vl_E', semitones(4), pp+0.05, 0.03);
    violin.wait(1.0);

    pluckWait(violin, 'vl_G', semitones(2), pp+0.1, 0.1);
    pluckWait(violin, 'vl_D', semitones(2), pp+0.1, 0.1);
    pluckWait(violin, 'vl_A', semitones(4), pp+0.1, 0.1);
    pluckWait(violin, 'vl_E', semitones(5), pp+0.1, 0.1);
    violin.wait(1.0);

    pluckWait(violin, 'vl_A', semitones(2), pp, 0.2);
    pluckWait(violin, 'vl_D', semitones(6), pp-0.05, 0.15);
    pluckWait(violin, 'vl_E', semitones(3), pp+0.05, 0.1);
    violin.pluck('vl_G', 0.0, pp);
    violin.wait(1.0);


    violin.comment(" arco chords")
    force = 2.0

    violin.finger('vl_G', semitones(2));
    violin.bow('vl_G', bp, force, velocity, 0.1);
    violin.wait(0.08);
    violin.finger('vl_D', semitones(2));
    violin.bow('vl_D', bp, force, velocity);
    violin.wait(0.08);
    violin.finger('vl_A', semitones(4));
    violin.bow('vl_A', bp, force, velocity);
    violin.wait(0.16);
    violin.finger('vl_E', semitones(5));
    violin.bow('vl_E', bp, force, velocity);
    violin.wait(0.24);
    violin.bow('vl_E', bp, 0.0, 0.0);
    violin.wait(0.5);

    velocity /= 2.0
    violin.finger('vl_A', semitones(2));
    violin.bow('vl_A', bp, force, velocity, 0.1);
    violin.wait(0.2);
    violin.finger('vl_D', semitones(6));
    violin.bow('vl_D', bp, force, velocity);
    violin.wait(0.2);
    violin.finger('vl_E', semitones(3));
    violin.bow('vl_E', bp, force, velocity);
    violin.wait(0.2);
    violin.finger('vl_G', 0.0);
    violin.bow('vl_G', bp, force, velocity);
    violin.wait(0.3);
    violin.bow('vl_G', bp, 0.0, 0.0);
    violin.wait(1.0);

    violin.comment('chords done')


    violin.comment(" gliss pizz")
    finger_pos = semitones(2)
    violin.pluck('vl_D', finger_pos, pp);
    for i in range(25):
        violin.wait(1.0/50)
        finger_pos += 0.0006
        violin.finger('vl_D', finger_pos)
    violin.wait(0.2)

    finger_pos = semitones(10)
    violin.pluck('vl_D', finger_pos, pp);
    for i in range(25):
        violin.wait(1.0/50)
        finger_pos -= 0.0021
        violin.finger('vl_D', finger_pos)
    violin.wait(0.2)

    violin.comment(" gliss bow")
    force = 0.8
    velocity = 0.2
    finger_pos = semitones(2)
    violin.finger('vl_D', finger_pos)
    violin.bow('vl_D', bp, force, velocity, 0.1)
    for i in range(25):
        violin.wait(1.0/50)
        finger_pos += 0.0006
        violin.finger('vl_D', finger_pos)
    violin.bowStop()
    violin.wait(0.2)

    finger_pos = semitones(10)
    violin.finger('vl_D', finger_pos)
    violin.bow('vl_D', bp, force, -velocity)
    for i in range(25):
        violin.wait(1.0/50)
        finger_pos -= 0.0021
        violin.finger('vl_D', finger_pos)
    violin.bowStop()
    violin.wait(0.2)



    violin.comment(" vibrato pizz")
    import math
    # vibrato
    finger_pos = semitones(5)
    violin.pluck('vl_D', finger_pos, pp);
    for i in range(90):
        violin.wait(1.0/49)
        wiggle = math.sin(i*0.5)
        #print wiggle
        finger_pos += 0.003 * wiggle
        violin.finger('vl_D', finger_pos)
    violin.wait(0.1)

    finger_pos = semitones(3)
    violin.pluck('vl_D', finger_pos, pp);
    for i in range(90):
        violin.wait(1.0/49)
        wiggle = math.sin(i*0.2)
        finger_pos += 0.006 * wiggle
        violin.finger('vl_D', finger_pos)
    violin.wait(0.1)


    violin.comment(" vibrato arco")
    finger_pos = semitones(5)
    violin.finger('vl_D', finger_pos)
    violin.bow('vl_D', bp, force, velocity, 0.1)
    for i in range(90):
        violin.wait(1.0/49)
        wiggle = math.sin(i*0.5)
        finger_pos += 0.003 * wiggle
        violin.finger('vl_D', finger_pos)
    violin.bowStop()
    violin.wait(0.3)

    finger_pos = semitones(3)
    violin.finger('vl_D', finger_pos)
    violin.bow('vl_D', bp, force, -velocity)
    for i in range(90):
        violin.wait(1.0/49)
        wiggle = math.sin(i*0.2)
        finger_pos += 0.006 * wiggle
        violin.finger('vl_D', finger_pos)
    violin.bowStop()
    violin.wait(0.3)



    violin.comment('vibrato and gliss done')
    violin.wait(0.5)
    violin.wait(0.1731)

    # Bach
#    semiquaver = 0.3;
#    violin.pluckWait('vl_G', semitones(7), 0.29, semiquaver);
#    violin.pluckWait('vl_G', semitones(7), 0.23, 0.0); # double stop
#    violin.pluckWait('vl_D', semitones(0), 0.25, 3*semiquaver);
#    violin.pluckWait('vl_G', semitones(9), 0.21, semiquaver);
#    violin.pluckWait('vl_G', semitones(10), 0.28, semiquaver);
#    violin.pluckWait('vl_D', semitones(5), 0.22, semiquaver);
#    violin.pluckWait('vl_D', semitones(7), 0.24, semiquaver);
#    violin.pluckWait('vl_D', semitones(8), 0.20, semiquaver);
#    violin.pluckWait('vl_G', semitones(6), 0.27, semiquaver);
#    violin.wait(0.8);

#    quaver = 0.4;
#    violin.pluckWait('vl_G', semitones(7), 0.29, 0);
#    violin.pluckWait('vl_D', semitones(3), 0.21, 0.3);
#    violin.pluckWait('vl_D', semitones(3), 0.25, 0);
#    violin.pluckWait('vl_A', semitones(0), 0.24, 3*quaver);

#    violin.pluckWait('vl_A', semitones(0), 0.27, quaver);
#
#    violin.pluckWait('vl_G', semitones(7), 0.28, 0.2);
#    violin.pluckWait('vl_D', semitones(5), 0.25, 0.2);
#    violin.pluckWait('vl_A', semitones(1), 0.24, 0.2);
#    violin.pluckWait('vl_E', semitones(0), 0.24, 2*quaver);
#
#    violin.pluckWait('vl_G', semitones(6), 0.23, 0.4);
#    violin.pluckWait('vl_D', semitones(5), 0.28, 0.1);
#    violin.pluckWait('vl_A', semitones(0), 0.21, 0.1);
#    violin.pluckWait('vl_E', semitones(0), 0.23, 3*quaver);
#

    violin.end()


if __name__ == "__main__":
    main()


