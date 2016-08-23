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
from requests.packages import urllib3 as urllib3r
import harlib
import json
import requests
import six
import urllib3
from datetime import datetime
from six.moves import http_client
from harlib.codecs.httplib import HttplibCodec
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

KEEP_SIZE = False
DEFAULT_VERSION = 'HTTP/0'

def separate(iterable):
    first = True
    last = False
    try:
        length = len(iterable)
    except:
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
    modules = ['urllib3.response', 'requests.packages.urllib3.response']
    httplib_codec = HttplibCodec()

    def __init__(self):
        pass

    ##########################################################################################
    ## Encoding

    def encode(self, har, raw_class):
        assert raw_class.__module__ in self.modules
        method_name = 'encode_%s_to_%s' % (
            har.__class__.__name__, raw_class.__name__)
        return getattr(self, method_name)(har)

    def encode_HarEntry_to_HTTPResponse(self, har):
        resp = self.encode_HarResponse_to_HTTPResponse(har.response)
        resp.strict = har._clientOptions.failOnError
        resp.decode_content = har._clientOptions.decodeContent
        resp.original_response = self.httplib_codec.encode(har, http_client.HTTPResponse)
        #resp._fp_bytes_read = self._clientOptions.contentRead
        #resp.connection = None
        #resp.pool = None
        return resp

    def encode_HarResponse_to_HTTPResponse(self, har):
        headers = dict(map(harlib.utils.pair_from_obj, har.headers))

        resp = self.response_class(
            body = None,
            headers = headers,
            status = har.status,
            version = harlib.utils.parse_http_version(har.httpVersion),
            reason = har.statusText,
            preload_content = False,
        )

        return resp

    ##########################################################################################
    ## Decoding

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
        har['_clientOptions'] = self.decode_HarClientOptions_from_HTTPResponse(raw)
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
        except:
            har['httpVersion'] = DEFAULT_VERSION

        har['headers'] = list(raw.headers.items())
        har['cookies'] = []

        har['content'] = self.decode_HarResponseBody_from_HTTPResponse(raw)
        har['redirectURL'] = ''

        if KEEP_SIZE:
            try:
                headers = '\r\n'.join(map(lambda x: '%s: %s' % x, har['headers']))
                har['headersSize'] = len(headers + '\r\n\r\n')
                har['bodySize'] = len(har['content']['text'])
            except:
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
        except:
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

    #def decode_HarPostDataParam_from_RequestField(self, raw, name=None):
    #if isinstance(obj, urllib3.fields.RequestField):
    #    har['value'] = obj.data
    #    har['fileName'] = obj._filename
    #    har['contentType'] = obj.headers.get('content-type')
    #    if hasattr(obj, 'headers'):
    #        if isinstance(obj.headers, Mapping):
    #            har['_headers'] = map(HarHeader, obj.headers.items())

    #    d = dict()
    #    if name:
    #        d['name'] = name
    #    else:
    #        d['name'] = raw[0]
    #        raw = raw[1:]
    #
    #    pass
    #
    #def decode_HarPostDataParam_from_RequestField(self, raw):
    #    pass
    #
    #def decode_HarPostDataParam_from_tuple(self, raw):
    #    pass


    ##########################################################################################
    ## Serialization

    def serialize_from_HTTPResponse(self, io, raw):
        # raw.status
        # raw.reason
        # raw.version
        # raw.headers.items()
        # raw.data
        pass

    ##########################################################################################
    ## TODO: Deserialization

