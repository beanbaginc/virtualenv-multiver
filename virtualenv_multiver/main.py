# Configures a single virtualenv to support multiple versions of Python.
#
# This will handle the hard work of installing each version of Python and
# patching the installed files.
#
# Primarily, this is important on the Mac, which makes use of a .Python
# symlink for executing the build of Python. This symlink is tied to a
# specific version of Python, and achieving cross-version support means
# changing the reference in the python binary.
from __future__ import unicode_literals

import itertools
import os
import re
import shutil
import subprocess
import sys
from glob import glob

try:
    from virtualenv import mach_o_change
except ImportError:
    # This isn't running on macOS using the system Python install.
    mach_o_change = None


DEBUG = (os.getenv('DEBUG') == '1')

PYTHON_VERSION_RE = re.compile(br'^Python (\d+)\.(\d+)')

DEFAULT_SCRIPTS = [
    'easy_install%s',
    'easy_install-%s',
    'idle%s',
    'pip%s',
    'pip-%s',
    'pydoc%s',
    'python%s-config',
    'pysetup%s',
    'wheel%s',
]


def debug(text):
    """Log a debug message to the console.

    Args:
        text (unicode):
            The text to log.
    """
    if DEBUG:
        print(text)


def patch_default_scripts(bin_path, script_suffix, python_bin_name):
    """Patch a set of default scripts for a given version of Python.

    This will replace the ``#!/path/to/python` line for any matched scripts
    with a version that points to the provided Python interpreter.

    Args:
        bin_path (unicode):
            The path to the virtualenv's bin directory.

        script_suffix (unicode):
            The suffix for the script filename to patch.

        python_bin_name (unicode):
            The name of the Python interpreter to put into the shebang.
    """
    expected_shebang = (
        '#!%s'
        % os.path.abspath(os.path.join(bin_path, python_bin_name))
    )

    scripts_to_patch = (
        os.path.join(bin_path, script_name % script_suffix)
        for script_name in DEFAULT_SCRIPTS
    )

    for script_path in scripts_to_patch:
        if os.path.exists(script_path):
            with open(script_path, 'r') as fp:
                lines = fp.read().splitlines(True)

            shebang = lines[0]
            norm_shebang = shebang.strip()

            if norm_shebang != expected_shebang:
                debug('Patching %s for %s' % (script_path, python_bin_name))

                # This shebang needs to be updated. Make sure we're preserving
                # the line ending so we don't break anything.
                ending = shebang[len(norm_shebang):]

                with open(script_path, 'w') as fp:
                    fp.write('%s%s' % (expected_shebang, ending))
                    fp.write(''.join(lines[1:]))


def symlink(source_path, dest_path):
    """Create or replace a symlink.

    Args:
        source_path (unicode):
            The path that the symlink will point to.

        dest_path (unicode):
            The path of the symlink.
    """
    try:
        os.unlink(dest_path)
    except OSError:
        pass

    debug('Symlinking %s -> %s' % (source_path, dest_path))

    os.symlink(source_path, dest_path)


def convert_symlink(bin_path, symlink_path):
    """Convert a symlink into a file or directory.

    Args:
        bin_path (unicode):
            The path to the virtualenv's :file:`bin` directory.

        symlink_path (unicode):
            The path to the symlink to convert.
    """
    link_target = os.readlink(symlink_path)

    while os.path.islink(link_target):
        link_target = os.readlink(link_target)

    if not os.path.isabs(link_target):
        link_target = os.path.abspath(os.path.join(bin_path,
                                                   link_target))

    debug('Converting symlink %s' % symlink_path)

    os.unlink(symlink_path)

    if os.path.isdir(link_target):
        os.mkdir(symlink_path, 0o755)
        shutil.copytree(link_target, symlink_path)
    else:
        shutil.copy(link_target, symlink_path)


def get_python_version(python_bin):
    """Return the Python major.minor version parsed from an interpreter.

    Args:
        python_bin (unicode):
            The path to the :file:`python` binary to execute.

    Returns:
        unicode:
        The "<major>.<minor>" version.
    """
    try:
        parsed_version = subprocess.check_output(
            [python_bin, '--version'],
            stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        sys.stderr.write('Failed to call %s --version: %s\n'
                         % (python_bin, e))
        sys.stderr.write('Your virtual environment is incomplete.\n')
        sys.exit(1)

    m = PYTHON_VERSION_RE.search(parsed_version)

    if not m:
        sys.stderr.write('Unable to parse Python version from "%s"\n'
                         % parsed_version)
        sys.stderr.write('Your virtual environment is incomplete.\n')
        sys.exit(1)

    return '%s.%s' % m.groups()


def get_site_py_path(python_bin):
    return subprocess.check_output(
        [python_bin, '-c', 'import site; print(site.__file__)']
    ).strip()


def update_pyvenv(venv_path, priv_bin_path, python_version):
    """Rename the pyvenv.cfg file to a version-specific file.

    This will rename the virtualenv's :file:`pyvenv.cfg` to a new name
    that contains the version information, and update any relevant
    :file:`site.py` if needed.

    Args:
        venv_path (unicode):
            The path to the virtualenv.

        priv_bin_path (unicode):
            The path to the private binary directory for the version of
            Python.

        python_version (unicode):
            The Python version (e.g., "2.7", "3.6").
    """
    pyvenv_path = os.path.join(venv_path, 'pyvenv.cfg')

    if os.path.exists(pyvenv_path):
        shutil.move(pyvenv_path, os.path.join(priv_bin_path, 'pyvenv.cfg'))

    site_py_paths = [
        os.path.join(venv_path, 'lib', 'python%s' % python_version, 'site.py'),
        os.path.join(venv_path, 'lib-python', python_version, 'site.py'),
    ]

    for site_py_path in site_py_paths:
        if os.path.exists(site_py_path):
            debug('Patching %s' % site_py_path)

            with open(site_py_path, 'r') as fp:
                data = fp.read()

            data = data.replace(
                '{}pyvenv.cfg"',
                '{}%s/pyvenv.cfg"' % os.path.basename(priv_bin_path))

            with open(site_py_path, 'w') as fp:
                fp.write(data)


def create_versioned_symlinks(bin_path, major_py_bins, major_py_latest):
    """Create versioned symlinks for the Python binaries and scripts.

    This will create ``bin`` and ``binX`` symlinks for all installed versions
    of the Python binaries and scripts.

    Args:
        bin_path (unicode):
            The path to the :file:``bin` directory in the virtualenv.

        major_py_bins (dict):
            A dictionary mapping major Python versions to :file:`python`
            binaries.

        major_py_latest (dict):
            A dictionary mapping major Python versions to the latest
            specified version in that series.

        has_pypy (bool, optional):
            Whether there's a pypy version being installed.
    """
    # Add python and pythonX symlinks for the last-specified major versions.
    for major_ver, pythonxy_bin in major_py_bins.items():
        symlink(pythonxy_bin, os.path.join(bin_path, 'python%s' % major_ver))

    # Add script and scriptX symlinks for the last-specified major versions.
    for major_ver, latest_ver in major_py_latest.items():
        for script_name_fmt in DEFAULT_SCRIPTS:
            script_x_filename = script_name_fmt % major_ver
            script_xy_filename = script_name_fmt % latest_ver

            if os.path.exists(os.path.join(bin_path, script_xy_filename)):
                symlink(script_xy_filename,
                        os.path.join(bin_path, script_x_filename))

    # Set the main 'python' binary to something useful. It *should* point to
    # python2, if installed. Otherwise, point it to the next version up.
    for major_ver in ('2', '3', '4'):
        if major_ver in major_py_bins:
            python_bin = major_py_bins[major_ver]

            symlink('python%s' % major_ver,
                    os.path.join(bin_path, 'python'))

            if os.path.basename(python_bin).startswith('pypy'):
                symlink('pypy%s' % major_ver,
                        os.path.join(bin_path, 'pypy'))

            for script_name_fmt in DEFAULT_SCRIPTS:
                script_filename = script_name_fmt % ''
                script_x_filename = script_name_fmt % major_ver

                if (not script_filename.endswith('-') and
                    os.path.exists(os.path.join(bin_path, script_x_filename))):
                    symlink(script_x_filename,
                            os.path.join(bin_path, script_filename))

            break


def make_version_sort_key(version):
    """Return a key for a Python version, for sorting purposes.

    Args:
        version (unicode):
            The provided Python version.

    Returns:
        tuple:
        A key used for sorting.
    """
    if version.startswith('pypy'):
        priority = 0
        version = version[4:]
    else:
        priority = 1

    return [priority] + version.split('.')


def main():
    if len(sys.argv) < 3:
        sys.stderr.write('Usage: virtualenv-multiver <path> <X.Y>...\n')
        sys.exit(1)

    path = sys.argv[1]
    versions = sorted(sys.argv[2:],
                      key=make_version_sort_key)

    bin_path = os.path.join(path, 'bin')
    lib_path = os.path.join(path, 'lib')
    python_bin_path = os.path.join(bin_path, 'python')
    pyvenv_cfg_path = os.path.join(path, 'pyvenv.cfg')

    major_py_bins = {}
    major_py_latest = {}

    # Sanity-check whether there are both pypy and non-pypy releases
    # specified.
    has_pypy_version = False
    has_cpy_version = False

    for version in versions:
        if version.startswith('pypy'):
            has_pypy_version = True
        else:
            has_cpy_version = True

    if has_pypy_version:
        if has_cpy_version:
            sys.stderr.write(
                'A virtualenv cannot contain both PyPy and CPython versions.\n'
                'Please create separate virtualenvs for each.\n')
            sys.exit(1)
        elif len(versions) != 1:
            sys.stderr.write(
                'WARNING: All PyPy interpreters will share the same copy of\n'
                '         site-packages! This is beyond our control. You\n'
                '         may not want to use virtualenv-multiver for this\n'
                '         if that will be a problem.\n'
                '\n')

    print('Installing virtual environments for %s' % ', '.join(versions))

    # Begin building the virtualenvs.
    for version in versions:
        is_pypy = version.startswith('pypy')

        if is_pypy:
            if version == 'pypy':
                major_version = '2'
            else:
                major_version = version[4:]

            pythonxy_bin = version
            pythonx_bin = version
        else:
            major_version = version[0]
            pythonxy_bin = 'python%s' % version
            pythonx_bin = 'python%s' % major_version

        # Install this version of Python into the virtualenv.
        subprocess.call(['virtualenv', '-p', pythonxy_bin, path])

        pythonxy_bin_path = os.path.join(bin_path, pythonxy_bin)

        # Get the version of Python.
        if is_pypy:
            python_version = get_python_version(pythonxy_bin_path)
        else:
            python_version = version

        # If pythonX.Y is a symlink, we'll need to turn it into a proper
        # executable.
        if os.path.islink(pythonxy_bin_path):
            convert_symlink(bin_path=bin_path,
                            symlink_path=pythonxy_bin_path)

        # If the "lib" directory is a symlink, we need to convert that as well.
        if os.path.islink(lib_path):
            convert_symlink(bin_path=bin_path,
                            symlink_path=lib_path)

        # Move the interpreter into a private version-specific bin directory,
        # where we'll be able to put the pyvenv.cfg.
        priv_bin_path = os.path.join(os.path.abspath(path),
                                     '.bin-%s' % version)
        priv_pythonxy_bin = os.path.join(priv_bin_path, pythonxy_bin)

        if not os.path.exists(priv_bin_path):
            os.mkdir(priv_bin_path, 0o755)

        shutil.move(pythonxy_bin_path, priv_pythonxy_bin)

        if is_pypy:
            # We also need to move any libpypy* files.
            for libpypy_filename in glob(os.path.join(bin_path, 'libpypy*')):
                shutil.move(libpypy_filename, priv_bin_path)

        if pythonxy_bin == 'pypy':
            # PyPy for Python 2.7 has its main binary as "pypy". Let's rename
            # that, so it can be installed in parallel with pypy3.
            pythonxy_bin = 'pypy2'
            pythonx_bin = 'pypy2'

        # Recompute these, since we've moved things around.
        pythonxy_bin_path = os.path.join(bin_path, pythonxy_bin)
        pythonx_bin_path = os.path.join(bin_path, pythonx_bin)

        # Link the wrapper in bin/ to the private interpreter in .bin-X.Y.
        # This should result in the correct interpreter being run, but with
        # the pyvenv.cfg (from modern virtualenvs) being found within the
        # .bin-X.Y.
        symlink(priv_pythonxy_bin, pythonxy_bin_path)

        # Rename any pyvenv.cfg and point to the new file in any site.py.
        update_pyvenv(venv_path=path,
                      priv_bin_path=priv_bin_path,
                      python_version=python_version)

        # Store some metadata for later script generation.
        major_py_bins[major_version] = pythonxy_bin
        major_py_latest[major_version] = python_version

        # If there's a .Python symlink at the root of the virtualenv, then
        # we're likely on a Mac. All python binaries are going to try to
        # actually run whatever this is pointing to. Instead, we'll need to
        # patch the binary to point to a version-specific symlink.
        mac_python_link = os.path.join(path, '.Python')

        if os.path.exists(mac_python_link):
            # Note that the new path must be shorter than the old one, so we're
            # shortening to ".PyX.Y".
            new_mac_python_link = os.path.join(path, '.Py%s' % version)
            shutil.move(mac_python_link, new_mac_python_link)

            orig_python_path = os.readlink(new_mac_python_link)
            old_python_exec_path = '@executable_path/../.Python'
            new_python_exec_path = '@executable_path/../.Py%s' % version

            # This logic is courtesy of virtualenv.
            try:
                mach_o_change(priv_pythonxy_bin, old_python_exec_path,
                              new_python_exec_path)
            except:
                try:
                    subprocess.call(['install_name_tool', '-change',
                                     old_python_exec_path,
                                     new_python_exec_path,
                                     priv_pythonxy_bin])
                except:
                    sys.stderr.write(
                        'Could not patch %s with the Python path. '
                        'Make sure to install the Apple development '
                        'tools.\n')
                    raise

        bins_to_remove = [
            os.path.join(bin_path, 'python'),
            os.path.join(bin_path, 'pypy'),
            os.path.join(path, '.Python'),
        ] + list(itertools.chain.from_iterable([
            (os.path.join(bin_path, script_name % ''),
             os.path.join(bin_path, script_name % major_version))
            for script_name in DEFAULT_SCRIPTS
        ]))

        if is_pypy:
            python_lib_dir = os.path.join(path, 'lib-python',
                                          'python-%s' % python_version)
            bins_to_remove.append(os.path.join(bin_path,
                                               'python%s' % python_version))
        else:
            python_lib_dir = os.path.join(path, 'lib', 'python-%s' % version)
            bins_to_remove.append(os.path.join(bin_path, pythonx_bin))

        for link_path in bins_to_remove:
            try:
                os.unlink(link_path)
                debug('Removed %s' % link_path)
            except OSError:
                pass

        # Update the path to all default scripts.
        #
        # We have three types we're updating (in this order):
        #
        # 1. The version-less scripts (pip, wheel, easy_install, etc.)
        # 2. The major-versioned scripts (pip2, pip3, easy_install2, etc.)
        # 3. The major.minor-versioned scripts (pip2.7, pip3.8,
        #    easy_install-2.7, etc.)
        patch_default_scripts(bin_path=bin_path,
                              script_suffix='',
                              python_bin_name='python')
        patch_default_scripts(bin_path=bin_path,
                              script_suffix=version[0],
                              python_bin_name=pythonx_bin)
        patch_default_scripts(bin_path=bin_path,
                              script_suffix=version,
                              python_bin_name=pythonxy_bin)

    # Create symlinks for all the versions of the scripts and interpreters.
    create_versioned_symlinks(bin_path=bin_path,
                              major_py_bins=major_py_bins,
                              major_py_latest=major_py_latest)

    # Create a single pyvenv.cfg for this virtualenv based on the last version
    # installed. This is still not ideal, because it's version-specific, but
    # in practice it should be okay.
    #
    # An individual Python interpreter is going to use the one bound to the
    # .bin-X.Y directory, so the majority case is covered.
    #
    # pip does look for this, though, in order to see if system packages are
    # used. So we need to set that.
    symlink(os.path.join('.bin-%s' % versions[-1], 'pyvenv.cfg'),
            os.path.join(path, 'pyvenv.cfg'))
