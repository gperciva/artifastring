#!/usr/bin/env python


INVESTIGATE = {
  'violin-e-open': {
    'inst': (0,0),
    'actions': {
      'st': 3,
      'xb': 0.104,
      'fb': 0.5,
      'vb': 0.5,
      'ba': 5.0,
      'fp': 0.0,
    },
    'expected_f0': 660.0,
    'var_forces': (0.02, 5.0),
  },

  'violin-e-open-2': {
    'inst': (0,1),
    'actions': {
      'st': 3,
      'xb': 0.105,
      'fb': 0.5,
      'vb': 0.5,
      'ba': 5.0,
      'fp': 0.0,
    },
    'expected_f0': 660.0,
    'var_forces': (0.02, 5.0),
  },

  'violin-e-fourth': {
    'inst': (0,0),
    'actions': {
      'st': 3,
      'xb': 0.10,
      'fb': 0.5,
      'vb': 0.5,
      'ba': 5.0,
      'fp': 0.25,
    },
    'expected_f0': 660.0,
    'var_forces': (0.01, 2.0),
  },

  'violin-g-open': {
    'inst': (0,0),
    'actions': {
      'st': 0,
      'xb': 0.104,
      'fb': 0.5,
      'vb': 0.5,
      'ba': 5.0,
      'fp': 0.0,
    },
    'expected_f0': 196.0,
    'var_forces': (0.01, 6.0),
  },

  'cello-a-open': {
    'inst': (2,0),
    'actions': {
      'st': 3,
      'xb': 0.18,
      'fb': 5.0,
      'vb': 0.5,
      'ba': 5.0,
      'fp': 0.0,
    },
    'expected_f0': 220.0,
    'var_forces': (0.1, 10.0),
  },

  'cello-d-open': {
    'inst': (2,0),
    'actions': {
      'st': 2,
      'xb': 0.18,
      'fb': 5.0,
      'vb': 0.5,
      'ba': 5.0,
      'fp': 0.0,
    },
    'expected_f0': 146.67,
    'var_forces': (0.2, 20.0),
  },


  'cello-g-open': {
    'inst': (2,0),
    'actions': {
      'st': 1,
      'xb': 0.18,
      'fb': 5.0,
      'vb': 0.5,
      'ba': 5.0,
      'fp': 0.0,
    },
    'expected_f0': 97.0,
    'var_forces': (0.2, 20.0),
  },

  'cello-c-open': {
    'inst': (2,0),
    'actions': {
      'st': 0,
      'xb': 0.104,
      'fb': 5.0,
      'vb': 0.5,
      'ba': 5.0,
      'fp': 0.0,
    },
    'expected_f0': 65.0,
    'var_forces': (1.0, 30.0),
  },

}


