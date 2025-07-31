Releases and Updates
====================

Version 3.0 (30-July-2025)
--------------------------

* Added support for specifying version ranges.

  `virtualenv-multiver` now supports specifying Python versions as a range.
  For example, `3.11-3.14`. This can be combined with individual versions
  to simplify setting up an environment with subsets of Python versions.

* Added a `pydo` command for running commands across all installed Python
  versions.

  `pydo` can be used to run `pip` or Python scripts using every Python
  version installed in a virtualenv. For example:

  ```shell
  $ pydo pip install <package>
  $ pydo ./my-script.py
  $ pydo python -m some-module
  ```

* Added a configuration file for specifying the Python versions used to
  create an environment.

  The list of Python versions for an environment can now be placed in a
  `.pydorc`, `pyproject.toml`, or `setup.cfg`.

  For example:

  ```ini
  # .pydorc or setup.cfg
  [pydo]
  pyvers=2.7,3.8-3.11

  # pyproject.toml
  [tool.pydo]
  pyvers = ["2.7", "3.8-3.11"]
  ```

* The latest compatible `pip`, `setuptools`, and `wheel` are now downloaded
  and installed by default.

  We now explicitly download the latest compatible versions in order to
  ensure working installs for all Python versions, to prevent too-new versions
  from being installed for older Python versions.

* Added arguments for controlling pip install behavior.

  `virtualenv-multiver` now supports options for controlling whether `pip`,
  `setuptools`, and `wheel` packages are installed, using `--no-pip`,
  `--no-setuptools`, and `--no-wheel`, respectively.

  `--no-download` can also be used to prevent downloading the latest compatible
  packages for the environment.

* Dropped support for installing this package on Python 3.7 or older.

* Fixed issues generating the `pyvenv.cfg` symlink.


Version 2.0.1 (20-January-2021)
-------------------------------

* Fixed generating interpreters that can be used in shell scripts.

  virtualenv-multiver 2.0 added support for modern virtualenv's pyvenv.cfg
  files by moving the pythonX.Y interpreters into special .bin-X.Y
  directories, where the pyvenv.cfg could live. It then added a wrapper
  script to forward calls there.

  This didn't always work. As execve documents, only compiled programs, not
  interpreted scripts, can be used as a shell interpreter. That didn't stop
  it from working on some systems, but it was clearly broken on others,
  resulting the script (e.g., pip) being executed as a bash script and not
  a Python script.

  At the time this was written, we couldn't use a symlink, as pyvenv.cfg
  would be found in the wrong location. It appears that's fixed (perhaps in
  a modern virtualenv). As such, we should be safe to use a symlink now,
  ditching the wrapper and avoiding the issues.


Version 2.0 (18-September-2020)
-------------------------------

* Updated to work with modern versions of virtualenv.

  Modern versions of virtualenv have a lot of new machinery to set up a
  virtualenv and to store configuration. There were a lot of complications
  to sort out from this, but virtualenv-multiver should now be more
  future-proof as a result. If you hit any issues, please let us know.

  Older versions of virtualenv should still be supported.

* The order of Python versions passed to virtualenv-multiver no longer
  matters.

  It used to be that the order impacted which version of Python the
  `python` and `pip` scripts would link to. Now the versions are sorted
  and scripts, symlinks, and binaries are generated with more care.


Version 1.0 (5-September-2020)
------------------------------

* Added support for creating a virtualenv on pypy.

* Fixed an issue patching the Python binaries when not using a
  system-provided version of Python on macOS.


Version 0.5.0 (28-June-2015)
----------------------------

* First public release.
