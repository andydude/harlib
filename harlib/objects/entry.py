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
import collections
import json
import six
from six.moves import (http_client, urllib)

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
        har = obj or None

        if isinstance(obj, collections.Mapping):
            har = obj
        elif isinstance(obj, HarObject):
            har = obj.to_json()
        elif isinstance(obj, (bytes, str, unicode, list, tuple)):
            raise ValueError('HarEntry got %s' % repr(obj))
        else:
            har = self.decode(obj)

        if isinstance(har, collections.Mapping):
            if not har.has_key('startedDateTime'):
                har['startedDateTime'] = None
            if not har['startedDateTime']:
                har['startedDateTime'] = self.get_started_datetime(obj)

        super(HarEntry, self).__init__(har)

    def get_started_datetime(self, obj):
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'

    #def get_connection(self, obj):
    #    from datetime import datetime
    #    now = datetime.now()
    #    return now.strftime('%s')
    #
    #def get_timings(self, obj):
    #    har = obj
    #    if isinstance(obj, http_client.HTTPResponse):
    #        har = dict(
    #            connect = -1,
    #            dns = -1,
    #            receive = -1,
    #            send = -1,
    #            ssl = -1,
    #            wait = -1,
    #            _total = -1
    #        )
    #    if isinstance(obj, requests.Response):
    #        total = obj.elapsed.total_seconds()*1000.0
    #        har = dict(
    #            connect = -1,
    #            dns = -1,
    #            receive = -1,
    #            send = -1,
    #            ssl = -1,
    #            wait = total,
    #            _total = total
    #        )
    #    return har

    #def to_httplib(self):

    ## urllib2 lacks a decent Response class
    #def to_urllib2(self):
    #    return self.encode(urllib.request.Request)
    #
    #def to_urllib3(self):
    #    return self.encode(urllib3r.HTTPResponse)
    #
    #def to_requests(self):
    #    return self.encode(requests.Response)

    def to_json(self, with_content=True):
        d = super(HarEntry, self).to_json()
        if not with_content:
            try:
                del d['request']['postData']['text']
                del d['request']['postData']['encoding']
            except: pass
            try:
                del d['response']['content']['text']
                del d['response']['content']['encoding']
            except: pass
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

        if isinstance(obj, (dict, collections.Mapping)):
            har = obj['entries']

        elif isinstance(obj, (list, collections.Sequence)):
            har = []
            entries = obj
            for entry in entries:
                har.extend(self.parse_entries(entry))

        elif isinstance(obj, HarEntry):
            har = [obj.to_json()]

        elif isinstance(obj, HarLog):
            har = [entry.to_json() for entry in obj.entries]

        elif obj == None:
            return []

        else:
            har = self.decode(obj)

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
