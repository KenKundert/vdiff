Vdiff
=====

Opens two files in vimdiff and provides single-stroke key mappings to make 
moving differences between two files efficient.

Usage
-----

``vdiff`` [options] <lfile> <rfile>

Options
-------

-v, --vim        Use vim (rather than default).
-g, --gvim       Use gvim (rather than default).
-f, --force      Edit the files even if they are the same.
-q, --quiet      Issue only error messages.
-h, --help       Print this helpful message.


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


Defaults
--------

Defaults will be read from ~/.config/vdiff/config if it exists. This is a Python 
file that is evaluated to determine the value of three variables: vimdiff, 
gvimdiff, and gui.  The first two are the strings used to invoke vimdiff and 
gvimdiff. The third is a boolean that indicates which should be the default. If 
gui is true, gvimdiff is used by default, otherwise vimdiff is the default. An 
example file might contain::

    vimdiff = 'gvimdiff -v'
    gvimdiff = 'gvimdiff -f'
    gui = True

These values also happen to be the default defaults.

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
