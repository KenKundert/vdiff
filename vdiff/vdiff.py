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
from inform import cull, debug, display, error, Error, os_error, warn
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
        cmd="+1<C-W>w:1,$+1diffget 2<CR>",
        desc="Update file1 to match file2"
    ),
    Map(
        key='}',
        cmd="+2<C-W>w:1,$+1diffget 1<CR>",
        desc="Update file2 to match file1"
    ),
    Map(
        key='S',
        cmd=':qa<CR>',
        desc="Save any changes in all files and quit"
    ),
    Map(
        key='Q',
        cmd=':qa!<CR>',
        desc="Quit without saving any file"
    ),
    Map(
        key='=',
        cmd='<C-w>=<C-w>w',
        desc="Make all panes the same size and rotate between them"
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
    "syntax off", # turn off syntax highlighting, conflicts with diff highlights
    "redraw",     # get rid of 'press enter to continue' message
    "norm ]c[c",  # start with cursor at first difference
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
    def __init__(self, file1, file2, file3=None, file4=None, useGUI=None):
        # cast filenames to strings so that we can support pathlib paths
        self.useGUI = useGUI
        self.file1 = str(file1) if file1 else None
        self.file2 = str(file2) if file2 else None
        self.file3 = str(file3) if file3 else None
        self.file4 = str(file4) if file4 else None

    # Read the defaults {{{2
    def read_defaults(self):
        settings = {}
        try:
            from appdirs import user_config_dir
            config_file = to_path(user_config_dir('vdiff'), 'config')
            try:
                code = config_file.read_text()
                try:
                    compiled = compile(code, str(config_file), 'exec')
                    exec(compiled, settings)
                except Exception as err:
                    error(err, culprit=config_file)
            except FileNotFoundError:
                pass
            except OSError as err:
                warn(os_error(err))
            if self.useGUI is not None:
                settings['gui'] = self.useGUI
        except ImportError:
            pass
        if settings.get('gui', DEFAULT_GUI):
            if 'DISPLAY' not in os.environ:
                warn('$DISPLAY not set, ignoring request for gvim.')
            else:
                self.cmd = settings.get('gvimdiff', DEFAULT_GVIM)
                return
        self.cmd = settings.get('vimdiff', DEFAULT_VIM)

    # Do the files differ {{{2
    def differ(self):
        try:
            with open(self.file1) as f:
                lcontents = f.read()
            with open(self.file2) as f:
                rcontents = f.read()
            return lcontents != rcontents
        except OSError as err:
            raise Error(os_error(err))
        except:
            # Any other errors, just assume files differ and move on.
            # Unicode errors can occur on old versions of CentOS.
            return True

    # Edit the files {{{2
    def edit(self):
        self.read_defaults()
        cmd = (
            self.cmd.split()
          + ['-S', settings]
          + cull([self.file1, self.file2, self.file3, self.file4])
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
            for each in cull([self.file1, self.file2, self.file3, self.file4]):
                path = to_path(each)
                dn = path.parent
                fn = path.name
                swpfile = to_path(dn, '.' + fn + '.swp')
                try:
                    rm(swpfile)
                except OSError as err:
                    error(os_error(err))

# vim: set sw=4 sts=4 et:
