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
import httplib
import json
import requests
import urllib
import urllib2
import six

from six.moves import http_cookiejar

try:
    import urllib3
except ImportError:
    from requests.packages import urllib3

from .metamodel import HarObject

class HarNameValuePair(HarObject):

    _required = [
        'name',
        'value',
    ]

    _optional = {
        'comment': '',
    }

    @staticmethod
    def from_pair(item):
        if '=' not in item:
            item += '='
            #raise ValueError(repr(item), 'must be of the form A = B')
        if '&' in item:
            raise ValueError(repr(item), 'must split on "&" first')
        name, value = item.split('=')
        return {'name': name, 'value': value}

    @staticmethod
    def pair2dict(pair):
        return {'name': pair[0], 'value': pair[1]}

    @staticmethod
    def dict2pair(data):
        return data['name'], data['value']

    @staticmethod
    def decode_query(o):
        har = []
        if isinstance(o, basestring):
            query = urllib3.util.parse_url(o).query
            if query is None: return []
            pairs = query.split('&')
            pairs = filter(lambda it: it != '', pairs)
            har = map(HarNameValuePair.from_pair, pairs)
        return har

    @staticmethod
    def encode_query(d):
        har = ''
        if isinstance(d, dict):
            d = d.items()
        if isinstance(d, list):
            if isinstance(d[0], dict):
                d = map(lambda p: (p['name'], p['value']), d)
            for name, value in d:
                har += '&' + str(name) + '=' + str(value)
        if har != '':
            return har[1:]
        else:
            return ''

class HarCookie(HarNameValuePair):

    _required = HarNameValuePair._required

    _optional = {
        'path': None,		# standard
        'domain': None,		# standard
        'expires': None,	# standard
        'httpOnly': None,	# standard
        'secure': None,		# standard
        '_discard': None,	# nonstandard cookie attribute
        '_maxAge': None,	# standard cookie attribute, but not part of HAR-1.2
        '_port': None,		# nonstandard cookie attribute
        '_version': None,	# nonstandard cookie attribute
        '_commentURL': None,	# nonstandard cookie attribute
        'comment': '',
    }

    _ordered = [
        'name',
        'value',
        'path',
        'domain',
        'expires',
        'httpOnly',
        'secure',
        '_discard',
        '_maxAge',
        '_port',
        '_version',
        '_commentURL',
        'comment',
    ]

    def __init__(self, obj=None):
        har = obj

        if isinstance(obj, HarCookie):
            har = obj.toJSON()

        if isinstance(obj, tuple):
            har = dict()
            har['name'] = obj[0]
            har['value'] = obj[1]

        if isinstance(obj, http_cookiejar.Cookie):
            har = dict()
            har['name'] = obj.name
            har['value'] = obj.value
            har['path'] = obj.path
            har['domain'] = obj.domain
            har['expires'] = obj.expires
            har['httpOnly'] = False
            har['secure'] = obj.secure

        super(HarCookie, self).__init__(har)

    def to_requests(self):
        return (self.name, self.value)

class HarHeader(HarNameValuePair):

    _required = HarNameValuePair._required

    use_titlecase = True

    def __init__(self, obj=None):
        har = obj

        if isinstance(obj, HarHeader):
            har = obj.toJSON()

        if isinstance(obj, (tuple, list)):
            har = dict()
            har['name'] = obj[0]
            har['value'] = obj[1]

        if self.use_titlecase:
            har['name'] = har['name'].title()

        super(HarHeader, self).__init__(har)

    def to_requests(self):
        return (self.name, self.value)

class HarMessageBody(HarObject):
    pass

