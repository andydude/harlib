#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# harlib
# Copyright (c) 2014-2017, Andrew Robbins, All rights reserved.
#
# This library ("it") is free software; it is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY; you can redistribute it and/or
# modify it under the terms of LGPLv3 <https://www.gnu.org/licenses/lgpl.html>.
from __future__ import absolute_import
from datetime import datetime
from six.moves import http_client
from six.moves import urllib
import six
from harlib import utils


class HttplibCodec(object):

    dict_class = dict
    response_class = http_client.HTTPResponse
    modules = [
        'cookielib',
        'httplib',
        'http.client',
        'http.cookiejar'
    ]

    def __init__(self):
        pass

    # Encoding

    def encode(self, har, raw_class):
        assert raw_class.__module__ in self.modules
        method_name = 'encode_%s_to_%s' % (
            har.__class__.__name__, raw_class.__name__)
        return getattr(self, method_name)(har)

    def encode_HarEntry_to_HTTPResponse(self, har):
        resp = self.encode_HarResponse_to_HTTPResponse(har.response)
        resp._method = har.request.method
        resp.strict = har._clientOptions.failOnError
        resp.debuglevel = har._clientOptions.verbosity
        resp.chunked = 1 if har._clientOptions.chunked else 0
        resp.will_close = 1 if har._clientOptions.autoClose else 0

        return resp

    def encode_HarResponse_to_HTTPResponse(self, har):
        # headers = dict(map(utils.pair_from_obj, har.headers))
        if har is None:
            return None

        class DummySocket(object):
            bufsize = 1024

            def close(self):
                pass

            def sendall(self, data):
                pass

            def readline(self, bufsize=1024):
                return ''
            
            def read(self, bufsize=1024):
                return ''
            
            def makefile(self, mode, bufsize=1024):
                self.bufsize = bufsize
                return self

        resp = http_client.HTTPResponse(DummySocket())
        resp.status = har.status
        resp.reason = har.statusText
        resp.version = utils.parse_http_version(har.httpVersion)
        resp.length = 0

        resp.msg = http_client.HTTPMessage(resp.fp)
        resp.msg.startofheaders = har._statusLineSize
        resp.msg.startofbody = har.headersSize

        return resp

    def encode_HarResponseBody_to_HTTPResponse(self, har):
        pass

    # Decoding

    def decode(self, raw, har_class):
        assert raw.__class__.__module__ in self.modules
        method_name = 'decode_%s_from_%s' % (
            har_class.__name__, raw.__class__.__name__)
        return getattr(self, method_name)(raw)

    def decode_HarEntry_from_HTTPResponse(self, raw):
        har = self.dict_class()
        har['startedDateTime'] = None
        har['time'] = 0
        har['request'] = raw
        har['response'] = raw
        har['cache'] = {}
        har['timings'] = None
        har['connection'] = ''
        har['_clientOptions'] = dict()
        har['_clientOptions']['autoClose'] = raw.will_close
        har['_clientOptions']['chunked'] = raw.chunked
        # har['_clientOptions']['failOnError'] = raw.strict
        har['_clientOptions']['verbosity'] = raw.debuglevel
        return har

    def decode_HarRequest_from_HTTPResponse(self, raw):
        har = self.dict_class()
        har['method'] = raw._method
        har['url'] = 'UNKNOWN'
        har['httpVersion'] = utils.render_http_version(raw.version)
        har['headers'] = []
        har['cookies'] = []
        har['queryString'] = []
        har['postData'] = {'mimeType': 'UNKNOWN'}
        return har

    def decode_HarResponse_from_HTTPResponse(self, raw):
        har = self.dict_class()
        har['status'] = raw.status
        har['statusText'] = raw.reason
        har['httpVersion'] = utils.render_http_version(raw.version)
        har['headers'] = self.decode_HarHeaders_from_HTTPResponse(raw)
        har['cookies'] = self.decode_HarCookies_from_HTTPResponse(raw)
        har['content'] = raw
        har['redirectURL'] = ''
        har['headersSize'] = -1
        har['bodySize'] = -1

        if six.PY3:
            if raw.headers:
                # har['headersSize'] = int(raw.headers.startofbody or 0)
                har['bodySize'] = int(raw.headers.get('content-length'))
                # har['bodySize'] = har['bodySize'] - har['headersSize']
                # print(vars(raw.headers))
        else:
            if raw.msg:
                # har['_statusLineSize'] = int(obj.msg.startofheaders or 0)
                har['headersSize'] = int(raw.msg.startofbody or 0)
                har['bodySize'] = int(raw.msg.getheader('content-length')) - \
                    har['headersSize']

        return har

    def decode_HarCookies_from_HTTPResponse(self, raw):
        pass

    def decode_HarHeaders_from_HTTPResponse(self, raw):
        if six.PY3:
            return self.decode_HarHeaders_from_HTTPMessage(raw.headers)
        else:
            return self.decode_HarHeaders_from_HTTPMessage(raw.msg)

    def decode_HarHeaders_from_HTTPMessage(self, raw):
        if six.PY3:
            headers = raw._headers
        else:
            headers = [x.strip().split(': ', 1) for x in raw.headers]
        return headers

    def decode_HarResponseBody_from_HTTPResponse(self, raw):
        har = self.dict_class()
        if six.PY3:
            har['mimeType'] = raw.headers.get_content_type()
        else:
            har['mimeType'] = raw.msg.getheader('content-type')
        har['text'] = raw.read()
        har['size'] = len(har['text'])
        har['compression'] = -1
        return har

    def decore_HarCookie_from_Cookie(self, raw):
        har = self.dict_class()
        har['name'] = raw.name
        har['value'] = raw.value
        har['path'] = raw.path
        har['domain'] = raw.domain
        har['expires'] = raw.expires
        har['httpOnly'] = False
        har['secure'] = raw.secure
        return har


