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


from .metamodel import HarObject

from .messages import (
    HarNameValuePair,
    HarCookie,
    HarHeader,
    HarQueryStringParam,
    HarPostDataParam,
    HarMessageBody,
    HarMessage,
)

class HarRequestBody(HarMessageBody): # <postData>

    _required = [
        'mimeType',
    ]

    _optional = {
        'text': '', # HAR-1.2 required
        'comment': '',
        '_encoding': '',
        '_compression': -1,
        'params': [],
        'mimeType': None,
    }

    _types = {
        'params': [HarPostDataParam],
    }

    def __init__(self, obj=None):
        if not obj:
            obj = None
        har = obj

        if isinstance(obj, HarObject):
            har = obj.toJSON()

        super(HarRequestBody, self).__init__(har)

class HarRequest(HarMessage):

    _required = [
        'method',
        'url',
        'cookies', # List of HarCookie
        'headers', # List of HarHeader
        'queryString', # List of QueryParams, # HAR-1.2 required
    ]

    _optional = {
        'httpVersion': '', 	# HAR-1.2 required
        'postData': {},
        'comment': '',
        '_requestLine': '',
        '_requestLineSize': -1,
        'headersSize': -1,
        'bodySize': -1,
        '_endpointIdentifier': '',
        '_originalURL': '',
    }

    _types = {
        'cookies': [HarCookie],
        'headers': [HarHeader],
        'postData': HarRequestBody,
        'queryString': [HarQueryStringParam],
        'headersSize': int,
        'bodySize': int,
        '_requestLineSize': int,
    }

    _ordered = [
        'method',
        'url',
        'httpVersion',
        'cookies',
        'headers',
        'queryString',
        'postData',
        'headersSize',
        'bodySize',
        'comment',
        '_requestLine',
        '_requestLineSize',
    ]

    def __init__(self, obj=None):
        har = obj

        if isinstance(obj, HarObject):
            har = obj.toJSON()

        if isinstance(obj, httplib.HTTPResponse):
            har = dict()
            har['method'] = obj._method
            har['url'] = 'UNKNOWN'
            har['httpVersion'] = self.get_version(obj)
            har['headers'] = []
            har['cookies'] = []
            har['postData'] = self.get_body(obj)
            har['queryString'] = []
            har['headersSize'] = -1
            har['bodySize'] = -1

        if isinstance(obj, urllib2.Request):
            har = dict()
            har['method'] = obj.get_method()
            har['url'] = obj.get_full_url()
            har['httpVersion'] = self.get_version(obj)
            har['headers'] = self.get_headers(obj.headers.items())
            har['cookies'] = self.get_cookies(obj)
            har['postData'] = self.get_body(obj)
            har['queryString'] = []
            har['headersSize'] = -1
            har['bodySize'] = -1

        if isinstance(obj, (requests.PreparedRequest, requests.Request)):
            har = dict()
            har['method'] = obj.method
            har['url'] = obj.url
            har['httpVersion'] = self.get_version(obj)
            har['headers'] = self.get_headers(obj)
            har['cookies'] = self.get_cookies(obj)
            har['postData'] = self.get_body(obj)
            har['queryString'] = self.get_query(obj)
            har['headersSize'] = -1
            har['bodySize'] = -1

            if hasattr(obj, 'origin'):
                har['_originURL'] = obj.origin
            if hasattr(obj, 'epid'):
                har['_endpointIdentifier'] = obj.epid

        super(HarRequest, self).__init__(har)

    @property
    def size(self):
        return self.headersSize + self.bodySize

    def get_param(self, name, default=None):
        for param in self.queryString:
            if param.name == name:
                return param.value
        return default

    def post_param(self, name, default=None):
        for param in self.postData.params:
            if param.name == name:
                return param
        return default

    def get_query(self, obj):
        if isinstance(obj, requests.Request):
            d = map(HarNameValuePair.pair2dict, obj.params.items())
        else:
            query = '?'
            if  '?' in obj.url:
                query += obj.url.split('?', 1)[1]
            d = HarQueryStringParam.decode_query(query)
        return d

    def get_body(self, obj):
        har = dict()

        if isinstance(obj, HarObject):
            har = obj.toJSON()

        if isinstance(obj, urllib2.Request):
            if obj.has_data():
                body_text = obj.data or ''
                har['mimeType'] = obj.headers.get('Content-Type')
                har['text'] = body_text
                try:
                    query = '?' + har['text']
                    har['params'] = HarQueryStringParam.decode_query(query)
                except:
                    har['params'] = []

        if isinstance(obj, httplib.HTTPResponse):
            har['mimeType'] = 'UNKNOWN'
            har['text'] = ''
            har['_size'] = 0
            har['params'] = []

        if isinstance(obj, requests.PreparedRequest):
            body_text = obj.body or ''

            har['mimeType'] = obj.headers.get('Content-Type')
            har['text'] = body_text or ''
            har['_size'] = len(har['text'])

            try:
                query = '?' + har['text']
                har['params'] = HarQueryStringParam.decode_query(query)
            except:
                har['params'] = []


        if isinstance(obj, requests.Request):
            body_params = {}
            body_params.update(obj.data)
            body_params.update(obj.files)

            har['mimeType'] = 'UNKNOWN'
            try:
                har['text'] = HarQueryStringParam.encode_query(body_params)
            except:
                har['text'] = ''
            har['_size'] = len(har['text'])

            har['params'] = body_params.items()

            if obj.headers:
                if obj.headers.get('Content-Type'):
                    har['mimeType'] = obj.headers.get('Content-Type')

        use_base64 = False
        try:
            har['text'].decode('ascii')
        except UnicodeDecodeError:
            use_base64 = True


        if use_base64:
            har['encoding'] = 'base64'
            har['text'] = base64.b64encode(har['text'])
        return har

    def to_requests(self):
        req = requests.Request(
            method = self.method, url = self.url,
            headers = dict(map(lambda x: x.to_requests(), self.headers or [])),
            cookies = dict(map(lambda x: x.to_requests(), self.cookies or [])),
        )
        if self.postData:
            req.data = self.postData.text
        #req.hooks -- impossible
        #req.auth -- impossible
        #req.params, req.data, req.files = self.body_params()
        return req

    def to_urllib2(self):
        req = urllib2.Request(self.url, self.postData.text, self.get_header_dict())
        return req

