"""Configuration loading for virtualenv-multiver and pydo.

Version Added:
    3.0
"""

import os
import sys

from configparser import (NoOptionError,
                          NoSectionError,
                          RawConfigParser)

from virtualenv_multiver.utils import split_pyvers

try:
    # Python 3.11+
    import tomllib as toml
except ImportError:
    try:
        # Third-party `toml` module for Python.
        import toml
    except ImportError:
        toml = None


def _load_toml_pyvers(config_path):
    """Load Python versions from a TOML file.

    Args:
        config_path (str):
            The path to the configuration file.

    Returns:
        list of str:
        The list of Python versions. This will be ``None`` if versions could
        not be loaded.
    """
    if toml is None:
        sys.stderr.write('Unable to parse "%s". The "toml" package is not '
                         'installed for Python %s.%s.\n'
                         % (config_path,
                            sys.version_info[0],
                            sys.version_info[1]))
        return None

    try:
        with open(config_path, 'r') as fp:
            config_data = toml.load(fp)
    except Exception as e:
        sys.stderr.write('Unable to read "%s": %s\n'
                         % (config_path, e))
        return None

    try:
        pyvers = config_data['tool']['pydo']['pyvers']
    except KeyError:
        return None

    if isinstance(pyvers, str):
        return split_pyvers(pyvers)
    elif isinstance(pyvers, list):
        norm_pyvers = []

        for pyver in pyvers:
            if isinstance(pyver, str):
                norm_pyvers.append(pyver)
            else:
                sys.stderr.write('%r in %s is a %s, not a string! Skipping.\n'
                                 % (pyver, config_path, type(pyver)))

        return norm_pyvers

    sys.stderr.write('Unexpected value for pyvers in "%s": %r\n'
                     % (config_path, pyvers))

    return None


def _load_ini_pyvers(config_path):
    """Load Python versions from an INI file.

    Args:
        config_path (str):
            The path to the configuration file.

    Returns:
        list of str:
        The list of Python versions. This will be ``None`` if versions could
        not be loaded.
    """
    config_parser = RawConfigParser()
    config_parser.read(config_path)

    try:
        pyvers = config_parser.get('pydo', 'pyvers')
    except (NoOptionError, NoSectionError):
        pyvers = None

    if not pyvers:
        return None

    return split_pyvers(pyvers)


def _walk_parents(start_dir):
    """Walk directory paths up to the root.

    Args:
        start_dir (str):
            The starting directory.

    Yields:
        str:
        The path to each directory.
    """
    config_dir = start_dir

    while True:
        yield config_dir

        config_dir, remain = os.path.split(config_dir)

        if not remain:
            # We've walked up to the root. Bail.
            break


def get_pyvers():
    """Return a list of Python versions from the environment.

    This will check the :file:`.pydorc` file in the active virtual environment
    (if any), and then look for and parse the following files in the current
    directory up to the root of the tree:

    * :file:`.pydorc`
    * :file:`pyproject.toml`
    * :file:`setup.cfg`

    The first file with Python versions wins.

    Returns:
        list of str:
        The list of Python versions. This will be ``None`` if versions could
        not be loaded.
    """
    venv_path = os.environ.get('VIRTUAL_ENV')

    if venv_path:
        venv_pydorc = os.path.join(venv_path, '.pydorc')

        if os.path.exists(venv_pydorc):
            return _load_ini_pyvers(venv_pydorc)

    config_filenames = [
        ('.pydorc', _load_ini_pyvers),
        ('pyproject.toml', _load_toml_pyvers),
        ('setup.cfg', _load_ini_pyvers),
    ]

    for cur_dir in _walk_parents(os.getcwd()):
        for config_filename, config_loader in config_filenames:
            config_path = os.path.join(cur_dir, config_filename)

            if os.path.exists(config_path):
                pyvers = config_loader(config_path)

                if pyvers is not None:
                    return pyvers

    return None
