Vdiff
=====

Opens two files in vimdiff.

Provides single-stroke key mappings to make moving differences between two files 
efficient.

Usage
-----

``vdiff`` [options] <lfile> <rfile>

Options
-------

-g, --gui          Using gvim (rather than vim).
-h, --help         Show this help message and exit.


Relevant Key Mappings
---------------------

==========    =========================================================
``Ctrl-j``    Move down to next difference
``Ctrl-k``    Move up to previous difference
``Ctrl-o``    Obtain difference
``Ctrl-p``    Push difference
``{``         Update the file on the left to match the one on the right
``}``         Update the file on the right to match the one on the left
``S``         Save any changes in both files and quit
``Q``         Quit without saving either file
``=``         Make both windows the same size and toggle between them
``+``         Update differences
==========    =========================================================

Installation
------------

Runs only on Unix systems.  Requires Python 2.6 or Python 3.2 or later.
Install by running ./install.
