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
from __future__ import unicode_literals
import harlib
import json
import six
from six.moves import http_client
from harlib.codecs.httplib import HttplibCodec
from ..compat import OrderedDict
from ..compat import requests
from ..compat import urllib3r

KEEP_SIZE = False
DEFAULT_VERSION = 'HTTP/0'


def separate(iterable):
    first = True
    last = False
    length = len(list(iterable))
    separated = []
    for index, value in enumerate(iterable):
        if index == length - 1:
            last = True
        separated.append((first, last, value))
        first = False
    return separated


def from_pair(x):
    return x[0] + ': ' + x[1]


class Urllib3Codec(object):

    dict_class = dict
    response_class = urllib3r.response.HTTPResponse
    modules = ['urllib3.response',
               'requests.packages.urllib3.response',
               'botocore.vendored.requests.packages.urllib3.response']
    httplib_codec = HttplibCodec()

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
        resp.strict = har._clientOptions.failOnError
        resp.decode_content = har._clientOptions.decodeContent
        resp.original_response = self.httplib_codec.encode(
            har, http_client.HTTPResponse)
        # resp._fp_bytes_read = self._clientOptions.contentRead
        # resp.connection = None
        # resp.pool = None
        return resp

    def encode_HarResponse_to_HTTPResponse(self, har):
        headers = dict(map(harlib.utils.pair_from_obj, har.headers))

        resp = self.response_class(
            body=None,
            headers=headers,
            status=har.status,
            version=harlib.utils.parse_http_version(har.httpVersion),
            reason=har.statusText,
            preload_content=False,
        )

        return resp

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
        har['_clientOptions'] = \
            self.decode_HarClientOptions_from_HTTPResponse(raw)
        return har

    def decode_HarClientOptions_from_HTTPResponse(self, raw):
        har = self.dict_class()
        har['decodeContent'] = raw.decode_content
        return har

    def decode_HarResponse_from_HTTPResponse(self, raw):
        har = self.dict_class()
        har['status'] = raw.status
        har['statusText'] = raw.reason
        try:
            har['httpVersion'] = harlib.utils.render_http_version(raw.version)
        except Exception:
            har['httpVersion'] = DEFAULT_VERSION

        har['headers'] = list(raw.headers.items())
        har['cookies'] = []

        har['content'] = self.decode_HarResponseBody_from_HTTPResponse(raw)
        har['redirectURL'] = ''

        if KEEP_SIZE:
            try:
                headers = '\r\n'.join(map(lambda x: '%s: %s' % x,
                                          har['headers']))
                har['headersSize'] = len(headers + '\r\n\r\n')
                har['bodySize'] = len(har['content']['text'])
            except Exception:
                har['headersSize'] = -1
                har['bodySize'] = -1
        else:
            har['headersSize'] = -1
            har['bodySize'] = -1

        return har

    def decode_HarResponseBody_from_HTTPResponse(self, raw):
        har = self.dict_class()
        har['mimeType'] = raw.headers.get('content-type')
        try:
            text = raw.data
        except Exception:
            text = ''

        har['text'] = text
        har['size'] = len(text)
        har['compression'] = -1
        return har

    def decode_HarRequest_from_HTTPResponse(self, raw):
        har = self.dict_class()
        har['method'] = 'UNKNOWN'
        har['url'] = 'UNKNOWN'
        har['headers'] = []
        har['cookies'] = []
        har['queryString'] = []
        har['postData'] = {'mimeType': 'UNKNOWN'}
        return har

    def decode_HarRequestBody_from_HTTPResponse(self, raw):
        return {'mimeType': 'UNKNOWN'}

    # Serialization

    def serialize_from_HTTPResponse(self, io, raw):
        # raw.status
        # raw.reason
        # raw.version
        # raw.headers.items()
        # raw.data
        pass

    # TODO: Deserialization


