#!/usr/bin/env python
import curses

import artifastring_osc

if __name__ == "__main__":
    curses.wrapper(artifastring_osc.main)
    #artifastring_osc(None)

