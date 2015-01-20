# scripts -- Scripting utilities
#
# A light-weight package with few dependencies that allows users to do             
# shell-script like things relatively easily in Python.

# License {{{1
# Copyright (C) 2015 Kenneth S. Kundert
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].

# Imports {{{1
from fnmatch import fnmatch
import itertools
import shutil
import glob
import errno
import os
import sys

# ScriptError Exception {{{1
class ScriptError(Exception):
    def __init__(self, message, fn=None, cmd=None):
        self.message = message
        self.filename = fn
        self.command = cmd
        if script_prefs.get('exit_upon_error'):
            sys.exit(str(self))

    def __str__(self):
        cmd = None
        if self.command:
            show_cmd = script_prefs.get('show_cmd_in_errors')
            if show_cmd:
                if type(self.command) is str:
                    cmd = self.command.split()
                else:
                    cmd = self.command
                cmd = ' '.join(cmd) if show_cmd == 'full' else cmd[0]
        msg = [str(each) for each in [cmd, self.filename, self.message] if each]
        return ': '.join(msg)

# Script Preferences {{{1
class ScriptPreferences(object):
    def __init__(self):
        self.preferences = {
            'exit_upon_error': False,
            'expanduser': True,
            'expandvars': False,
            'encoding': 'utf-8',
            'show_cmd_in_errors': True,
                # valid choices are False, True, or 'full'
        }

    def get(self, name):
        return self.preferences[name]

    def set(self, name, value):
        if name not in self.preferences:
            raise ScriptError('unknown preference')
        self.preferences[name] = value

script_prefs = ScriptPreferences()

# File system utility functions (cp, mv, rm, ln, touch, mkdir, ls, etc.) {{{1
# first, some utility functions {{{2
def _flatten(listoflists):
    for pathlist in listoflists:
        if type(pathlist) is str:
            pathlist = [pathlist]
        for path in pathlist:
            yield path

def _len(listoflists):
    # only returns 0, 1, or 2. Any length greater than 2 is reported as 2
    count = 0
    for pathlist in listoflists:
        if type(pathlist) is str:
            pathlist = [pathlist]
        for path in pathlist:
            count += 1
            if count > 1:
                return count
        return count

def _str(path):
    if type(path) is str:
        return path
    else:
        raise ScriptError('%s: is not scalar' % path)

# cp {{{2
def cp(*paths):
    "Copy files or directories"
    dest = _str(paths[-1])
    srcs = paths[:-1]
    if len(srcs) < 1:
        raise ScriptError('cp: too few arguments')
    try:
        if os.path.isdir(dest):
            for src in _flatten(srcs):
                fulldest = join(dest, os.path.basename(src))
                if os.path.isdir(src):
                    shutil.copytree(src, fulldest)
                else:
                    shutil.copy2(src, fulldest)
            return
        else:
            if _len(srcs) > 1:
                raise ScriptError('cp: destination (%s) must be directory.' % dest)
        src = _str(srcs[0])
        if os.path.isfile(dest):
            if os.path.isdir(src):
                raise ScriptError('cp: cannot copy a directory onto a file (%s).' % dest)
            else:
                # overwrite destination
                shutil.copy2(src, dest)
        else:
            # destination does not exist
            assert not os.path.lexists(dest)
            if os.path.isdir(src):
                shutil.copytree(src, dest)
            else:
                shutil.copy2(src, dest)
    except (IOError, OSError) as err:
        raise ScriptError(err.strerror, err.filename)
    except shutil.Error as err:
        raise ScriptError(', '.join([
            "Cannot copy %s to %s: %s" % arg for arg in err.paths
        ]))

# mv {{{2
def mv(*paths):
    "Move file or directory (supports moves across filesystems)"
    dest = _str(paths[-1])
    srcs = paths[:-1]
    if _len(srcs) < 1:
        raise ScriptError('mv: too few arguments')
    try:
        if os.path.isdir(dest):
            for src in _flatten(srcs):
                fulldest = join(dest, os.path.basename(src))
                shutil.move(src, fulldest)
            return
        else:
            if _len(srcs) > 1:
                raise ScriptError('mv: destination (%s) must be directory.' % dest)
        src = _str(srcs[0])
        if os.path.isfile(dest):
            if os.path.isdir(src):
                raise ScriptError('mv: cannot move a directory onto a file (%s).' % dest)
            else:
                # overwrite destination
                shutil.move(src, dest)
        else:
            # destination does not exist
            assert not os.path.lexists(dest)
            shutil.move(src, dest)
    except (IOError, OSError) as err:
        raise ScriptError(err.strerror, err.filename)
    except shutil.Error as err:
        raise ScriptError(
            "Cannot rename %s to %s: %s" % (src, dest, ', '.join(err.args))
        )


