#!/usr/bin/env/python


# L        : Rossing table 16.1, +- 1%
# L viola  : memory of "14.5 to 16.5 inches"

# T, pl    : Rossing table 16.1

# E        : Jansson table 4.5

# d violin : Jansson tabel 4.7
# d viola ADG - like violin?
# d viola C - total estimate?
# d cello - measure one instrument, assume range is +- 5% from measured

FRICTION_CHARACTERISTICS = {
    'violin' : {
        's': (0.6, 0.9),
        'd': (0.2, 0.4),
        'v0': (0.05, 0.3),
    },
    'viola' : {
        's': (0.7, 1.0),
        'd': (0.2, 0.5),
        'v0': (0.05, 0.3),
    },
    'cello' : {
        's': (0.8, 1.2),
        'd': (0.3, 0.5),
        'v0': (0.05, 0.3),
    },
}

PHYSICAL_CONSTANT_RANGES = {
    'violin' : {
        'L': (0.324, 0.331),
        'e': {
            'T': (71.4,90.7),
            'pl': (0.38e-3,0.48e-3),
            'd': (0.249e-3,0.264e-3),
            'E': (2.0e9,220.e9), # use for solid steel?
            #'E': (2.0e9,25e9),
        },
        'a': {
            'T': (48.3,62.7),
            'pl': (0.58e-3,0.75e-3),
            'd': (0.452e-3,0.701e-3),
            'E': (2.0e9,25e9),
        },
        'd': {
            'T': (34.3,60.6),
            'pl': (0.92e-3,1.63e-3),
            'd': (0.671e-3,0.914e-3),
            'E': (2.0e9,25e9),
        },
        'g': {
            'T': (35.0,51.1),
            'pl': (2.12e-3,3.09e-3),
            'd': (0.790e-3,0.833e-3),
            'E': (2.0e9,25e9),
        },
    },
    'viola' : {
        'L': (0.368, 0.419),
        'a': {
            'T': (60.6,100.2),
            'pl': (0.56e-3,0.92e-3),
            'd': (0.452e-3,0.701e-3),
            'E': (2.0e9,220.e9),
        },
        'd': {
            'T': (47.6,60.7),
            'pl': (0.98e-3,1.25e-3),
            'd': (0.671e-3,0.914e-3),
            #'E': (2.0e9,25e9),
            'E': (2.0e9,220.e9),  # for viola 2 A string on D
        },
        'g': {
            'T': (47.6,60.7),
            'pl': (2.20e-3,2.81e-3),
            'd': (0.790e-3,0.833e-3),
            'E': (2.0e9,25e9),
        },
        'c': {
            'T': (47.6,60.7),
            'pl': (4.95e-3,6.31e-3),
            'd': (0.8e-3,1.0e-3),
            'E': (2.0e9,25e9),
        },
    },
    'cello' : {
        'L': (0.683, 0.697),
        'a': {
            'T': (138.3,177.2),
            'pl': (1.50e-3,1.92e-3),
            'd': (0.62e-3,0.68e-3),
            'E': (2.0e9,25e9),
        },
        'd': {
            'T': (121.0,146.9),
            'pl': (2.94e-3,3.57e-3),
            'd': (0.93e-3,1.03e-3),
            'E': (2.0e9,25e9),
        },
        'g': {
            'T': (116.8,138.3),
            'pl': (6.38e-3,7.56e-3),
            'd': (1.07e-3,1.18e-3),
            'E': (2.0e9,25e9),
        },
        'c': {
            'T': (116.7,138.3),
            'pl': (14.33e-3,16.98e-3),
            'd': (1.60e-3,1.76e-3),
            'E': (2.0e9,25e9),
        },
    }
}

if __name__ == "__main__":
    import os
    if not os.path.exists('out'):
        os.makedirs('out')

    filename = "out/constants-instruments.txt"
    out = open(filename, 'w')
    text = "instrument&Lmin&Lmax&smin&smax&dmin&dmax&v0min&v0max"
    out.write(text + "\n")
    for inst in ['violin', 'viola', 'cello']:
        inst_dict = FRICTION_CHARACTERISTICS[inst]
        string_dict = PHYSICAL_CONSTANT_RANGES[inst]
        L = string_dict['L']
        #print inst, inst_dict
        text = "%s" % inst
        text += "&%.5g&%.5g" % (
            L[0], L[1])
        #for key, value in inst_dict.items():
        #    print key, value
        for friction_key in ['s', 'd', 'v0']:
            friction_params = inst_dict[friction_key]
            text += "&%.5g&%.5g" % (
                friction_params[0], friction_params[1])
        out.write(text + "\n")
    out.close()

    filename = "out/constants-strings.txt"
    out = open(filename, 'w')
    text = "instrument&plmin&plmax&dmin&dmax&Emin&Emax&Tmin&Tmax"
    out.write(text + "\n")
    for inst in ['violin', 'viola', 'cello']:
        inst_dict = PHYSICAL_CONSTANT_RANGES[inst]
        #print inst, inst_dict
        #text = "%s" % inst
        #for key, value in inst_dict.items():
        #    print key, value
        for st_text in ['e', 'a', 'd', 'g', 'c']:
            try:
                st_dict = inst_dict[st_text]
            except:
                continue
            text = "%s %s" % (inst, st_text)
            if st_text == 'L':
                continue
            for string_key in ['pl', 'd', 'E', 'T']:
                string_params = st_dict[string_key]
                text += "&%.5g&%.5g" % (
                    string_params[0], string_params[1])
            out.write(text + "\n")
    out.close()




