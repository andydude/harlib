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
from collections import Mapping, Sequence
import six

from .metamodel import HarObject

from .options import (
    HarClientOptions,
    HarServerOptions,
    HarSocketOption,
)

from .request import HarRequest
from .response import HarResponse


class HarCache(HarObject):

    _required = []

    _optional = {
        'beforeRequest': None,
        'afterRequest': None,
        'comment': '',
    }

    def __init__(self, obj=None):
        super(HarCache, self).__init__(obj)


class HarPage(HarObject):

    _required = [
        'startedDateTime',
        'id',
        'title',
        'pageTimings',
    ]

    _optional = {
        'comment': '',
    }

    def __init__(self, obj=None):
        super(HarPage, self).__init__(obj)


class HarPageTimings(HarObject):

    _optional = {
        'onContentLoad',
        'onLoad',
        'comment',
    }

    def __init__(self, obj=None):
        super(HarPageTimings, self).__init__(obj)


class HarTimings(HarObject):

    _required = [
        'send',
        'wait',
        'receive',
    ]

    _optional = {
        'blocked': -1,
        'dns': -1,
        'connect': -1,
        'ssl': -1,
        'send': -1,
        'wait': -1,
        'receive': -1,
        'comment': '',
        '_total': -1,  # aka ../time
    }

    _types = {
        'blocked': int,
        'dns': int,
        'connect': int,
        'ssl': int,
        'send': int,
        'wait': int,
        'receive': int,
        '_total': int,  # aka ../time
    }


class HarTimeouts(HarTimings):
    pass


class HarNameVersionPair(HarObject):

    _required = [
        'name',
        'version',
    ]

    _optional = {
        'name': None,
        'version': None,
        'comment': '',
    }

    def __init__(self, obj=None):
        if not obj:
            obj = None
        super(HarNameVersionPair, self).__init__(obj)


class HarCreator(HarNameVersionPair):
    pass


class HarBrowser(HarNameVersionPair):
    pass


class HarEntry(HarObject):

    _required = [
        'startedDateTime',
        'time',
        'request',
        'response',
    ]

    _optional = {
        'cache': {},
        'comment': '',
        'connection': '',
        'pageref': '',
        'serverIPAddress': '',
        'timings': {'send': -1, 'wait': -1, 'receive': -1},
        '_clientIPAddress': '',
        '_clientPort': 0,
        '_serverPort': 0,
        '_socketOptions': [],
        '_serverOptions': {},
        '_clientOptions': {},
        '_timeouts': {'send': -1, 'wait': -1, 'receive': -1},
    }

    _types = {
        'time': float,
        'cache': HarCache,
        'request': HarRequest,
        'response': HarResponse,
        '_clientPort': int,
        '_serverPort': int,
        '_socketOptions': [HarSocketOption],
        '_serverOptions': HarServerOptions,
        '_clientOptions': HarClientOptions,
        '_timeouts': HarTimeouts,
        'timings': HarTimings,
    }

    _ordered = [
        'startedDateTime',
        'time',
        'request',
        'response',
        'cache',
        'timings',
        '_timeouts',
        'connection',
        'pageref',
        'comment',
        'serverIPAddress',
        '_serverPort',
        '_serverOptions',
        '_clientIPAddress',
        '_clientPort',
        '_clientOptions',
        '_socketOptions',
    ]

    def __init__(self, obj=None):
        har = obj or None

        if isinstance(obj, Mapping):
            har = obj
        elif isinstance(obj, HarObject):
            har = obj.to_json()
        elif isinstance(obj, six.string_types):
            raise ValueError('HarEntry got %s' % repr(obj))
        elif isinstance(obj, (list, tuple)):
            raise ValueError('HarEntry got %s' % repr(obj))
        else:
            har = self.decode(obj)

        if isinstance(har, Mapping):
            if 'startedDateTime' not in har:
                har['startedDateTime'] = None
            if not har['startedDateTime']:
                har['startedDateTime'] = self.get_started_datetime(obj)

        super(HarEntry, self).__init__(har)

    def get_started_datetime(self, obj):
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'

    def to_json(self, with_content=True, dict_class=dict):
        d = super(HarEntry, self).to_json()
        if not with_content:
            try:
                del d['request']['postData']['text']
                del d['request']['postData']['encoding']
            except Exception:
                pass
            try:
                del d['response']['content']['text']
                del d['response']['content']['encoding']
            except Exception:
                pass
        return d


class HarLog(HarObject):

    _required = [
        'version',
        'creator',
        'entries',
    ]

    _optional = {
        'browser': {},
        'pages': [],
        'comment': '',
    }

    _types = {
        'creator': HarCreator,
        'browser': HarBrowser,
        'entries': [HarEntry],
        'pages': [HarPage],
    }

    def __init__(self, obj=None):
        import harlib
        har = dict()
        har['version'] = '1.2'
        har['creator'] = dict()
        har['creator']['name'] = harlib.__title__
        har['creator']['version'] = harlib.__version__
        har['entries'] = self.parse_entries(obj)

        super(HarObject, self).__init__(har)

    def parse_entries(self, obj):
        har = None

        if isinstance(obj, (dict, Mapping)):
            har = obj['entries']

        elif isinstance(obj, (list, Sequence)):
            har = []
            entries = obj
            for entry in entries:
                har.extend(self.parse_entries(entry))

        elif isinstance(obj, HarEntry):
            har = [obj.to_json()]

        elif isinstance(obj, HarLog):
            har = [entry.to_json() for entry in obj.entries]

        elif obj is None:
            return []

        else:
            har = self.decode(obj)

        return har


class HarFile(HarObject):
    _required = ['log']
    _types = {'log': HarLog}

    def __init__(self, obj=None):
        har = None

        if isinstance(obj, (dict, Mapping)):
            har = obj

        elif isinstance(obj, (list, Sequence)):
            har = dict()
            har['log'] = obj

        else:
            raise ValueError('HarFile got %s' % repr(obj))

        super(HarObject, self).__init__(har)
