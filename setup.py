#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright <2013> Suneel Chakravorty <suneel0101@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup

setup(name='django-restroom',
      version='0.0.1',
      description='Super lightweight REST API framework for Django',
      author='Suneel Chakravorty',
      author_email='suneel0101@gmail.com.com',
      url='https://github.com/suneel0101/django-restroom',
      packages=['restroom'],
      install_requires=[
          "django",
      ],
      package_data={
          'django-restroom': ['LICENSE', '*.md'],
      })
