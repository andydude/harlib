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
from collections import Mapping
import json
import six
from six.moves import http_client as httplib
from six.moves import http_cookiejar
from .metamodel import HarObject

class HarNameValuePair(HarObject):

    _required = [
        'name',
        'value',
    ]

    _optional = {
        'comment': '',
    }

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
            har = obj.to_json()
        elif isinstance(obj, (tuple, list)):
            har = self.decode(tuple(obj))

        super(HarCookie, self).__init__(har)

    def to_requests(self):
        return self.encode(tuple)

class HarHeader(HarNameValuePair):

    _required = HarNameValuePair._required

    use_titlecase = True

    def __init__(self, obj=None):
        har = obj

        if isinstance(obj, HarHeader):
            har = obj.to_json()
        elif isinstance(obj, (tuple, list)):
            har = self.decode(tuple(obj))

        if self.use_titlecase:
            har['name'] = har['name'].title()

        super(HarHeader, self).__init__(har)

    def to_requests(self):
        return self.encode(tuple)

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

    #def to_version(self, v):
    #    v_num = float(v.split('/', 1)[1])
    #    return int(v_num*10.0)
    #    
    #def get_version(self, obj):
    #    v = 'HTTP/1.1'
    #    if isinstance(obj, (httplib.HTTPResponse, urllib3.response.HTTPResponse)):
    #        v_str = str(float(obj.version)/10.0)
    #        v = 'HTTP/%s' % v_str
    #    if isinstance(obj, requests.Response):
    #        v_str = str(float(obj.raw.version)/10.0)
    #        v = 'HTTP/%s' % v_str
    #    return v

    #def get_cookies(self, obj):
    #    cookies = []
    #    cookiejar = None
    #    if isinstance(obj, httplib.HTTPResponse):
    #        obj = obj.msg
    #    if isinstance(obj, httplib.HTTPMessage):
    #        cookies = []
    #    if isinstance(obj, requests.PreparedRequest):
    #        cookies = obj._cookies
    #    if isinstance(obj, requests.Request):
    #        cookies = obj.cookies
    #    if isinstance(obj, requests.Response):
    #        cookies = obj.cookies
    #    if isinstance(obj, Mapping):
    #        cookies = obj
    #    if isinstance(cookies, Mapping):
    #        cookies = cookies.items()
    #    #if isinstance(cookies, six.string_types):
    #    #    cookies = map(lambda x: x.split('=', 1), cookies.split(';'))
    #    return cookies
    #
    #def get_headers(self, obj):
    #    '''
    #    Takes any object and returns the associated list of header pairs.
    #    '''
    #    headers = []
    #    if isinstance(obj, django.http.response.HttpResponse):
    #        headers = obj._headers.items()
    #    if isinstance(obj, httplib.HTTPResponse):
    #        obj = obj.msg
    #    if isinstance(obj, httplib.HTTPMessage):
    #        headers = map(lambda x: x.strip().split(': ', 1), obj.headers)
    #
    #    if isinstance(obj, requests.Request):
    #        headers = obj.headers.items()
    #    if isinstance(obj, requests.PreparedRequest):
    #        headers = obj.headers.lower_items()
    #    if isinstance(obj, requests.Response):
    #        headers = obj.headers.lower_items()
    #    if isinstance(obj, Mapping):
    #        headers = obj.items()
    #    if isinstance(obj, list):
    #        headers = obj
    #    return headers

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

    _types = {
        '_headers': [HarHeader],
    }

    def __init__(self, obj=None):
        har = obj

        if isinstance(obj, Mapping):
            har = obj
        elif isinstance(obj, HarObject):
            har = obj.to_json()
        else:
            har = self.decode(obj)

        super(HarPostDataParam, self).__init__(har)

class HarQueryStringParam(HarNameValuePair):
    pass