class Urllib2Codec(object):

    dict_class = dict
    request_class = urllib.request.Request
    response_class = urllib.response.addinfourl
    modules = [
        'urllib2',
        'urllib',
        'urllib.request']
    httplib_codec = HttplibCodec()
    http_version = 'HTTP/1.1'

    def __init__(self):
        pass

    # Encoding

    def encode(self, har, raw_class):
        assert raw_class.__module__ in self.modules
        method_name = 'encode_%s_to_%s' % (
            har.__class__.__name__, raw_class.__name__)
        return getattr(self, method_name)(har)

    def encode_HarEntry_to_addinfourl(self, har):
        raise NotImplementedError

    def encode_HarEntry_to_Request(self, har):
        req = self.encode_HarRequest_to_Request(har.request)
        req.origin_req_host = har._clientOptions.host
        req.unverifiable = har._clientOptions.unverifiable
        return req

    def encode_HarRequest_to_Request(self, har):
        req = urllib.request.Request(
            har.url,
            har.postData.text,
            har.get_header_dict())
        return req

    def encode_HarResponse_to_HTTPResponse(self, har):
        # TODO
        resp = None
        return resp

    # Decoding

    def decode(self, raw, har_class):
        assert raw.__class__.__module__ in self.modules
        method_name = 'decode_%s_from_%s' % (
            har_class.__name__, raw.__class__.__name__)
        return getattr(self, method_name)(raw)

    def decode_HarEntry_from_addinfourl(self, raw):
        started = datetime.now().isoformat()
        timings = {'send': -1, 'wait': -1, 'receive': -1}
        har = self.dict_class()
        har['startedDateTime'] = started
        har['time'] = 0
        har['request'] = raw
        har['response'] = raw
        har['cache'] = {}
        har['timings'] = timings
        har['connection'] = ''
        return har

    def decode_HarEntry_from_Request(self, raw):
        started = datetime.now().isoformat()
        timings = {'send': -1, 'wait': -1, 'receive': -1}
        har = self.dict_class()
        har['startedDateTime'] = started
        har['time'] = 0
        har['request'] = raw
        har['response'] = raw
        har['cache'] = {}
        har['timings'] = timings
        har['connection'] = ''
        har['_clientOptions'] = self.dict_class()
        har['_clientOptions']['host'] = raw.origin_req_host
        har['_clientOptions']['unverifiable'] = raw.unverifiable
        return har

    def decode_HarRequest_from_Request(self, raw):
        har = self.dict_class()
        har['method'] = raw.get_method()
        har['url'] = raw.get_full_url()
        har['httpVersion'] = self.http_version
        har['headers'] = self.decode_HarHeaders_from_Request(raw)
        har['cookies'] = []
        har['postData'] = raw
        har['queryString'] = []
        har['headersSize'] = -1
        har['bodySize'] = -1
        return har

    def decode_HarResponse_from_addinfourl(self, raw):
        har = self.dict_class()
        har['status'] = raw.code
        har['statusText'] = http_client.responses.get(raw.code, 'UNKNOWN')
        har['httpVersion'] = self.http_version
        har['headers'] = self.httplib_codec. \
            decode_HarHeaders_from_HTTPMessage(raw.headers)
        har['cookies'] = []
        har['content'] = raw
        har['redirectURL'] = raw.url
        har['headersSize'] = -1
        har['bodySize'] = -1
        return har

    def decode_HarResponseBody_from_addinfourl(self, raw):
        har = self.dict_class()
        har['mimeType'] = raw.headers.getheader('Content-Type')
        har['text'] = raw.read()
        har['size'] = len(har['text'])
        har['compression'] = -1
        return har

    def decode_HarRequestBody_from_Request(self, raw):
        if six.PY3:
            if not raw.data:
                return None
        else:
            if not raw.has_data():
                return None

        har = self.dict_class()
        har['mimeType'] = raw.headers.get('Content-Type')
        har['text'] = raw.data or ''
        har['_size'] = len(har['text'])
        try:
            query = '?' + har['text']
            har['params'] = utils.decode_query(query)
        except:
            raise
        return har

    def decode_HarHeaders_from_Request(self, raw):
        return list(raw.headers.items())
