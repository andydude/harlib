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
import os
import six
from six.moves import (http_client, urllib)
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
        '_size': -1,
        'text': '', # HAR-1.2 required
        'comment': '',
        '_compression': -1,
        '_encoding': '',
        'params': [],
    }

    _types = {
        '_size': int,
        '_compression': int,
        'params': [HarPostDataParam],
    }

    def __init__(self, obj=None):
        har = obj or None

        if isinstance(obj, collections.Mapping):
            har = obj
        elif isinstance(obj, HarObject):
            har = obj.to_json()
        else:
            har = self.decode(obj)

        super(HarRequestBody, self).__init__(har)

class HarRequest(HarMessage):

    _required = [
        'method',
        'url',
        'cookies',
        'headers',
        'queryString', 		# HAR-1.2 required
    ]

    _optional = {
        'httpVersion': '', 	# HAR-1.2 required
        'headersSize': -1,
        'bodySize': -1,
        'postData': {'mimeType': 'UNKNOWN'},
        'comment': '',
        '_requestLine': '',
        '_requestLineSize': -1,
        '_endpointID': '',
        '_originURL': '',
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
        har = obj or None

        if isinstance(obj, collections.Mapping):
            har = obj
        elif isinstance(obj, HarObject):
            har = obj.to_json()
        else:
            har = self.decode(obj)

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
    
    #def get_query(self, obj):
    #    if isinstance(obj, requests.Request):
    #        d = map(HarNameValuePair.pair2dict, obj.params.items())
    #    else:
    #        query = '?'
    #        if  '?' in obj.url:
    #            query += obj.url.split('?', 1)[1]
    #        d = HarQueryStringParam.decode_query(query)
    #    return d

    #def get_body(self, obj):
    #    har = dict()
    #
    #    if isinstance(obj, HarObject):
    #        har = obj.to_json()
    #
    #    if isinstance(obj, django.http.request.HttpRequest):
    #        har['mimeType'] = 'UNKNOWN'
    #        har['text'] = obj.body
    #        har['_size'] = len(har['text'])
    #        try:
    #            query = '?' + har['text']
    #            har['params'] = HarQueryStringParam.decode_query(query)
    #        except:
    #            har['params'] = []
    #
    #    if isinstance(obj, http_client.HTTPResponse):
    #        har['mimeType'] = 'UNKNOWN'
    #        har['text'] = ''
    #        har['_size'] = 0
    #        har['params'] = []
    #
    #    if isinstance(obj, requests.PreparedRequest):
    #        body_text = obj.body or ''
    #
    #        har['mimeType'] = obj.headers.get('Content-Type')
    #        har['text'] = body_text or ''
    #        har['_size'] = len(har['text'])
    #
    #        try:
    #            query = '?' + har['text']
    #            har['params'] = HarQueryStringParam.decode_query(query)
    #        except:
    #            har['params'] = []
    #
    #
    #    if isinstance(obj, requests.Request):
    #        body_params = {}
    #        body_params.update(obj.data)
    #        body_params.update(obj.files)
    #
    #        har['mimeType'] = 'UNKNOWN'
    #        try:
    #            har['text'] = HarQueryStringParam.encode_query(body_params)
    #        except:
    #            har['text'] = ''
    #        har['_size'] = len(har['text'])
    #
    #        har['params'] = body_params.items()
    #
    #        if obj.headers:
    #            if obj.headers.get('Content-Type'):
    #                har['mimeType'] = obj.headers.get('Content-Type')
    #
    #    use_base64 = False
    #    try:
    #        har['text'].decode('ascii')
    #    except UnicodeDecodeError:
    #        use_base64 = True
    #
    #
    #    if use_base64:
    #        har['encoding'] = 'base64'
    #        har['text'] = base64.b64encode(har['text'])
    #    return har

    #def to_requests(self):
    #
    #def to_urllib2(self):
    #    return self.encode(urllib.request.Request)

