# VDiff

# License {{{1
# Copyright (C) 2014-2021 Kenneth S. Kundert
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
import os

from inform import Error, error, os_error, warn
from shlib import Cmd, rm, set_prefs, to_path

set_prefs(use_inform=True)

# Defaults {{{1
DEFAULT_GUI = True
DEFAULT_VIM = "gvimdiff -v"
DEFAULT_GVIM = "gvimdiff -f"


# Map class {{{1
class Map(object):
    def __init__(self, key, cmd, desc):
        self.key = key
        self.cmd = cmd
        self.desc = desc

    def mapping(self):
        if self.key.startswith("Ctrl-"):
            key = "<C-%s>" % self.key.replace("Ctrl-", "")
        else:
            key = self.key
        return " ".join(["map", key, self.cmd])


# Settings {{{1
mappings = [
    Map(key="Ctrl-j", cmd="]c", desc="Move down to next difference"),
    Map(key="Ctrl-k", cmd="[c", desc="Move up to previous difference"),
    Map(
        # Normally I map this to 'move to next file', which is death here.
        # So remap it to next difference too, but leave it undocumented.
        key="Ctrl-n",
        cmd="]c",
        desc="Move down to next difference",
    ),
    Map(key="Ctrl-o", cmd="do", desc="Obtain difference"),
    Map(key="Ctrl-p", cmd="dp", desc="Push difference"),
    Map(
        key="{",
        # cmd="+1<C-W>w:1,$+1diffget 2<CR>",
        # though documentation says the above should work if there are extra
        # lines at the top or bottom of files, it does not.
        cmd="+1<C-W>w:%diffget 2<CR>+2<C-W>w:%diffput 1<CR>+1<C-W>w",
        desc="Update file1 to match file2",
    ),
    Map(
        key="}",
        # cmd="+2<C-W>w:1,$+1diffget 1<CR>",
        # though documentation says the above should work if there are extra
        # lines at the top or bottom of files, it does not.
        cmd="+2<C-W>w:%diffget 1<CR>+1<C-W>w:%diffput 2<CR>+1<C-W>w",
        # +                -- diffupdate
        # 2<C-W>w          -- move to buffer 2
        # :%diffget 1<CR>  -- pull differences from buffer 1 to buffer 2
        # +                -- diffupdate
        # 1<C-W>w          -- move to buffer 1
        # :%diffput 2<CR>  -- push differences from buffer 1 to buffer 2
        # +                -- diffupdate
        # 1<C-W>w          -- move to buffer 1
        desc="Update file2 to match file1",
    ),
    Map(
        key="S",
        cmd=":qa<CR>",
        desc="Save any changes in all files and quit"
        # this assumes that autowriteall is set
        # use autowrite rather than forcing the write so the modification
        # time on the file is not changed if no change occurs
    ),
    Map(key="Q", cmd=":qa!<CR>", desc="Quit without saving any file"),
    Map(
        key="=",
        cmd="<C-w>=<C-w>w",
        desc="Make all panes the same size and rotate between them",
    ),
    Map(key="+", cmd=":diffupdate<CR>", desc="Update differences"),
]
options = [
    "autowriteall",
]
init = [
    "syntax off",  # turn off syntax highlighting, conflicts with diff highlights
    "redraw",  # get rid of 'press enter to continue' message
    "norm gg]c[c",  # start with cursor at first difference
    # gg takes cursor to top of file, to overcome Vim's tendency
    # to start with the cursor placed where was the last time you
    # edited the file. Then ]c jumps to next diff, and if there is
    # a diff on the first line, that would be the second diff, so
    # use [c to jump from there to previous diff if it exists.
]
settings = "/tmp/vdiff%s" % os.getuid()

# Initialization {{{1
lines = [m.mapping() for m in mappings] + ["set %s" % (" ".join(options))] + init
with open(settings, "w") as f:
    f.write("\n".join(lines) + "\n")


