#!/usr/bin/env python

NAMES = {
    'violin': {
            'colin' : 'I',
            'graham' : 'II',
            'jen' : 'III',
            'melissa' : 'IV',
            'mom' : 'V',
        },
    'viola': {
            'graham' : 'I',
            'wcams' : 'II',
        },
    'cello': {
            'graham' : 'I',
            'wilf' : 'II',
            'old' : 'III',
        },

}

SAVE_FFTS = {
    # time, hertz
    'violin-e-colin-01': [('general', 5.0, 0, 5500)],
    #'violin-e-glasgow-01': [('general', 4.0, 0, 2900)],
    #'cello-a-glasgow-01': [
    #    ('general', 4.0, 0, 1000),
    #    ('split-low', 0.5, 4780, 4960),
    #    ('split-high', 0.5, 5900, 6120),
    #    ],
    'viola-d-graham-01': [
        ('general', 5.0, 0, 2000),
        ],
    'cello-c-graham-01': [
        ('general', 5.0, 0, 550),
        ],
    #'cello-g-glasgow-05': [
        #('nonlinear', 2.0, 1625, 1850),
        #('nonlinear', 2.5, 1425, 1650),
        #('nonlinear', 3.0, 1540, 1760),
    #    ('nonlinear', 3.0, 1640, 1760),
    #    ],
}

SAVE_PARTIALS = {
    'violin-e-colin-01': [0, 1, 2, 4, 9],
    #'cello-a-glasgow-01': [0, 1, 2, 4, 9],
    'viola-d-graham-01': [0, 1, 2, 4, 9],
    'cello-c-graham-01': [0, 1, 2, 4, 9],
    #'cello-g-glasgow-05': [0, 1, 2, 9, 14, 15],
    #'cello-g-glasgow-05': range(20),
}

def anonymize_name(name):
    try:
        inst = name.split('-')[0]
        city = name.split('-')[2]
        number = [NAMES[inst][city]]
        text = '-'.join( name.split('-')[0:2] + number)
    except:
        return name
    sp = text.split('-')
    text = '-'.join( [sp[0], sp[1].upper(), sp[2]] )
    return text

def save_fft(name):
    try:
        frames = SAVE_FFTS[name]
        return frames
    except:
        return False

def save_partials(name):
    print name
    try:
        frames = SAVE_PARTIALS[name]
        return frames
    except:
        return False


