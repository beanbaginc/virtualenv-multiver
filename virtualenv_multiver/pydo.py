"""pydo, the multi-Python command runner.

``pydo`` can run a command across a range of Python versions. It looks for
a ``commandX.Y`` or ``command-X.Y`` that it can run for the provided command
and for each version of Python.

Usage::

    $ pydo [<version> [<version> ...]] <command>

Versions are in X.Y form, and can include ranges like ``3.8-3.10``.

If you don't specify any versions, the Python versions available in the
virtualenv-multiver environment will be used.

You can also configure the list of default versions in ``.pydorc``,
``pyproject.toml``, or ``setup.cfg``.

Version Added:
    3.0
"""

from __future__ import print_function, unicode_literals

import argparse
import os
import re
import subprocess
import sys

from virtualenv_multiver.config import get_pyvers
from virtualenv_multiver.utils import (norm_pyvers,
                                       validate_pyvers,
                                       which)


PYVER_RE = re.compile(r'^[23](\.\d+)?')


def build_pyver_commands(pyvers, command, command_args):
    """Build command lines used to run Python commands for multiple versions.

    Args:
        pyvers (list of str):
            The normalized list of Python versions.

        command (str):
            The command to run.

        command_args (list of str):
            The list of arguments to pass to each command.

    Returns:
        list of tuple:
        The list of command lines in the following form:

        Tuple:
            0 (str):
                The Python version to use.

            1 (list of str):
                The command line to run.
    """
    pyver_commands = []

    for pyver in pyvers:
        candidates = [
            '%s%s' % (command, pyver),
            '%s-%s' % (command, pyver),
        ]

        for candidate in candidates:
            exe_path = which(candidate)

            if exe_path:
                pyver_command = [exe_path]
                break
        else:
            pyver_command = [which('python%s' % pyver), command]

        pyver_commands.append((pyver, pyver_command + command_args))

    return pyver_commands


def run_pyver_command(pyver_command):
    """Run a comamnd for a Python version.

    Output and errors will be streamed to the terminal.

    Args:
        pyver_command (list of str):
            The command line to run.

    Returns:
        int:
        The result code.
    """
    p = subprocess.Popen(pyver_command,
                         stdin=subprocess.PIPE,
                         stdout=sys.stdout,
                         stderr=sys.stderr,
                         shell=False,
                         cwd=os.getcwd(),
                         env=os.environ)

    return p.wait()


def parse_args(argv):
    """Parse arguments from the command line.

    Args:
        argv (list of str):
            The list of command line arguments to parse.

    Returns:
        tuple:
        A 4-tuple of results:

        Tuple:
            0 (list of str):
                The list of Python versions to use.

            1 (str):
                The command to run for each Python version.

            2 (list of str):
                The list of arguments to pass to the command.

            3 (argparse.Namespace):
                The parsed options for pydo.
    """
    parser = argparse.ArgumentParser(
        description='Run a command across multiple versions of Python')
    parser.add_argument(
        '--fail-fast',
        action='store_true',
        default=False,
        help='Fail immediately if any commands return a non-0 exit code.')
    parser.add_argument(
        'pyver',
        type=str,
        default=None,
        nargs='*',
        help=('A space-separated list of explicit Python versions to use. '
              'If not specified, this will look for the versions in the '
              'following configuration files (in order): '
              '$VIRTUAL_ENV/.pydorc, ./.pydorc, ./pyproject.toml, '
              './setup.cfg'))
    parser.add_argument(
        'command',
        type=str,
        help=('A command and arguments to run. This will select the '
              'appropriate version of the command if using "python", "pip", '
              'or a command available in the form of "<command>-<pyver>".'))
    parser.add_argument(
        'args',
        type=str,
        nargs='*',
        help=('Arguments to pass to the command.'))

    args, remaining_args = parser.parse_known_args(argv[1:])

    # argparse will get all this wrong, since we've been bad and made a bunch
    # of variable-length optional arguments. Do a second round of parsing and
    # sort them into the right buckets.
    combined_args = args.pyver + [args.command] + args.args + remaining_args
    pyvers = []
    command = None
    command_args = []

    for arg in combined_args:
        if command is None:
            if PYVER_RE.match(arg):
                pyvers.append(arg)
            else:
                command = arg
        else:
            command_args.append(arg)

    if command == 'pip':
        command = 'python'
        command_args = ['-m', 'pip'] + command_args

    return pyvers, command, command_args, args


def main(argv=sys.argv):
    try:
        # We may be running in an environment like pyenv, so we have to make
        # sure that any current virtualenv takes precedence in $PATH.
        venv_path = os.environ.get('VIRTUAL_ENV')

        if venv_path:
            os.environ['PATH'] = '%s%s%s' % (os.path.join(venv_path, 'bin'),
                                             os.pathsep,
                                             os.environ.get('PATH', ''))

        pyvers, command, command_args, options = parse_args(argv)

        if not pyvers:
            pyvers = get_pyvers()

        pyvers = norm_pyvers(pyvers)
        validate_pyvers(pyvers)

        pyver_commands = build_pyver_commands(pyvers, command, command_args)

        exit_codes = []
        success = True

        for pyver, pyver_command in pyver_commands:
            header = (
                '🐍 pydo: Python %s: %s'
                % (pyver, subprocess.list2cmdline(pyver_command))
            )

            print('=' * len(header))
            print(header)
            print('=' * len(header))

            exit_code = run_pyver_command(pyver_command)
            exit_codes.append(exit_code)

            if exit_code != 0:
                success = False

                if options.fail_fast:
                    sys.exit(exit_code)

        if not success:
            sys.exit(max(exit_codes))
    except Exception as e:
        sys.stderr.write('ERROR: %s\n' % e)
        sys.exit(1)


if __name__ == '__main__':
    main()
