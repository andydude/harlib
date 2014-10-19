#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# harlib
# Copyright (c) 2014, Andrew Robbins, All rights reserved.
# 
# This library ("it") is free software; it is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; you can redistribute it and/or modify it under the terms of the
# GNU Lesser General Public License ("LGPLv3") <https://www.gnu.org/licenses/lgpl.html>.
from __future__ import absolute_import
from .metamodel import HarObject

class HarClientOptions(HarObject):

    _optional = {
        'autoClose': False,
        'autoHost': False,
        'autoOrigin': False,
        'autoRedirect': False,
        'autoReferer': False,
        'charset': 'utf-8',
        'chunked': False,
        'connection': '',
        'contentRead': False,
        'decodeContent': False,
        'failOnError': False,
        'host': '',
        'mimeType': 'text/plain',
        'transferEncoding': '',
        'unverifiable': False,
        'verbosity': False,
    }

    _types = {
        'autoClose': bool,
        'autoHost': bool,
        'autoOrigin': bool,
        'autoRedirect': bool,
        'autoReferer': bool,
        'chunked': bool,
        'contentRead': bool,
        'decodeContent': bool,
        'failOnError': bool,
        'unverifiable': bool,
        'verbosity': int,
    }

class HarServerOptions(HarObject):

    _optional = {
        'verbosity': None,
    }

class HarSocketOption(HarObject):

    _required = [
        'level',
        'name',
        'value',
    ]

    _optional = {
        #'level_id': '',
        #'name_id': '',
        #'value_name': '',
        'comment': '',
    }

    def __init__(self, obj=None):
        super(HarSocketOption, self).__init__(obj)
