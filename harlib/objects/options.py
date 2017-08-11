#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# harlib
# Copyright (c) 2014-2017, Andrew Robbins, All rights reserved.
#
# This library ("it") is free software; it is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY; you can redistribute it and/or
# modify it under the terms of LGPLv3 <https://www.gnu.org/licenses/lgpl.html>.
'''
harlib - HTTP Archive (HAR) format library
'''
from __future__ import absolute_import
from .metamodel import HarObject


class HarClientOptions(HarObject):
    '''
    TODO
    '''

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
        'proxies': {},
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
        'proxies': dict,
    }


class HarServerOptions(HarObject):
    '''
    TODO
    '''

    _optional = {
        'verbosity': None,
    }


class HarSocketOption(HarObject):
    '''
    TODO
    '''

    _required = [
        'level',
        'name',
        'value',
    ]

    _optional = {
        'comment': '',
    }
