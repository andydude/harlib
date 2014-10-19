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

from .messages import (
    HarCookie,
    HarHeader,
    HarMessageBody,
    HarMessage,
)

class HarResponseBody(HarMessageBody): # <content>

    _required = [
        'mimeType',
    ]

    _optional = {
        'size': -1,
        'text': '', 		# HAR-1.2 optional string
        'encoding': '', 	# HAR-1.2 optional string
        'compression': -1, 	# HAR-1.2 optional number
        'comment': '',
        'mimeType': None,
    }

    _types = {
        'size': int,
        'compression': int,
    }

    def __init__(self, obj=None):
        if not obj:
            obj = None
        har = obj
        super(HarResponseBody, self).__init__(har)

class HarResponse(HarMessage):

    _required = [
        'status',
        'statusText',
        'cookies',
        'headers',
        'content',
        'redirectURL',
    ]

    _optional = {
        'headersSize': -1,
        'bodySize': -1,
        'httpVersion': '', 	# HAR-1.2 required
        'comment': '',
        '_statusLineSize': -1,
        '_statusLine': '',
        '_checkResult': None,
        '_parseResult': None,
    }

    _types = {
        'status': int,
        'bodySize': int,
        'headersSize': int,
        'cookies': [HarCookie],
        'headers': [HarHeader],
        'content': HarResponseBody,
        '_statusLineSize': int,
    }

    _ordered = [
        'status',
        'statusText',
        'httpVersion',
        'cookies',
        'headers',
        'content',
        'redirectURL',
        'headersSize',
        'bodySize',
        'comment',
        '_statusLine',
        '_statusLineSize',
        '_checkResult',
        '_parseResult',
    ]

    def __init__(self, obj=None):
        har = obj

        if isinstance(obj, HarObject):
            har = obj.toJSON()

        if isinstance(obj, urllib.addinfourl):
            har = dict()
            har['status'] = obj.code
            har['statusText'] = httplib.responses.get(obj.code, 'UNKNOWN')
            har['httpVersion'] = self.get_version(obj)
            har['headers'] = self.get_headers(obj.headers)
            har['cookies'] = self.get_cookies(obj)
            har['content'] = self.get_body(obj)
            har['redirectURL'] = ''
            har['headersSize'] = -1
            har['bodySize'] = -1

        if isinstance(obj, httplib.HTTPResponse):
            har = dict()
            har['status'] = obj.status
            har['statusText'] = obj.reason
            har['httpVersion'] = self.get_version(obj)
            har['headers'] = self.get_headers(obj)
            har['cookies'] = self.get_cookies(obj)
            har['content'] = self.get_body(obj)
            har['redirectURL'] = ''
            har['headersSize'] = -1
            har['bodySize'] = -1

            if obj.msg:
                #har['_statusLineSize'] = int(obj.msg.startofheaders or 0)
                har['headersSize'] = int(obj.msg.startofbody or 0)
                har['bodySize'] = int(obj.msg.getheader('content-length')) - har['headersSize']

        if isinstance(obj, requests.Response):
            har = dict()
            har['status'] = obj.status_code
            har['statusText'] = obj.reason
            har['httpVersion'] = self.get_version(obj)
            har['headers'] = self.get_headers(obj)
            har['cookies'] = self.get_cookies(obj)
            har['content'] = self.get_body(obj)
            har['redirectURL'] = obj.url
            har['headersSize'] = -1
            har['bodySize'] = -1

            if hasattr(obj, 'check_result'):
                har['_checkResult'] = obj.check_result
            if hasattr(obj, 'parse_result'):
                har['_parseResult'] = obj.parse_result

        super(HarResponse, self).__init__(har)

    @property
    def size(self):
        return self.headersSize + self.bodySize

    def get_body(self, obj):
        har = dict()
        text = ''

        if isinstance(obj, HarObject):
            har = obj.toJSON()

        if isinstance(obj, urllib.addinfourl):
            har['mimeType'] = obj.headers.getheader('content-type')
            text = obj.read()

        if isinstance(obj, httplib.HTTPResponse):
            har['mimeType'] = obj.msg.getheader('content-type')
            text = obj.read()

        if isinstance(obj, requests.Response):
            har['mimeType'] = obj.headers.get('content-type')
            try:
                text = obj.text
            except:
                text = ''

        har['text'] = text
        har['size'] = len(text)
        har['compression'] = -1

        use_base64 = False
        if use_base64:
            har['encoding'] = 'base64'
            #har['text'] = re-encode

        return har

    def to_httplib(self):

        class DummySocket(object):
            bufsize = 1024
            def close(self): pass
            def sendall(self, data): pass
            def readline(self, bufsize=1024): return ''
            def read(self, bufsize=1024): return ''
            def makefile(self, mode, bufsize=1024):
                self.bufsize = bufsize
                return self

        resp = httplib.HTTPResponse(DummySocket())
        resp.status = self.status
        resp.reason = self.statusText
        resp.version = int(float(self.httpVersion.split('/')[1])*10.0)
        resp.length = 0

        #resp.msg = httplib.HTTPMessage(resp.fp)
        #resp.msg.startofheaders = self._statusLineSize
        #resp.msg.startofbody = self.headersSize

        return resp

    def to_urllib(self):
        resp = urllib.addinfourl
        # TODO
        # maybe not, addinfourl sucks...

    def to_urllib3(self):
        ResponseCls = urllib3.HTTPResponse
        headers = dict(map(lambda x: x.to_requests(), self.headers))

        resp = ResponseCls(
            body = None,
            headers = headers,
            status = self.status,
            version = self.to_version(self.httpVersion),
            reason = self.statusText,
            preload_content = False,
        )

        return resp

    def to_requests(self):
        ResponseCls = requests.Response
        HeadersCls = requests.structures.CaseInsensitiveDict
        CookiesCls = requests.cookies.RequestsCookieJar
        headers = map(lambda x: x.to_requests(), self.headers)
        cookies = map(lambda x: x.to_requests(), self.cookies)

        resp = ResponseCls()
        resp._content = self.content.text
        resp._content_consumed = True
        resp.status_code = self.status
        resp.reason = self.statusText
        resp.cookies = CookiesCls(collections.OrderedDict(cookies))
        resp.headers = HeadersCls(collections.OrderedDict(headers))
        resp.raw = self.to_urllib3()
        resp.url = self.redirectURL
        resp.history = []
        #resp.elapsed = 0 # entry.time
        #resp.encoding = None # entry._clientOptions.charset

        return resp