class RequestsCodec(object):

    dict_class = dict
    response_class = requests.Response
    modules = ['requests.models', 'one.web.http.objects']
    urllib3_codec = Urllib3Codec()

    def __init__(self):
        pass

    ##########################################################################################
    ## Encoding

    def encode(self, har, raw_class):
        assert raw_class.__module__ in self.modules
        raw_type = raw_class.__name__
        har_type = har.__class__.__name__
        method_name = 'encode_%s_to_%s' % (har_type, raw_type)
        return getattr(self, method_name)(har)


    def encode_HarEntry_to_Response(self, har):
        from datetime import timedelta
        resp = self.encode_HarResponse_to_Response(har.response)
        resp.url = har.response.redirectURL or har.request.url
        resp.elapsed = timedelta(0, float(har.time)/1000.0)
        resp.encoding = har._clientOptions.charset
        resp.raw = self.urllib3_codec.encode(har, urllib3r.response.HTTPResponse)
        return resp

    def encode_HarResponse_to_Response(self, har):
        ResponseCls = requests.Response
        HeadersCls = requests.structures.CaseInsensitiveDict
        CookiesCls = requests.cookies.RequestsCookieJar
        headers = map(lambda x: x.to_requests(), har.headers)
        cookies = map(lambda x: x.to_requests(), har.cookies)

        resp = ResponseCls()
        resp._content = har.content.text
        resp._content_consumed = True
        resp.status_code = har.status
        resp.reason = har.statusText
        resp.cookies = CookiesCls(OrderedDict(cookies))
        resp.headers = HeadersCls(OrderedDict(headers))
        resp.raw = self.urllib3_codec.encode(har, urllib3r.response.HTTPResponse)
        resp.url = har.redirectURL
        resp.history = []
        #resp.elapsed = 0 # entry.time
        #resp.encoding = None # entry._clientOptions.charset

        return resp

    def encode_HarRequest_to_Request(self, har):
        RequestCls = requests.models.Request
        HeadersCls = dict
        CookiesCls = dict
        headers = map(lambda x: x.to_requests(), har.headers)
        cookies = map(lambda x: x.to_requests(), har.cookies)

        req = RequestCls(method = har.method, url = har.url)
        req.headers = HeadersCls(headers)
        req.cookies = HeadersCls(cookies) if har.cookies else None
        req.params = dict(map(harlib.utils.pair_from_obj, har.queryString))

        if har.postData:
            req.data = dict(map(harlib.utils.pair_from_obj, har.postData.params))

        #req.hooks -- impossible
        #req.auth -- impossible
        #req.params, req.data, req.files = self.body_params()
        return req

    def encode_HarRequest_to_PreparedRequest(self, har):
        RequestCls = requests.models.PreparedRequest
        HeadersCls = dict
        CookiesCls = requests.cookies.RequestsCookieJar
        headers = map(lambda x: x.to_requests(), har.headers) or []
        cookies = map(lambda x: x.to_requests(), har.cookies) or []

        preq = RequestCls()
        preq.method = har.method
        preq.url = har.url
        preq.headers = HeadersCls(OrderedDict(headers))
        preq._cookies = CookiesCls(OrderedDict(cookies))

        if har.postData:
            preq.body = har.postData.text

        #req.hooks -- impossible
        #req.auth -- impossible
        #req.params, req.data, req.files = self.body_params()
        return preq

    ##########################################################################################
    ## Decoding

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
        from datetime import datetime
        started = (datetime.utcnow() - raw.elapsed).isoformat() + 'Z'

        har = self.dict_class()
        har['startedDateTime'] = None
        har['time'] = raw.elapsed.total_seconds()*1000.0
        har['request'] = raw.request
        har['response'] = raw
        har['cache'] = {}
        har['timings'] = self.decode_HarTimings_from_Response(raw)
        har['connection'] = ''
        try:
            har['_clientOptions'] = self.decode_HarClientOptions_from_Response(raw)
        except:
            pass
        return har

    def decode_HarClientOptions_from_Response(self, raw):
        har = self.dict_class()
        har['charset'] = raw.encoding
        har['decodeContent'] = raw.raw.decode_content
        #har['contentRead'] = raw.raw._fp_bytes_read
        return har

    def decode_HarClientOptions_from_Session(self, raw):
        har = self.dict_class()
        proxies = self.dict_class()
        try:
            proxies['http'] = raw.adapters['http://'].proxy_manager.keys()[0]
        except:
            pass
        try:
            proxies['https'] = raw.adapters['https://'].proxy_manager.keys()[0]
        except:
            pass
        har['proxies'] = proxies
        return har

    def decode_HarResponse_from_Response(self, raw):
        har = self.dict_class()
        har['status'] = raw.status_code
        har['statusText'] = raw.reason
        try:
            har['httpVersion'] = harlib.utils.render_http_version(raw.raw.version)
        except:
            har['httpVersion'] = DEFAULT_VERSION

        har['headers'] = list(raw.headers.lower_items())
        har['cookies'] = list(raw.cookies.items()) if raw.cookies else []

        har['content'] = self.decode_HarResponseBody_from_Response(raw)
        har['redirectURL'] = raw.url if raw.url != raw.request.url else ''

        try:
            headers = '\r\n'.join(map(from_pair, har['headers']))
            har['headersSize'] = len(headers + '\r\n\r\n')
            har['bodySize'] = len(har['content']['text'])
        except:
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
        except:
            text = ''

        har['text'] = text
        har['size'] = len(text)
        har['compression'] = -1
        return har

    def decode_HarTimings_from_Response(self, raw):
        total = raw.elapsed.total_seconds()*1000.0

        har = self.dict_class()
        har['connect'] = -1
        har['dns'] = -1
        har['receive'] = -1
        har['send']= -1
        har['ssl'] = -1
        har['wait'] = total
        har['_total'] = total
        return har

    def decode_HarRequest_from_Request(self, raw):
        har = self.dict_class()
        har['method'] = raw.method
        har['url'] = raw.url
        har['httpVersion'] = 'HTTP/1.1' # requests uses this default

        if isinstance(raw, requests.models.Request):
            har['headers'] = list(raw.headers.items())
            har['cookies'] = list(raw.cookies.items()) if raw.cookies else []
        elif isinstance(raw, requests.models.PreparedRequest):
            har['headers'] = list(raw.headers.lower_items())
            har['cookies'] = list(raw._cookies.items()) if raw._cookies else []
        else:
            print("unknown request type")

        har['postData'] = self.decode_HarRequestBody(raw)
        har['queryString'] = self.decode_HarQueryStringParams(raw)

        try:
            headers = '\r\n'.join(map(from_pair, har['headers']))
            har['headersSize'] = len(headers + '\r\n\r\n')
            har['bodySize'] = len(har['postData']['text'])
        except:
            har['headersSize'] = -1
            har['bodySize'] = -1

        if hasattr(raw, 'origin'):
            har['_originURL'] = raw.origin
        if hasattr(raw, 'epid'):
            har['_endpointID'] = raw.epid

        return har

    def decode_HarRequestBody(self, raw):
        if isinstance(raw, requests.models.Request):
            return self.decode_HarRequestBody_from_Request(raw)
        elif isinstance(raw, requests.models.PreparedRequest):
            return self.decode_HarRequestBody_from_PreparedRequest(raw)
        else:
            raise ValueError

    def decode_HarRequestBody_from_Request(self, raw):
        body_params = {}
        body_params.update(raw.data)
        body_params.update(raw.files)

        har = self.dict_class()
        har['mimeType'] = 'UNKNOWN'
        try:
            har['text'] = harlib.utils.encode_query(body_params)
        except:
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
        har['mimeType'] = raw.headers.get('Content-Type')
        har['text'] = body_text or ''
        har['_size'] = len(har['text'])

        if not har['mimeType']:
            har['params'] = []
        elif har['mimeType'].startswith('multipart/form-data'):
            try:
                har['params'] = harlib.utils.decode_multipart(har['text'], har['mimeType'])
            except Exception as err:
                har['params'] = []
        elif har['mimeType'].startswith('application/x-www-form-urlencoded'):
            try:
                query = '?' + har['text']
                har['params'] = harlib.utils.decode_query(query)
            except Exception as err:
                har['params'] = []
        elif har['mimeType'].startswith('application/json'):
            try:
                har['params'] = harlib.utils.decode_json(har['text'])
            except Exception as err:
                har['params'] = []
        return har

    def decode_HarQueryStringParams(self, raw):
        if isinstance(raw, requests.models.Request):
            return self.decode_HarQueryStringParams_from_Request(raw)
        elif isinstance(raw, requests.models.PreparedRequest):
            return self.decode_HarQueryStringParams_from_PreparedRequest(raw)
        else:
            raise ValueError

    def decode_HarQueryStringParams_from_Request(self, raw):
        return map(harlib.utils.dict_from_pair, raw.params.items())

    def decode_HarQueryStringParams_from_PreparedRequest(self, raw):
        try:
            query = '?' + raw.url.split('?', 1)[1]
            return harlib.utils.decode_query(query)
        except:
            return []

    decode_HarRequest_from_PreparedRequest = decode_HarRequest_from_Request

    ##########################################################################################
    ## Serialization

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
        io.write('\t\t{')
        io.write('"name": "' + six.binary_type(raw[0]) + '", ')
        io.write('"value": "' + six.binary_type(raw[1]) + '"')
        io.write('}') # newline handled by separate()

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

        # usually 4 tabs, omitted
        io.write('"request": {\n')
        io.write('\t"method": "' + six.binary_type(raw.method) + '",\n')
        io.write('\t"url": "' + six.binary_type(raw.url) + '",\n')
        io.write('\t"httpVersion": "HTTP/1.1",\n')
        io.write('\t"cookies": [\n')
        io.write('\t],\n')
        io.write('\t"headers": [\n')

        if isinstance(raw, requests.models.Request):
            cookies = list(raw.cookies.items()) if raw.cookies else []
            headers = list(raw.headers.items())
        elif isinstance(raw, requests.models.PreparedRequest):
            cookies = list(raw._cookies.items()) if raw._cookies else []
            headers = list(raw.headers.lower_items())
        else:
            cookies = []
            headers = []
        for _, last, header in separate(headers):
            try:
                self.serialize_HarHeader_from_tuple(io, (header[0].title(), header[1]))
            except Exception as err:
                print(repr(err))
            if last:
                io.write('\n')
            else:
                io.write(',\n')

        io.write('\t],\n')
        io.write('\t"queryString": [\n')
        io.write('\t],\n')
        io.write('\t"postData": {\n')
        io.write('\t\t"mimeType": "' + six.binary_type(raw.headers.get('content-type')) + '",\n')
        io.write('\t\t"size": -1,\n')
        io.write('\t\t"text": ""\n')
        io.write('\t},\n')
        io.write('\t"headersSize": -1,\n')
        io.write('\t"bodySize": -1\n')
        io.write('},\n')

    serialize_HarRequest_from_Request = serialize_HarRequest_from_PreparedRequest

    def get_EnvironmentError_from_Exception(self, raw):

        if isinstance(raw, requests.exceptions.ConnectionError):
            suberr = self.get_EnvironmentError_from_Exception(raw.message)
            errno = suberr.errno
            strerror = suberr.strerror
            filename = suberr.filename
            return EnvironmentError(errno, strerror, filename)
        elif isinstance(raw, requests.packages.urllib3.exceptions.MaxRetryError):
            suberr = self.get_EnvironmentError_from_Exception(raw.reason)
            errno = suberr.errno
            strerror = suberr.strerror
            filename = raw.url
            return EnvironmentError(errno, strerror, filename)
        elif isinstance(raw, requests.packages.urllib3.exceptions.NewConnectionError):
            assert isinstance(raw.message, six.string_types)
            if 'Failed to establish a new connection: ' in raw.message:
                import re
                _, env_str = raw.message.split('Failed to establish a new connection: ', 1)
                env_re = re.compile('\[Errno (?P<errno>\d{0,6})\] (?P<strerror>.*)')
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
            print(0, repr(raw))
            print(1, repr(raw.args))
            print(2, repr(vars(raw)))
        #while not isinstance(raw, six.string_types):
        #    raw = raw.message

    def serialize_HarResponse_from_Exception(self, io, raw):
        err = self.get_EnvironmentError_from_Exception(raw)

        # usually 4 tabs, omitted
        io.write('"response": {\n')
        io.write('\t"status": ' + six.binary_type(err.errno) + ',\n')
        io.write('\t"statusText": "' + six.binary_type(err.strerror) + '",\n')
        io.write('\t"httpVersion": "HTTP/1.1",\n')
        io.write('\t"cookies": [\n')
        io.write('\t],\n')
        io.write('\t"headers": [\n')
        io.write('\t],\n')
        io.write('\t"content": {\n')
        io.write('\t\t"mimeType": "application/x-error",\n')
        io.write('\t\t"size": -1,\n')
        io.write('\t\t"text": ')
        io.write(six.binary_type(json.dumps(repr(raw))))
        io.write('\n\t},\n')

        io.write('\t"redirectURL": "' + six.binary_type(err.filename) + '",\n')
        io.write('\t"headersSize": -1,\n')
        io.write('\t"bodySize": -1\n')
        io.write('},\n')

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

        # usually 4 tabs, omitted
        io.write('"response": {\n')
        io.write('\t"status": ' + six.binary_type(raw.status_code) + ',\n')
        io.write('\t"statusText": "' + six.binary_type(raw.reason) + '",\n')
        io.write('\t"httpVersion": "HTTP/1.1",\n')
        io.write('\t"cookies": [\n')
        io.write('\t],\n')
        io.write('\t"headers": [\n')

        for _, last, header in separate(list(raw.headers.lower_items())):
            self.serialize_HarHeader_from_tuple(io, (header[0].title(), header[1]))
            if last:
                io.write('\n')
            else:
                io.write(',\n')

        io.write('\t],\n')
        io.write('\t"content": {\n')
        io.write('\t\t"mimeType": "' + six.binary_type(raw.headers.get('content-type')) + '",\n')
        io.write('\t\t"size": -1,\n')
        io.write('\t\t"text": ')
        io.write(six.binary_type(json.dumps(raw.content)))
        io.write('\n\t},\n')

        io.write('\t"redirectURL": "",\n')
        io.write('\t"headersSize": -1,\n')
        io.write('\t"bodySize": -1\n')
        io.write('},\n')
        pass

    def serialize_HarTimings_from_Response(self, io, raw):
        total = raw.elapsed.total_seconds()*1000.0
        # usually 4 tabs, omitted
        io.write('"timings": {\n')
        io.write('\t"send": -1,\n')
        io.write('\t"wait": ' + six.binary_type(total) + ',\n')
        io.write('\t"receive": -1\n')
        io.write('},\n')


    def serialize_HarEntry_from_Response(self, io, raw):
        started = datetime.now().isoformat()
        try:
            total = raw.elapsed.total_seconds()*1000.0
        except:
            total = 0

        # usually 3 tabs, omitted
        io.write('{\n')
        io.write('"startedDateTime": "' + six.binary_type(started) + '",\n')
        io.write('"time": "' + six.binary_type(total) + '",\n')
        self.serialize_HarRequest_from_PreparedRequest(io, raw.request)
        if hasattr(raw, '_error'):
            self.serialize_HarResponse_from_Exception(io, raw._error)
        else:
            self.serialize_HarResponse_from_Response(io, raw)
            self.serialize_HarTimings_from_Response(io, raw)
        io.write('"cache": {}\n')
        io.write('}') # newline handled by separate()

    def serialize_HarLog_from_Responses(self, io, raws):
        from harlib import __version__
        io.write('{\n\t"log": {\n')
        io.write('\t\t"version": "1.2",\n')
        io.write('\t\t"creator": {\n')
        io.write('\t\t\t"name": "harlib",\n')
        io.write('\t\t\t"version": "' + six.binary_type(__version__) + '"\n')
        io.write('\t\t},\n')
        io.write('\t\t"entries": [\n')

        for _, last, raw in separate(list(raws)):
            self.serialize_HarEntry_from_Response(io, raw)
            if last:
                io.write('\n')
            else:
                io.write(',\n')

        io.write('\t\t]\n')
        io.write('\t}\n}\n')

    ##########################################################################################
    ## TODO: Deserialization
