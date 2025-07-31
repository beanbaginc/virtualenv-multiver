virtualenv-multiver
===================

[![Latest Release](https://img.shields.io/pypi/v/virtualenv-multiver)](https://pypi.org/project/virtualenv-multiver)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Review Board](https://img.shields.io/badge/Review%20Board-d0e6ff?label=reviewed%20with)](https://www.reviewboard.org)
[![Python](https://img.shields.io/pypi/pyversions/virtualenv-multiver)](https://pypi.org/project/virtualenv-multiver)

`virtualenv-multiver` is a wrapper around
[virtualenv](https://virtualenv.pypa.io/en/latest/), the standard tool for
creating isolated Python environments. It's built to allow multiple versions of
Python to be usable within a single environment. This is really handy when
you're doing development and testing across a range of Python versions, and you
don't want to have to juggle your active environment for every version.

It also comes with a handy tool called ``pydo``, which can run a Python/Pip
command across a range of Python versions.


Installation
============

Simple::

```console
$ pip install virtualenv-multiver
```


Virtualenv Usage
================

Also simple. To create a new virtual environment, just provide the path to
that environment and the versions you want installed. For example::

```console
$ virtualenv-multiver ~/venvs/my-project 2.7 3.8-3.11
```

Or for pypy::

```console
$ virtualenv-multiver ~/venvs/my-project pypy pypy3
```

The resulting virtual environment will include all those versions of Python
without any additional configuration.


pydo Usage
==========

``pydo`` can run a command across a range of Python versions. It looks for
a ``commandX.Y`` or ``command-X.Y`` that it can run for the provided command
and for each version of Python.

Usage:

```console
$ pydo [<version> [<version> ...]] <command>
```

Versions are in X.Y form, and can include ranges like ``3.8-3.14``.

For example:

```console
$ pydo 2.7 3.6 3.8-3.14 pip install -e .
```

This will automatically run:

```console
$ python2.7 -m pip install -e .
$ python3.6 -m pip install -e .
$ python3.8 -m pip install -e .
$ python3.9 -m pip install -e .
$ python3.10 -m pip install -e .
$ python3.11 -m pip install -e .
$ python3.12 -m pip install -e .
$ python3.13 -m pip install -e .
$ python3.14 -m pip install -e .
```

If you don't specify any versions, the Python versions available in the
virtualenv-multiver environment will be used.

You can also configure the list of default versions in ``.pydorc``,
``pyproject.toml``, or ``setup.cfg``.


Configuring pydo
----------------

``pydo`` first checks for a ``$VIRTUAL_ENV/.pydorc`` file.

If not found, it will check in the current directory and all parent
directories for each of these files:

* ``.pydorc``
* ``pyproject.toml``
* ``setup.cfg``


### .pydorc

``pydo`` first checks for a ``.pydorc`` file. One is automatically generated
in your virtualenv-multiver environment (for environments created using
``virtualenv-multiver`` 3.0 or higher).

Format:

```ini
[pydo]
pyvers=<version>[, <version>, ...]
```

For example:

```ini
[pydo]
pyvers=2.7,3.8-3.11
```


### pyproject.toml

``pydo`` next checks for a ``pyproject.toml`` file. This requires ``toml``
support in your Python environment.

Format:

```ini
[tool.pydo]
pyvers = ["<version>", "..."]
```

For example:

```ini
[tool.pydo]
pyvers = ["2.7", "3.8-3.11"]
```


### setup.cfg

``pydo`` finally checks for a ``setup.cfg`` file.

Format:

```ini
[pydo]
pyvers=<version>[, <version>, ...]
```

For example:

```ini
[pydo]
pyvers=2.7,3.8-3.11
```


FAQ
===

How does virtualenv-multiver work?
----------------------------------

``virtualenv-multiver`` runs through the list of Python versions provided and
calls out to ``virtualenv`` for each version

After each ``virtualenv`` call, it fixes up the tree a bit. This involves:

* Ensuring symlinks point to the right place (``python2`` points to the
  latest ``python2.*`` specified, for instance)

* Patching any installed scripts (such as ``pip3.8``) and making sure it
  points to the correct, versioned interpreter

* Moves and patches some binaries and configuration files around to avoid
  collision issues.

Once done, it sets the top-level symlinks for ``python2``, ``python3``,
``pip2``, ``pip3``, etc. (any that specify a major version) to point to the
latest version in that series.

It then sets the generic, version-less ones (``python``, ``pip``, etc.) to
point to the Python 2 versions (if Python 2 is installed), or Python 3 (if
not). This helps ensure compatibility with scripts that expect ``python`` to
mean "Python 2".


Are all versions of CPython supported?
--------------------------------------

Yes. Pretty much. It depends on whether virtualenv itself will support the
version.


Is PyPY supported?
------------------

Yes. Sorta.

PyPy doesn't cleanly install alongside CPython in a virtual environment, due
to CPython and PyPy claiming some of the same files and directories. We only
allow PyPy to install independently or alongside another PyPy.

You may have issues even with multiple PyPy installations. They'll install and
run, but will share the same ``site-packages`` directory, which is beyond our
control for the moment.

If this isn't a problem for you, go for it. Otherwise, you may want to stick
to a standard ``virtualenv`` call for those.


How do I report a bug?
----------------------

You can file an issue on the GitHub issue tracker.


Who uses this?
--------------

We use ``virtualenv-multiver`` at [Beanbag](https://www.beanbaginc.com/) for
our [Review Board](https://www.reviewboard.org/) and
[RBCommons](https://rbcommons.com/) products.

If you use this, let us know and we'll add you to a list here!


What else do you build?
-----------------------

Lots of things. Check out some of our other [open source projects](
https://www.beanbaginc.com/opensource/).
