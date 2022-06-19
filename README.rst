Vdiff
=====

:Author: Ken Kundert
:Version: 2.6.1
:Released: 2022-06-19


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

Defaults will be read from ~/.config/vdiff/settings.nt if it exists. This is 
a NestedText_ file can contain three variables: *vimdiff*, *gvimdiff*, and 
*gui*.  The first two contain the commands used to invoke vimdiff and gvimdiff.  
The third is a Boolean that indicates which should be the default. If *gui* is 
*yes*, gvimdiff is used by default, otherwise vimdiff is the default. An example 
file might contain::

    vimdiff: gvimdiff -v
    gvimdiff: gvimdiff -f
    gui: yes

These values also happen to be the default defaults.

As a Package
------------

You can also use *vdiff* in your own Python programs. To do so, you would do 
something like the following::

    from inform import display, Error
    from vdiff import Vdiff

    with Vdiff(l_filename, r_filename) as vdiff:
        try:
            if vdiff.differ():
                vdiff.edit()
            else:
                display('%s and %s are the same.' % (l_filename, r_filename))
        except KeyboardInterrupt:
            pass
        except Error as err:
            err.report()

You can also use *vdiff* to compare string::

    from inform import display, Error
    from vdiff import Vdiff

    with Vdiff(l_identifier, r_identifier) as vdiff:
        try:
            if vdiff.differ():
                vdiff.compare_strings(l_string, r_string):
            else:
                display('%s and %s are the same.' % (l_identifier, r_identifier))
        except Error as err:
            err.report()


Using Vdiff with Mercurial
--------------------------

To use Vdiff with Mercurial_ , merge the following entries into your ~/.hgrc 
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


Using Vdiff with Git
--------------------

To use Vdiff with Git_ , merge the following entries into your ~/.gitconfig 
file::

    [merge]
        tool = vdiff
    [mergetool "vdiff"]
        cmd = vdiff_executable $LOCAL $REMOTE

These will result in Vdiff being used whenever a merge conflict occurs.


Using Vdiff with Emborg
-----------------------

To use Vdiff with Emborg_ , merge the following entries into your 
~/.config/emborg/settings file::

    manage_diffs_cmd = "vdiff -g"

This results in Vdiff being used for interactive compare operations.


Installation
------------

Runs only on Unix systems.  Requires Python 3.6 or later.
Install by running './install' or 'pip3 install vdiff'.


.. _NestedText: https://nestedtext.org
.. _Mercurial: https://www.mercurial-scm.org
.. _Git: https://git-scm.com
.. _Emborg: https://emborg.readthedocs.io