# rm {{{2
def rm(*paths):
    "Remove file or directory (without complaint if does not exist)"
    for path in _flatten(paths):
        try:
            if os.path.isdir(str(path)):
                shutil.rmtree(str(path))
            else:
                os.remove(str(path))
        except (IOError, OSError) as err:
            # don't complain if the file never existed
            if err.errno != errno.ENOENT:
                raise ScriptError(err.strerror, err.filename)

# ln {{{2
def ln(src, link):
    "Create symbolic link."
    try:
        os.symlink(str(src), str(link))
    except (IOError, OSError) as err:
        raise ScriptError(err.strerror, err.filename)

# touch {{{2
def touch(*paths):
    """
    Touch one or more files. If files do not exist, create them.
    """
    for path in _flatten(paths):
        try:
            open(path, 'ab').close()
        except (IOError, OSError) as err:
            sys.exit("%s: %s." % (err.filename, err.strerror))

# mkdir {{{2
def mkdir(*paths):
    """
    Create a directory and all parent directories. Returns without complaint if
    directory already exists.
    """
    for path in _flatten(paths):
        try:
            os.makedirs(path)
        except (IOError, OSError) as err:
            if err.errno != errno.EEXIST:
                sys.exit("%s: %s." % (err.filename, err.strerror))

# ls {{{2
def ls(glb='*', path=''):
    """
    Path is expected to be a directory. If not given, the current working 
    directory is assumed. If glb is not given, the directory is listed (minus 
    any dot files).  If glb is given, it is applied to the items in the 
    directory and only those items that match are returned.
    
    >>> from scripts import *

    >>> sorted(ls('*.py'))
    ['clones.py', 'scripts.py', 'setup.py', 'test.clones.py', 'test.doctests.py']

    """
    if os.path.isfile(path if path else '.'):
        # A file, just return the file
        return [path]
    elif not os.path.isdir(path if path else '.'):
        # Nonexistent, return nothing
        return []
    # A directory, list the directory
    return glob.iglob(os.path.join(path, glb))

# lsd {{{2
def lsd(glb='*', path=''):
    """
    Path is expected to be a directory. If glb is not given, the directory is 
    listed (minus any dot files). If glb is given, it is applied to the items 
    in the directory and only those items that match are returned.

    >>> sorted(lsd('.hg*'))
    ['.hg']

    """
    if not os.path.isdir(path if path else '.'):
        # Is file or is nonexistent, return nothing
        return []
    # A directory, list the directory
    return [p for p in glob.iglob(os.path.join(path, glb)) if os.path.isdir(p)]

# lsf {{{2
def lsf(glb='*', path=''):
    """
    Path is expected to be a directory. If glb is not given, the directory is 
    listed (minus any dot files). If glb is given, it is applied to the items 
    in the directory and only those items that match are returned.

    >>> sorted(lsf('.hg*'))
    ['.hgignore']

    """
    if os.path.isfile(path if path else '.'):
        # A file, just return the file
        return [path]
    elif not os.path.isdir(path if path else '.'):
        # Nonexistent, return nothing
        return []
    # A directory, list the directory
    return [p for p in glob.iglob(os.path.join(path, glb)) if os.path.isfile(p)]

# Path functions (join, exists, isfile, abspath, head, fopen, etc.) {{{1
# join {{{2
def join(*args, **kwargs):
    """
    Combine path components into a path. If a subsequent path component is an
    absolute path, previous components are discarded.

    >>> python = join('bin', '/usr/bin', 'python')
    >>> python
    '/usr/bin/python'

    >>> home1 = join('~', expanduser=True)
    >>> home2 = join('$HOME', expandvars=True)
    >>> home1 == home2
    True

    """
    if len(args):
        path = os.path.join(*args)
    else:
        path = '.'
    if kwargs.get('expanduser') or script_prefs.get('expanduser'):
        path = os.path.expanduser(path)
    if kwargs.get('expandvars') or script_prefs.get('expandvars'):
        path = os.path.expandvars(path)
    return path

