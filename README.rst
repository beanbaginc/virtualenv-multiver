===================
virtualenv-multiver
===================

``virtualenv-multiver`` is a wrapper around virtualenv_, the standard tool for
creating isolated Python environments. It's built to allow multiple versions
of Python to be usable within a single environment. This is really handy when
you're doing development and testing across a range of Python versions, and
you don't want to have to juggle your active environment for every version.


.. _virtualenv: https://virtualenv.pypa.io/en/latest/


Installation
============

Simple::

    pip install virtualenv-multiver


Usage
=====

Also simple. To create a new virtual environment, just provide the path to
that environment and the versions you want installed. For example::

    virtualenv-multiver ~/venvs/my-project 2.7 3.6 3.7 3.8

Or::

    virtualenv-multiver ~/venvs/my-project pypy pypy3

The resulting virtual environment will include all those versions of Python
without any additional configuration.


FAQ
===

How does this work?
-------------------

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

We use ``virtualenv-multiver`` at Beanbag_ for our `Review Board`_ and
RBCommons_ products.

If you use this, let us know and we'll add you to a list here!


.. _Beanbag: https://www.beanbaginc.com/
.. _Review Board: https://www.reviewboard.org/
.. _RBCommons: https://rbcommons.com/


What else do you build?
-----------------------

Lots of things. Check out some of our other `open source projects`_.

.. _open source projects: https://www.beanbaginc.com/opensource/
