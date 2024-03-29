#!/usr/bin/env python
#
# setup.py -- Installation for virtualenv-multiver
#
# Copyright (C) 2015 Beanbag, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# 'Software'), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from setuptools import setup, find_packages

from virtualenv_multiver import get_package_version


PACKAGE_NAME = 'virtualenv-multiver'


with open('README.rst', 'r') as fp:
    readme = fp.read()


setup(name=PACKAGE_NAME,
      version=get_package_version(),
      license='MIT',
      description='Python multi-version wrapper for virtualenv.',
      long_description=readme,
      url='https://github.com/beanbaginc/virtualenv-multiver',
      maintainer='Christian Hammond',
      maintainer_email='christian@beanbaginc.com',
      packages=find_packages(),
      install_requires=[
          'six',
          'toml',
          'virtualenv',
      ],
      entry_points={
          'console_scripts': [
              'pydo = virtualenv_multiver.pydo:main',
              'virtualenv-multiver = virtualenv_multiver.main:main',
          ],
      },
      python_requires=','.join([
          '>=2.7',
          '!=3.0.*',
          '!=3.1.*',
          '!=3.2.*',
          '!=3.3.*',
          '!=3.4.*',
          '!=3.5.*',
      ]),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Other Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Topic :: Software Development',
          'Topic :: Software Development :: Testing',
      ]
)
