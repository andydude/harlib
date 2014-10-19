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

import collections
import json
import requests
import six

from six.moves import http_client as httplib

try:
    import urllib3
except ImportError:
    from requests.packages import urllib3

from .metamodel import HarObject

from .options import (
    HarClientOptions, 
    HarServerOptions,
    HarSocketOption,
)

from .request import (
    HarRequest, 
    HarRequestBody, 
)

from .response import (
    HarResponse,
    HarResponseBody,
)

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
        if not obj: obj = None
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
        har = obj

        started = self.get_started_datetime(obj)
        timings = self.get_timings(obj)
        connref = self.get_connection(obj)

        if isinstance(obj, (bytes, str, unicode, list, tuple)):
            raise ValueError('HarEntry got %s' % repr(obj))

        if isinstance(obj, HarObject):
            har = obj.toJSON()
            har['_socketOptions'] = map(lambda x: x.toJSON(), obj._socketOptions)

        if isinstance(obj, urllib.addinfourl):
            har = dict()
            har['startedDateTime'] = started
            har['time'] = -1
            har['request'] = obj
            har['response'] = obj
            har['cache'] = {}
            har['timings'] = timings
            har['connection'] = connref

        if isinstance(obj, httplib.HTTPResponse):
            har = dict()
            har['startedDateTime'] = started
            har['time'] = -1
            har['request'] = obj
            har['response'] = obj
            har['cache'] = {}
            har['timings'] = timings
            har['connection'] = connref
            har['_clientOptions'] = dict()
            har['_clientOptions']['autoClose'] = obj.will_close
            har['_clientOptions']['chunked'] = obj.chunked
            har['_clientOptions']['failOnError'] = obj.strict
            har['_clientOptions']['verbosity'] = obj.debuglevel

        if isinstance(obj, urllib2.Request):
            har = dict()
            har['startedDateTime'] = started
            har['time'] = -1
            har['request'] = obj
            har['response'] = obj
            har['cache'] = {}
            har['timings'] = timings
            har['connection'] = connref
            har['_clientOptions'] = dict()
            har['_clientOptions']['host'] = obj.origin_req_host
            har['_clientOptions']['unverifiable'] = obj.unverifiable

        if isinstance(obj, urllib3.HTTPResponse):
            #har = dict(
            #    startedDateTime = started,
            #    time = -1,
            #    request = obj,
            #    response = obj,
            #    cache = {},
            #    timings = timings,
            #    connection = self.get_connection(obj),
            #)
            #har['_clientOptions'] = dict(
            #    decodeContent = obj.decode_content,
            #)
            pass

        if isinstance(obj, requests.Response):
            har = dict()
            har['startedDateTime'] = started
            har['time'] = obj.elapsed.total_seconds()*1000.0
            har['request'] = obj.request
            har['response'] = obj
            har['cache'] = {}
            har['timings'] = timings
            har['connection'] = self.get_connection(obj)
            har['_clientOptions'] = dict()
            har['_clientOptions']['charset'] = obj.encoding
            har['_clientOptions']['decodeContent'] = obj.raw.decode_content
            #har['_clientOptions']['contentRead'] = obj.raw._fp_bytes_read

        super(HarEntry, self).__init__(har)

    def get_connection(self, obj):
        from datetime import datetime
        now = datetime.now()
        return now.strftime('%s')

    def get_started_datetime(self, obj):
        from datetime import datetime
        now = datetime.utcnow()
        if isinstance(obj, requests.Response):
            return (now - obj.elapsed).isoformat() + 'Z'
        return now.isoformat() + 'Z'

    def get_timings(self, obj):
        har = obj
        if isinstance(obj, httplib.HTTPResponse):
            har = dict(
                connect = -1,
                dns = -1,
                receive = -1,
                send = -1,
                ssl = -1,
                wait = -1,
                _total = -1
            )
        if isinstance(obj, requests.Response):
            total = obj.elapsed.total_seconds()*1000.0
            har = dict(
                connect = -1,
                dns = -1,
                receive = -1,
                send = -1,
                ssl = -1,
                wait = total,
                _total = total
            )
        return har

    def to_httplib(self):
        resp = self.response.to_httplib()
        resp._method = self.request.method
        resp.strict = self._clientOptions.failOnError
        resp.debuglevel = self._clientOptions.verbosity
        resp.chunked = 1 if self._clientOptions.chunked else 0
        resp.will_close = 1 if self._clientOptions.autoClose else 0

        return resp

    # urllib2 lacks a decent Response class
    def to_urllib2(self):
        req = self.request.to_urllib2()
        req.origin_req_host = self._clientOptions.host
        req.unverifiable = self._clientOptions.unverifiable

        return req

    def to_urllib3(self):
        resp = self.response.to_urllib3()
        resp.strict = self._clientOptions.failOnError
        resp.decode_content = self._clientOptions.decodeContent
        resp.original_response = self.to_httplib()
        #resp._fp_bytes_read = self._clientOptions.contentRead
        #resp.connection = None
        #resp.pool = None

        return resp

    def to_requests(self):
        from datetime import timedelta
        resp = self.response.to_requests()
        resp.elapsed = timedelta(0, float(self.time)/1000.0)
        resp.encoding = self._clientOptions.charset
        resp.raw = self.to_urllib3()

        return resp

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

        if isinstance(obj, (dict, collections.Mapping)):
            har = obj['entries']

        elif isinstance(obj, (list, collections.Sequence)):
            har = []
            entries = obj
            for entry in entries:
                har.extend(self.parse_entries(entry))

        elif isinstance(obj, requests.Response):
            har = []
            resp = obj
            if hasattr(resp, 'history') and resp.history and len(resp.history) > 0:
                for tome in resp.history:
                    har.append(tome)
            har.append(resp)

        elif isinstance(obj, HarEntry):
            har = [obj.toJSON()]

        elif isinstance(obj, HarLog):
            har = [entry.toJSON() for entry in obj.entries]

        elif not obj:
            return []

        else:
            raise ValueError('HarLog got %s' % repr(obj))

        return har

class HarFile(HarObject):
    _required = ['log']
    _types = {'log': HarLog}

    def __init__(self, obj=None):
        har = None

        if isinstance(obj, (dict, collections.Mapping)):
            har = obj

        elif isinstance(obj, (list, collections.Sequence)):
            har = dict()
            har['log'] = obj

        else:
            raise ValueError('HarFile got %s' % repr(obj))

        super(HarObject, self).__init__(har)
