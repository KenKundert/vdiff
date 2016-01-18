Vdiff
=====

Opens two files in vimdiff and provides single-stroke key mappings to make 
moving differences between two files efficient.

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


As a Package
------------

You can also use vdiff in your own Python programs. To do so, you would do 
something like the following::

    from inform import Error
    from vdiff import Vdiff

    vdiff = Vdiff(lfile="...", rfile="...", useGUI=True)

    try:
        vdiff.edit()
    except KeyboardInterrupt:
        vdiff.cleanup()
    except Error as err:
        err.report()


Installation
------------

Runs only on Unix systems.  Requires Python 3.5 or later.
Install by running './install' or 'pip3 install vdiff'.