class RequestsCodec(object):

    dict_class = dict
    response_class = requests.Response
    modules = ['requests.models',
               'botocore.awsrequest',
               'botocore.vendored.requests.models',
               'one.web.http.objects']
    urllib3_codec = Urllib3Codec()

    def __init__(self):
        pass

    # Encoding

    def encode(self, har, raw_class):
        assert raw_class.__module__ in self.modules
        raw_type = raw_class.__name__
        har_type = har.__class__.__name__
        method_name = 'encode_%s_to_%s' % (har_type, raw_type)
        return getattr(self, method_name)(har)

    def encode_HarLog_to_Response(self, har):
        most = har.entries[:-1]
        most = list(map(self.encode_HarEntry_to_Response, most))
        last = har.entries[-1]
        last = self.encode_HarEntry_to_Response(last)
        last.history = most
        return last

    def encode_HarEntry_to_Request(self, har):
        return self.encode_HarRequest_to_Request(self, har.request)

    def encode_HarEntry_to_Response(self, har):
        from datetime import timedelta
        resp = self.encode_HarResponse_to_Response(har.response)
        resp.url = har.response.redirectURL or har.request.url
        resp.elapsed = timedelta(0, float(har.time) / 1000.0)
        resp.encoding = har._clientOptions.charset
        resp.raw = self.urllib3_codec.encode(
            har, urllib3r.response.HTTPResponse)
        return resp

    def encode_HarResponse_to_Response(self, har):
        ResponseCls = requests.Response
        HeadersCls = requests.structures.CaseInsensitiveDict
        CookiesCls = requests.cookies.RequestsCookieJar
        headers = list(map(lambda x: x.to_requests(), har.headers))
        cookies = list(map(lambda x: x.to_requests(), har.cookies))

        content = har.content.text
        if isinstance(content, six.text_type):
            content = content.encode('utf-8')

        resp = ResponseCls()
        resp._content = content
        resp._content_consumed = True
        resp.status_code = har.status
        resp.reason = har.statusText
        resp.cookies = CookiesCls(OrderedDict(cookies))
        resp.headers = HeadersCls(OrderedDict(headers))
        resp.raw = self.urllib3_codec.encode(
            har, urllib3r.response.HTTPResponse)
        resp.url = har.redirectURL
        resp.history = []
        # resp.elapsed = 0 # entry.time
        # resp.encoding = None # entry._clientOptions.charset

        return resp

    def encode_HarRequest_to_Request(self, har):
        RequestCls = requests.models.Request
        HeadersCls = dict
        CookiesCls = dict
        headers = list(map(lambda x: x.to_requests(), har.headers))
        cookies = list(map(lambda x: x.to_requests(), har.cookies))

        req = RequestCls(method=har.method, url=har.url)
        req.headers = HeadersCls(headers)
        req.cookies = CookiesCls(cookies) if har.cookies else None
        req.params = dict(map(harlib.utils.pair_from_obj, har.queryString))

        if har.postData:
            req.data = dict(map(harlib.utils.pair_from_obj,
                                har.postData.params))

        # req.hooks -- impossible
        # req.auth -- impossible
        # req.params, req.data, req.files = self.body_params()
        return req

    def encode_HarRequest_to_PreparedRequest(self, har):
        RequestCls = requests.models.PreparedRequest
        HeadersCls = dict
        CookiesCls = requests.cookies.RequestsCookieJar
        headers = list(map(lambda x: x.to_requests(), har.headers)) or []
        cookies = list(map(lambda x: x.to_requests(), har.cookies)) or []

        preq = RequestCls()
        preq.method = har.method
        preq.url = har.url
        preq.headers = HeadersCls(OrderedDict(headers))
        preq._cookies = CookiesCls(OrderedDict(cookies))

        if har.postData:
            preq.body = har.postData.text

        # req.hooks -- impossible
        # req.auth -- impossible
        # req.params, req.data, req.files = self.body_params()
        return preq

    def encode_HarRequest_to_AWSRequest(self, har):
        from botocore.awsrequest import AWSRequest
        kwargs = {}
        kwargs['method'] = har.method
        kwargs['url'] = har.url
        req = AWSRequest(**kwargs)
        return req

    def encode_HarRequest_to_AWSPreparedRequest(self, har):
        from botocore.awsrequest import AWSPreparedRequest
        req = self.encode_HarRequest_to_AWSRequest(har)
        preq = AWSPreparedRequest(req)
        return preq

    # Decoding

    def decode(self, raw, har_class):
        assert raw.__class__.__module__ in self.modules
        method_name = 'decode_%s_from_%s' % (
            har_class.__name__, raw.__class__.__name__)
        return getattr(self, method_name)(raw)

    def decode_HarLog_from_OneResponse(self, raw):
        resp = requests.models.Response()
        resp.__dict__ = raw.__dict__.copy()
        return self.decode_HarLog_from_Response(resp)

    def decode_HarLog_from_Response(self, raw):
        har = []
        if hasattr(raw, 'history') and raw.history and len(raw.history) > 0:
            for tome in raw.history:
                har.append(tome)
        har.append(raw)
        return har

    def decode_HarEntry_from_Response(self, raw):
        # started = (datetime.utcnow() - raw.elapsed).isoformat() + 'Z'

        har = self.dict_class()
        har['startedDateTime'] = None
        har['time'] = raw.elapsed.total_seconds() * 1000.0
        har['request'] = raw.request
        har['response'] = raw
        har['cache'] = {}
        har['timings'] = self.decode_HarTimings_from_Response(raw)
        har['connection'] = ''
        try:
            har['_clientOptions'] = \
                self.decode_HarClientOptions_from_Response(raw)
        except Exception:
            pass
        return har

    def decode_HarClientOptions_from_Response(self, raw):
        har = self.dict_class()
        har['charset'] = raw.encoding
        har['decodeContent'] = raw.raw.decode_content
        # har['contentRead'] = raw.raw._fp_bytes_read
        return har

    def decode_HarClientOptions_from_Session(self, raw):
        har = self.dict_class()
        proxies = self.dict_class()
        try:
            proxies['http'] = raw.adapters['http://'].proxy_manager.keys()[0]
        except Exception:
            pass
        try:
            proxies['https'] = raw.adapters['https://'].proxy_manager.keys()[0]
        except Exception:
            pass
        har['proxies'] = proxies
        return har

    def decode_HarResponse_from_Response(self, raw):
        har = self.dict_class()
        har['status'] = raw.status_code
        har['statusText'] = raw.reason
        try:
            har['httpVersion'] = \
                harlib.utils.render_http_version(raw.raw.version)
        except Exception:
            har['httpVersion'] = DEFAULT_VERSION

        har['headers'] = list(raw.headers.lower_items())
        har['cookies'] = list(raw.cookies.items()) if raw.cookies else []

        har['content'] = self.decode_HarResponseBody_from_Response(raw)
        har['redirectURL'] = raw.url if raw.url != raw.request.url else ''

        try:
            headers = '\r\n'.join(map(from_pair, har['headers']))
            har['headersSize'] = len(headers + '\r\n\r\n')
            har['bodySize'] = len(har['content']['text'])
        except Exception:
            har['headersSize'] = -1
            har['bodySize'] = -1

        if hasattr(raw, 'check_result'):
            har['_checkResult'] = raw.check_result
        if hasattr(raw, 'parse_result'):
            har['_parseResult'] = raw.parse_result

        return har

    def decode_HarResponseBody_from_Response(self, raw):
        har = self.dict_class()
        har['mimeType'] = raw.headers.get('content-type')
        try:
            text = raw.text
        except Exception:
            text = ''

        har['text'] = text
        har['size'] = len(text)
        har['compression'] = -1
        return har

    def decode_HarTimings_from_Response(self, raw):
        total = raw.elapsed.total_seconds() * 1000.0

        har = self.dict_class()
        har['connect'] = -1
        har['dns'] = -1
        har['receive'] = -1
        har['send'] = -1
        har['ssl'] = -1
        har['wait'] = total
        har['_total'] = total
        return har

    def decode_HarRequest_from_Request(self, raw):
        har = self.dict_class()
        har['method'] = raw.method
        har['url'] = raw.url
        har['httpVersion'] = 'HTTP/1.1'  # requests uses this default

        if raw.__class__.__name__ in ['Request', 'AWSRequest']:
            har['headers'] = list(raw.headers.items())
            har['cookies'] = list(raw.cookies.items()) if raw.cookies else []
        elif raw.__class__.__name__ in ['PreparedRequest',
                                        'AWSPreparedRequest']:
            if not raw.headers:
                har['headers'] = []
            elif hasattr(raw.headers, 'lower_items'):
                har['headers'] = list(raw.headers.lower_items())
            else:
                har['headers'] = list(raw.headers.items())
            har['cookies'] = list(raw._cookies.items()) if raw._cookies else []
        else:
            print("unknown request type")

        har['postData'] = self.decode_HarRequestBody(raw)
        har['queryString'] = self.decode_HarQueryStringParams(raw)

        try:
            headers = '\r\n'.join(map(from_pair, har['headers']))
            har['headersSize'] = len(headers + '\r\n\r\n')
            har['bodySize'] = len(har['postData']['text'])
        except Exception:
            har['headersSize'] = -1
            har['bodySize'] = -1

        if hasattr(raw, 'origin'):
            har['_originURL'] = raw.origin
        if hasattr(raw, 'epid'):
            har['_endpointID'] = raw.epid

        return har

    def decode_HarRequestBody(self, raw):
        if raw.__class__.__name__ in ['Request', 'AWSRequest']:
            return self.decode_HarRequestBody_from_Request(raw)
        elif raw.__class__.__name__ in ['PreparedRequest',
                                        'AWSPreparedRequest']:
            return self.decode_HarRequestBody_from_PreparedRequest(raw)
        else:
            raise ValueError(raw.__class__.__name__)

    def decode_HarRequestBody_from_Request(self, raw):
        body_params = {}
        if isinstance(raw.data, dict):
            body_params.update(raw.data)
        if isinstance(raw.files, dict):
            body_params.update(raw.files)

        har = self.dict_class()
        har['mimeType'] = 'UNKNOWN'
        try:
            har['text'] = harlib.utils.encode_query(body_params)
        except Exception:
            har['text'] = ''
        har['_size'] = len(har['text'])

        har['params'] = body_params.items()

        if raw.headers:
            if raw.headers.get('Content-Type'):
                har['mimeType'] = raw.headers.get('Content-Type')

        return har

    def decode_HarRequestBody_from_PreparedRequest(self, raw):
        body_text = raw.body or ''

        har = self.dict_class()
        if not raw.headers:
            har['mimeType'] = 'unknown'
        else:
            har['mimeType'] = raw.headers.get('Content-Type')
        har['text'] = body_text or ''
        har['_size'] = len(har['text'])

        if not har['mimeType']:
            har['params'] = []
        elif har['mimeType'].startswith('multipart/form-data'):
            try:
                har['params'] = harlib.utils.decode_multipart(
                    har['text'], har['mimeType'])
            except Exception:
                har['params'] = []
        elif har['mimeType'].startswith('application/x-www-form-urlencoded'):
            try:
                query = '?' + har['text']
                har['params'] = harlib.utils.decode_query(query)
            except Exception:
                har['params'] = []
        elif har['mimeType'].startswith('application/json'):
            try:
                har['params'] = harlib.utils.decode_json(har['text'])
            except Exception:
                har['params'] = []
        return har

    def decode_HarQueryStringParams(self, raw):
        prefix = 'decode_HarQueryStringParams_from_'
        return getattr(self, prefix + raw.__class__.__name__)(raw)

    def decode_HarQueryStringParams_from_Request(self, raw):
        return list(map(harlib.utils.dict_from_pair, raw.params.items()))

    def decode_HarQueryStringParams_from_PreparedRequest(self, raw):
        try:
            query = '?' + raw.url.split('?', 1)[1]
            return harlib.utils.decode_query(query)
        except Exception:
            return []

    decode_HarQueryStringParams_from_AWSRequest = \
        decode_HarQueryStringParams_from_Request
    decode_HarQueryStringParams_from_AWSPreparedRequest = \
        decode_HarQueryStringParams_from_PreparedRequest

    decode_HarRequest_from_AWSRequest = decode_HarRequest_from_Request
    decode_HarRequest_from_AWSPreparedRequest = decode_HarRequest_from_Request
    decode_HarRequest_from_PreparedRequest = decode_HarRequest_from_Request

    # Serialization

    def serialize(self, io, raw, har_class):
        if raw is None:
            return
        assert raw.__class__.__module__ in self.modules
        method_name = 'serialize_%s_from_%s' % (
            har_class.__name__, raw.__class__.__name__)
        if isinstance(raw, Exception):
            method_name = 'serialize_%s_from_%s' % (
                har_class.__name__, Exception.__name__)
        return getattr(self, method_name)(io, raw)

    def serialize_HarHeader_from_tuple(self, io, raw):
        name = raw[0]
        if isinstance(name, six.text_type):
            name = name.encode('utf-8')
        value = raw[1]
        if isinstance(value, six.text_type):
            value = value.encode('utf-8')

        io.write(b'\t\t{')
        io.write(b'"name": "' + six.binary_type(name) + b'", ')
        io.write(b'"value": "' + six.binary_type(value) + b'"')
        io.write(b'}')  # newline handled by separate()

    def serialize_HarRequest_from_PreparedRequest(self, io, raw):
        # raw is a PreparedRequest
        # raw.url
        # raw.headers
        # raw.headers.lower_items
        # raw._cookies
        # raw.body

        # raw is a Request
        # raw.status
        # raw.params.items()
        # raw.data
        # raw.files
        # raw.json?
        # raw.json
        # raw.headers.items
        # raw.cookies

        if raw.__class__.__name__ in ['Request', 'AWSRequest']:
            cookies = list(raw.cookies.items()) if raw.cookies else []
            headers = list(raw.headers.items())
        elif raw.__class__.__name__ in ['PreparedRequest',
                                        'AWSPreparedRequest']:
            cookies = list(raw._cookies.items()) if raw._cookies else []
            headers = list(raw.headers.lower_items())
        else:
            cookies = []
            headers = []

        def f(x):
            return x
        f(cookies)
        method = raw.method
        if isinstance(method, six.text_type):
            method = method.encode('utf-8')
        url = raw.url
        if isinstance(url, six.text_type):
            url = url.encode('utf-8')

        # usually 4 tabs, omitted
        io.write(b'"request": {\n')
        io.write(b'\t"method": "' + six.binary_type(method) + b'",\n')
        io.write(b'\t"url": "' + six.binary_type(url) + b'",\n')
        io.write(b'\t"httpVersion": "HTTP/1.1",\n')
        io.write(b'\t"cookies": [\n')
        io.write(b'\t],\n')
        io.write(b'\t"headers": [\n')

        for _, last, header in separate(headers):
            try:
                self.serialize_HarHeader_from_tuple(
                    io, (header[0].title(), header[1]))
            except Exception as err:
                print(repr(err))
            if last:
                io.write(b'\n')
            else:
                io.write(b',\n')

        ctype = raw.headers.get('content-type')
        if isinstance(ctype, six.text_type):
            ctype = ctype.encode('utf-8')

        io.write(b'\t],\n')
        io.write(b'\t"queryString": [\n')
        io.write(b'\t],\n')
        io.write(b'\t"postData": {\n')
        io.write(b'\t\t"mimeType": "' +
                 six.binary_type(ctype) + b'",\n')
        io.write(b'\t\t"size": -1,\n')
        io.write(b'\t\t"text": ""\n')
        io.write(b'\t},\n')
        io.write(b'\t"headersSize": -1,\n')
        io.write(b'\t"bodySize": -1\n')
        io.write(b'},\n')

    serialize_HarRequest_from_Request = \
        serialize_HarRequest_from_PreparedRequest

    def get_EnvironmentError_from_Exception(self, raw):

        if isinstance(raw, requests.exceptions.ConnectionError):
            suberr = self.get_EnvironmentError_from_Exception(raw.message)
            errno = suberr.errno
            strerror = suberr.strerror
            filename = suberr.filename
            return EnvironmentError(errno, strerror, filename)
        elif isinstance(raw, requests.packages.urllib3.
                        exceptions.MaxRetryError):
            suberr = self.get_EnvironmentError_from_Exception(raw.reason)
            errno = suberr.errno
            strerror = suberr.strerror
            filename = raw.url
            return EnvironmentError(errno, strerror, filename)
        elif isinstance(raw, requests.packages.urllib3.
                        exceptions.NewConnectionError):
            assert isinstance(raw.message, six.string_types)
            if 'Failed to establish a new connection: ' in raw.message:
                import re
                _, env_str = raw.message.split(
                    'Failed to establish a new connection: ', 1)
                env_re = re.compile('\[Errno (?P<errno>\d{0,6})\] '
                                    '(?P<strerror>.*)')
                match = env_re.match(env_str)
                errno = match.group('errno')
                strerror = match.group('strerror')
                filename = ''
            else:
                errno = 'UNKNOWN'
                strerror = 'UNKNOWN'
                filename = ''
            return EnvironmentError(errno, strerror, filename)
        else:
            print("unknown error in requests decoder")

    def serialize_HarResponse_from_Exception(self, io, raw):
        err = self.get_EnvironmentError_from_Exception(raw)

        status = str(err.errno)
        if isinstance(status, six.text_type):
            status = status.encode('utf-8')
        reason = err.strerror
        if isinstance(reason, six.text_type):
            reason = reason.encode('utf-8')

        # usually 4 tabs, omitted
        io.write(b'"response": {\n')
        io.write(b'\t"status": ' + six.binary_type(err.errno) + b',\n')
        io.write(b'\t"statusText": "' +
                 six.binary_type(err.strerror) + b'",\n')
        io.write(b'\t"httpVersion": "HTTP/1.1",\n')
        io.write(b'\t"cookies": [\n')
        io.write(b'\t],\n')
        io.write(b'\t"headers": [\n')
        io.write(b'\t],\n')
        io.write(b'\t"content": {\n')
        io.write(b'\t\t"mimeType": "application/x-error",\n')
        io.write(b'\t\t"size": -1,\n')
        io.write(b'\t\t"text": ')
        io.write(six.binary_type(json.dumps(repr(raw))))
        io.write(b'\n\t},\n')

        io.write(b'\t"redirectURL": "' +
                 six.binary_type(err.filename) + '",\n')
        io.write(b'\t"headersSize": -1,\n')
        io.write(b'\t"bodySize": -1\n')
        io.write(b'},\n')

    def serialize_HarResponse_from_Response(self, io, raw):
        # raw.status_code
        # raw.reason
        # raw.raw.version
        # raw.headers.lower_items()
        # raw.url
        # raw.history
        # raw.elapsed
        # raw.request
        # raw.encoding
        # raw.request.url
        status = str(raw.status_code)
        if isinstance(status, six.text_type):
            status = status.encode('utf-8')
        reason = raw.reason
        if isinstance(reason, six.text_type):
            reason = reason.encode('utf-8')

        # usually 4 tabs, omitted
        io.write(b'"response": {\n')
        io.write(b'\t"status": ' + six.binary_type(status) + b',\n')
        io.write(b'\t"statusText": "' + six.binary_type(reason) + b'",\n')
        io.write(b'\t"httpVersion": "HTTP/1.1",\n')
        io.write(b'\t"cookies": [\n')
        io.write(b'\t],\n')
        io.write(b'\t"headers": [\n')

        for _, last, header in separate(list(raw.headers.lower_items())):
            self.serialize_HarHeader_from_tuple(
                io, (header[0].title(), header[1]))
            if last:
                io.write(b'\n')
            else:
                io.write(b',\n')

        ctype = raw.headers.get('content-type')
        if isinstance(ctype, six.text_type):
            ctype = ctype.encode('utf-8')

        io.write(b'\t],\n')
        io.write(b'\t"content": {\n')
        io.write(b'\t\t"mimeType": "' + six.binary_type(ctype) + b'",\n')
        io.write(b'\t\t"size": -1,\n')
        io.write(b'\t\t"text": ')
        if six.PY3:
            io.write(six.binary_type(json.dumps(raw.text).encode('utf-8')))
        else:
            io.write(six.binary_type(json.dumps(raw.content)))
        io.write(b'\n\t},\n')

        io.write(b'\t"redirectURL": "",\n')
        io.write(b'\t"headersSize": -1,\n')
        io.write(b'\t"bodySize": -1\n')
        io.write(b'},\n')
        pass

    def serialize_HarTimings_from_Response(self, io, raw):
        total = raw.elapsed.total_seconds() * 1000.0
        total = six.text_type(total).encode('utf-8')
        # usually 4 tabs, omitted
        io.write(b'"timings": {\n')
        io.write(b'\t"send": -1,\n')
        io.write(b'\t"wait": ' + six.binary_type(total) + b',\n')
        io.write(b'\t"receive": -1\n')
        io.write(b'},\n')

    def serialize_HarEntry_from_Response(self, io, raw):
        from datetime import datetime
        started = datetime.now().isoformat().encode('utf-8')
        try:
            total = raw.elapsed.total_seconds() * 1000.0
        except Exception:
            total = 0
        total = str(total).encode('utf-8')

        # usually 3 tabs, omitted
        io.write(b'{\n')
        io.write(b'"startedDateTime": "' + six.binary_type(started) + b'",\n')
        io.write(b'"time": "' + six.binary_type(total) + b'",\n')
        self.serialize_HarRequest_from_PreparedRequest(io, raw.request)
        if hasattr(raw, '_error'):
            self.serialize_HarResponse_from_Exception(io, raw._error)
        else:
            self.serialize_HarResponse_from_Response(io, raw)
            self.serialize_HarTimings_from_Response(io, raw)
        io.write(b'"cache": {}\n')
        io.write(b'}')  # newline handled by separate()

    def serialize_HarLog_from_Responses(self, io, raws):
        from harlib import __version__
        io.write(b'{\n\t"log": {\n')
        io.write(b'\t\t"version": "1.2",\n')
        io.write(b'\t\t"creator": {\n')
        io.write(b'\t\t\t"name": "harlib",\n')
        io.write(b'\t\t\t"version": "' + six.binary_type(__version__) + b'"\n')
        io.write(b'\t\t},\n')
        io.write(b'\t\t"entries": [\n')

        for _, last, raw in separate(list(raws)):
            self.serialize_HarEntry_from_Response(io, raw)
            if last:
                io.write(b'\n')
            else:
                io.write(b',\n')

        io.write(b'\t\t]\n')
        io.write(b'\t}\n}\n')

    # TODO: Deserialization
