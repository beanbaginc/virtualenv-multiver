"""Internal utility functions for virtualenv-multiver.

Version Added:
    3.0
"""

import os
import re
import sys


_which_cache = {}


class PyVerError(ValueError):
    """An error with a Python version."""


def norm_pyvers(pyvers):
    """Normalize a list of Python versions.

    This will filter out any empty versions, remove duplicates, and expand
    version ranges.

    Args:
        pyvers (list of str):
            The list of Python versions or version ranges.

    Returns:
        list of str:
        The normalized list of Python versions.
    """
    norm_pyvers = []

    for pyver in pyvers:
        if not pyver or pyver in norm_pyvers:
            continue

        if '-' in pyver:
            parts = pyver.split('-')
            min_pyver = parts[0].split('.')
            max_pyver = parts[1].split('.')

            if min_pyver[0] != max_pyver[0]:
                raise PyVerError(
                    'Cannot use version ranges (%s-%s) with different major '
                    'Python versions!'
                    % (parts[0], parts[1]))

            major_pyver = min_pyver[0]

            for i in range(int(min_pyver[1]), int(max_pyver[1]) + 1):
                pyver = '%s.%s' % (major_pyver, i)

                if pyver not in norm_pyvers:
                    pyvers.append('%s.%s' % (major_pyver, i))
        else:
            norm_pyvers.append(pyver)

    return norm_pyvers or None


def split_pyvers(pyvers_str):
    """Split a string of Python versions into a normalized list.

    Args:
        pyvers_str (str):
            A string containing a space/comma-separated list of Python
            versions/version ranges.

    Returns:
        list of str:
        The list of Python versions.
    """
    return norm_pyvers(re.split(r'[\s,]+', pyvers_str))


def validate_pyvers(pyvers):
    """Validate a list of Python versions.

    This will check each Python version in a list to ensure a valid Python
    executable can be found.

    Args:
        pyvers (list of str):
            The normalized list of Python versions.

    Raises:
        virtualenv_multiver.utils.PyVerError:
            One or more versions could not be found.
    """
    if not pyvers:
        raise PyVerError('No suitable versions of Python were found in any '
                         'configuration file or on the command line.')

    for pyver in pyvers:
        python_exe = 'python%s' % pyver

        if not which(python_exe):
            raise PyVerError('%s was not found in the path.' % python_exe)


def which(name):
    """Return whether an executable is in the user's search path.

    This expects a name without any system-specific executable extension.
    It will append the proper extension as necessary. For example, use
    "myapp" and not "myapp.exe".

    Results are cached for future lookup.

    Args:
        name (str):
            The name of the executable.

    Returns:
        bool:
        ``True`` if the app is in the path. ``False`` if it is not.
    """
    try:
        return _which_cache[name]
    except KeyError:
        # Python < 3.3
        if sys.platform == 'win32' and not name.endswith('.exe'):
            name = '%s.exe' % name

        for dir in os.environ['PATH'].split(os.pathsep):
            candidate = os.path.join(os.path.join(dir, name))

            if os.path.exists(candidate):
                return candidate

        result = None

        _which_cache[name] = result

        return result
