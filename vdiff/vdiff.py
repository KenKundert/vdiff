# VDiff

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
from inform import os_error, debug, display, error, Error, warn
from shlib import to_path, rm, Cmd
import sys, os

# Defaults {{{1
DEFAULT_GUI = True
DEFAULT_VIM = 'gvimdiff -v'
DEFAULT_GVIM = 'gvimdiff -f'

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
init = [
    "redraw",    # get rid of 'press enter to continue' message
    "norm ]c[c", # start with cursor at first difference
                 # actually, ]c jumps to next diff, and if there is a diff on
                 # the first line, that would be the second diff, so use [c to
                 # jump from there to previous diff if it exists.
]
settings = '/tmp/vdiff%s' % os.getuid()

# Initialization {{{1
lines = (
    [m.mapping() for m in mappings]
  + ['set %s' % (' '.join(options))]
  + init
)
with open(settings, 'w') as f:
    f.write('\n'.join(lines) + '\n')

# vim: set sw=4 sts=4 et:
# Vdiff class {{{1
class Vdiff(object):
    def __init__(self, lfile, rfile, useGUI=None):
        self.read_defaults(useGUI)
        if self.gui and 'DISPLAY' not in os.environ:
            warn('$DISPLAY not set, ignoring request for gvim.')
            self.gui = False
        self.lfile = lfile
        self.rfile = rfile
        self.cmd = self.gvim if self.gui else self.vim

    # Read the defaults {{{2
    def read_defaults(self, useGUI):
        settings = {}
        try:
            from appdirs import user_config_dir
            import yaml, errno
            configFileName = os.path.join(user_config_dir('vdiff'), 'config')
            try:
                with open(configFileName) as f:
                    settings = yaml.safe_load(f)
            except (IOError, OSError) as err:
                if err.errno != errno.ENOENT:
                    warn(os_error(err))
            except yaml.YAMLError as err:
                warn(err)
            if useGUI is not None:
                settings['gui'] = useGUI
        except ImportError:
            pass
        self.gui = settings.get('gui', DEFAULT_GUI)
        self.vim = settings.get('vim', DEFAULT_VIM)
        self.gvim = settings.get('gvim', DEFAULT_GVIM)

    # Do the files differ {{{2
    def differ(self):
        try:
            with open(self.lfile) as f:
                lcontents = f.read()
            with open(self.rfile) as f:
                rcontents = f.read()
        except OSError as err:
            raise Error(os_error(err))
        return lcontents != rcontents

    # Edit the files {{{2
    def edit(self):
        cmd = (
            self.cmd.split()
          + ['-S', settings]
          + [self.lfile, self.rfile]
        )
        try:
            self.vim = Cmd(cmd, modes='W1')
            #debug("CMD:", self.vim)
            return self.vim.run()
        except OSError as err:
            raise Error(os_error(err))

    # clean up if user kills us {{{2
    def cleanup(self):
        if self.vim:
            self.vim.kill()
            for each in [self.lfile, self.rfile]:
                path = to_path(each)
                dn = path.parent
                fn = path.name
                swpfile = to_path(dn, '.' + fn + '.swp')
                try:
                    rm(swpfile)
                except OSError as err:
                    error(os_error(err))

# vim: set sw=4 sts=4 et:
