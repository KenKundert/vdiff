Vdiff
=====

Opens two files in vimdiff.

Provides single-stroke key mappings to make updating files efficient.

Arguments
---------

``vdiff`` [options] <lfile> <rfile>

Options
-------

-h, --help         Show this help message and exit.
-g, --gui          Using gvim (rather than vim).


Relevant Key Mappings
---------------------

CTRL-J      Move to next change.
CTRL-K      Move to previous change.
CTRL-O      Obtain change under cursor from other buffer.
CTRL-P      Push change under cursor to other buffer.
O           Obtain all changes from other buffer.
P           Push all changes to other buffer.
S           Save changes and quit.
Q           Quit without saving changes.

Installation
------------

Runs only on Unix systems.  Requires Python 2.6 or later or Python 3.2.
Install by running ./install.
