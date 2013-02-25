#!/usr/bin/env python
import curses

import artifastring_interactive

if __name__ == "__main__":
    curses.wrapper(artifastring_interactive.main)
    #artifastring_interactive.main(None)

