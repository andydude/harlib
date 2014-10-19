#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# harlib
# Copyright (c) 2014, Andrew Robbins, All rights reserved.
# 
# This library ("it") is free software; it is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; you can redistribute it and/or modify it under the terms of the
# GNU Lesser General Public License ("LGPLv3") <https://www.gnu.org/licenses/lgpl.html>.
'''
harlib - HTTP Archive (HAR) format library
'''
from __future__ import absolute_import
from setuptools import setup, find_packages
import json
import one

if __name__ == '__main__':
    setup_config = json.load(open("package.json"))
    setup(
        long_description = open('README.md').read(),
        install_requires = open("requires.txt").readlines(),
        packages = find_packages(),
        download_url = one.__download_url__,
        url = one.__homepage_url__,
        version = one.__version__,
        **setup_config
    )
