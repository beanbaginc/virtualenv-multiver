virtualenv-multiver
===================

[Virtualenv](https://virtualenv.pypa.io/) is a great tool for creating isolated
Python environments, for development or production installs.

One problem: It's not always easy to create a development environment
supporting multiple versions of Python. Particularly on a Mac, where
there are implementation details keeping an environment from really handling
two versions of Python.

This script fixes this annoying little problem, easily setting up a virtualenv
to work with multiple versions of Python.


Installation
------------

To install, run:

    $ pip install virtualenv-multiver


Usage
-----

Usage is simple. Simply run the script with the path and the list of Python
versions. For example:

    $ virtualenv-multiver my-environment 2.6 2.7 3.4

You can run this to create a new environment, or you can run it on an existing
environment to convert it to a multi-Python environment.


Who's using it?
---------------

We use virtualenv-multiver at [Beanbag](http://www.beanbaginc.com/) to help with
the development and packaging of [Review Board](https://www.reviewboard.org/).

If you use virtualenv-multiver, let us know and we'll add you to a shiny new
list on this page.