# vim: set sw=4 sts=4 et:
# Vdiff class {{{1
class Vdiff(object):
    def __init__(self, *paths, useGUI=None):
        # cast filenames to strings so that we can support pathlib paths
        self.useGUI = useGUI
        self.paths = [to_path(p) for p in paths if p]
        if len(self.paths) < 2:
            raise Error('too few paths, at least two are required.')
        if len(self.paths) > 4:
            raise Error('too many paths, no more than four are allowed.')
        self.string1_fp = self.string2_fp = None
        self.vim = None
        self.all_are_files = all(p.is_file() for p in self.paths)
        if not self.all_are_files:
            if all(p.is_dir() for p in self.paths):
                if len(self.paths) > 2:
                    raise Error('too many directories, no more than two are allowed.')
            else:
                codicils = []
                for p in self.paths:
                    if p.is_dir():
                        kind = 'dir'
                    elif p.is_file():
                        kind = 'file'
                    elif not p.exists():
                        kind = 'missing'
                    else:
                        kind = 'unknown'
                    codicils.append(f"{kind}: {p!s}")
                raise Error(
                    'Arguments are incompatible or not found.',
                    'They should all be existing files or directories, not a mix.',
                    codicil = codicils,
                    sep = '\n',
                )

    # Read the defaults {{{2
    def read_defaults(self):
        settings = {}
        try:
            from appdirs import user_config_dir

            config_file = to_path(user_config_dir("vdiff"), "config")
            try:
                code = config_file.read_text()
                try:
                    compiled = compile(code, str(config_file), "exec")
                    exec(compiled, settings)
                except Exception as e:
                    error(e, culprit=config_file)
            except FileNotFoundError:
                pass
            except OSError as e:
                warn(os_error(e))
            if self.useGUI is not None:
                settings["gui"] = self.useGUI
        except ImportError:
            pass
        if settings.get("gui", DEFAULT_GUI):
            if "DISPLAY" not in os.environ:
                warn("$DISPLAY not set, ignoring request for gvim.")
            else:
                self.cmd = settings.get("gvimdiff", DEFAULT_GVIM)
                return
        self.cmd = settings.get("vimdiff", DEFAULT_VIM)

    # Do the files differ {{{2
    def differ(self):
        try:
            if self.all_are_files:
                with open(self.paths[0]) as f:
                    lcontents = f.read()
                with open(self.paths[1]) as f:
                    rcontents = f.read()
                return lcontents != rcontents
            else:
                # currently do not bother to check that directories differs
                return True
        except OSError as e:
            raise Error(os_error(e))
        except:  # noqa: E722
            # Any other errors, just assume files differ and move on.
            # Unicode errors can occur on old versions of CentOS.
            return True

    # Edit the files {{{2
    def edit(self):
        self.read_defaults()
        cmdline_options = ["-S", settings]
        paths = [str(p) for p in self.paths]
        if not self.all_are_files:
            cmdline_options += ["-c", f'DirDiff {paths[0]} {paths[1]}']
            paths = []
        cmd = (
            self.cmd.split()
            + cmdline_options
            + paths
        )
        self.vim = Cmd(cmd, modes="soeW1")
        return self.vim.run()

    # compare strings {{{2
    def compare_strings(self, string1, string2):
        """Compares two strings.

        Writes them to temp files allowing you to open them in the difference editor.
        """
        from tempfile import NamedTemporaryFile
        assert self.string1_fp is None, 'cannot call compare_strings twice.'
        assert self.string2_fp is None, 'cannot call compare_strings twice.'
        try:
            self.string1_fp = NamedTemporaryFile(
                mode = 'w+',
                encoding = 'utf-8',
                prefix = f'vdiff-{self.paths[0]!s}-'
            )
            self.file1 = self.string1_fp.name
            self.string1_fp.write(string1)
            self.string1_fp.flush()
            self.string2_fp = NamedTemporaryFile(
                mode = 'w+',
                encoding = 'utf-8',
                prefix = f'vdiff-{self.paths[1]!s}-'
            )
            self.file2 = self.string2_fp.name
            self.string2_fp.write(string2)
            self.string2_fp.flush()
        except OSError as e:
            raise Error(os_error(e))

    # clean up if user kills us {{{2
    def cleanup(self):
        if self.vim:
            self.vim.kill()
            for path in self.paths:
                dn = path.parent
                fn = path.name
                swpfile = to_path(dn, "." + fn + ".swp")
                try:
                    rm(swpfile)
                except OSError as e:
                    error(os_error(e))
        if self.string1_fp:
            self.string1_fp.close()
        if self.string2_fp:
            self.string2_fp.close()

    # context manager {{{2
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.cleanup()

# vim: set sw=4 sts=4 et ft=python3:
