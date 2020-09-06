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

import os
import shutil
import subprocess
import sys

try:
    from virtualenv import mach_o_change
except ImportError:
    # This isn't running on macOS using the system Python install.
    mach_o_change = None


def main():
    if len(sys.argv) < 3:
        sys.stderr.write('Usage: virtualenv-multiver <path> <X.Y>...\n')
        sys.exit(1)

    path = sys.argv[1]
    versions = sys.argv[2:]

    bin_path = os.path.join(path, 'bin')
    python_bin_path = os.path.join(bin_path, 'python')

    for version in versions:
        if version.startswith('pypy'):
            pythonxy_bin = version
            pythonx_bin = version
        else:
            pythonxy_bin = 'python%s' % version
            pythonx_bin = 'python%s' % version[0]

        pythonxy_bin_path = os.path.join(bin_path, pythonxy_bin)

        # virtualenv seems to either create the binary as 'pythonX.Y', or as
        # simply 'python'. We can't trust that it won't overwrite something we
        # care about, so delete these links. They'll be rebuilt by virtualenv.
        for link_path in (os.path.join(bin_path, 'python'),
                          os.path.join(bin_path, pythonx_bin),
                          os.path.join(path, '.Python')):
            try:
                os.unlink(link_path)
            except OSError:
                pass

        # Install this version of Python into the virtualenv.
        subprocess.call(['virtualenv', '-p', pythonxy_bin, path])

        # If pythonX.Y is a symlink, we'll need to turn it into a proper
        # executable.
        if os.path.islink(pythonxy_bin_path):
            os.unlink(pythonxy_bin_path)
            shutil.move(python_bin_path, pythonxy_bin_path)
            os.symlink(pythonxy_bin, python_bin_path)

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
                mach_o_change(pythonxy_bin_path, old_python_exec_path,
                              new_python_exec_path)
            except:
                try:
                    subprocess.call(['install_name_tool', '-change',
                                     old_python_exec_path,
                                     new_python_exec_path,
                                     pythonxy_bin_path])
                except:
                    sys.stderr.write(
                        'Could not patch %s with the Python path. '
                        'Make sure to install the Apple development '
                        'tools.\n')
                    raise
