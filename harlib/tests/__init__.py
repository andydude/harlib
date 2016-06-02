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


try:
    from . import httplib
except ImportError as err:
    print(repr(err))

try:
    from . import requests
except ImportError as err:
    print(repr(err))

try:
    from . import django
except ImportError as err:
    print(repr(err))


try:
    from . import urllib2
except ImportError as err:
    print(repr(err))

try:
    from . import urllib3
except ImportError as err:
    print(repr(err))