# exists {{{2
def exists(path):
    """
    Tests whether path exists.

    >>> exists(python)
    True

    """
    return os.path.lexists(path)

# missing {{{2
def missing(path):
    """
    Tests whether path does not exist.

    >>> missing(python)
    False

    """
    return not exists(path)

# isfile {{{2
def isfile(path):
    """
    Tests whether path exists and is file.

    >>> isfile(python)
    True

    """
    return os.path.isfile(path)

# isdir {{{2
def isdir(path):
    """
    Tests whether path exists and is file.

    >>> isdir(python)
    False

    """
    return os.path.isdir(path)

# islink {{{2
def islink(path):
    """
    Tests whether path exists and is link.

    >>> islink(python)
    True

    """
    return os.path.islink(path)

# isreadable {{{2
def isreadable(path):
    """
    Tests whether path exists and is readable.

    >>> isreadable(python)
    True

    """
    return os.access(path, os.R_OK)

# iswritable {{{2
def iswritable(path):
    """
    Tests whether path exists and is writable.

    >>> iswritable(python)
    False

    """
    return os.access(path, os.W_OK)

# isexecutable {{{2
def isexecutable(path):
    """
    Tests whether path exists and is executable.

    >>> isexecutable(python)
    True

    """
    return os.access(path, os.X_OK)

# abspath {{{2
def abspath(path):
    """
    Returns absolute path as a path object.

    >>> abspath('../../../../../../../../../../../..')
    '/'

    """
    return os.path.abspath(path)

# relpath {{{2
def relpath(path):
    """
    Returns relative path from current working directory as a path object.

    >>> relpath('/')[:9]
    '../../../'

    """
    return os.path.relpath(path)

# pathfrom {{{2
def pathfrom(path, start):
    """
    Returns relative path from start as a path object.

    >>> pathfrom('.', '..')
    'scripts'

    """
    return os.path.relpath(path, start)

# normpath {{{2
def normpath(path):
    """
    Returns a cleaned up version of path.

    >>> normpath('.//././foo/..')
    '.'

    """
    return os.path.normpath(path)

# head {{{2
def head(path):
    """
    Returns path with last component removed.

    >>> head(python)
    '/usr/bin'

    """
    return os.path.dirname(path)

# tail {{{2
def tail(path):
    """
    Returns last component of path.

    >>> tail(python)
    'python'

    """
    return os.path.basename(path)

# cleave {{{2
def cleave(path):
    """
    Returns head and tail as a tuple.

    >>> cleave(python)
    ('/usr/bin', 'python')

    """
    return os.path.split(path)

# split {{{2
def split(path):
    """
    Returns all components of a path as a list.

    >>> split(python)
    ['', 'usr', 'bin', 'python']

    """
    return path.split(os.sep)

# stem {{{2
def stem(path):
    """
    Returns path with the extension removed.

    >>> stem('./scripts.py')
    './scripts'

    """
    return os.path.splitext(path)[0]

# extension {{{2
def extension(path):
    """
    Returns the extension as a string.

    >>> extension('./scripts.py')
    '.py'

    """
    return os.path.splitext(path)[1]

# cleavext {{{2
def cleaveext(path):
    """
    Returns root and extension as a tuple.

    >>> cleaveext('./scripts.py')
    ('./scripts', '.py')

    """
    return os.path.splitext(path)

# addext {{{2
def addext(path, ext):
    """
    Add an extension to the path.

    >>> addext('python.py', '.bkup')
    'python.py.bkup'

    """
    return path + ext

# fopen {{{2
def fopen(path, mode='rU'):                                                                                          
    """
    Open path as file with specified mode. Return file descriptor.
    """
    try:
        return open(path, mode)
    except (IOError, OSError) as err:
        raise ScriptError(err.strerror, fn=err.filename)

# Path list functions (all_paths, expand, filter, etc.) {{{1
# all_paths {{{2
def all_paths(*fragments):
    """
    Combine path fragments to to a path list. Each fragment must be a string
    or an iterable that generates strings.
    """

    if len(fragments) == 0:
        return []
    else:
        return [os.path.join(*f) for f in itertools.product(
            *((f,) if type(f) is str else f for f in fragments)
        )]

