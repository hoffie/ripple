ripple
======

Ripple is a Python-based command line time tracking tool which works on a human-readable text file.

Usage
-----

  $ r start finally fixing feature X of this project +uni

... do some work ...

  $ r stop
  $ r
  Task 1, started today 19:10, finished today 19:20 (10 min 4 sec): finally fixing feature X of this project +uni

  duration of all entries shown: 10 min 4 sec
  
  $ r start +slacking
  $ r end
  $ r
  Task 1, started today 19:10, finished today 19:20 (10 min 4 sec): finally fixing feature X of this project +uni
  Task 2, started today 19:12, finished today 19:12 (2 sec): +slacking

  duration of all entries shown: 10 min 6 sec
  
  $ r ls +uni
  Task 1, started today 19:10, finished today 19:20 (10 min 4 sec): finally fixing feature X of this project +uni

  duration of all entries shown: 10 min 4 sec

  
The interface is very basic, but the resulting file is human-readable and can easily be updated using your favorite editor.
This allows for efficient time tracking and summaries, while still permitting extended use cases.
See `r help` for furter information.


Setup
-----
Besides python (tested with 2.7), no external dependencies or special configurations are needed,
although some kind of shortcut comes in handy:

Assuming ~/bin is part of your $PATH:

  ln -s /path/to/ripple/ripple.py ~/bin/ripple
  ln -s /path/to/ripple/ripple.py ~/bin/r
  
Storage
-------
Entries are kept in ~/.ripple.txt by default.
Changing that is either possible using a symlink or by setting the RIPPLE_DB environment variable.

Portability
-----------
Only tested on Linux so far.

Motivation
----------
While there are lots of other time tracking tools available,
Ripple is available where most programmers spend lots of time (the command line),
it does not get into your way while still leaving data files which are easily readable even without Ripple.

License
-------
This project can be used under the terms of the MIT license.

Authors
-------
Christian Hoffmann <ch@hoffie.info>
