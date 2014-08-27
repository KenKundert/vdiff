# VDiff
#
# Copyright (C) 2014 Kenneth S. Kundert

# License {{{1
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
from __future__ import print_function, division
import sys
from subprocess import call, Popen as popen, PIPE

# Settings {{{1
vim = 'gvim'
flags = ['-d']
mappings = [
    ('<C-J>', ']c'),
    ('<C-K>', '[c'),
    ('<C-O>', 'do'),
    ('<C-P>', 'dp'),
    ('O', ":1,$+1diffget<CR>"),
    ('P', ":1,$diffput<CR>"),
    #('R', ':diffupdate<CR>'),
        # nice, but one to many
        # Vim allows only a limited number of this type of command
    ('S', ':qa<CR>'),
    ('Q', ':qa!<CR>'),
]
options = [
    'autowriteall',
]
init = "1" # initially place cursor on first line

# Initialization {{{1
vim_mappings = ['+map %s %s' % each for each in mappings]
vim_options = '+set %s' % ' '.join(options)
vim_init = '+'+init

# Edit the files {{{1
def vdiff(lfile, rfile, useGUI=True):
    vim_flags = flags + (['-f'] if useGUI else ['-v'])
    cmd = (
        [vim]
        + vim_flags
        + vim_mappings
        + [vim_options, vim_init, lfile, rfile]
    )
    try:
        return call(cmd)
    except OSError as error:
        print("Error found when running: %s" % cmd)
        exit(str(error))