# expand {{{2
def expand(glb):
    for path in glob.iglob(glb):
        yield path

# fexpand {{{2
def fexpand(glb):
    for path in glob.iglob(glb):
        if os.path.isfile(path):
            yield path

# dexpand {{{2
def dexpand(glb):
    for path in glob.iglob(glb):
        if os.path.isdir(path):
            yield path

# filter {{{2
def filter(glb, paths):
    for path in paths:
        if not fnmatch(tail(path), glb):
            yield path


# Execution classes and functions (Cmd, Run, Sh, run, bg, shbg, which){{{1
# Command class {{{2
class Cmd(object):
    """
    Specify a command

    cmd may be a string or a list.
    mode is a string that specifies various options
        S, s: Use, or do not use, shell
        O, o: Capture, or do not capture, stdout
        E, e: Capture, or do not capture, stderr
        W, s: Wait, or do not wait, for command to terminate before proceding
    only one of the following may be given, and it must be given last
        *: accept any output status code
        N: accept any output status code equal to N or less
        M,N,...: accept status codes M, N, ...
    """
    # __init__ {{{3
    def __init__(self, cmd, modes=None, encoding=None):
        self.cmd = cmd
        self.use_shell = False
        self.save_stdout = False
        self.save_stderr = False
        self.wait_for_termination = True
        self.encoding = script_prefs.get('encoding') if encoding is None else encoding
        self._interpret_modes(modes)
        self._sanity_check()

    # _interpret_modes {{{3
    def _interpret_modes(self, modes):
        accept = ''
        if modes:
            for i in range(len(modes)):
                mode = modes[i]
                if   mode == 's': self.use_shell = False
                elif mode == 'S': self.use_shell = True
                elif mode == 'o': self.save_stdout = False
                elif mode == 'O': self.save_stdout = True
                elif mode == 'e': self.save_stderr = False
                elif mode == 'E': self.save_stderr = True
                elif mode == 'w': self.wait_for_termination = False
                elif mode == 'W': self.wait_for_termination = True
                else: accept = modes[i:]; break
        self.accept = _Accept(accept)

    # _sanity_check {{{3
    def _sanity_check(self):
        if self.save_stdout or self.save_stderr:
            assert self.wait_for_termination

    # run {{{3
    def run(self, stdin=None):
        """
        Run the command

        If stdin is given, it should be a string. Otherwise, no connection is
        made to stdin of the command.

        Returns exit status if wait_for_termination is True.
        """
        import subprocess

        # I have never been able to get Popen to work properly if cmd is not
        # a string when using the shell
        if type(self.cmd) is not str and self.use_shell:
            cmd = ' '.join(self.cmd)
        else:
            cmd = self.cmd

        # indicate streams to intercept
        streams = {}
        if stdin is not None:
            streams['stdin'] = subprocess.PIPE
        if self.save_stdout:
            streams['stdout'] = subprocess.PIPE
        if self.save_stderr:
            streams['stderr'] = subprocess.PIPE

        # run the command
        try:
            process = subprocess.Popen(
                cmd, shell=self.use_shell, **streams
            )
        except (IOError, OSError) as err:
            raise ScriptError(err.strerror, fn=err.filename, cmd=cmd)

        # write to stdin
        if stdin is not None:
            process.stdin.write(stdin.encode(self.encoding))
            process.stdin.close()

        # store needed information and wait for termination if desired
        self.pid = process.pid
        self.process = process
        if self.wait_for_termination:
            return self.wait()

    # wait {{{3
    def wait(self):
        """
        Wait for command to terminate.

        This should only be used it wait-for-termination is False.

        Returns exit status of the command.
        """
        process = self.process

        # Read the outputs
        if self.save_stdout:
            self.stdout = process.stdout.read().decode(self.encoding)
        else:
            self.stderr = None
        if self.save_stderr:
            self.stderr = process.stderr.read().decode(self.encoding)
        else:
            self.stderr = None

        # wait for process to complete
        self.status = process.wait()

        # close output streams
        if process.stdout:
            process.stdout.close()
        if process.stderr:
            process.stderr.close()

        # check return code
        if self.accept.unacceptable(self.status):
            if self.stderr:
                raise ScriptError(self.stderr.strip(), cmd=self.cmd)
            else:
                raise ScriptError(
                    "unexpected exit status (%d)" % self.status,
                    cmd=self.cmd
                )
        return self.status

    # kill {{{3
    def kill(self):
        self.process.kill()
        self.process.wait()

    # __str__ {{{3
    def __str__(self):
        if type(self.cmd) is str:
            return self.cmd
        else:
            return ' '.join(self.cmd)

