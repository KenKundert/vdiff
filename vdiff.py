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
from scripts import cleave, join, rm, Cmd, script_prefs, ScriptError
import sys, os
script_prefs.set('exit_upon_error', False)

# Map class {{{1
class Map(object):
    def __init__(self, key, cmd, desc):
        self.key = key
        self.cmd = cmd
        self.desc = desc
    def mapping(self):
        if self.key.startswith('Ctrl-'):
            key = '<C-%s>' % self.key.replace('Ctrl-', '')
        else:
            key = self.key
        return ' '.join(['map', key, self.cmd])

# Settings {{{1
vim = 'gvim'
flags = ['-d']
mappings = [
    Map(
        key='Ctrl-j',
        cmd=']c',
        desc="Move down to next difference"
    ),
    Map(
        key='Ctrl-k',
        cmd='[c',
        desc="Move up to previous difference"
    ),
    Map(
        key='Ctrl-o',
        cmd='do',
        desc="Obtain difference"
    ),
    Map(
        key='Ctrl-p',
        cmd='dp',
        desc="Push difference"
    ),
    Map(
        key='{',
        cmd="+1<C-W>w:1,$+1diffget<CR>",
        desc="Update the file on the left to match the one on the right"
    ),
    Map(
        key='}',
        cmd="+2<C-W>w:1,$+1diffget<CR>",
        desc="Update the file on the right to match the one on the left"
    ),
    Map(
        key='S',
        cmd=':qa<CR>',
        desc="Save any changes in both files and quit"
    ),
    Map(
        key='Q',
        cmd=':qa!<CR>',
        desc="Quit without saving either file"
    ),
    Map(
        key='=',
        cmd='<C-w>=<C-w>w',
        desc="Make both windows the same size and toggle between them"
    ),
    Map(
        key='+',
        cmd=':diffupdate<CR>',
        desc="Update differences"
    ),
]
options = [
    'autowriteall',
]
init = "1" # initially place cursor on first line
settings = '/tmp/vdiff%s' % os.getuid()

# Initialization {{{1
lines = (
    [m.mapping() for m in mappings]
  + ['set %s' % (' '.join(options))]
  + [init]
)
with open(settings, 'w') as f:
    f.write('\n'.join(lines) + '\n')

# Vdiff class {{{1
class Vdiff(object):
    def __init__(self, lfile, rfile, useGUI=True):
        self.lfile = lfile
        self.rfile = rfile
        self.useGUI = useGUI
        self.vim = None

    # Edit the files {{{2
    def edit(self):
        vim_flags = flags + (['-f'] if self.useGUI else ['-v'])
        cmd = (
            [vim]
          + vim_flags
          + ['-S', settings]
          + [self.lfile, self.rfile]
        )
        try:
            self.vim = Cmd(cmd, modes='W')
            #print("CMD: %s" % str(self.vim))
            return self.vim.run()
        except ScriptError as error:
            print("Error found when running: %s" % ' '.join(cmd))
            raise SystemExit(str(error))

    # clean up if user kills us {{{2
    def cleanup(self):
        if self.vim:
            self.vim.kill()
            for each in [self.lfile, self.rfile]:
                dn, fn = cleave(each)
                swpfile = join(dn, '.' + fn + '.swp')
                try:
                    rm(swpfile)
                except ScriptError as err:
                    print(str(err))

# vim: set sw=4 sts=4 et:

