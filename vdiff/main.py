#!/usr/bin/env python

"""vdiff

Opens two files in vimdiff.
Provides single-stroke key mappings to make moving differences between two files 
efficient.

Usage:
    vdiff [options] <lfile> <rfile>

Options:
    -g, --gui   Use gvim (rather than vim).
    -h, --help  Print this helpful message.

Relevant Key Mappings:
{mappings}
"""

# License {{{1
# Copyright (C) 2014-2016 Kenneth S. Kundert
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
from inform import Inform, Error, fatal
from .vdiff import Vdiff, mappings
import sys, os

# Main {{{1
def main():
    mappingSummary = '\n'.join([
        '    %-9s %s' % (m.key, m.desc) for m in mappings
    ])
    cmdSummary = __doc__.format(mappings = mappingSummary)
    arguments = docopt(cmdSummary)
    Inform(log=False)

    vdiff = Vdiff(arguments['<lfile>'], arguments['<rfile>'], arguments['--gui'])

    try:
        status = vdiff.edit()
    except KeyboardInterrupt:
        vdiff.cleanup()
        sys.exit('Killed by user')
    except Error as err:
        err.terminate()

# vim: set sw=4 sts=4 et:
