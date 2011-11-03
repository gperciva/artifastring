#!/usr/bin/env python

### Answer from: http://stackoverflow.com/a/1695250
### use like this: Numbers = enum(ONE=1, TWO=2, THREE='three')
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

