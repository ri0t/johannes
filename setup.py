#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# johannes - a minimalist Python library management system
# ========================================================
# Copyright (C) 2011-2014 Heiko 'riot' Weinen <riot@c-base.org>
# and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup
import os

# TODO: rebuild the package finder using setuptools & pkg_resources

def include_readme():
    readme = open("README.rst")
    include = readme.readlines(10)[2:10]
    readme.close()
    return "".join(include)


def is_package(path):
    return (
        os.path.isdir(path) and
        os.path.isfile(os.path.join(path, '__init__.py'))
    )


def find_packages(path, base=""):
    """ Find all packages in path """
    packages = {}
    for item in os.listdir(path):
        dir = os.path.join(path, item)
        if is_package(dir):
            if base:
                module_name = "%(base)s.%(item)s" % vars()
            else:
                module_name = item
            packages[module_name] = dir
            packages.update(find_packages(dir, module_name))
    return packages


packages = find_packages(".")
package_names = packages.keys()

setup(name="johannes",
      version="0.0.3",
      description="johannes",

      author="Heiko 'riot' Weinen",
      author_email="riot@c-base.org",
      url="https://github.com/ri0t/johannes",
      license="GNU General Public License v3",
      packages=package_names,
      package_dir=packages,
      scripts=[
          'server.py',
      ],
      data_files=[
          ('/etc/init.d', ["etc/init.d/johannes"]),
          ('/etc/johannes', ["etc/johannes/config.json"])
      ],

      long_description=include_readme(),
      # These versions are not strictly checked, older ones may or may not work.
      install_requires=[
          #'CherryPy==3.3.0',
          #'Axon==1.7.0',
          #'Kamaelia==1.1.2',
          #'Pynmea==0.3.1',
          #'Mako==0.9.1',
          #'jsonpickle==0.1',
          #'pymongo==2.6.3',
          #'bson==0.3.3',
          'isbntools==3.3.6',
          'flask==0.10.1',
          'voluptuous==0.8.5',
      ]

)
