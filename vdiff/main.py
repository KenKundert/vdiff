#!/usr/bin/env python

"""vdiff

Opens two files in vimdiff.
Provides single-stroke key mappings to make moving differences between two files
efficient.

Usage:
    vdiff [options] <file1> <file2> [<file3> [<file4>]]

Options:
    -v, --vim        Use vim (rather than default).
    -g, --gvim       Use gvim (rather than default).
    -f, --force      Edit the files even if they are the same.
    -q, --quiet      Issue only error messages.
    -h, --help       Print this helpful message.

Relevant Key Mappings:
{mappings}

When comparing 3 or 4 files, you must prepend the buffer number to the push or
obtain command. The buffers are numbered from the left to the right starting
with 1.  For example, to obtain the difference from buffer 3, move to that
difference and type '3 Ctrl-o'.
"""

# License {{{1
# Copyright (C) 2014-2020 Kenneth S. Kundert
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/.


# Imports {{{1
from docopt import docopt

from inform import Error, Inform, display

from .vdiff import Vdiff, mappings


# Main {{{1
def main():
    try:
        mappingSummary = "\n".join(["    %-9s %s" % (m.key, m.desc) for m in mappings])

        # Read command line
        cmdSummary = __doc__.format(mappings=mappingSummary)
        arguments = docopt(cmdSummary)

        # Configure output to user
        Inform(log=False, quiet=arguments["--quiet"])

        # Process command line arguments
        file1 = arguments["<file1>"]
        file2 = arguments["<file2>"]
        file3 = arguments["<file3>"]
        file4 = arguments["<file4>"]
        useGUI = None
        if arguments["--vim"]:
            useGUI = False
        if arguments["--gvim"]:
            useGUI = True
        force = arguments["--force"]

        # Run vdiff
        vdiff = Vdiff(file1, file2, file3, file4, useGUI)
        if force or vdiff.differ():
            vdiff.edit()
        else:
            display("%s and %s are the same." % (file1, file2))
    except KeyboardInterrupt:
        vdiff.cleanup()
        raise SystemExit("Killed by user")
    except Error as err:
        err.terminate()
