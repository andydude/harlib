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
from django.http.response import HttpResponse
import os.path

# Create your views here.

def index(request):
    selfdir = os.path.dirname(__file__)
    with open(selfdir + '/templates/harlib_viewer/index.html') as f:
        d = f.read()
    return HttpResponse(d)
