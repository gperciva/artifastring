For ncurses interaction, just run
    ./artifastring_interactive.py

For the OSC server, you need liblo and its python bindings.  For
use with the "Control" Android/iOS app, you need to:
- connect the tablet with your computer with a wireless network
  (I make my netbook an ad-hoc wifi)
  Some a helper script for my netbook running Ubuntu is in
    ad-hoc-wifi/
- start a web server on your computer, and put the
    osc.js
  file on the webserver
- start the Control app; point the interface at your computer and
  the osc.js file on the webserver
- in the Control app, set the OSC destination to your computer
- run
    ./artifastring_osc.py
  and enjoy.

I haven't spent any time thinking about the interface and how it
could be improved for serious use; this is a proof-of-concept
implementation.