# Run class {{{2
class Run(Cmd):
    "Run a command immediately."
    def __init__(self, cmd, modes=None, stdin=None, encoding=None):
        self.cmd = cmd
        self.stdin = None
        self.use_shell = False
        self.save_stdout = False
        self.save_stderr = False
        self.wait_for_termination = True
        self.accept = (0,)
        self.encoding = script_prefs.get('encoding') if not encoding else encoding
        self._interpret_modes(modes)
        self._sanity_check()
        self.run(stdin)

# Sh class {{{2
class Sh(Cmd):
    "Run a command immediately in the shell."
    def __init__(self, cmd, modes=None, stdin=None, encoding=None):
        self.cmd = cmd
        self.stdin = None
        self.use_shell = True
        self.save_stdout = False
        self.save_stderr = False
        self.wait_for_termination = True
        self.encoding = script_prefs.get('encoding') if not encoding else encoding
        self._interpret_modes(modes)
        self._sanity_check()
        self.run(stdin)


# run {{{2
def run(cmd, stdin=None, accept=0, shell=False):
    "Run a command without capturing its output."
    import subprocess

    # I have never been able to get Popen to work properly if cmd is not
    # a string when using the shell
    if type(cmd) is not str and shell:
        cmd = ' '.join(cmd)

    streams = {} if stdin is None else {'stdin': subprocess.PIPE}
    try:
        process = subprocess.Popen(cmd, shell=shell, **streams)
    except (IOError, OSError) as err:
        raise ScriptError(err.strerror, err.filename, cmd)
    if stdin is not None:
        process.stdin.write(stdin.encode(script_prefs.get('encoding')))
        process.stdin.close()
    status = process.wait()
    if _Accept(accept).unacceptable(status):
        raise ScriptError(
            "unexpected exit status (%d)" % status, cmd=cmd
        )
    return status

# sh {{{2
def sh(cmd, stdin=None, accept=0, shell=True):
    "Execute a command with a shell without capturing its output"
    return run(cmd, stdin, accept, shell=True)


# bg {{{2
def bg(cmd, stdin=None, shell=False):
    "Execute a command in the background without capturing its output."
    import subprocess
    streams = {'stdin': subprocess.PIPE} if stdin is not None else {}
    try:
        process = subprocess.Popen(cmd, shell=shell, **streams)
    except (IOError, OSError) as err:
        raise ScriptError(err.strerror, err.filename, cmd)
    if stdin is not None:
        process.stdin.write(stdin.encode(script_prefs.get('encoding')))
        process.stdin.close()
    return process.pid

# shbg {{{2
def shbg(cmd, stdin=None, shell=True):
    "Execute a command with a shell in the background without capturing its output."
    return bg(cmd, stdin, shell=True)


# which {{{2
def which(name, path=None, flags=os.X_OK):
    "Search PATH for executable files with the given name."
    result = []
    if path is None:
        path = os.environ.get('PATH', '')
    for p in path.split(os.pathsep):
        p = os.path.join(p, name)
        if os.access(p, flags):
            result.append(p)
    return result

# _Accept class {{{2
class _Accept(object):
    # accept exit codes may be specified as:
    # 1. True or the string '*':
    #       all codes are acceptable, or
    # 2. an integer N or the string 'N':
    #       code must be less than or equal to N, or
    # 3. a tuple of integers or a string of the form 'M,N,...':
    #       code must be one of the numbers
    # 4. 0 or empty string:
    #       the only valid return code is 0 (default)
    def __init__(self, accept=0):
        if type(accept) == str:
            if accept == '*':
                accept = True
            else:
                try:
                    codes = tuple([int(n) for n in accept.split(',')])
                    accept = codes[0] if len(codes) == 1 else codes
                except ValueError:
                    if accept:
                        raise ScriptError('invalid modes string')
                    else:
                        accept = 0
        self.accept = accept

    def unacceptable(self, status):
        if self.accept is True:
            return False
        elif type(self.accept) is tuple:
            return status not in self.accept
        else:
            return status > self.accept
