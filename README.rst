Vdiff
=====

:Author: Ken Kundert
:Version: 2.5.0
:Released: 2020-04-16


Opens two files in *vimdiff* and provides single-stroke key mappings to make 
moving differences between two files efficient. Up to two additional files may 
be opened at the same time, but these are generally used for reference purposes.

Usage
-----

``vdiff`` [options] <file1> <file2> [<file3> [<file4>]]

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
``{``         Update file1 to match file2
``}``         Update file2 to match file1
``S``         Save any changes in all files and quit
``Q``         Quit without saving any file
``=``         Make all panes the same size and rotate between them
``+``         Update differences
==========    =========================================================

When comparing 3 or 4 files, you must prepend the buffer number to the push or
obtain command. The buffers are numbered from the left to the right starting
with 1.  For example, to obtain the difference from buffer 3, move to that
difference and type '3 Ctrl-o'.


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

    from inform import display, Error
    from vdiff import Vdiff

    vdiff = Vdiff(lfile, rfile)

    try:
        if vdiff.differ():
            vdiff.edit()
        else:
            display('%s and %s are the same.' % (lfile, rfile))
    except KeyboardInterrupt:
        vdiff.cleanup()
    except Error as err:
        err.report()


Using Vdiff with Mercurial
--------------------------

To use Vdiff with Mercurial, merge the following entries into your ~/.hgrc 
file::

    [ui]
    merge = vdiff

    [extensions]
    extdiff =

    [extdiff]
    cmd.vdiff = vdiff
    opts.vimdiff = -g

These will result in Vdiff being used whenever a merge conflict occurs. It also 
allows you to use 'hg vdiff' to view differences between versions.


Installation
------------

Runs only on Unix systems.  Requires Python 3.5 or later.
Install by running './install' or 'pip3 install vdiff'.