class HarMessage(HarObject):

    _required = [
        'cookies', # List of HarCookie
        'headers', # List of HarHeader
    ]

    _optional = {
        'comment': '',
        'httpVersion': '',
        'headersSize': -1,
        'bodySize': -1,
    }

    _types = {
        'cookies': [HarCookie],
        'headers': [HarHeader],
        'headersSize': int,
        'bodySize': int,
    }

    def to_version(self, v):
        v_num = float(v.split('/', 1)[1])
        return int(v_num*10.0)
        
    def get_version(self, obj):
        v = 'HTTP/1.1'
        if isinstance(obj, (httplib.HTTPResponse, urllib3.response.HTTPResponse)):
            v_str = str(float(obj.version)/10.0)
            v = 'HTTP/%s' % v_str
        if isinstance(obj, requests.Response):
            v_str = str(float(obj.raw.version)/10.0)
            v = 'HTTP/%s' % v_str
        return v

    def get_cookies(self, obj):
        cookies = []
        cookiejar = None
        if isinstance(obj, httplib.HTTPResponse):
            obj = obj.msg
        if isinstance(obj, httplib.HTTPMessage):
            cookies = []
        if isinstance(obj, requests.PreparedRequest):
            cookies = obj._cookies
        if isinstance(obj, requests.Request):
            cookies = obj.cookies
        if isinstance(obj, requests.Response):
            cookies = obj.cookies
        if isinstance(cookies, dict):
            cookies = cookies.items()
        return cookies

    def get_headers(self, obj):
        '''
        Takes any object and returns the associated list of header pairs.
        '''
        headers = []
        if isinstance(obj, httplib.HTTPResponse):
            obj = obj.msg
        if isinstance(obj, httplib.HTTPMessage):
            headers = map(lambda x: x.strip().split(': ', 1), obj.headers)
        if isinstance(obj, requests.Request):
            headers = obj.headers.items()
        if isinstance(obj, requests.PreparedRequest):
            headers = obj.headers.lower_items()
        if isinstance(obj, requests.Response):
            headers = obj.headers.lower_items()
        if isinstance(obj, dict):
            headers = obj.items()
        if isinstance(obj, list):
            headers = obj
        return headers

    def get_cookie(self, name, default=None):
        for cookie in self.cookies:
            if name.lower() == cookie.name.lower():
                return cookie
        return default

    def get_header(self, name, default=None):
        for header in self.headers:
            if name.lower() == header.name.lower():
                return header.value
        return default

    def get_header_dict(self, dict_class=dict):
        headers = []
        for header in self.headers:
            headers.append((header.name, header.value))
        return dict_class(headers)

class HarPostDataParam(HarNameValuePair): # <params>

    _required = [
        'name',
    ]

    _optional = {
        'value': None,
        'fileName': None,
        'contentType': None, # 'text/plain; charset=UTF-8'
        'comment': '',
        '_headers': [],
    }

    def __init__(self, obj=None):
        har = obj

        if isinstance(obj, HarObject):
            har = obj.toJSON()

        if isinstance(obj, (tuple, list)):
            har = self.parse_param(obj[1], obj[0])

        super(HarPostDataParam, self).__init__(har)

    @staticmethod
    def parse_param(obj, name=None):
        d = dict()
        if name:
            d['name'] = name
        else:
            d['name'] = obj[0]
            obj = obj[1:]

        if isinstance(obj, urllib3.fields.RequestField):
            d['value'] = obj.data
            d['fileName'] = obj._filename
            d['contentType'] = obj.headers.get('content-type')
            if hasattr(obj, 'headers'):
                if isinstance(obj.headers, dict):
                    d['_headers'] = map(HarHeader, obj.headers.items())
        elif isinstance(obj, tuple):
            if len(obj) == 1:
                d['value'] = obj[0]
            elif len(obj) == 2:
                d['value'] = obj[1]
                d['fileName'] = obj[0]
            elif len(obj) == 3:
                d['value'] = obj[1]
                d['fileName'] = obj[0]
                d['contentType'] = obj[2]
            elif len(obj) == 4:
                d['value'] = obj[1]
                d['fileName'] = obj[0]
                d['contentType'] = obj[2]
                if hasattr(obj[3], 'items'):
                    d['_headers'] = map(HarHeader, obj[3].items())
        else:
            d['value'] = obj

        return d

class HarQueryStringParam(HarNameValuePair):
    pass
